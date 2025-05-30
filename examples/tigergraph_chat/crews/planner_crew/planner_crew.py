from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class PlannerCrew:
    def __init__(self, verbose=False):
        self.verbose = verbose

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["planner_agent"],  # pyright: ignore
        )

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],  # pyright: ignore
        )

    # ------------------------------ Crew ------------------------------
    @crew
    def crew(self) -> Crew:
        """Creates the Crew"""
        return Crew(
            agents=self.agents,  # pyright: ignore
            tasks=self.tasks,  # pyright: ignore
            verbose=self.verbose,
        )
