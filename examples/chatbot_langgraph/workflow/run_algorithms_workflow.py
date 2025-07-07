from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import interrupt
from langgraph.config import get_stream_writer

from examples.chatbot_langgraph.workflow.chat_session_state import ChatSessionState, FlowStatus
from examples.chatbot_langgraph.prompts import (
    SUGGEST_ALGORITHMS_PROMPT,
    EDIT_ALGORITHM_SELECTION_PROMPT,
    RUN_ALGORITHMS_PROMPT,
)


async def generate_run_algorithms_subgraph(llm, run_algorithms_agent):
    builder = StateGraph(ChatSessionState)

    async def suggest_algorithms(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🤖 Suggesting graph algorithms..."})

        message = await llm.ainvoke(
            [
                SystemMessage(content=SUGGEST_ALGORITHMS_PROMPT),
                *state.messages,
            ]
        )
        state.messages.append(message)
        writer({"message": message})
        return state

    async def wait_for_user_review_algos(state: ChatSessionState) -> ChatSessionState:
        human_review = interrupt(
            "Please review and confirm the suggested algorithms, or request changes."
        )
        state.messages.append(HumanMessage(content=human_review))
        if any(
            kw in human_review.lower()
            for kw in ["confirmed", "approved", "go ahead", "ok"]
        ):
            state.flow_status = FlowStatus.USER_CONFIRMED_ALGORITHMS
        else:
            state.flow_status = FlowStatus.USER_REQUESTED_ALGO_CHANGES
        return state

    async def confirm_algorithm_selection(state: ChatSessionState) -> FlowStatus:
        # return state.flow_status
        if state.flow_status == FlowStatus.USER_REQUESTED_ALGO_CHANGES:
            return FlowStatus.USER_REQUESTED_ALGO_CHANGES
        else:
            return FlowStatus.USER_CONFIRMED_ALGORITHMS

    async def edit_algorithm_selection(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "✏️ Editing algorithm selection..."})

        message = await llm.ainvoke(
            [
                SystemMessage(content=EDIT_ALGORITHM_SELECTION_PROMPT),
                *state.messages,
            ]
        )
        state.messages.append(message)
        writer({"message": message})
        return state

    async def run_algorithms(state: ChatSessionState) -> ChatSessionState:
        writer = get_stream_writer()
        writer({"status": "🚀 Running selected algorithms..."})

        try:
            response = await run_algorithms_agent.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=RUN_ALGORITHMS_PROMPT),
                        *state.messages,
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
            if isinstance(latest_message, AIMessage):
                state.messages.append(latest_message)
                writer({"message": latest_message})
        except Exception as e:
            message = AIMessage(content=f"\n[Error] {type(e).__name__}: {str(e)}")
            state.messages.append(message)
            writer({"message": message})

        return state

    # Add nodes
    builder.add_node(suggest_algorithms)
    builder.add_node(wait_for_user_review_algos)
    builder.add_node(edit_algorithm_selection)
    builder.add_node(run_algorithms)

    # Add edges
    builder.add_edge(START, "suggest_algorithms")
    builder.add_edge("suggest_algorithms", "wait_for_user_review_algos")
    builder.add_conditional_edges(
        "wait_for_user_review_algos",
        confirm_algorithm_selection,
        {
            FlowStatus.USER_CONFIRMED_ALGORITHMS: "run_algorithms",
            FlowStatus.USER_REQUESTED_ALGO_CHANGES: "edit_algorithm_selection",
        },
    )
    builder.add_edge("edit_algorithm_selection", "wait_for_user_review_algos")
    builder.add_edge("run_algorithms", END)

    return builder.compile(checkpointer=True)
