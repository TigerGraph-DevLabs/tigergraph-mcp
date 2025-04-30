from functools import cached_property

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tasks.task_output import TaskOutput
from crewai.tools import BaseTool

from tigergraph_mcp import TigerGraphToolName
from chat_session_manager import chat_session


def print_output(output: TaskOutput):
    message = output.raw
    chat_session.chat_ui.send(message, user=output.agent, respond=False)


@CrewBase
class ToolExecutorCrews:
    def __init__(self, tools: dict[str, BaseTool]):
        self._tool_registry = tools

    @cached_property
    def tool_registry(self) -> dict[str, BaseTool]:
        return self._tool_registry

    # ------------------------------ Schema Operations ------------------------------
    @agent
    def schema_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["schema_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.CREATE_SCHEMA],
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.DROP_GRAPH],
            ],
        )

    @task
    def create_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_schema_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def create_schema_crew(self) -> Crew:
        return Crew(
            agents=[self.schema_agent()],
            tasks=[self.create_schema_task()],
            verbose=True,
        )

    @task
    def get_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config["get_schema_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def get_schema_crew(self) -> Crew:
        return Crew(
            agents=[self.schema_agent()],
            tasks=[self.get_schema_task()],
            verbose=True,
        )

    @task
    def graph_drop_task(self) -> Task:
        return Task(
            config=self.tasks_config["graph_drop_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def drop_graph_crew(self) -> Crew:
        return Crew(
            agents=[self.schema_agent()],
            tasks=[self.graph_drop_task()],
            verbose=True,
        )

    # ------------------------------ Data Loading Operations ------------------------------
    @agent
    def data_loader_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["data_loader_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.LOAD_DATA],
            ],
        )

    @task
    def load_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["load_data_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def load_data_crew(self) -> Crew:
        return Crew(
            agents=[self.data_loader_agent()],
            tasks=[self.load_data_task()],
            verbose=True,
        )

    # ------------------------------ Node Operations ------------------------------
    @agent
    def node_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["node_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.ADD_NODE],
                self.tool_registry[TigerGraphToolName.ADD_NODES],
                self.tool_registry[TigerGraphToolName.CLEAR_GRAPH_DATA],
                self.tool_registry[TigerGraphToolName.GET_NODE_DATA],
                self.tool_registry[TigerGraphToolName.GET_NODE_EDGES],
                self.tool_registry[TigerGraphToolName.HAS_NODE],
                self.tool_registry[TigerGraphToolName.REMOVE_NODE],
            ],
        )

    @task
    def add_node_task(self) -> Task:
        return Task(
            config=self.tasks_config["add_node_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def add_node_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.add_node_task()],
            verbose=True,
        )

    @task
    def add_nodes_task(self) -> Task:
        return Task(
            config=self.tasks_config["add_nodes_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def add_nodes_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.add_nodes_task()],
            verbose=True,
        )

    @task
    def remove_node_task(self) -> Task:
        return Task(
            config=self.tasks_config["remove_node_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def remove_node_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.remove_node_task()],
            verbose=True,
        )

    @task
    def has_node_task(self) -> Task:
        return Task(
            config=self.tasks_config["has_node_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def has_node_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.has_node_task()],
            verbose=True,
        )

    @task
    def get_node_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["get_node_data_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def get_node_data_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.get_node_data_task()],
            verbose=True,
        )

    @task
    def get_node_edges_task(self) -> Task:
        return Task(
            config=self.tasks_config["get_node_edges_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def get_node_edges_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.get_node_edges_task()],
            verbose=True,
        )

    @task
    def clear_graph_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["clear_graph_data_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def clear_graph_data_crew(self) -> Crew:
        return Crew(
            agents=[self.node_agent()],
            tasks=[self.clear_graph_data_task()],
            verbose=True,
        )
