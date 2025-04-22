from dotenv import load_dotenv
import panel as pn
import threading

from mcp import StdioServerParameters
from mcpadapt.core import MCPAdapt
from mcpadapt.crewai_adapter import CrewAIAdapter

from chat_flow import ChatFlow
from chat_session_manager import chat_session


class TigerGraphChatApp:
    def __init__(self):
        load_dotenv()
        pn.extension(design="material")
        chat_session.chat_ui.callback = self.callback
        self.send_welcome_message()
        self.user_input_event = threading.Event()

    def callback(self, contents: str):
        """Handles user messages and either starts a crew or records input."""
        if not chat_session.is_flow_active():
            thread = threading.Thread(target=self.start_chat_flow, args=(contents,))
            thread.start()
        else:
            chat_session.submit_user_input(contents)

    def start_chat_flow(self, message):
        """Starts a new CrewAI process if one isn't already running."""
        chat_session.set_flow_active(True)
        try:
            with MCPAdapt(
                StdioServerParameters(command="tigergraph-mcp"),
                CrewAIAdapter(),
            ) as tools:
                tool_registry = {tool.name: tool for tool in tools}
                flow = ChatFlow(
                    tool_registry=tool_registry,
                    conversation_history=[f"User: {message}"],
                )
                flow.kickoff()
        except Exception as e:
            chat_session.chat_ui.send(
                f"An error occurred: {e}", user="Assistant", respond=False
            )
        chat_session.set_flow_active(False)

    def send_welcome_message(self):
        """Sends the initial welcome message."""
        chat_session.chat_ui.send(
            "**Welcome!** I'm your **TigerGraph Assistant**, here to help with all things **TigerGraph**—from designing graph schemas and loading data to running queries and performing vector searches. How can I assist you today? 🚀",
            user="Assistant",
            respond=False,
        )

    def run(self):
        """Makes the chat interface servable."""
        chat_session.chat_ui.servable()


TigerGraphChatApp().run()
