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
    CLASSIFY_COLUMNS_PROMPT,
    DRAFT_SCHEMA_PROMPT,
    EDIT_SCHEMA_PROMPT,
    CREATE_SCHEMA_PROMPT,
)


async def generate_schema_creation_subgraph(llm, create_schema_agent):
    builder = StateGraph(ChatSessionState)

    async def classify_columns(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🧠 Drafting schema..."})

        human_message = HumanMessage(
            content="Analyze the provided data tables and classify each column as one of: "
            "`primary_id`, `node`, or `attribute`. Also infer the data type. \n"
            f"{state.previewed_sample_data}"
        )
        message = await llm.ainvoke(
            [
                SystemMessage(content=CLASSIFY_COLUMNS_PROMPT),
                *state.messages,
                human_message,
            ]
        )
        state.current_schema_draft = message.content
        return state

    async def draft_schema(state: ChatSessionState) -> ChatSessionState:
        human_message = HumanMessage(
            content="Using classified columns and table data, draft a complete TigerGraph "
            "schema including graph name, node types, and edge types following best practices. "
            "Here is the classified columns and table data: "
            + state.current_schema_draft
        )
        message = await llm.ainvoke(
            [
                SystemMessage(content=DRAFT_SCHEMA_PROMPT),
                *state.messages,
                human_message,
            ]
        )
        state.messages.append(message)
        state.current_schema_draft = message.content
        writer = get_stream_writer()
        writer({"message": message})
        return state

    async def wait_for_user_review_schema(state: ChatSessionState) -> ChatSessionState:
        human_review = interrupt("Please provide feedback")
        state.messages.append(HumanMessage(content=human_review))
        if is_confirmed(human_review):
            state.flow_status = FlowStatus.USER_CONFIRMED_SCHEMA
        else:
            state.flow_status = FlowStatus.USER_REQUESTED_SCHEMA_CHANGES
        return state

    async def handle_user_confirmation(state: ChatSessionState) -> FlowStatus:
        if state.flow_status == FlowStatus.USER_REQUESTED_SCHEMA_CHANGES:
            return FlowStatus.USER_REQUESTED_SCHEMA_CHANGES
        else:
            return FlowStatus.USER_CONFIRMED_SCHEMA

    async def edit_schema(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "✏️ Editing schema..."})

        message = await llm.ainvoke(
            [
                SystemMessage(content=EDIT_SCHEMA_PROMPT),
                *state.messages,
            ]
        )
        state.messages.append(message)
        state.current_schema_draft = message.content
        writer = get_stream_writer()
        writer({"message": message})
        return state

    async def create_schema(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🛠️ Creating schema..."})

        state.flow_status = FlowStatus.SCHEMA_CREATED_FAILED
        try:
            response = await create_schema_agent.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=CREATE_SCHEMA_PROMPT),
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
                    state.flow_status = FlowStatus.SCHEMA_CREATED_SUCCESSFUL
        except Exception as e:
            message = AIMessage(content=f"\n[Error] {type(e).__name__}: {str(e)}")
            writer({"message": message})

        # Cleanup
        state.current_schema_draft = ""
        return state

    # Add nodes
    builder.add_node(classify_columns)
    builder.add_node(draft_schema)
    builder.add_node(wait_for_user_review_schema)
    builder.add_node(handle_user_confirmation)
    builder.add_node(edit_schema)
    builder.add_node(create_schema)

    # Add edges
    builder.add_edge(START, "classify_columns")
    builder.add_edge("classify_columns", "draft_schema")
    builder.add_edge("draft_schema", "wait_for_user_review_schema")
    builder.add_conditional_edges(
        "wait_for_user_review_schema",
        handle_user_confirmation,
        {
            FlowStatus.USER_REQUESTED_SCHEMA_CHANGES: "edit_schema",
            FlowStatus.USER_CONFIRMED_SCHEMA: "create_schema",
        },
    )
    builder.add_edge("edit_schema", "wait_for_user_review_schema")
    builder.add_edge("create_schema", END)

    return builder.compile(checkpointer=True)
