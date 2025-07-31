from langgraph.graph import StateGraph, START, END
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

from examples.chatbot_langgraph.workflow.chat_session_state import (
    ChatSessionState,
    FlowStatus,
    is_confirmed,
)
from examples.chatbot_langgraph.prompts import (
    GET_SCHEMA_PROMPT,
    LOAD_CONFIG_FILE_PROMPT,
    LOAD_CONFIG_NODE_MAPPING_PROMPT,
    LOAD_CONFIG_EDGE_MAPPING_PROMPT,
    EDIT_LOADING_JOB_PROMPT,
    RUN_LOADING_JOB_PROMPT,
)


async def generate_data_loading_subgraph(llm, load_data_agent):
    builder = StateGraph(ChatSessionState)

    async def load_config_file(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🧾 Drafting loading config..."})

        # Get the latest schema
        get_schema_message = HumanMessage(
            content="Get the graph schema of the created graph."
        )
        response = await load_data_agent.ainvoke(
            {
                "messages": [
                    SystemMessage(content=GET_SCHEMA_PROMPT),
                    *state.messages,
                    get_schema_message,
                ]
            },
        )
        latest_message = None
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if isinstance(messages, list) and messages:
                latest_message = messages[-1]
        if not isinstance(latest_message, AIMessage):
            raise ValueError("Expected an AIMessage, but got something else.")
        state.messages.append(latest_message)

        # Generate the first step of a TigerGraph loading job config: define the `files` section
        # with valid file aliases, file paths, and CSV parsing options
        human_message = HumanMessage(
            content="Please define the `files` section with valid file aliases, "
            "file paths, and CSV parsing options based on the graph schema."
        )
        message = await llm.ainvoke(
            [
                SystemMessage(content=LOAD_CONFIG_FILE_PROMPT),
                *state.messages,
                human_message,
            ]
        )
        state.current_loading_job_draft = message.content
        return state

    async def load_config_node_mapping(state: ChatSessionState) -> ChatSessionState:
        # Generate the second step of a TigerGraph loading job config: Add node mappings to the
        # loading job config based on the previously defined `files` section.
        human_message = HumanMessage(content=state.current_loading_job_draft)
        message = await llm.ainvoke(
            [
                SystemMessage(content=LOAD_CONFIG_NODE_MAPPING_PROMPT),
                *state.messages,
                human_message,
            ]
        )
        state.current_loading_job_draft = message.content
        return state

    async def load_config_edge_mapping(state: ChatSessionState) -> ChatSessionState:
        # Generate the third step of a TigerGraph loading job config: Add edge mappings to the
        # loading job config based on the previously defined `files` section with node mappings.
        human_message = HumanMessage(content=state.current_loading_job_draft)
        message = await llm.ainvoke(
            [
                SystemMessage(content=LOAD_CONFIG_EDGE_MAPPING_PROMPT),
                *state.messages,
                human_message,
            ]
        )
        state.messages.append(message)
        state.current_loading_job_draft = message.content
        writer = get_stream_writer()
        writer({"message": message})
        return state

    async def wait_for_user_review_job(state: ChatSessionState) -> ChatSessionState:
        human_review = interrupt("Please provide feedback")
        state.messages.append(HumanMessage(content=human_review))
        if is_confirmed(human_review):
            state.flow_status = FlowStatus.USER_CONFIRMED_JOB
        else:
            state.flow_status = FlowStatus.USER_REQUESTED_JOB_CHANGES
        return state

    async def confirm_loading_job(state: ChatSessionState) -> FlowStatus:
        if state.flow_status == FlowStatus.USER_REQUESTED_JOB_CHANGES:
            return FlowStatus.USER_REQUESTED_JOB_CHANGES
        else:
            return FlowStatus.USER_CONFIRMED_JOB

    async def edit_loading_job(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "✏️ Editing loading config..."})
        message = await llm.ainvoke(
            [
                SystemMessage(content=EDIT_LOADING_JOB_PROMPT),
                *state.messages,
            ]
        )
        state.messages.append(message)
        state.current_loading_job_draft = message.content
        writer({"message": message})
        return state

    async def run_loading_job(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "📥 Loading data..."})

        state.flow_status = FlowStatus.DATA_LOADED_FAILED
        try:
            response = await load_data_agent.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=RUN_LOADING_JOB_PROMPT),
                        *state.messages,
                    ]
                },
            )

            # If structured response exists and is successful, update status
            if isinstance(response, dict) and "structured_response" in response:
                structured_response = response["structured_response"]
                message = AIMessage(content=structured_response.message)
                state.messages.append(message)
                writer({"message": message})
                if structured_response.success:
                    state.flow_status = FlowStatus.DATA_LOADED_SUCCESSFUL
        except Exception as e:
            message = AIMessage(content=f"\n[Error] {type(e).__name__}: {str(e)}")
            writer({"message": message})

        # Cleanup
        state.current_loading_job_draft = ""
        return state

    # Add nodes
    builder.add_node(load_config_file)
    builder.add_node(load_config_node_mapping)
    builder.add_node(load_config_edge_mapping)
    builder.add_node(wait_for_user_review_job)
    builder.add_node(edit_loading_job)
    builder.add_node(run_loading_job)

    # Add edges
    builder.add_edge(START, "load_config_file")
    builder.add_edge("load_config_file", "load_config_node_mapping")
    builder.add_edge("load_config_node_mapping", "load_config_edge_mapping")
    builder.add_edge("load_config_edge_mapping", "wait_for_user_review_job")
    builder.add_conditional_edges(
        "wait_for_user_review_job",
        confirm_loading_job,
        {
            FlowStatus.USER_REQUESTED_JOB_CHANGES: "edit_loading_job",
            FlowStatus.USER_CONFIRMED_JOB: "run_loading_job",
        },
    )
    builder.add_edge("edit_loading_job", "wait_for_user_review_job")
    builder.add_edge("run_loading_job", END)

    return builder.compile(checkpointer=True)
