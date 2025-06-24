from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langgraph.types import interrupt

from tigergraphx.core import TigerGraphAPI
from tigergraphx.config import TigerGraphConnectionConfig

from prompts import PREVIEW_SAMPLE_DATA_PROMPT
from workflow.chat_session_state import ChatSessionState, FlowStatus
from workflow.schema_creation_workflow import generate_schema_creation_subgraph
from workflow.data_loading_workflow import generate_data_loading_subgraph

S3_ANONYMOUS_SOURCE_NAME = "s3_anonymous_source"
DATA_PREVIEW_ERROR_MESSAGE = (
    "There was a problem previewing your data. Please ensure your S3 path "
    "is correct and publicly accessible, then try again."
)


async def generate_onboarding_subgraph(
    llm, create_schema_agent, load_data_agent, preview_sample_data_agent
):
    builder = StateGraph(ChatSessionState)

    def prepare_data_source_and_prompt(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🔍 Checking data source existence..."})

        config = TigerGraphConnectionConfig()
        api = TigerGraphAPI(config)

        try:
            api.get_data_source(S3_ANONYMOUS_SOURCE_NAME)
        except Exception:
            writer({"status": "🔧 Creating S3 data source..."})
            api.create_data_source(
                S3_ANONYMOUS_SOURCE_NAME,
                data_source_type="s3",
                extra_config={
                    "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
                },
            )

        # Final message to user
        final_prompt = (
            "Please provide the S3 path(s) to your data file(s) to get started.\n"
            "Only S3 paths with anonymous access are supported.\n\n"
            "Example: `s3://bucket-name/path/to/your/file.csv`"
        )
        message = AIMessage(content=final_prompt)
        state.messages.append(message)
        writer({"message": message})

        return state

    async def wait_and_preview_sample_data(state: ChatSessionState) -> ChatSessionState:
        human_review = interrupt("Please provide feedback")
        message = HumanMessage(
            content=f"Please preview the data in the data source '{S3_ANONYMOUS_SOURCE_NAME}'. "
            + human_review
        )
        state.messages.append(message)

        writer = get_stream_writer()
        writer({"status": "📄 Previewing sample data..."})

        response = await preview_sample_data_agent.ainvoke(
            {
                "messages": [
                    SystemMessage(content=PREVIEW_SAMPLE_DATA_PROMPT),
                    message,
                ]
            }
        )

        # Safely extract the latest AI message, if present
        latest_message = None
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if isinstance(messages, list) and messages:
                latest_message = messages[-1]

        # Check the latest message and update flow status accordingly
        if not isinstance(latest_message, AIMessage):
            state.flow_status = FlowStatus.PREVIEW_FAILED
        elif "⚠️ No valid file paths detected in the command." in latest_message.content:
            state.messages.append(latest_message)
            state.flow_status = FlowStatus.PREVIEW_FAILED
        else:
            state.flow_status = FlowStatus.PREVIEW_SUCCESSFUL
            state.messages.append(latest_message)
            writer({"message": latest_message})
            state.previewed_sample_data = str(latest_message.content)
        return state

    async def evaluate_preview_result(state: ChatSessionState) -> FlowStatus:
        if state.flow_status == FlowStatus.PREVIEW_FAILED:
            return FlowStatus.PREVIEW_FAILED
        else:
            return FlowStatus.PREVIEW_SUCCESSFUL

    async def prompt_file_paths_retry(state: ChatSessionState) -> ChatSessionState:
        message = AIMessage(content=DATA_PREVIEW_ERROR_MESSAGE)
        state.messages.append(message)
        writer = get_stream_writer()
        writer({"message": message})
        return state

    call_schema_creation_subgraph = await generate_schema_creation_subgraph(
        llm, create_schema_agent
    )

    call_data_loading_subgraph = await generate_data_loading_subgraph(
        llm, load_data_agent
    )

    async def route_schema_creation_status(state: ChatSessionState) -> FlowStatus:
        if state.flow_status == FlowStatus.SCHEMA_CREATED_FAILED:
            return FlowStatus.SCHEMA_CREATED_FAILED
        else:
            return FlowStatus.SCHEMA_CREATED_SUCCESSFUL

    # Add nodes
    builder.add_node(prepare_data_source_and_prompt)
    builder.add_node(wait_and_preview_sample_data)
    builder.add_node(prompt_file_paths_retry)
    builder.add_node("call_schema_creation_subgraph", call_schema_creation_subgraph)
    builder.add_node("call_data_loading_subgraph", call_data_loading_subgraph)

    # Add edges
    builder.add_edge(START, "prepare_data_source_and_prompt")
    builder.add_edge("prepare_data_source_and_prompt", "wait_and_preview_sample_data")
    builder.add_conditional_edges(
        "wait_and_preview_sample_data",
        evaluate_preview_result,
        {
            FlowStatus.PREVIEW_FAILED: "prompt_file_paths_retry",
            FlowStatus.PREVIEW_SUCCESSFUL: "call_schema_creation_subgraph",
        },
    )
    builder.add_edge("prompt_file_paths_retry", "wait_and_preview_sample_data")
    builder.add_conditional_edges(
        "call_schema_creation_subgraph",
        route_schema_creation_status,
        {
            FlowStatus.SCHEMA_CREATED_FAILED: END,
            FlowStatus.SCHEMA_CREATED_SUCCESSFUL: "call_data_loading_subgraph",
        },
    )
    builder.add_edge("call_data_loading_subgraph", END)

    return builder.compile(checkpointer=True)
