from typing import Dict, List
from pydantic import BaseModel, Field
import json
import logging

from crewai.flow.flow import Flow, listen, or_, router, start
from crewai.tools import BaseTool
from tigergraph_mcp import TigerGraphToolName

from chat_session_manager import chat_session
from crews import (
    PlannerCrew,
    SchemaCreationCrews,
    ToolExecutorCrews,
)

logger = logging.getLogger(__name__)


class ChatSessionState(BaseModel):
    conversation_history: List[str] = Field(default_factory=list)
    tool_registry: Dict[str, BaseTool] = Field(default_factory=dict)
    task_plan: List[Dict[str, str]] = Field(
        default_factory=list
    )  # [{"tool_name": ..., "command": ...}]
    current_task_index: int = 0

    # Schema creation flow control
    schema_flow_stage: str = "draft"  # Can be "draft", "edit", or "create"
    schema_draft: str = ""  # Current schema draft text


class ChatFlow(Flow[ChatSessionState]):
    @start()
    def initialize_session(self):
        logger.info("Session initialized.")

    @listen(or_(initialize_session, "awaiting_user_clarification"))
    def identify_tools_from_input(self):
        logger.debug("Matching tool(s) from conversation...")

        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "tools": str(self.state.tool_registry.keys()),
        }

        crew = PlannerCrew().crew()
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

    @router(identify_tools_from_input)
    def route_based_on_tool_match(self):
        self._send_message(f"🧭 Task plan: {str(self.state.task_plan)}")
        return "task_ready" if self.state.task_plan else "tool_matching_failed"

    @router("tool_matching_failed")
    def prompt_for_clarification(self):
        self._send_message(self.get_help_message())
        self._wait_for_user_input()
        return "awaiting_user_clarification"

    def get_help_message(self) -> str:
        tool_list = "\n".join(
            f"- **{name}**" for name in self.state.tool_registry.keys()
        )
        return f"""
😅 I couldn't match your request with any of my available tools.

### 💡 What I can help you with:
{tool_list}

### 📝 Tips for Clear Instructions:
- Ask me to **create a schema**, e.g., *"Design a schema for a movie recommendation system."*
- Request **data loading**, e.g., *"Load nodes and edges from these CSV files."*
- Try **graph operations**, e.g., *"Add a node called 'User' with these attributes."*
- Ask **questions about nodes**, e.g., *"Does node 'Product123' exist?"*

If you're not sure where to start, try saying something like:

> "I have a dataset. Help me create a graph schema for it."

I'm here to help – just let me know what you'd like to do! 🚀
""".strip()

    @router("task_ready")
    def run_next_task_in_plan(self):
        task_plan = self.state.task_plan
        current_index = self.state.current_task_index

        if current_index >= len(task_plan):
            self._wait_for_user_input()
            self.state.task_plan = []
            self.state.current_task_index = 0
            return "awaiting_user_clarification"

        task_step = task_plan[current_index]
        tool_name_str = task_step.get("tool_name", "")
        tool_enum = TigerGraphToolName.from_value(tool_name_str)
        if not tool_enum:
            return "tool_matching_failed"

        if tool_enum == TigerGraphToolName.CREATE_SCHEMA:
            crew_factory = SchemaCreationCrews(tools=self.state.tool_registry)

            if self.state.schema_flow_stage == "draft":
                crew = crew_factory.draft_schema_crew()
                output = crew.kickoff(
                    inputs={
                        "conversation_history": str(self.state.conversation_history),
                        "current_command": task_step["command"],
                    }
                )
                self.state.schema_draft = output.raw
                self._send_message(self.state.schema_draft)
                self.state.schema_flow_stage = "edit"
                return "task_ready"

            elif self.state.schema_flow_stage == "edit":
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
                    self.state.schema_flow_stage = "create"
                    return "task_ready"

                crew = crew_factory.edit_schema_crew()
                output = crew.kickoff(
                    inputs={
                        "conversation_history": str(self.state.conversation_history),
                    }
                )
                self.state.schema_draft = output.raw
                self._send_message(self.state.schema_draft)
                return "task_ready"

            elif self.state.schema_flow_stage == "create":
                crew = crew_factory.create_schema_crew()
                output = crew.kickoff(inputs={"final_schema": self.state.schema_draft})
                self._send_message(output.raw)

                # Cleanup
                self.state.schema_flow_stage = "draft"
                self.state.schema_draft = ""

        else:
            # Convert tool name to method name: "graph__create_schema" -> "create_schema_crew"
            crew_method_name = tool_enum.name.lower() + "_crew"
            crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)

            if not hasattr(crew_factory, crew_method_name):
                available = [m for m in dir(crew_factory) if m.endswith("_crew")]
                self._send_message(
                    f"🚫 Task `{tool_enum}` is not available. Available: {available}",
                )
                return

            crew = getattr(crew_factory, crew_method_name)()
            output = crew.kickoff(
                inputs={
                    "conversation_history": str(self.state.conversation_history),
                    "current_command": task_step["command"],
                }
            )
            self._send_message(output.raw)

        self.state.current_task_index += 1
        return "task_ready"

    def _wait_for_user_input(self):
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(f"User: {user_input}")
        return user_input

    def _send_message(self, message: str):
        chat_session.chat_ui.send(message, user="Assistant", respond=False)
        self.state.conversation_history.append(f"Assistant: {message}")
