import random
from datetime import datetime

from engine.placeable import Placeable
from interaction.agents.agent import Agent, decide_next_target, find_placeable_by_type, draw_circle, in_bounds, \
    heuristic, next_class_start
from interaction.timer import sample_gamma_time, add_minutes_to_time
from interaction.traverse_algorithms.pathfinder import PathFinder
from interaction.traverse_algorithms.random_block import random_subtile_in_rectangle
from interaction.utilities import *


class Student(Agent):
    def __init__(self, id, schedule, style="lazy", behaviour="quiet", mask="no-mask", vaccine="no-vax"):
        """
        Constructor for Student class.
        :param id: The id of the agents.
        :param schedule: The schedule of the agents.
        :param style: The style of the agents (lazy, smart, neutral).
        :param behaviour: The behaviour of the agents (quiet, active).
        :param mask: The mask of the agents.
        :param vaccine: The vaccine.
        """
        super().__init__(id, schedule, style, behaviour, mask, vaccine)
        self.__map_density = None  # Be careful to initiate this parameter :)

        # Current state of the agents [susceptible, infected, quarantined, recovered]
        self.pandemic_status = PandemicStatus.SUSCEPTIBLE

        # Current activity state of the agents
        self.__activity = Activity.OUTSIDE
        self.__place = None
        self.__state = {
            "last_time": None,         # Last simulated time
            "restart": True,           # When we restart the agent
            "break": True,             # Whether the agent is allowed to take a break or not
            "desk_delay_end": None,    # When we finish waiting at the desk
            "back_hotspot_end": None       # When we finish at the back hotspot
        }

        # A* path
        self.__path = []
        self.__target = None  # (col, row) in sub-tile

        # Possibly store assigned chair index or placeable reference
        self.__chair_index = id

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

    @property
    def chair_index(self):
        return self.__chair_index

    def act(self, current_time: str, placeables: list[Placeable], agent_props: dict):
        self.__map_density = agent_props["map_density"]
        # parse times
        fmt = "%H:%M:%S"
        arriving_time = datetime.strptime(self.schedule["arriving"], fmt).time()
        leaving_time = datetime.strptime(self.schedule["leaving"], fmt).time()
        current_time = datetime.strptime(current_time, fmt).time()

        # Reset restart parameter
        if self.__state["last_time"] is None or current_time < self.__state["last_time"]:
            self.__state["restart"] = True
        # Reset break parameter
        if not self.__state["break"] and current_time.minute < 50:
            self.__state["break"] = True

        # 1) Check if the agents is outside the environment and the time to arrive => Spawn on a random tile on the entrance
        if self.activity == Activity.OUTSIDE:
            if current_time >= arriving_time and self.__state["restart"]:
                entrance = find_placeable_by_type(placeables, "Entrance")
                if entrance is not None:
                    print(f"[INFO] Agent {self.id} spawned on the entrance")
                    self.__state["restart"] = False
                    gx, gy = random_subtile_in_rectangle(entrance, agent_props["map_density"])
                    self.grid_position = (gx, gy)

                    # Prepare self properties
                    self.agent_properties = (Activity.MOVING, Place.BACKSPOT)

        # 2) Check if the agents is in the moving state, then follow or compute the path
        elif self.activity == Activity.MOVING:
            # If there is no path, compute one
            if not self.__path:
                if self.__target is None:
                    self.__target = decide_next_target(self, placeables, agent_props["map_density"])
                # use A* to compute the path
                if self.__target is not None:
                    start_cell = (self.__gy, self.__gx)
                    goal_cell = (self.__target[1], self.__target[0])
                    path = PathFinder.astar_pathfinding(agent_props["collision_grid"], start_cell, goal_cell, in_bounds, heuristic)
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
            # Check if the day is finished
            if self.place == Place.ENTRANCE:
                self.activity = Activity.OUTSIDE
                self.grid_position = (-1, -1)
            else:
                # If agent's day is over, go to entrance
                if current_time >= leaving_time:
                    self.agent_properties = (Activity.MOVING, Place.ENTRANCE)
                # Check for different activities
                else:
                    # --- Check for break ---
                    if current_time.minute >= 50 and self.place != Place.BACKSPOT and self.__state["break"]:
                        self.__state["break"] = False  # Break logic shouldn't be triggered again this hour
                        # Decide if we want to leave the desk
                        if random.random() < behaviour_probabilities[self.behaviour]:
                            # Generate a short desk delay up to 5 min
                            wait_minutes = sample_gamma_time(shape=2.0, scale=1.0, max_minutes=5)
                            self.__state["desk_delay_end"] = add_minutes_to_time(current_time, wait_minutes)
                            self.__state["back_hotspot_end"] = None  # When the break is done
                    # Check if we have a pending desk delay that expired
                    if self.__state["desk_delay_end"]:
                        # If we've reached or passed the time to leave desk
                        if current_time >= self.__state["desk_delay_end"]:
                            # If minutes_left is positive, he shall go the hotspot
                            if 60 - current_time.minute > 0:
                                back_hotspot_time = sample_gamma_time(shape=2.0, scale=1.0, max_minutes=60-current_time.minute)
                                self.__state["back_hotspot_end"] = add_minutes_to_time(current_time, back_hotspot_time)
                                self.__state["desk_delay_end"] = None
                                self.agent_properties = (Activity.MOVING, Place.BACKSPOT)
                    # --- Class time logic ---
                    elif current_time.minute < 50 and self.place != Place.DESK:
                        self.agent_properties = (Activity.MOVING, Place.DESK)

        self.__state["last_time"] = current_time
        # print(f"[INFO] Agent {self.id} is now at {self.__gx}, {self.__gy} and status is {self.activity} at {current_time}")

    def draw(self, screen, screen_width, screen_height, tile_size):
        draw_circle(screen, self.__gx, self.__gy, f"{self.id}", tile_size, self.__map_density)
