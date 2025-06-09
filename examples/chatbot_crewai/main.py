from dotenv import dotenv_values, load_dotenv
from pathlib import Path
import panel as pn
import threading

from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter

from chat_flow import ChatFlow
from chat_session_manager import chat_session


class TigerGraphChatApp:
    dotenv_path: Path = Path(".env")

    def __init__(self):
        load_dotenv(dotenv_path=self.dotenv_path)
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
            env_dict: dict = dotenv_values(
                dotenv_path=self.dotenv_path.expanduser().resolve()
            )
            with MCPServerAdapter(
                StdioServerParameters(command="tigergraph-mcp", env=env_dict),
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
            "**Welcome!** I'm your **TigerGraph Assistant**—here to help you design schemas, load and explore data, run queries, and more. Type what you'd like to do, or say **'onboarding'** to get started or **'help'** to see what I can do. 🚀",
            user="Assistant",
            respond=False,
        )

    def run(self):
        """Makes the chat interface servable."""
        chat_session.chat_ui.servable()


TigerGraphChatApp().run()
