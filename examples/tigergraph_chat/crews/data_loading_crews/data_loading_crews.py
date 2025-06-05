from functools import cached_property

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool

from tigergraph_mcp import TigerGraphToolName


@CrewBase
class DataLoadingCrews:
    def __init__(self, tools: dict[str, BaseTool], llm="gpt-4o", verbose=False):
        self._tool_registry = tools
        self.verbose = verbose
        self.llm = llm

    @cached_property
    def tool_registry(self) -> dict[str, BaseTool]:
        return self._tool_registry

    @agent
    def load_config_file_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["load_config_file_agent"],  # pyright: ignore
            llm=self.llm,
        )

    @agent
    def load_config_node_mapping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["load_config_node_mapping_agent"],  # pyright: ignore
            tools=[self.tool_registry[TigerGraphToolName.GET_SCHEMA]],
            llm=self.llm,
        )

    @agent
    def load_config_edge_mapping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["load_config_edge_mapping_agent"],  # pyright: ignore
            tools=[self.tool_registry[TigerGraphToolName.GET_SCHEMA]],
            llm=self.llm,
        )

    @task
    def load_config_file_task(self) -> Task:
        return Task(
            config=self.tasks_config["load_config_file_task"],  # pyright: ignore
        )

    @task
    def load_config_node_mapping_task(self) -> Task:
        return Task(
            config=self.tasks_config["load_config_node_mapping_task"],  # pyright: ignore
        )

    @task
    def load_config_edge_mapping_task(self) -> Task:
        return Task(
            config=self.tasks_config["load_config_edge_mapping_task"],  # pyright: ignore
        )

    @crew
    def draft_loading_job_crew(self) -> Crew:
        return Crew(
            agents=[
                self.load_config_file_agent(),
                self.load_config_node_mapping_agent(),
                self.load_config_edge_mapping_agent(),
            ],
            tasks=[
                self.load_config_file_task(),
                self.load_config_node_mapping_task(),
                self.load_config_edge_mapping_task(),
            ],
            verbose=self.verbose,
        )

    @agent
    def edit_loading_job_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["edit_loading_job_agent"],  # pyright: ignore
            llm=self.llm,
        )

    @task
    def edit_loading_job_task(self) -> Task:
        return Task(
            config=self.tasks_config["edit_loading_job_task"],  # pyright: ignore
        )

    @crew
    def edit_loading_job_crew(self) -> Crew:
        return Crew(
            agents=[
                self.edit_loading_job_agent(),
            ],
            tasks=[
                self.edit_loading_job_task(),
            ],
            verbose=self.verbose,
        )

    @agent
    def run_loading_job_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["run_loading_job_agent"],  # pyright: ignore
            tools=[self.tool_registry[TigerGraphToolName.LOAD_DATA]],
            llm=self.llm,
        )

    @task
    def run_loading_job_task(self) -> Task:
        return Task(
            config=self.tasks_config["run_loading_job_task"],  # pyright: ignore
        )

    @crew
    def run_loading_job_crew(self) -> Crew:
        return Crew(
            agents=[
                self.run_loading_job_agent(),
            ],
            tasks=[
                self.run_loading_job_task(),
            ],
            verbose=self.verbose,
        )
