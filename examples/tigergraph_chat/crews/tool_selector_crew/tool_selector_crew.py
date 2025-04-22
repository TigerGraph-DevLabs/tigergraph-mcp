from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ToolSelectorCrew:
    @agent
    def tool_selector_agent(self) -> Agent:
        return Agent(  # pyright: ignore
            config=self.agents_config["tool_selector_agent"],  # pyright: ignore
        )

    @task
    def select_tool_task(self) -> Task:
        return Task(
            config=self.tasks_config["select_tool_task"],  # pyright: ignore
        )

    # ------------------------------ Crew ------------------------------
    @crew
    def crew(self) -> Crew:
        """Creates the Crew"""
        return Crew(
            agents=self.agents,  # pyright: ignore
            tasks=self.tasks,  # pyright: ignore
        )
