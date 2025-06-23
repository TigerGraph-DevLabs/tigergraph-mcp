from pathlib import Path
from dotenv import dotenv_values, load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, START
from langgraph.types import interrupt
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.config import get_stream_writer

from tigergraph_mcp import TigerGraphToolName
from prompts import ONBOARDING_DETECTOR_PROMPT
from workflow.chat_session_state import ChatSessionState, FlowStatus, ToolCallResult
from workflow.onboarding_workflow import generate_onboarding_subgraph
from workflow.task_execution_workflow import generate_task_execution_subgraph


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

    # Categorize tools
    schema_tools = []
    load_data_tools = []
    general_tools = []
    preview_sample_data_tools = []
    for tool in tools:
        tool_enum = TigerGraphToolName.from_value(tool.name)
        if tool_enum == TigerGraphToolName.CREATE_SCHEMA:
            schema_tools.append(tool)
        elif tool_enum == TigerGraphToolName.LOAD_DATA:
            load_data_tools.append(tool)
        elif tool_enum == TigerGraphToolName.GET_SCHEMA:
            load_data_tools.append(tool)
            general_tools.append(tool)
        elif tool_enum == TigerGraphToolName.PREVIEW_SAMPLE_DATA:
            preview_sample_data_tools.append(tool)
            general_tools.append(tool)
        else:
            general_tools.append(tool)

    # Load environment and initialize model
    load_dotenv(dotenv_path=dotenv_path)
    llm = init_chat_model(model=model, temperature=temperature)

    # Create category-specific agents
    create_schema_agent = create_react_agent(
        model=model, tools=schema_tools, response_format=ToolCallResult
    )
    load_data_agent = create_react_agent(
        model=model, tools=load_data_tools, response_format=ToolCallResult
    )
    preview_sample_data_agent = create_react_agent(
        model=model, tools=preview_sample_data_tools
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

    async def detect_user_intent(state: ChatSessionState) -> ChatSessionState:
        last_command = state.messages[len(state.messages) - 1].content
        if last_command == "onboarding":
            state.flow_status = FlowStatus.ONBOARDING_REQUIRED
            return state

        if last_command == "help":
            state.flow_status = FlowStatus.HELP_REQUESTED
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
        state.flow_status = FlowStatus.TOOL_EXECUTION_READY
        return state

    async def route_user_intent(state: ChatSessionState) -> FlowStatus:
        if state.flow_status == FlowStatus.TOOL_EXECUTION_READY:
            return FlowStatus.TOOL_EXECUTION_READY
        elif state.flow_status == FlowStatus.ONBOARDING_REQUIRED:
            return FlowStatus.ONBOARDING_REQUIRED
        else:
            return FlowStatus.HELP_REQUESTED

    async def handle_help_request(state: ChatSessionState) -> ChatSessionState:
        message = AIMessage(content=_get_help_message(tools))
        state.messages.append(message)
        writer = get_stream_writer()
        writer({"message": message})
        return state

    builder = StateGraph(ChatSessionState)

    # Add nodes
    builder.add_node(send_welcome_message)
    builder.add_node(wait_for_user_input)
    builder.add_node(detect_user_intent)
    builder.add_node(handle_help_request)
    call_onboarding_subgraph = await generate_onboarding_subgraph(
        llm, create_schema_agent, load_data_agent, preview_sample_data_agent
    )
    builder.add_node("call_onboarding_subgraph", call_onboarding_subgraph)
    call_task_execution_subgraph = await generate_task_execution_subgraph(
        llm, general_tools, create_schema_agent, load_data_agent
    )
    builder.add_node("call_task_execution_subgraph", call_task_execution_subgraph)

    # Add edges
    builder.add_edge(START, "send_welcome_message")
    builder.add_edge("send_welcome_message", "wait_for_user_input")
    builder.add_edge("wait_for_user_input", "detect_user_intent")
    builder.add_conditional_edges(
        "detect_user_intent",
        route_user_intent,
        {
            FlowStatus.TOOL_EXECUTION_READY: "call_task_execution_subgraph",
            FlowStatus.ONBOARDING_REQUIRED: "call_onboarding_subgraph",
            FlowStatus.HELP_REQUESTED: "handle_help_request",
        },
    )
    builder.add_edge("call_task_execution_subgraph", "wait_for_user_input")
    builder.add_edge("call_onboarding_subgraph", "wait_for_user_input")
    builder.add_edge("handle_help_request", "wait_for_user_input")

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
