from functools import cached_property

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool

from tigergraph_mcp import TigerGraphToolName

verbose = True


@CrewBase
class SchemaCreationCrews:
    def __init__(self, tools: dict[str, BaseTool]):
        self._tool_registry = tools

    @cached_property
    def tool_registry(self) -> dict[str, BaseTool]:
        return self._tool_registry

    @agent
    def draft_schema_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["draft_schema_agent"],  # pyright: ignore
            llm="gpt-4o",
        )

    @task
    def draft_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config["draft_schema_task"],  # pyright: ignore
        )

    @crew
    def draft_schema_crew(self) -> Crew:
        return Crew(
            agents=[
                self.draft_schema_agent(),
            ],
            tasks=[
                self.draft_schema_task(),
            ],
            verbose=verbose,
        )

    @agent
    def edit_schema_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["edit_schema_agent"],  # pyright: ignore
            llm="gpt-4o",
        )

    @task
    def edit_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config["edit_schema_task"],  # pyright: ignore
        )

    @crew
    def edit_schema_crew(self) -> Crew:
        return Crew(
            agents=[
                self.edit_schema_agent(),
            ],
            tasks=[
                self.edit_schema_task(),
            ],
            verbose=verbose,
        )

    @agent
    def create_schema_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["create_schema_agent"],  # pyright: ignore
            tools=[self.tool_registry[TigerGraphToolName.CREATE_SCHEMA]],
            llm="gpt-4o",
        )

    @task
    def create_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_schema_task"],  # pyright: ignore
        )

    @crew
    def create_schema_crew(self) -> Crew:
        return Crew(
            agents=[
                self.create_schema_agent(),
            ],
            tasks=[
                self.create_schema_task(),
            ],
            verbose=verbose,
        )
