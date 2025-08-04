from langgraph.graph import StateGraph, START, END
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langgraph.config import get_stream_writer
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool

from examples.chatbot_langgraph.workflow.chat_session_state import ChatSessionState, FlowStatus
from examples.chatbot_langgraph.prompts import (
    PLAN_TOOL_EXECUTION_PROMPT,
)
from examples.chatbot_langgraph.workflow.schema_creation_workflow import (
    generate_schema_creation_subgraph,
)
from examples.chatbot_langgraph.workflow.data_loading_workflow import generate_data_loading_subgraph


async def generate_task_execution_subgraph(
    llm, general_tools, create_schema_agent, load_data_agent
):
    builder = StateGraph(ChatSessionState)

    schema_creation_tool = Tool.from_function(
        func=lambda _: "",
        name="trigger_graph_schema_creation",
        description=(
            "Triggers the subgraph flow to analyze input files, suggest a graph schema, "
            "incorporate user feedback, and create the schema in TigerGraph. "
            "This tool acts as a trigger only; the actual logic runs in a dedicated subgraph.\n\n"
            "⚠️ Important: This tool must be called **individually**, without being grouped "
            "with any other tools in the same tool_calls block."
        ),
    )
    load_data_tool = Tool.from_function(
        func=lambda _: "",
        name="trigger_load_data",
        description=(
            "Triggers the subgraph flow to map file contents to the graph schema and load data "
            "into TigerGraph. This tool acts as a trigger only; the actual loading logic runs in "
            "a dedicated subgraph.\n\n"
            "⚠️ Important: This tool must be called **individually**, without being grouped "
            "with any other tools in the same tool_calls block."
        ),
    )
    general_tools.append(schema_creation_tool)
    general_tools.append(load_data_tool)
    llm_with_tools = llm.bind_tools(general_tools)

    async def execute_next_task(state: ChatSessionState) -> ChatSessionState:
        message = await llm_with_tools.ainvoke(
            [
                SystemMessage(content=PLAN_TOOL_EXECUTION_PROMPT),
                *state.messages,
            ]
        )
        state.messages.append(message)
        writer = get_stream_writer()
        if message.content:
            writer({"message": message})
        return state

    async def route_task_plan_status(state: ChatSessionState) -> str:
        last_message = state.messages[-1]
        if not isinstance(last_message, AIMessage):
            return FlowStatus.TASK_PLAN_COMPLETED
        if not last_message.tool_calls:
            return FlowStatus.TASK_PLAN_COMPLETED
        return FlowStatus.TASK_PLAN_IN_PROGRESS

    async def route_tool_completion(state: ChatSessionState) -> str:
        last_message = state.messages[-1]
        if isinstance(last_message, ToolMessage):
            if last_message.name == "trigger_graph_schema_creation":
                return FlowStatus.TRIGGER_SCHEMA_SUBGRAPH
            if last_message.name == "trigger_load_data":
                return FlowStatus.TRIGGER_LOADING_SUBGRAPH
        return FlowStatus.PROCEED_TO_NEXT_TASK

    call_schema_creation_subgraph = await generate_schema_creation_subgraph(
        llm, create_schema_agent
    )
    call_data_loading_subgraph = await generate_data_loading_subgraph(llm, load_data_agent)

    builder = StateGraph(ChatSessionState)

    builder.add_node(execute_next_task)
    builder.add_node("execute_tool_call", ToolNode(general_tools))
    builder.add_node("call_schema_creation_subgraph", call_schema_creation_subgraph)
    builder.add_node("call_data_loading_subgraph", call_data_loading_subgraph)

    builder.add_edge(START, "execute_next_task")
    builder.add_conditional_edges(
        "execute_next_task",
        route_task_plan_status,
        {
            FlowStatus.TASK_PLAN_IN_PROGRESS: "execute_tool_call",
            FlowStatus.TASK_PLAN_COMPLETED: END,
        },
    )
    builder.add_conditional_edges(
        "execute_tool_call",
        route_tool_completion,
        {
            FlowStatus.TRIGGER_SCHEMA_SUBGRAPH: "call_schema_creation_subgraph",
            FlowStatus.TRIGGER_LOADING_SUBGRAPH: "call_data_loading_subgraph",
            FlowStatus.PROCEED_TO_NEXT_TASK: "execute_next_task",
        },
    )
    builder.add_edge("call_schema_creation_subgraph", "execute_next_task")
    builder.add_edge("call_data_loading_subgraph", "execute_next_task")

    return builder.compile(checkpointer=True)
