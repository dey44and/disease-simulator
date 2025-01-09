import math
import random
from datetime import datetime

from interaction.agents.agent import Agent, find_placeable_by_type, decide_next_target, draw_circle, in_bounds, \
    heuristic
from interaction.disease.spread_simulator import SpreadSimulator
from interaction.disease.health_manager import PandemicStateManager
from interaction.traversealgorithms.pathfinder import PathFinder
from interaction.traversealgorithms.random_block import random_subtile_in_rectangle
from interaction.utilities import Activity, Place, behaviour_probabilities, mask_protection_probabilities, \
    vaccine_protection_probabilities


class Teacher(Agent):
    def __init__(self, id, schedule, style="lazy", behaviour="quiet", mask="no-mask", vaccine="no-vax"):
        """
        Constructor for Teacher class.
        :param id: The id of the agents.
        :param schedule: The schedule of the agents.
        :param style: The style of the agents (lazy, smart, neutral).
        :param behaviour: The behaviour of the agents (quiet, active).
        :param mask: The mask of the agents.
        :param vaccine: The vaccine.
        """
        super().__init__(id, schedule, style, behaviour, mask, vaccine)
        self.__map_density = None  # Be careful to initiate this parameter :)

        # Current pandemic status of the agents [susceptible, infected, quarantined, recovered]
        self.__health_manager = PandemicStateManager(agent_id=id)

        # Current activity state of the agents
        self.__activity = Activity.OUTSIDE
        self.__place = None
        self.__state = {
            "last_time": None,
            "restart": True,
            "break": False,
        }

        # A* path
        self.__path = []
        self.__target = None  # (col, row) in sub-tile

        # agent's position in sub-tile coordinates (grid-based)
        self.__gx = -1
        self.__gy = -1

    @property
    def activity(self):
        return self.__activity

    @activity.setter
    def activity(self, value):
        self.__activity = value

    @property
    def place(self):
        return self.__place

    @place.setter
    def place(self, value):
        self.__place = value

    @property
    def grid_position(self):
        return self.__gx, self.__gy

    @grid_position.setter
    def grid_position(self, value):
        x, y = value
        self.__gx = x
        self.__gy = y

    @property
    def agent_properties(self):
        return self.activity, self.place, self.__path, self.__target

    @agent_properties.setter
    def agent_properties(self, value):
        activity, place = value
        self.activity = activity
        self.place = place
        self.__path = []
        self.__target = None

    # ----------------------------------
    # Health Manager Hooks
    # ----------------------------------

    def morning_infection_check(self, agent_props: dict, current_dt: datetime):
        """
        Called once at the start of each day (or once when the day changes).
        If SUSCEPTIBLE => infection_prob chance to become infected.
        Also check if quarantine is expired => become RECOVERED if so.
        """
        # 1. update quarantine if we were quarantined
        self.__health_manager.update_quarantine(current_dt)

        if self.__health_manager.is_quarantined():
            # still quarantined => skip infection check
            return

        infection_prob = agent_props.get("infection_prob", 0.0)
        if self.__health_manager.is_susceptible():
            if random.random() < infection_prob:
                self.__health_manager.become_infected(current_dt)

    def update_during_day(self, current_dt: datetime):
        """
        Called every simulation tick (or every so often) to handle transitions from pre-symp => symptomatic.
        """
        self.__health_manager.update_status_during_day(current_dt)

    def end_of_day_test(self, current_dt: datetime):
        """
        At the end of the day, if agent is symptomatic => quarantine.
        """
        self.__health_manager.end_of_day_test(current_dt)
        if self.__health_manager.is_quarantined():
            # We consider agent removed from environment
            self.__activity = Activity.OUTSIDE
            self.__gx = -1
            self.__gy = -1

    def _check_infection_from_environment(
            self,
            current_dt: datetime,
            spread_simulator: SpreadSimulator,
            agent_props: dict
    ):
        """
        If the agent is susceptible, we check the local droplet load,
        apply mask & vaccine, and see if infection occurs.
        """
        mask_eff = mask_protection_probabilities.get(self.mask, 0.0)
        vaccine_eff = vaccine_protection_probabilities.get(self.vaccine, 0.0)

        # 1) Gather total droplet load from sub-cells
        start_x = self.__gx * agent_props.get("grid_density", 1)
        start_y = self.__gy * agent_props.get("grid_density", 1)

        total_load = 0.0
        count = 0
        for rx in range(start_x, start_x + agent_props.get("grid_density", 1)):
            for ry in range(start_y, start_y + agent_props.get("grid_density", 1)):
                abs_load = spread_simulator.get_rate(ry, rx)  # Possibly you define this
                total_load += abs_load
                count += 1
        avg_load = total_load / count if count > 0 else 0.0

        # 2) Apply mask => a fraction passes
        load_after_mask = avg_load * (1 - mask_eff)

        # 3) Convert load => infection probability
        #    Option: exponential approach => p = 1 - exp(-k * load_after_mask)
        k = agent_props.get("infection_k", 0.00014)  # TODO: a scale factor for environment-based infection
        raw_prob = 1 - math.exp(-k * load_after_mask)

        # 4) Vaccine further reduces infection chance
        #    E.g. final p = raw_prob * (1 - vaccine_eff)
        p_infection = raw_prob * (1 - vaccine_eff)

        # Random draw => infect
        if random.random() < p_infection:
            self.__health_manager.become_infected(current_dt)

    # ----------------------------------
    # Act Logic
    # ----------------------------------

    def _simulate_movement_and_breaks(self, current_time, placeables, agent_props):
        # parse times
        fmt = "%H:%M:%S"
        arriving_time = datetime.strptime(self.schedule["arriving"], fmt).time()
        leaving_time = datetime.strptime(self.schedule["leaving"], fmt).time()
        current_time = datetime.strptime(current_time, fmt).time()

        # Reset restart parameter
        if self.__state["last_time"] is None or current_time < self.__state["last_time"]:
            self.__state["restart"] = True

        # 1) Check if the agents is outside the environment and the time to arrive => Spawn on a random tile on the entrance
        if self.activity == Activity.OUTSIDE:
            if current_time >= arriving_time and (
                    self.__state["restart"] or current_time.minute < 50 and self.__state["break"]):
                entrance = find_placeable_by_type(placeables, "Entrance")
                if entrance is not None:
                    # print(f"[INFO] Agent teacher spawned on the entrance")
                    self.__state["restart"] = False
                    self.__state["break"] = False
                    self.grid_position = random_subtile_in_rectangle(entrance, map_density=agent_props["map_density"])

                    # Prepare self properties
                    self.agent_properties = (Activity.MOVING, Place.BACK)

        # 2) Check if the agents is in the moving state, then follow or compute the path
        elif self.activity == Activity.MOVING:
            # If there is no path, compute one
            if not self.__path:
                if self.__target is None:
                    self.__target = decide_next_target(self, placeables, map_density=agent_props["map_density"])
                # use A* to compute the path
                if self.__target is not None:
                    start_cell = (self.__gy, self.__gx)
                    goal_cell = (self.__target[1], self.__target[0])
                    path = PathFinder.astar_pathfinding(agent_props["collision_grid"], start_cell, goal_cell,
                                                        in_bounds, heuristic)
                    if not path:
                        # If the point cannot be reached, become IDLE
                        self.activity = Activity.IDLE
                        return
                    # store path except the first coordinates (the starting point)
                    self.__path = path[1:]
            # If there is a path, move to the next point
            else:
                next_cell = self.__path.pop(0)
                nr, nc = next_cell
                self.grid_position = (nc, nr)
                if not self.__path:
                    # If the destination has been reached, the agents become IDLE
                    self.activity = Activity.IDLE

        # 3) If agents is in the idle state, check for break or leaving
        elif self.activity == Activity.IDLE:
            # check leaving
            if self.place == Place.ENTRANCE:
                # Agent has finished its day or Agent shall leave the environment during the break
                self.activity = Activity.OUTSIDE
                self.grid_position = (-1, -1)
            else:
                # If agent's day is over
                if current_time >= leaving_time:
                    # Prepare self properties
                    self.agent_properties = (Activity.MOVING, Place.ENTRANCE)
                # If the class is started and the agents is not at his desk
                elif current_time.minute < 50 and self.place != Place.TEACHER_DESK:
                    self.agent_properties = (Activity.MOVING, Place.TEACHER_DESK)
                # If it's time for a break depending on the teacher's style
                elif current_time.minute >= 50 and self.place == Place.TEACHER_DESK:
                    if random.random() < behaviour_probabilities[self.behaviour]:
                        self.agent_properties = (Activity.MOVING, Place.ENTRANCE)
                        self.__state["break"] = True

        self.__state["last_time"] = current_time
        # print(f"[INFO] Agent {self.id} is now at {self.__gx}, {self.__gy} and status is {self.activity} at {current_time}")

    def act(self, current_date: datetime.date, current_time, placeables, agent_props, spread_simulator: SpreadSimulator):
        self.__map_density = agent_props["map_density"]
        current_dt = datetime.combine(current_date, datetime.strptime(current_time, "%H:%M:%S").time())

        # If quarantined => skip environment
        if self.__health_manager.is_quarantined():
            return

        # If susceptible => sample environment => mask => vaccine => infection chance
        if self.__health_manager.is_susceptible() and spread_simulator:
            self._check_infection_from_environment(current_dt, spread_simulator, agent_props)

        # If pre-symptomatic => shed virus
        if spread_simulator and self.__health_manager.is_infectious():
            # Shed with some mask effect
            mask_eff = mask_protection_probabilities.get(self.mask, 0.0)
            shed_amount = agent_props["base_shedding"] * (1 - mask_eff)
            (gx, gy) = (self.__gx * agent_props["grid_density"], self.__gy * agent_props["grid_density"])
            # If you do sub-tiles, loop them
            for rx in range(gx, gx + agent_props["grid_density"]):
                for ry in range(gy, gy + agent_props["grid_density"]):
                    spread_simulator.add_source(ry, rx, shed_amount)

        # Update any transitions from pre to symptomatic
        self.update_during_day(current_dt)

        # Simulate the movement of the agent
        self._simulate_movement_and_breaks(current_time, placeables, agent_props)


    def draw(self, screen, screen_width, screen_height, tile_size):
        draw_circle(screen, self.__gx, self.__gy, "T", tile_size, self.__map_density, self.__health_manager.status)
