from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class PlannerCrew:
    def __init__(self, llm="gpt-4o", verbose=False):
        self.verbose = verbose
        self.llm = llm

    @agent
    def onboarding_detector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["onboarding_detector_agent"],  # pyright: ignore
            llm=self.llm,
        )

    @task
    def onboarding_detector_task(self) -> Task:
        return Task(
            config=self.tasks_config["onboarding_detector_task"],  # pyright: ignore
        )

    @crew
    def onboarding_detector_crew(self) -> Crew:
        return Crew(
            agents=[
                self.onboarding_detector_agent(),
            ],
            tasks=[
                self.onboarding_detector_task(),
            ],
            verbose=self.verbose,
        )

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["planner_agent"],  # pyright: ignore
            llm=self.llm,
        )

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],  # pyright: ignore
        )

    @crew
    def planning_crew(self) -> Crew:
        return Crew(
            agents=[
                self.planner_agent(),
            ],
            tasks=[
                self.planning_task(),
            ],
            verbose=self.verbose,
        )
