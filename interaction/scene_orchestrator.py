import logging
from datetime import datetime, timedelta

from engine.placeable import Placeable
from interaction.agents.student import Student
from interaction.agents.teacher import Teacher
from interaction.disease.spread_simulator import SpreadSimulator
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
            timer: Timer,
            spread_simulator: SpreadSimulator,
    ):
        """
        Constructor.
        :param agents: List of agents.
        :param agents_prop: Dictionary of agents' properties.
        :param teacher: Reference to teacher object.
        :param placeables: List with placeables.
        :param timer: Reference to timer object.
        :param spread_simulator: Reference to spread simulator.
        """
        # Set logger properties
        self.__logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        self.__agents = agents
        self.__agents_prop = agents_prop
        self.__teacher = teacher
        self.__placeables = placeables
        self.__timer = timer
        self.__spread_simulator = spread_simulator

        self.__last_time = self.__timer.current_time_of_day
        self.__finished = False

        if self.__teacher is None:
            self.__logger.warning("Teacher doesn't exist, but the simulation will continue.")

    def simulate_once(self):
        """
        Jump by the number of seconds from the config file.
        """
        if self.__finished:
            return

        # Simulate the action for each agent
        fmt = "%H:%M:%S"
        current_date = self.__last_time.date()
        start_time = datetime.combine(current_date, datetime.strptime(self.__agents_prop["start_time"], fmt).time())
        end_time = datetime.combine(current_date, datetime.strptime(self.__agents_prop["end_time"], fmt).time())

        # 1) MORNING check
        if self.__last_time == start_time:
            self.__logger.info(f"A new simulation started at {start_time}")
            # Simulate for students
            for agent in self.__agents:
                agent.morning_infection_check(self.__agents_prop, current_dt=self.__last_time)
            # Simulate for teacher
            if self.__teacher:
                self.__teacher.morning_infection_check(self.__agents_prop, current_dt=self.__last_time)

        # 2) RUN the day
        for agent in self.__agents:
            agent.act(current_date, self.__timer.time_str, self.__placeables, self.__agents_prop, self.__spread_simulator)
        if self.__teacher:
            self.__teacher.act(current_date, self.__timer.time_str, self.__placeables, self.__agents_prop, self.__spread_simulator)

        # 3) ENDING check
        if self.__last_time == end_time - timedelta(seconds=self.__agents_prop["time_step_seconds"]):
            # Simulate for students
            for agent in self.__agents:
                agent.end_of_day_test(self.__last_time)
            # Simulate for teacher
            if self.__teacher:
                self.__teacher.end_of_day_test(self.__last_time)

        # Simulate the virus spread
        self.__spread_simulator.update()

        # Go to the next moment
        current_time = self.__timer.tick()

        # Check for end of the day or the simulation
        if current_time.time() == end_time.time():
            self.__spread_simulator.reset_grid()
        self.__finished = self.__timer.check_finished()
        self.__last_time = self.__timer.current_time_of_day

    @property
    def agents(self) -> list[Student]:
        return self.__agents

    @property
    def teacher(self) -> Teacher:
        return self.__teacher

    @property
    def placeables(self) -> list[Placeable]:
        return self.__placeables

    @property
    def timer(self) -> Timer:
        return self.__timer

    @property
    def finished(self) -> bool:
        return self.__finished

    @property
    def spread_simulator(self) -> SpreadSimulator:
        return self.__spread_simulator

    def agents_prop(self, prop: str):
        return self.__agents_prop[prop]