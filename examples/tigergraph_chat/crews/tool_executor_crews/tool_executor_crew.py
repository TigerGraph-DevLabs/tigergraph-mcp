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

    # ------------------------------ Edge Operations ------------------------------
    @agent
    def edge_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["edge_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.ADD_EDGE],
                self.tool_registry[TigerGraphToolName.ADD_EDGES],
                self.tool_registry[TigerGraphToolName.HAS_EDGE],
                self.tool_registry[TigerGraphToolName.GET_EDGE_DATA],
            ],
        )

    @task
    def add_edge_task(self) -> Task:
        return Task(config=self.tasks_config["add_edge_task"])  # pyright: ignore

    @crew
    def add_edge_crew(self) -> Crew:
        return Crew(
            agents=[self.edge_agent()],
            tasks=[self.add_edge_task()],
            verbose=True,
        )

    @task
    def add_edges_task(self) -> Task:
        return Task(config=self.tasks_config["add_edges_task"])  # pyright: ignore

    @crew
    def add_edges_crew(self) -> Crew:
        return Crew(
            agents=[self.edge_agent()],
            tasks=[self.add_edges_task()],
            verbose=True,
        )

    @task
    def has_edge_task(self) -> Task:
        return Task(config=self.tasks_config["has_edge_task"])  # pyright: ignore

    @crew
    def has_edge_crew(self) -> Crew:
        return Crew(
            agents=[self.edge_agent()],
            tasks=[self.has_edge_task()],
            verbose=True,
        )

    @task
    def get_edge_data_task(self) -> Task:
        return Task(config=self.tasks_config["get_edge_data_task"])  # pyright: ignore

    @crew
    def get_edge_data_crew(self) -> Crew:
        return Crew(
            agents=[self.edge_agent()],
            tasks=[self.get_edge_data_task()],
            verbose=True,
        )

    # ------------------------------ Statistics Operations ------------------------------
    @agent
    def statistics_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["statistics_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.DEGREE],
                self.tool_registry[TigerGraphToolName.NUMBER_OF_NODES],
                self.tool_registry[TigerGraphToolName.NUMBER_OF_EDGES],
            ],
        )

    @task
    def degree_task(self) -> Task:
        return Task(config=self.tasks_config["degree_task"])  # pyright: ignore

    @crew
    def degree_crew(self) -> Crew:
        return Crew(
            agents=[self.statistics_agent()],
            tasks=[self.degree_task()],
            verbose=True,
        )

    @task
    def number_of_nodes_task(self) -> Task:
        return Task(config=self.tasks_config["number_of_nodes_task"])  # pyright: ignore

    @crew
    def number_of_nodes_crew(self) -> Crew:
        return Crew(
            agents=[self.statistics_agent()],
            tasks=[self.number_of_nodes_task()],
            verbose=True,
        )

    @task
    def number_of_edges_task(self) -> Task:
        return Task(config=self.tasks_config["number_of_edges_task"])  # pyright: ignore

    @crew
    def number_of_edges_crew(self) -> Crew:
        return Crew(
            agents=[self.statistics_agent()],
            tasks=[self.number_of_edges_task()],
            verbose=True,
        )

    # ------------------------------ Query Operations ------------------------------
    @agent
    def query_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["query_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.CREATE_QUERY],
                self.tool_registry[TigerGraphToolName.INSTALL_QUERY],
                self.tool_registry[TigerGraphToolName.DROP_QUERY],
                self.tool_registry[TigerGraphToolName.RUN_QUERY],
                self.tool_registry[TigerGraphToolName.GET_NODES],
                self.tool_registry[TigerGraphToolName.GET_NEIGHBORS],
                self.tool_registry[TigerGraphToolName.BREADTH_FIRST_SEARCH],
            ],
        )

    @task
    def create_query_task(self) -> Task:
        return Task(config=self.tasks_config["create_query_task"])  # pyright: ignore

    @crew
    def create_query_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.create_query_task()],
            verbose=True,
        )

    @task
    def install_query_task(self) -> Task:
        return Task(config=self.tasks_config["install_query_task"])  # pyright: ignore

    @crew
    def install_query_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.install_query_task()],
            verbose=True,
        )

    @task
    def run_query_task(self) -> Task:
        return Task(config=self.tasks_config["run_query_task"])  # pyright: ignore

    @crew
    def run_query_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.run_query_task()],
            verbose=True,
        )

    @task
    def drop_query_task(self) -> Task:
        return Task(config=self.tasks_config["drop_query_task"])  # pyright: ignore

    @crew
    def drop_query_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.drop_query_task()],
            verbose=True,
        )

    @task
    def get_nodes_task(self) -> Task:
        return Task(config=self.tasks_config["get_nodes_task"])  # pyright: ignore

    @crew
    def get_nodes_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.get_nodes_task()],
            verbose=True,
        )

    @task
    def get_neighbors_task(self) -> Task:
        return Task(config=self.tasks_config["get_neighbors_task"])  # pyright: ignore

    @crew
    def get_neighbors_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.get_neighbors_task()],
            verbose=True,
        )

    @task
    def breadth_first_search_task(self) -> Task:
        return Task(config=self.tasks_config["breadth_first_search_task"])  # pyright: ignore

    @crew
    def breadth_first_search_crew(self) -> Crew:
        return Crew(
            agents=[self.query_agent()],
            tasks=[self.breadth_first_search_task()],
            verbose=True,
        )

    # ------------------------------ Vector Operations ------------------------------
    @agent
    def vector_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["vector_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.GET_SCHEMA],
                self.tool_registry[TigerGraphToolName.UPSERT],
                self.tool_registry[TigerGraphToolName.FETCH_NODE],
                self.tool_registry[TigerGraphToolName.FETCH_NODES],
                self.tool_registry[TigerGraphToolName.SEARCH],
                self.tool_registry[TigerGraphToolName.SEARCH_MULTI_VECTOR_ATTRIBUTES],
                self.tool_registry[TigerGraphToolName.SEARCH_TOP_K_SIMILAR_NODES],
            ],
        )

    @task
    def upsert_vector_task(self) -> Task:
        return Task(config=self.tasks_config["upsert_vector_task"])  # pyright: ignore

    @crew
    def upsert_vector_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.upsert_vector_task()],
            verbose=True,
        )

    @task
    def fetch_node_task(self) -> Task:
        return Task(config=self.tasks_config["fetch_node_task"])  # pyright: ignore

    @crew
    def fetch_node_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.fetch_node_task()],
            verbose=True,
        )

    @task
    def fetch_nodes_task(self) -> Task:
        return Task(config=self.tasks_config["fetch_nodes_task"])  # pyright: ignore

    @crew
    def fetch_nodes_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.fetch_nodes_task()],
            verbose=True,
        )

    @task
    def vector_search_task(self) -> Task:
        return Task(config=self.tasks_config["vector_search_task"])  # pyright: ignore

    @crew
    def vector_search_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.vector_search_task()],
            verbose=True,
        )

    @task
    def search_multi_vector_attributes_task(self) -> Task:
        return Task(config=self.tasks_config["search_multi_vector_attributes_task"])  # pyright: ignore

    @crew
    def search_multi_vector_attributes_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.search_multi_vector_attributes_task()],
            verbose=True,
        )

    @task
    def search_top_k_similar_nodes_task(self) -> Task:
        return Task(config=self.tasks_config["search_top_k_similar_nodes_task"])  # pyright: ignore

    @crew
    def search_top_k_similar_nodes_crew(self) -> Crew:
        return Crew(
            agents=[self.vector_agent()],
            tasks=[self.search_top_k_similar_nodes_task()],
            verbose=True,
        )

    # ------------------------------ Data Source Operations ------------------------------
    @agent
    def data_source_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["data_source_agent"],  # pyright: ignore
            tools=[
                self.tool_registry[TigerGraphToolName.CREATE_DATA_SOURCE],
                self.tool_registry[TigerGraphToolName.DROP_DATA_SOURCE],
                self.tool_registry[TigerGraphToolName.PREVIEW_SAMPLE_DATA],
            ],
        )

    @task
    def create_data_source_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_data_source_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def create_data_source_crew(self) -> Crew:
        return Crew(
            agents=[self.data_source_agent()],
            tasks=[self.create_data_source_task()],
            verbose=True,
        )

    @task
    def drop_data_source_task(self) -> Task:
        return Task(
            config=self.tasks_config["drop_data_source_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def drop_data_source_crew(self) -> Crew:
        return Crew(
            agents=[self.data_source_agent()],
            tasks=[self.drop_data_source_task()],
            verbose=True,
        )

    @task
    def preview_sample_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["preview_sample_data_task"],  # pyright: ignore
            # callback=print_output,
            # human_input=True,
        )

    @crew
    def preview_sample_data_crew(self) -> Crew:
        return Crew(
            agents=[self.data_source_agent()],
            tasks=[self.preview_sample_data_task()],
            verbose=True,
        )
