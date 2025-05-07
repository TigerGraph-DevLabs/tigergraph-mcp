from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import os
from functools import lru_cache

from crewai.flow.flow import Flow, listen, or_, router, start
from crewai.tools import BaseTool
from tigergraph_mcp import TigerGraphToolName

from chat_session_manager import chat_session
from crews import ToolSelectorCrew, ToolExecutorCrews
import logging

logger = logging.getLogger(__name__)


class ChatSessionState(BaseModel):
    conversation_history: List[str] = Field(default_factory=list)
    tool_registry: Dict[str, BaseTool] = Field(default_factory=dict)
    matched_tool: Optional[str] = None


class ChatFlow(Flow[ChatSessionState]):
    @start()
    def initialize_session(self):
        logger.info("Session initialized.")

    @listen(or_(initialize_session, "user_provided_followup"))
    def match_tool_from_instructions(self):
        """Use CrewAI to select the most relevant tool based on instructions."""
        logger.debug("Matching tool from conversation...")
        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "tools": str(self.state.tool_registry.keys()),
        }

        crew = ToolSelectorCrew().crew()
        output = crew.kickoff(inputs=inputs)

        selected = output.raw
        logger.debug(f"Tool selector output: {selected}")

        if selected and selected in self.state.tool_registry:
            self.state.matched_tool = selected
        else:
            logger.warning(f"Unrecognized or no tool matched: {selected}")

    @router(match_tool_from_instructions)
    def route_tool_decision(self):
        return "tool_selected" if self.state.matched_tool else "no_tool_matched"

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

        help_message = f"""
😅 I couldn't match your request with any of my available tools.

Here'ls how you can interact with me:

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
        return help_message

    @router("tool_selected")
    def dispatch_tool(self):
        task = TigerGraphToolName.from_value(self.state.matched_tool or "")
        return self._handle_task(task) if task else "no_tool_matched"

    def _handle_task(self, task_name: TigerGraphToolName):
        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "connection_config": self._get_connection_config_from_env(),
        }

        # Convert tool name to method name: "graph/create_schema" -> "create_schema_crew"
        crew_method_name = task_name.name.lower() + "_crew"
        crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)

        if not hasattr(crew_factory, crew_method_name):
            available = [m for m in dir(crew_factory) if m.endswith("_crew")]
            raise ValueError(
                f"No crew found for task: {task_name}. Available: {available}"
            )

        crew = getattr(crew_factory, crew_method_name)()
        output = crew.kickoff(inputs=inputs)
        output_text = output.raw
        chat_session.chat_ui.send(output_text, user="Assistant", respond=False)
        self.state.conversation_history.append(f"Assistant: {output_text}")
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(f"User: {user_input}")
        self.state.matched_tool = None
        return "user_provided_followup"

    @lru_cache(maxsize=1)
    def _get_connection_config_from_env(self) -> Dict:
        return {
            "host": os.environ.get("TG_HOST", "http://127.0.0.1"),
            "restpp_port": os.environ.get("TG_RESTPP_PORT", "14240"),
            "gsql_port": os.environ.get("TG_GSQL_PORT", "14240"),
            "username": os.environ.get("TG_USERNAME", ""),
            "password": os.environ.get("TG_PASSWORD", ""),
            "secret": os.environ.get("TG_SECRET", ""),
            "token": os.environ.get("TG_TOKEN", ""),
        }
