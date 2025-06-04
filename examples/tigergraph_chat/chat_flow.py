from typing import Dict, List
from pydantic import BaseModel, Field
import json
import logging

from crewai.flow.flow import Flow, router, or_, start
from crewai.tools import BaseTool
from tigergraph_mcp import TigerGraphToolName
from panel.chat import ChatMessage

from chat_session_manager import chat_session
from crews import (
    PlannerCrew,
    SchemaCreationCrews,
    DataLoadingCrews,
    ToolExecutorCrews,
)

logger = logging.getLogger(__name__)
verbose = False
S3_ANONYMOUS_SOURCE_NAME = "s3_anonymous_source"


class ChatSessionState(BaseModel):
    # Conversation and Task Management
    conversation_history: List[str] = Field(default_factory=list)
    tool_registry: Dict[str, BaseTool] = Field(default_factory=dict)
    task_plan: List[Dict[str, str]] = Field(
        default_factory=list
    )  # e.g., [{"tool_name": ..., "command": ...}]
    current_task_index: int = 0  # Index of the currently executing task
    current_tool_name: str = ""  # Tool name of the currently executing task
    current_command: str = ""  # Command of the currently executing task

    # Onboarding Data Preview
    last_user_file_input: str = ""
    last_data_preview: str = ""  # Output from the most recent data preview
    is_from_onboarding: bool = (
        False  # Set to True if it was generated during onboarding
    )

    # Schema Creation State
    current_schema_draft: str = ""  # Latest schema draft

    # Loading Job State
    current_loading_job_draft: str = ""  # Latest loading job draft


