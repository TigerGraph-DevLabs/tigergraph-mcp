from typing import Dict, List
from pydantic import BaseModel, Field
import json

from crewai.flow.flow import Flow, listen, or_, router, start
from crewai.tools import BaseTool
from tigergraph_mcp import TigerGraphToolName

from chat_session_manager import chat_session
from crews import PlannerCrew, ToolExecutorCrews
import logging

logger = logging.getLogger(__name__)


class ChatSessionState(BaseModel):
    conversation_history: List[str] = Field(default_factory=list)
    tool_registry: Dict[str, BaseTool] = Field(default_factory=dict)
    task_plan: List[Dict[str, str]] = Field(
        default_factory=list
    )  # [{"tool_name": ..., "command": ...}]
    current_task_index: int = 0


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
        chat_session.chat_ui.send(
            f"🧭 Task plan: {str(self.state.task_plan)}",
            user="Assistant",
            respond=False,
        )
        return "task_ready" if self.state.task_plan else "tool_matching_failed"

    @router("tool_matching_failed")
    def prompt_for_clarification(self):
        help_message = self.get_help_message()
        chat_session.chat_ui.send(help_message, user="Assistant", respond=False)
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(user_input)
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
            user_input = chat_session.wait_for_user_input()
            self.state.conversation_history.append(f"User: {user_input}")
            self.state.task_plan = []
            self.state.current_task_index = 0
            return "awaiting_user_clarification"

        task_step = task_plan[current_index]
        tool_name_str = task_step.get("tool_name", "")
        tool_enum = TigerGraphToolName.from_value(tool_name_str)
        if not tool_enum:
            return "tool_matching_failed"

        # Convert tool name to method name: "graph__create_schema" -> "create_schema_crew"
        crew_method_name = tool_enum.name.lower() + "_crew"
        crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)

        if not hasattr(crew_factory, crew_method_name):
            available = [m for m in dir(crew_factory) if m.endswith("_crew")]
            chat_session.chat_ui.send(
                f"🚫 Task `{tool_enum}` is not available. Available: {available}",
                user="Assistant",
                respond=False,
            )
            return

        crew = getattr(crew_factory, crew_method_name)()
        output = crew.kickoff(
            inputs={
                "conversation_history": str(self.state.conversation_history),
                "current_command": task_plan[current_index]["command"],
            }
        )
        output_text = output.raw

        chat_session.chat_ui.send(output_text, user="Assistant", respond=False)
        self.state.conversation_history.append(f"Assistant: {output_text}")
        self.state.current_task_index += 1
        return "task_ready"
