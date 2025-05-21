from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from chat_session_manager import chat_session


class HumanInputToolInput(BaseModel):
    """Input schema for HumanInputTool."""

    message_to_user: str = Field(..., description="The message to send to the user.")


class HumanInputTool(BaseTool):
    name: str = "get_human_input"
    description: str = "Prompt the user and get their input."
    args_schema: Type[BaseModel] = HumanInputToolInput

    def _run(self, message_to_user: str):
        chat_session.chat_ui.send(message_to_user, user="Assistant", respond=False)
        return chat_session.wait_for_user_input()
