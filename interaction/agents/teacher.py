import random
from datetime import datetime

from interaction.agents.agent import Agent, find_placeable_by_type, decide_next_target, draw_circle, in_bounds, \
    heuristic
from interaction.traverse_algorithms.pathfinder import PathFinder
from interaction.traverse_algorithms.random_block import random_subtile_in_rectangle
from interaction.utilities import Activity, Place, behaviour_probabilities


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

    def act(self, current_time, placeables, agent_props):
        self.__map_density = agent_props["map_density"]
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
            if current_time >= arriving_time and (self.__state["restart"] or current_time.minute < 50 and self.__state["break"]):
                entrance = find_placeable_by_type(placeables, "Entrance")
                if entrance is not None:
                    print(f"[INFO] Agent teacher spawned on the entrance")
                    self.__state["restart"] = False
                    self.__state["break"] = False
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
        # print(self.__state)

    def draw(self, screen, screen_width, screen_height, tile_size):
        draw_circle(screen, self.__gx, self.__gy, "T", tile_size, self.__map_density)
