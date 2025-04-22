from typing import Dict, List, Optional
from pydantic import BaseModel
import os

from crewai.flow.flow import Flow, listen, or_, router, start
from crewai.tools import BaseTool
from tigergraph_mcp import TigerGraphToolName

from chat_session_manager import chat_session
from crews import ToolSelectorCrew, ToolExecutorCrews


class ChatSessionState(BaseModel):
    conversation_history: List[str] = []
    tool_registry: Dict[str, BaseTool] = {}
    matched_tool: Optional[str] = None


class ChatFlow(Flow[ChatSessionState]):
    @start()
    def initialize_session(self):
        pass

    @listen(or_(initialize_session, "user_provided_followup"))
    def match_tool_from_instructions(self):
        """Use CrewAI to select the most relevant tool based on instructions."""
        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "tools": str(self.state.tool_registry.keys()),
        }

        crew = ToolSelectorCrew().crew()
        output = crew.kickoff(inputs=inputs)

        if output.raw != "None":
            self.state.matched_tool = output.raw

    @router(match_tool_from_instructions)
    def route_tool_decision(self):
        """Route based on whether a relevant tool was identified."""
        return "tool_selected" if self.state.matched_tool else "no_tool_matched"

    @router("no_tool_matched")
    def handle_no_tool_match(self):
        """Handles the case when no tool is matched — provides a helpful message to the user."""
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
    def proceed_with_tool(self):
        """Tool was selected – proceed to tool execution logic."""
        return self.state.matched_tool

    @router(TigerGraphToolName.CREATE_SCHEMA.value)
    def create_schema(self):
        return self._handle_task(TigerGraphToolName.CREATE_SCHEMA)

    @router(TigerGraphToolName.GET_SCHEMA.value)
    def get_schema(self):
        return self._handle_task(TigerGraphToolName.GET_SCHEMA)

    @router(TigerGraphToolName.DROP_GRAPH.value)
    def drop_graph(self):
        return self._handle_task(TigerGraphToolName.DROP_GRAPH)

    @router(TigerGraphToolName.LOAD_DATA.value)
    def load_data(self):
        return self._handle_task(TigerGraphToolName.LOAD_DATA)

    @router(TigerGraphToolName.ADD_NODE.value)
    def add_node(self):
        return self._handle_task(TigerGraphToolName.ADD_NODE)

    @router(TigerGraphToolName.ADD_NODES.value)
    def add_nodes(self):
        return self._handle_task(TigerGraphToolName.ADD_NODES)

    @router(TigerGraphToolName.CLEAR_GRAPH_DATA.value)
    def clear_graph_data(self):
        return self._handle_task(TigerGraphToolName.CLEAR_GRAPH_DATA)

    @router(TigerGraphToolName.GET_NODE_DATA.value)
    def get_node_data(self):
        return self._handle_task(TigerGraphToolName.GET_NODE_DATA)

    @router(TigerGraphToolName.GET_NODE_EDGES.value)
    def get_node_edges(self):
        return self._handle_task(TigerGraphToolName.GET_NODE_EDGES)

    @router(TigerGraphToolName.HAS_NODE.value)
    def has_node(self):
        return self._handle_task(TigerGraphToolName.HAS_NODE)

    @router(TigerGraphToolName.REMOVE_NODE.value)
    def remove_node(self):
        return self._handle_task(TigerGraphToolName.REMOVE_NODE)

    def _handle_task(self, task_name: TigerGraphToolName):
        inputs = {
            "conversation_history": str(self.state.conversation_history),
            "connection_config": self._get_connection_config_from_env(),
        }

        # Convert tool name to method name: "graph/create_schema" -> "create_schema_crew"
        crew_method_name = task_name.name.lower() + "_crew"
        crew_factory = ToolExecutorCrews(tools=self.state.tool_registry)

        if not hasattr(crew_factory, crew_method_name):
            raise ValueError(f"No crew found for task: {task_name}")

        crew = getattr(crew_factory, crew_method_name)()
        output = crew.kickoff(inputs=inputs)
        output_text = output.raw
        chat_session.chat_ui.send(output_text, user="Assistant", respond=False)
        self.state.conversation_history.append(f"Assistant: {output_text}")
        user_input = chat_session.wait_for_user_input()
        self.state.conversation_history.append(f"User: {user_input}")
        return "user_provided_followup"

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
