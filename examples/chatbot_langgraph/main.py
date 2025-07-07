import asyncio

from langchain_core.messages import AIMessage
from langgraph.types import Command

from examples.chatbot_langgraph.workflow import build_graph


async def _handle_stream_events(workflow, input_data, config):
    async for event in workflow.astream(
        input_data,
        config=config,
        subgraphs=True,
        stream_mode="custom",
    ):
        if isinstance(event, tuple) and len(event) == 2:
            _, chunk = event
            if isinstance(chunk, dict):
                if "status" in chunk:
                    status = chunk["status"]
                    print("""
==================================== Status ====================================
""")
                    print(status)
                elif "message" in chunk:
                    message = chunk["message"]
                    if isinstance(message, AIMessage):
                        print()
                        message.pretty_print()


async def run_assistant():
    workflow = await build_graph(
        model="openai:gpt-4.1-mini-2025-04-14", temperature=0.1, dotenv_path=".env"
    )
    config = {"configurable": {"thread_id": "1"}}

    session_initialized = False
    while True:
        try:
            if not session_initialized:
                await _handle_stream_events(workflow, {}, config)
                session_initialized = True
            else:
                print("""
================================ Human Message =================================
""")
                user_input = input("User: ").strip()
                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye! 👋")
                    break
                await _handle_stream_events(
                    workflow, Command(resume=user_input), config
                )
        except Exception as e:
            print(f"\n[Error] {type(e).__name__}: {str(e)}")
            break


if __name__ == "__main__":
    asyncio.run(run_assistant())