class ChatFlow(Flow[ChatSessionState]):
    # ------------------------------ Main Workflow ------------------------------
    @start()
    def initialize_session(self):
        logger.info("Session initialized.")

    @router(
        or_(initialize_session, "on_user_command_received", "on_user_input_updated")
    )
    def analyze_and_evaluate_plan(self):
        logger.debug("Matching tool(s) from conversation...")

        last_command = ""
        if len(self.state.conversation_history) > 0:
            last_command = self.state.conversation_history[
                len(self.state.conversation_history) - 1
            ]
        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "last_command": last_command,
            "tools": str(self.state.tool_registry.keys()),
        }

        crew = PlannerCrew(verbose=verbose).onboarding_detector_crew()
        output = crew.kickoff(inputs=inputs)
        raw_output = output.raw.strip()
        logger.debug(f"Onboarding detector raw output: {raw_output}")

        if raw_output == "onboarding":
            return "onboarding_required"

        crew = PlannerCrew(verbose=verbose).planning_crew()
        output = crew.kickoff(inputs=inputs)
        raw_output = output.raw.strip()
        logger.debug(f"Planner raw output: {raw_output}")

        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, list) and all(
                isinstance(step, dict) and "tool_name" in step and "command" in step
                for step in parsed
            ):
                valid_steps = [
                    step
                    for step in parsed
                    if step["tool_name"] in self.state.tool_registry
                ]
                self.state.task_plan = valid_steps
                self.state.current_task_index = 0
                logger.debug(
                    f"Planner returned valid tool-command steps: {valid_steps}"
                )

            else:
                logger.warning("Planner output did not match expected formats.")
                self.state.task_plan = []

        except json.JSONDecodeError:
            logger.warning("No valid tools matched.")
            self.state.task_plan = []

        if not self.state.task_plan:
            return "tool_matching_failed"

        self._send_message(f"🧭 Task plan: {str(self.state.task_plan)}")
        return "task_plan_ready"

    @router(or_("task_plan_ready", "on_task_completed"))
    def check_task_plan_progress(self):
        if self.state.current_task_index >= len(self.state.task_plan):
            self.state.task_plan = []
            self.state.current_task_index = 0
            return "no_tasks_remaining"
        else:
            return "more_tasks_remaining"

    @router("more_tasks_remaining")
    def evaluate_task_type(self):
        task_step = self.state.task_plan[self.state.current_task_index]
        self.state.current_tool_name = task_step.get("tool_name", "")
        self.state.current_command = task_step.get("command", "")
        tool_enum = TigerGraphToolName.from_value(self.state.current_tool_name)

        if not tool_enum:
            return "task_type_unclear"
        if tool_enum == TigerGraphToolName.CREATE_SCHEMA:
            return "task_type_create_schema"
        if tool_enum == TigerGraphToolName.LOAD_DATA:
            return "task_type_load_data"
        else:
            return "task_type_general_tool"

    @router("task_type_general_tool")
    def execute_general_tool(self):
        # Convert tool name to method name: "graph__create_schema" -> "create_schema_crew"
        tool_enum = TigerGraphToolName.from_value(self.state.current_tool_name)
        if not tool_enum:
            return "task_type_unclear"
        crew_method_name = tool_enum.name.lower() + "_crew"
        crew_factory = ToolExecutorCrews(
            tools=self.state.tool_registry, verbose=verbose
        )

        if not hasattr(crew_factory, crew_method_name):
            available = [m for m in dir(crew_factory) if m.endswith("_crew")]
            self._send_message(
                f"🚫 Tool `{self.state.current_tool_name}` is not available. Available: {available}",
            )
            return

        chat_message = self._send_message("⚙️ Executing tool...", record_history=False)
        crew = getattr(crew_factory, crew_method_name)()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
                "current_command": self.state.current_command,
            }
        )
        self._update_message(chat_message, output.raw)
        return "on_tool_executed"

    @router(or_("on_tool_executed", "schema_standalone", "load_standalone"))
    def proceed_to_next_task(self):
        self.state.current_task_index += 1
        return "on_task_completed"

    @router(or_("no_tasks_remaining", "on_onboarding_completed"))
    def wait_for_user_input(self):
        self._wait_for_user_input()
        return "on_user_command_received"

    @router(or_("tool_matching_failed", "task_type_unclear"))
    def request_clarification(self):
        self._send_message(self._get_help_message())
        self._wait_for_user_input()
        return "on_user_input_updated"

    # ------------------------------ Onboarding Workflow ------------------------------
    @router("onboarding_required")
    def prepare_data_source_and_prompt(self):
        chat_message = self._send_message(
            "🔍 Checking data source existence...", record_history=False
        )
        from tigergraphx.core import TigerGraphAPI
        from tigergraphx.config import TigerGraphConnectionConfig

        config = TigerGraphConnectionConfig()
        api = TigerGraphAPI(config)
        try:
            api.get_data_source(S3_ANONYMOUS_SOURCE_NAME)
        except Exception:
            self._update_message(
                chat_message, "🔧 Creating S3 data source...", record_history=False
            )
            api.create_data_source(
                S3_ANONYMOUS_SOURCE_NAME,
                data_source_type="s3",
                extra_config={
                    "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
                },
            )
        self._update_message(
            chat_message,
            "Please provide the S3 path(s) to your data file(s) to get started. Only S3 paths with anonymous access are supported.",
        )
        return "on_prompt_displayed"

    @router(or_("on_prompt_displayed", "on_retry_prompt_displayed"))
    def wait_and_preview_sample_data(self):
        user_input = self._wait_for_user_input()
        self.last_user_file_input = user_input  # Cache for reuse

        chat_message = self._send_message(
            "📄 Previewing sample data...", record_history=False
        )
        crew_factory = ToolExecutorCrews(
            tools=self.state.tool_registry, verbose=verbose
        )
        crew = crew_factory.preview_sample_data_crew()
        current_command = (
            f"Please preview the data in the data source '{S3_ANONYMOUS_SOURCE_NAME}'. "
            f"{self.last_user_file_input}"
        )
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
                "current_command": current_command,
            },
        )
        self.state.last_data_preview = output.raw
        self._update_message(chat_message, output.raw)
        return "on_data_previewed"

    @router("on_data_previewed")
    def evaluate_preview_result(self):
        if "❌ Error previewing sample data from" in self.state.last_data_preview:
            return "preview_failed"
        self.state.is_from_onboarding = True
        self.state.current_command = (
            "Please generate a graph schema based on the previewed data files."
        )
        return "preview_successful"

    @router("preview_failed")
    def prompt_file_paths_retry(self):
        self._send_message(
            "There was a problem previewing your data. Please ensure your S3 path"
            "is correct and publicly accessible, then try again."
        )
        return "on_retry_prompt_displayed"

    # ------------------------------ Schema Creation Workflow ------------------------------
    @router(or_("task_type_create_schema", "preview_successful"))
    def draft_schema(self):
        chat_message = self._send_message("Drafting schema...", record_history=False)
        crew_factory = SchemaCreationCrews(
            tools=self.state.tool_registry, verbose=verbose
        )
        crew = crew_factory.draft_schema_crew()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
                "current_command": self.state.current_command,
            }
        )
        self.state.current_schema_draft = output.raw
        if chat_message:
            self._update_message(chat_message, self.state.current_schema_draft)
        return "on_schema_drafted"

    @router(or_("on_schema_drafted", "on_schema_edited"))
    def handle_user_confirmation(self):
        user_input = self._wait_for_user_input()
        if any(
            kw in user_input.lower()
            for kw in [
                "confirmed",
                "approved",
                "go ahead",
                "ok",
            ]
        ):
            return "user_confirmed_schema"
        return "user_requested_changes"

    @router("user_requested_changes")
    def edit_schema(self):
        chat_message = self._send_message("✏️ Editing schema...", record_history=False)
        crew_factory = SchemaCreationCrews(tools=self.state.tool_registry)
        crew = crew_factory.edit_schema_crew()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
            }
        )
        self.state.current_schema_draft = output.raw
        self._update_message(chat_message, self.state.current_schema_draft)
        return "on_schema_edited"

    @router("user_confirmed_schema")
    def create_schema(self):
        chat_message = self._send_message("🛠️ Creating schema...", record_history=False)
        crew_factory = SchemaCreationCrews(tools=self.state.tool_registry)
        crew = crew_factory.create_schema_crew()
        output = crew.kickoff(inputs={"final_schema": self.state.current_schema_draft})
        self._update_message(chat_message, output.raw)

        # Cleanup
        self.state.current_schema_draft = ""
        return "on_schema_created"

    @router("on_schema_created")
    def check_schema_origin(self):
        if self.state.is_from_onboarding:
            self.state.current_command = (
                "Load the data into TigerGraph using the data source"
                f"named '{S3_ANONYMOUS_SOURCE_NAME}'."
            )
            return "schema_from_onboarding"
        return "schema_standalone"

    # ------------------------------ Load Data Workflow ------------------------------
    @router(or_("task_type_load_data", "schema_from_onboarding"))
    def draft_loading_job(self):
        chat_message = self._send_message(
            "🧾 Drafting loading config...", record_history=False
        )
        crew_factory = DataLoadingCrews(tools=self.state.tool_registry)
        crew = crew_factory.draft_loading_job_crew()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
                "current_command": self.state.current_command,
            }
        )
        self.state.current_loading_job_draft = output.raw
        self._update_message(chat_message, self.state.current_loading_job_draft)
        return "on_job_drafted"

    @router(or_("on_job_drafted", "on_job_edited"))
    def confirm_loading_job(self):
        user_input = self._wait_for_user_input()
        if any(
            kw in user_input.lower()
            for kw in [
                "confirmed",
                "approved",
                "go ahead",
                "ok",
            ]
        ):
            return "user_confirmed_job"
        return "user_requested_job_changes"

    @router("user_requested_job_changes")
    def edit_loading_job(self):
        chat_message = self._send_message(
            "✏️ Editing loading config...", record_history=False
        )
        crew_factory = DataLoadingCrews(tools=self.state.tool_registry)
        crew = crew_factory.edit_loading_job_crew()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
            }
        )
        self.state.current_loading_job_draft = output.raw
        self._update_message(chat_message, self.state.current_loading_job_draft)
        return "on_job_edited"

    @router("user_confirmed_job")
    def run_loading_job(self):
        chat_message = self._send_message("📥 Loading data...", record_history=False)
        crew_factory = DataLoadingCrews(tools=self.state.tool_registry)
        crew = crew_factory.run_loading_job_crew()
        output = crew.kickoff(
            inputs={"final_loading_job_config": self.state.current_loading_job_draft}
        )
        self._update_message(chat_message, output.raw)

        self.state.current_loading_job_draft = ""
        return "on_job_completed"

    @router("on_job_completed")
    def check_load_data_origin(self):
        return (
            "load_from_onboarding"
            if self.state.is_from_onboarding
            else "load_standalone"
        )

    # ------------------------------ Utility Functions ------------------------------
    def _wait_for_user_input(self):
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(f"User: {user_input}")
        return user_input

    def _send_message(self, message: str, record_history: bool = True) -> ChatMessage:
        chat_message = chat_session.chat_ui.send(
            message, user="Assistant", respond=False
        )
        if chat_message is None:
            raise RuntimeError("Failed to send chat message.")
        if record_history:
            self.state.conversation_history.append(f"Assistant: {message}")
        return chat_message

    def _update_message(
        self, chat_message: ChatMessage, message: str, record_history: bool = True
    ):
        chat_message.update(message)
        if record_history:
            self.state.conversation_history.append(f"Assistant: {message}")

    def _get_help_message(self) -> str:
        tool_list = ", ".join(f"**{name}**" for name in self.state.tool_registry.keys())
        return f"""
Hi there! Here are some things I can help you with:

### 💡 Available features:
{tool_list}

### 📝 Example instructions:
- **Create a schema**: "Generate a graph schema from these two CSV files."
- **Add data**: "Add a person named John who is 30 years old and lives in San Francisco."
- **Connect nodes**: "Create an edge to show that John works at TigerGraph."
- **Query the graph**: "Are there any people over 30 in the graph?"

### 🚀 New here?
Say **"onboarding"** to start an interactive walkthrough.

Just tell me what you'd like to do!
""".strip()
