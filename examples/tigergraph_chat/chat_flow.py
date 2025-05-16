from typing import Dict, List, Optional
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
    task_plan: List[str] = Field(default_factory=list)
    current_task_index: int = 0


class ChatFlow(Flow[ChatSessionState]):
    @start()
    def initialize_session(self):
        logger.info("Session initialized.")

    @listen(or_(initialize_session, "user_provided_followup"))
    def match_tool_from_instructions(self):
        logger.debug("Matching tool(s) from conversation...")

        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "tools": str(self.state.tool_registry.keys()),
        }

        crew = PlannerCrew().crew()
        output = crew.kickoff(inputs=inputs)
        raw_output = output.raw.strip()
        logger.debug(f"Planner raw output: {raw_output}")

        selected_tools = []
        try:
            parsed = json.loads(raw_output)

            if isinstance(parsed, dict):
                tools = parsed.get("tools") or [parsed.get("tool_name")]
                if isinstance(tools, str):
                    tools = [tools]
                selected_tools = [t for t in tools if t in self.state.tool_registry]
                # Optional: You can capture tool_arguments here if you plan to route with them
                logger.debug(f"Planner returned tools: {selected_tools}")
            elif isinstance(parsed, list):
                selected_tools = [t for t in parsed if t in self.state.tool_registry]
                logger.debug(f"Planner returned tool list: {selected_tools}")
            elif isinstance(parsed, str) and parsed in self.state.tool_registry:
                selected_tools = [parsed]
                logger.debug(f"Planner returned single tool: {selected_tools}")

        except json.JSONDecodeError:
            logger.warning("Planner output is not valid JSON, using fallback logic.")
            if raw_output in self.state.tool_registry:
                selected_tools = [raw_output]
                logger.debug(f"Matched raw string to tool: {selected_tools}")

        if selected_tools:
            self.state.task_plan = selected_tools
            self.state.current_task_index = 0
        else:
            logger.warning("No valid tools matched.")

    @router(match_tool_from_instructions)
    def route_tool_decision(self):
        chat_session.chat_ui.send(
            f"🧭 Task plan: {str(self.state.task_plan)}",
            user="Assistant",
            respond=False,
        )
        return "task_ready" if self.state.task_plan else "no_tool_matched"

    @router("no_tool_matched")
    def handle_no_tool_match(self):
        help_message = self.get_help_message()
        chat_session.chat_ui.send(help_message, user="Assistant", respond=False)
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(user_input)
        return "user_provided_followup"

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
    def execute_task_plan_step(self):
        task_list = self.state.task_plan
        idx = self.state.current_task_index

        if idx >= len(task_list):
            chat_session.chat_ui.send(
                "✅ All tasks in your plan have been completed!",
                user="Assistant",
                respond=False,
            )
            user_input = chat_session.wait_for_user_input()
            self.state.conversation_history.append(f"User: {user_input}")
            self.state.task_plan = []
            self.state.current_task_index = 0
            return "user_provided_followup"

        current_task = TigerGraphToolName.from_value(task_list[idx] or "")
        if not current_task:
            return "no_tool_matched"

        # Convert tool name to method name: "graph__create_schema" -> "create_schema_crew"
        crew_method_name = current_task.name.lower() + "_crew"
        crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)

        if not hasattr(crew_factory, crew_method_name):
            available = [m for m in dir(crew_factory) if m.endswith("_crew")]
            chat_session.chat_ui.send(
                f"🚫 Task `{current_task}` is not available. Available: {available}",
                user="Assistant",
                respond=False,
            )
            return

        crew = getattr(crew_factory, crew_method_name)()
        output = crew.kickoff(
            inputs={"conversation_history": str(self.state.conversation_history)}
        )
        output_text = output.raw

        chat_session.chat_ui.send(output_text, user="Assistant", respond=False)
        self.state.conversation_history.append(f"Assistant: {output_text}")
        self.state.current_task_index += 1
        return "task_ready"

    # @router("tool_selected")
    # def dispatch_tool(self):
    #     task = TigerGraphToolName.from_value(self.state.matched_tool or "")
    #     return self._handle_task(task) if task else "no_tool_matched"
    #
    # def _handle_task(self, task_name: TigerGraphToolName):
    #     inputs = {
    #         "conversation_history": str(self.state.conversation_history),
    #     }
    #
    #     # Convert tool name to method name: "graph/create_schema" -> "create_schema_crew"
    #     crew_method_name = task_name.name.lower() + "_crew"
    #     crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)
    #
    #     if not hasattr(crew_factory, crew_method_name):
    #         available = [m for m in dir(crew_factory) if m.endswith("_crew")]
    #         raise ValueError(
    #             f"No crew found for task: {task_name}. Available: {available}"
    #         )
    #
    #     crew = getattr(crew_factory, crew_method_name)()
    #     output = crew.kickoff(inputs=inputs)
    #     output_text = output.raw
    #     chat_session.chat_ui.send(output_text, user="Assistant", respond=False)
    #     self.state.conversation_history.append(f"Assistant: {output_text}")
    #     user_input = chat_session.wait_for_user_input()
    #     self.state.conversation_history.append(f"User: {user_input}")
    #     self.state.matched_tool = None
    #     return "user_provided_followup"
