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
    def draft_loading_job_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["draft_loading_job_agent"],  # pyright: ignore
            tools=[self.tool_registry[TigerGraphToolName.GET_SCHEMA]],
            llm=self.llm,
        )

    @task
    def draft_loading_job_task(self) -> Task:
        return Task(
            config=self.tasks_config["draft_loading_job_task"],  # pyright: ignore
        )

    @crew
    def draft_loading_job_crew(self) -> Crew:
        return Crew(
            agents=[
                self.draft_loading_job_agent(),
            ],
            tasks=[
                self.draft_loading_job_task(),
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
