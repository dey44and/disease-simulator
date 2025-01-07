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
            agent.act(self.__timer.time_str, self.__placeables, self.__agents_prop)
        self.__teacher.act(self.__timer.time_str, self.__placeables, self.__agents_prop)

        # Go to the next moment
        self.__timer.tick()
        self.__finished = self.__timer.check_finished()

    @property
    def agents(self):
        return self.__agents

    @property
    def teacher(self):
        return self.__teacher

    @property
    def placeables(self):
        return self.__placeables

    @property
    def timer(self):
        return self.__timer

    @property
    def finished(self) -> bool:
        return self.__finished

    def agents_prop(self, prop: str):
        return self.__agents_prop[prop]