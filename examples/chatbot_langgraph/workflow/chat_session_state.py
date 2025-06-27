from typing import Annotated, List, Optional
from pydantic import BaseModel
from enum import Enum

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class FlowStatus(str, Enum):
    # Main workflow
    TOOL_EXECUTION_READY = "tool_execution_ready"
    HELP_REQUESTED = "help_requested"
    ONBOARDING_REQUIRED = "onboarding_required"

    # Task execution subgraph
    TASK_PLAN_IN_PROGRESS = "task_plan_in_progress"
    TASK_PLAN_COMPLETED = "task_plan_completed"

    TRIGGER_SCHEMA_SUBGRAPH = "trigger_schema_subgraph"
    TRIGGER_LOADING_SUBGRAPH = "trigger_loading_subgraph"
    PROCEED_TO_NEXT_TASK = "proceed_to_next_task"

    # Onboarding subgraph
    PREVIEW_SUCCESSFUL = "preview_successful"
    PREVIEW_FAILED = "preview_failed"

    # Schema creation subgraph
    USER_CONFIRMED_SCHEMA = "user_confirmed_schema"
    USER_REQUESTED_SCHEMA_CHANGES = "user_requested_schema_changes"

    SCHEMA_CREATED_SUCCESSFUL = "schema_created_successful"
    SCHEMA_CREATED_FAILED = "schema_created_failed"

    DATA_LOADED_SUCCESSFUL = "data_loaded_successful"
    DATA_LOADED_FAILED = "data_loaded_failed"

    # Data loading subgraph
    USER_CONFIRMED_JOB = "user_confirmed_job"
    USER_REQUESTED_JOB_CHANGES = "user_requested_job_changes"

    # Run algorithm subgraph
    USER_CONFIRMED_ALGORITHMS = "user_confirmed_algorithms"
    USER_REQUESTED_ALGO_CHANGES = "user_requested_algo_changes"


class ChatSessionState(BaseModel):
    # Conversation
    messages: Annotated[List[BaseMessage], add_messages] = []

    # Workflow control
    flow_status: Optional[FlowStatus] = None

    # Onboarding
    previewed_sample_data: str = ""

    # Schema Creation State
    current_schema_draft: str = ""  # Latest schema draft

    # Loading Job State
    current_loading_job_draft: str = ""  # Latest loading job draft


class ToolCallResult(BaseModel):
    success: bool
    message: str
