from typing import Annotated, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class FlowStatus(str, Enum):
    TASK_PLAN_READY = "task_plan_ready"
    TOOL_MATCHING_FAILED = "tool_matching_failed"
    ONBOARDING_REQUIRED = "onboarding_required"

    NO_TASKS_REMAINING = "no_tasks_remaining"
    TASK_TYPE_GENERAL_TOOL = "task_type_general_tool"
    TASK_TYPE_CREATE_SCHEMA = "task_type_create_schema"
    TASK_TYPE_LOAD_DATA = "task_type_load_data"
    TASK_TYPE_UNCLEAR = "task_type_unclear"

    # Onboarding subgraph
    PREVIEW_SUCCESSFUL = "preview_successful"
    PREVIEW_FAILED = "preview_failed"

    # Schema creation subgraph
    USER_CONFIRMED_SCHEMA = "user_confirmed_schema"
    USER_REQUESTED_SCHEMA_CHANGES = "user_requested_schema_changes"

    SCHEMA_CREATED_SUCCESSFUL = "SCHEMA_CREATED_SUCCESSFUL"
    SCHEMA_CREATED_FAILED = "schema_created_failed"

    # Data loading subgraph
    USER_CONFIRMED_JOB = "user_confirmed_job"
    USER_REQUESTED_JOB_CHANGES = "user_requested_job_changes"


class ChatSessionState(BaseModel):
    # Conversation
    messages: Annotated[List[BaseMessage], add_messages] = []

    # Workflow control
    flow_status: Optional[FlowStatus] = None

    # # Task Management
    # task_plan: List[Dict[str, str]] = Field(
    #     default_factory=list
    # )  # e.g., [{"tool_name": ..., "command": ...}]
    # current_task_index: int = 0  # Index of the currently executing task
    # current_tool_name: str = ""  # Tool name of the currently executing task
    # current_command: str = ""  # Command of the currently executing task

    # Schema Creation State
    current_schema_draft: str = ""  # Latest schema draft

    # Loading Job State
    current_loading_job_draft: str = ""  # Latest loading job draft

class ToolCallResult(BaseModel):
    success: bool
    message: str
