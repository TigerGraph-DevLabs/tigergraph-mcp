import panel as pn
import threading


class ChatSessionManager:
    def __init__(self):
        self.latest_input = ""
        self.flow_active = False
        self.input_ready_event = threading.Event()
        pn.extension(design="material")
        self.chat_ui = pn.chat.ChatInterface()

    def wait_for_user_input(self):
        """Blocks until user input is submitted."""
        self.input_ready_event.wait()
        self.input_ready_event.clear()
        return self.latest_input

    def submit_user_input(self, value: str):
        """Called when the user sends input through the UI."""
        self.latest_input = value
        self.input_ready_event.set()

    def is_flow_active(self):
        return self.flow_active

    def set_flow_active(self, active: bool):
        self.flow_active = active


chat_session = ChatSessionManager()
