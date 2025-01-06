from engine.placeable import Placeable
from interaction.agents.student import Student
from interaction.agents.teacher import Teacher
from interaction.timer import Timer


class SceneOrchestrator:
    """
    Class designed to coordinate the environment.
    """
    def __init__(
            self,
            agents: list[Student],
            agents_prop,
            teacher: Teacher,
            placeables: list[Placeable],
            timer: Timer
    ):
        self.__agents = agents
        self.__agents_prop = agents_prop
        self.__teacher = teacher
        self.__placeables = placeables
        self.__timer = timer
        self.__finished = False

    def simulate_once(self):
        """
        Jump by the number of seconds from the config file.
        """
        if self.__finished:
            return

        # Simulate the action for each agent
        for agent in self.__agents:
            agent.act(self.__timer.get_time_str(), self.__placeables, self.__agents_prop)
        self.__teacher.act(self.__timer.get_time_str(), self.__placeables, self.__agents_prop)

        # Go to the next moment
        self.__timer.tick()
        self.__finished = self.__timer.check_finished()

    def get_agents(self):
        return self.__agents

    def get_teacher(self):
        return self.__teacher

    def get_placeables(self):
        return self.__placeables

    def get_timer(self):
        return self.__timer

    def get_agents_prop(self, prop: str):
        return self.__agents_prop[prop]

    def is_finished(self) -> bool:
        return self.__finished