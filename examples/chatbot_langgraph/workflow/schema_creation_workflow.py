from langgraph.graph import StateGraph, START, END
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

from workflow.chat_session_state import ChatSessionState, FlowStatus
from prompts import (
    CLASSIFY_COLUMNS_PROMPT,
    DRAFT_SCHEMA_PROMPT,
    EDIT_SCHEMA_PROMPT,
    CREATE_SCHEMA_PROMPT,
)


async def generate_schema_creation_subgraph(llm, tool_executor_agent):
    builder = StateGraph(ChatSessionState)

    async def classify_columns(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🧠 Drafting schema..."})

        preview_message = HumanMessage(content=state.messages[-1].content)
        message = await llm.ainvoke(
            [
                SystemMessage(content=CLASSIFY_COLUMNS_PROMPT),
                preview_message,
            ]
        )
        state.current_schema_draft = message.content
        return state

    async def draft_schema(state: ChatSessionState) -> ChatSessionState:
        preview_message = AIMessage(content=state.messages[-1].content)
        schema_draft_message = HumanMessage(content=state.current_schema_draft)
        message = await llm.ainvoke(
            [
                SystemMessage(content=DRAFT_SCHEMA_PROMPT),
                preview_message,
                schema_draft_message,
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
        if any(
            kw in human_review.lower()
            for kw in [
                "confirmed",
                "approved",
                "go ahead",
                "ok",
            ]
        ):
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
            response = await tool_executor_agent.ainvoke(
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
