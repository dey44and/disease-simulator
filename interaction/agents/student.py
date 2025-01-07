import random
from datetime import datetime

from engine.placeable import Placeable
from interaction.agents.agent import Agent, decide_next_target, find_placeable_by_type, draw_circle
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
        self.activity = Activity.OUTSIDE
        self.place = None
        self.__state = {
            "last_time": None,
            "restart": True,
            "break": True,
        }

        # A* path
        self.__path = []
        self.__target = None  # (col, row) in sub-tile

        # Possibly store assigned chair index or placeable reference
        self.__chair_index = id

        # agent's position in sub-tile coordinates (grid-based)
        self.__gx = -1
        self.__gy = -1

    def _set_grid_position(self, gx, gy):
        self.__gx = gx
        self.__gy = gy

    def _set_agent_properties(self, activity, place):
        self.activity = activity
        self.place = place
        self.__path = []
        self.__target = None

    def _get_grid_position(self):
        return self.__gx, self.__gy

    def get_chair_index(self):
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

        # Functions used to compute the path between points
        def in_bounds(grid, cell):
            # Method used to check the position of the cell inside the grid
            x, y = cell
            return 0 <= x < len(grid) and 0 <= y < len(grid[0])

        def heuristic(a, b):
            # We are using Manhattan distance as the heuristic function
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # 1) Check if the agents is outside the environment and the time to arrive => Spawn on a random tile on the entrance
        if self.activity == Activity.OUTSIDE:
            if current_time >= arriving_time and self.__state["restart"]:
                entrance = find_placeable_by_type(placeables, "Entrance")
                if entrance is not None:
                    print(f"[INFO] Agent {self.id} spawned on the entrance")
                    self.__state["restart"] = False
                    gx, gy = random_subtile_in_rectangle(entrance, agent_props["map_density"])
                    self._set_grid_position(gx, gy)

                    # Prepare self properties
                    self._set_agent_properties(Activity.MOVING, Place.BACKSPOT)

        # 2) Check if the agents is in the moving state, then follow or compute the path
        elif self.activity == Activity.MOVING:
            # If there is no path, compute one
            if not self.__path:
                if self.__target is None:
                    self.__target = decide_next_target(self, placeables, current_time, agent_props["map_density"])
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
                self._set_grid_position(nc, nr)
                if not self.__path:
                    # If the destination has been reached, the agents become IDLE
                    self.activity = Activity.IDLE

        # 3) If agents is in the idle state, check for break or leaving
        elif self.activity == Activity.IDLE:
            m = current_time.minute
            # check leaving
            if self.place == Place.ENTRANCE:
                # Agent has finished its day
                self.activity = Activity.OUTSIDE
                self._set_grid_position(-1, -1)
            else:
                # If agent's day is over
                if current_time >= leaving_time:
                    # Prepare self properties
                    self._set_agent_properties(Activity.MOVING, Place.ENTRANCE)
                # If break time (xx:50 - xx+1:00) or study time (xx:00 - xx:50)
                else:
                    if m >= 50 and self.place != Place.BACKSPOT and self.__state["break"]:
                        self.__state["break"] = False
                        # check agents behaviour
                        if random.random() < behaviour_probabilities[self.behaviour]:
                            self._set_agent_properties(Activity.MOVING, Place.BACKSPOT)
                    # If the class is started and the agents is not at his desk
                    elif m < 50 and self.place != Place.DESK:
                        self._set_agent_properties(Activity.MOVING, Place.DESK)

        self.__state["last_time"] = current_time
        # print(f"[INFO] Agent {self.id} is now at {self.__gx}, {self.__gy} and status is {self.activity} at {current_time}")

    def draw(self, screen, screen_width, screen_height, tile_size):
        draw_circle(screen, self.__gx, self.__gy, f"{self.id}", tile_size, self.__map_density)
