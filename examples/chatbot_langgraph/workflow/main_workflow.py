from pathlib import Path
from dotenv import dotenv_values, load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.config import get_stream_writer
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from prompts import ONBOARDING_DETECTOR_PROMPT
from workflow.chat_session_state import ChatSessionState, FlowStatus, ToolCallResult
from workflow.onboarding_workflow import generate_onboarding_subgraph


WELCOME_MESSAGE = (
    "**Welcome!** I'm your **TigerGraph Assistant**—here to help you design schemas, "
    "load and explore data, run queries, and more.\n\n"
    "Type what you'd like to do, or say **'onboarding'** to get started, "
    "or **'help'** to see what I can do. 🚀"
)


async def build_graph(
    model: str = "openai:gpt-4.1-mini-2025-04-14",
    temperature: float = 0.1,
    dotenv_path: str = ".env",
):
    # Initialize TigerGraph-MCP tools
    env_dict = dotenv_values(dotenv_path=Path(dotenv_path).expanduser().resolve())
    client = MultiServerMCPClient(
        {
            "tigergraph-mcp-server": {  # pyright: ignore
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "tigergraph_mcp.main"],
                "env": env_dict,
            },
        }
    )
    tools = await client.get_tools()

    # Initialize LLM and agent
    load_dotenv(dotenv_path=dotenv_path)
    llm = init_chat_model(model=model, temperature=temperature)
    tool_executor_agent = create_react_agent(
        "openai:gpt-4.1-mini-2025-04-14", tools=tools, response_format=ToolCallResult
    )

    async def send_welcome_message(state: ChatSessionState) -> ChatSessionState:
        message = AIMessage(content=WELCOME_MESSAGE)
        state.messages.append(message)
        writer = get_stream_writer()
        writer({"message": message})
        return state

    async def wait_for_user_input(state: ChatSessionState) -> ChatSessionState:
        human_review = interrupt("Please provide feedback")
        state.messages.append(HumanMessage(content=human_review))
        return state

    async def analyze_task_plan(state: ChatSessionState) -> ChatSessionState:
        print("analyze_task_plan...")
        last_command = state.messages[len(state.messages) - 1].content
        if last_command == "onboarding":
            state.flow_status = FlowStatus.ONBOARDING_REQUIRED
            return state

        if last_command == "help":
            state.flow_status = FlowStatus.TOOL_MATCHING_FAILED
            return state

        response = await llm.ainvoke(
            [
                SystemMessage(content=ONBOARDING_DETECTOR_PROMPT),
                HumanMessage(content=last_command),
            ]
        )
        if str(response.content).strip().lower() == "true":
            state.flow_status = FlowStatus.ONBOARDING_REQUIRED
            return state
        state.flow_status = FlowStatus.TOOL_MATCHING_FAILED
        return state

    async def route_task_plan_status(state: ChatSessionState) -> FlowStatus:
        print("route_task_plan_status...")
        if state.flow_status == FlowStatus.TASK_PLAN_READY:
            return FlowStatus.TASK_PLAN_READY
        elif state.flow_status == FlowStatus.ONBOARDING_REQUIRED:
            return FlowStatus.ONBOARDING_REQUIRED
        else:
            return FlowStatus.TOOL_MATCHING_FAILED

    async def evaluate_next_task(state: ChatSessionState):
        print("evaluate_next_task...")

    async def route_next_task_type(state: ChatSessionState) -> FlowStatus:
        print("route_next_task_type...")
        if state.flow_status == FlowStatus.NO_TASKS_REMAINING:
            return FlowStatus.NO_TASKS_REMAINING
        elif state.flow_status == FlowStatus.TASK_TYPE_GENERAL_TOOL:
            return FlowStatus.TASK_TYPE_GENERAL_TOOL
        elif state.flow_status == FlowStatus.TASK_TYPE_CREATE_SCHEMA:
            return FlowStatus.TASK_TYPE_CREATE_SCHEMA
        elif state.flow_status == FlowStatus.TASK_TYPE_LOAD_DATA:
            return FlowStatus.TASK_TYPE_LOAD_DATA
        else:
            return FlowStatus.TASK_TYPE_UNCLEAR

    async def execute_general_tool(state: ChatSessionState):
        print("execute_general_tool...")

    async def proceed_to_next_task(state: ChatSessionState):
        print("proceed_to_next_task...")

    async def request_clarification(state: ChatSessionState) -> ChatSessionState:
        print("request_clarification...")
        message = AIMessage(content=_get_help_message(tools))
        state.messages.append(message)
        writer = get_stream_writer()
        writer({"message": message})
        return state

    builder = StateGraph(ChatSessionState)

    # Add nodes
    builder.add_node(send_welcome_message)
    builder.add_node(wait_for_user_input)
    builder.add_node(analyze_task_plan)
    builder.add_node(evaluate_next_task)
    builder.add_node(execute_general_tool)
    builder.add_node(proceed_to_next_task)
    builder.add_node(request_clarification)
    call_onboarding_subgraph = await generate_onboarding_subgraph(
        llm, tool_executor_agent
    )
    builder.add_node("call_onboarding_subgraph", call_onboarding_subgraph)

    # Add edges
    builder.add_edge(START, "send_welcome_message")
    builder.add_edge("send_welcome_message", "wait_for_user_input")
    builder.add_edge("wait_for_user_input", "analyze_task_plan")
    builder.add_conditional_edges(
        "analyze_task_plan",
        route_task_plan_status,
        {
            FlowStatus.TASK_PLAN_READY: "evaluate_next_task",
            FlowStatus.ONBOARDING_REQUIRED: "call_onboarding_subgraph",
            FlowStatus.TOOL_MATCHING_FAILED: "request_clarification",
        },
    )
    builder.add_conditional_edges(
        "evaluate_next_task",
        route_next_task_type,
        {
            FlowStatus.NO_TASKS_REMAINING: "wait_for_user_input",
            FlowStatus.TASK_TYPE_GENERAL_TOOL: "execute_general_tool",
            FlowStatus.TASK_TYPE_CREATE_SCHEMA: END,
            FlowStatus.TASK_TYPE_LOAD_DATA: END,
            FlowStatus.TASK_TYPE_UNCLEAR: "request_clarification",
        },
    )
    builder.add_edge("execute_general_tool", "proceed_to_next_task")
    builder.add_edge("proceed_to_next_task", "evaluate_next_task")
    builder.add_edge("request_clarification", "wait_for_user_input")
    builder.add_edge("wait_for_user_input", "analyze_task_plan")
    builder.add_edge("call_onboarding_subgraph", "wait_for_user_input")

    return builder.compile(checkpointer=MemorySaver())


def _get_help_message(tools) -> str:
    tool_list = ", ".join(f"**{tool.name}**" for tool in tools)
    return f"""
Hi there! Here are some things I can help you with:

### 💡 Available features:
{tool_list}

### 📝 Example instructions:
- **Create a schema**: "Generate a graph schema from these two CSV files."
- **Add data**: "Add a person named John who is 30 years old and lives in San Francisco."
- **Connect nodes**: "Create an edge to show that John works at TigerGraph."
- **Query the graph**: "Are there any people over 30 in the graph?"

### 🚀 New here?
Say **"onboarding"** to start an interactive walkthrough.

Just tell me what you'd like to do!
""".strip()
