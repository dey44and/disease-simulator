import random

import pygame as pg

from engine.colors import BLACK, WHITE
from interaction.pathfinder import PathFinder
from interaction.utilities import *
from datetime import datetime


class Agent(object):
    def __init__(self, id, schedule, style="lazy", behaviour="quiet", mask="no-mask", vaccine="no-vax"):
        """
        Constructor for Agent class.
        :param id: The id of the agent.
        :param schedule: The schedule of the agent.
        :param style: The style of the agent (lazy, smart, neutral).
        :param behaviour: The behaviour of the agent (quiet, active).
        :param mask: The mask of the agent.
        :param vaccine: The vaccine.
        """
        if style not in style_probabilities.keys():
            raise ValueError("Invalid agent style")
        if behaviour not in behaviour_probabilities.keys():
            raise ValueError("Invalid agent behaviour")
        if mask not in mask_protection_probabilities.keys():
            raise ValueError("Invalid agent mask")
        if vaccine not in vaccine_protection_probabilities.keys():
            raise ValueError("Invalid agent vaccine")
        self.id = id
        self.schedule = schedule
        self.style = style
        self.behaviour = behaviour
        self.mask = mask
        self.vaccine = vaccine
        self.map_density = None # Be careful to initiate this parameter :)

        # Current state of the agent [susceptible, infected, quarantined, recovered]
        self.pandemic_status = PandemicStatus.SUSCEPTIBLE

        # Current activity state of the agent
        self.activity = Activity.OUTSIDE

        # A* path
        self.__path = []
        self.__target = None  # (col, row) in sub-tile

        # Possibly store assigned chair index or placeable reference
        self.chair_index = id

        # agent's position in sub-tile coordinates (grid-based)
        self.__gx = -1
        self.__gy = -1

    def set_grid_position(self, gx, gy):
        self.__gx = gx
        self.__gy = gy

    def get_grid_position(self):
        return self.__gx, self.__gy

    def act(self, current_time, placeables, agent_props):
        """
        Called each simulation 'tick'. Manages daily logic:
          - If OUTSIDE and it's time to arrive, spawn in entrance
          - If MOVING, follow path
          - If IDLE, check break times or leaving times
        """
        self.map_density = agent_props["map_density"]
        # parse times
        fmt = "%H:%M:%S"
        arriving_time = datetime.strptime(self.schedule["arriving"], fmt).time()
        leaving_time = datetime.strptime(self.schedule["leaving"], fmt).time()
        current_time = datetime.strptime(current_time, fmt).time()

        map_density = agent_props["map_density"]
        collision_grid = agent_props["collision_grid"]
        tile_size = agent_props["tile_size"]

        # Some functions
        def in_bounds(grid, cell):
            x, y = cell
            return 0 <= x < len(grid) and 0 <= y < len(grid[0])

        def heuristic(a, b):
            # We are using Manhattan distance as the euristic function
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # --- 1) If OUTSIDE and time to arrive => spawn in entrance
        if self.activity == Activity.OUTSIDE:
            if current_time >= arriving_time:
                print(f"[INFO] Agent {self.id} appears and starts moving")
                entrance = find_placeable_by_type(placeables, "Entrance")
                if entrance is not None:
                    # pick a random sub-tile inside the entrance rectangle
                    gx, gy = random_subtile_in_rectangle(entrance, map_density)
                    print(f"[INFO] Entrance {entrance.x}, {entrance.y}")
                    print(f"[INFO] The starting position is {gx}, {gy}")
                    self.set_grid_position(gx, gy)
                    self.activity = Activity.MOVING
                    self.__path = []
                    self.__target = None

        # --- 2) If MOVING => follow or compute path
        elif self.activity == Activity.MOVING:
            if not self.__path:
                # No path => compute a new target if we don't have one
                if self.__target is None:
                    self.__target = decide_next_target(
                        self, placeables, current_time, map_density
                    )
                    print(f"[INFO] The target is now {self.__target}")
                # compute A* if there's a valid target
                if self.__target is not None:
                    start_cell = (self.__gy, self.__gx)  # row,col
                    goal_cell = (self.__target[1], self.__target[0])
                    path = PathFinder.astar_pathfinding(collision_grid, start_cell, goal_cell, in_bounds, heuristic)
                    if not path:
                        # can't reach => become idle
                        self.activity = Activity.IDLE
                        return
                    # store path (excluding the first cell, which is our current pos)
                    self.__path = path[1:]
            else:
                # We have a path => pop next cell
                next_cell = self.__path.pop(0)
                nr, nc = next_cell
                self.set_grid_position(nc, nr)
                if not self.__path:
                    # reached destination
                    self.activity = Activity.IDLE

        # --- 3) If IDLE => check break or leaving
        elif self.activity == Activity.IDLE:
            h = current_time.hour
            m = current_time.minute

            # If break time (xx:50 .. xx+1:00)
            if m >= 50:
                # check if agent is "active" => might go to back_hotspot
                p_active = behaviour_probabilities[self.behaviour]
                if random.random() < p_active:
                    # Start moving
                    self.activity = Activity.MOVING
                    self.__path = []
                    self.__target = None
                # else remain idle at seat
            # check leaving
            if current_time >= leaving_time:
                # plan route to exit
                self.activity = Activity.MOVING
                self.__path = []
                self.__target = None

        # else: other states (AT_WHITEBOARD, etc.)
        print(f"[INFO] Agent {self.id} is now at {self.__gx}, {self.__gy} and status is {self.activity}")

    def draw(self, screen, screen_width, screen_height, tile_size):
        if self.map_density:
            # tile coords
            tx = int(self.__gx / self.map_density)
            ty = int(self.__gy / self.map_density)

            abs_x = int(tx * tile_size + tile_size / 2)
            abs_y = int(ty * tile_size + tile_size / 2)
            abs_radius = tile_size / 2.5

            pg.draw.circle(screen, WHITE, (abs_x, abs_y), abs_radius)
            pg.draw.circle(screen, BLACK, (abs_x, abs_y), abs_radius, width=3)
            # Create a font
            font = pg.font.Font(None, 24)
            text_surface = font.render(f"{self.id}", True, BLACK)  # black color
            screen.blit(text_surface, (abs_x - abs_radius / 2, abs_y - abs_radius / 2))

def find_placeable_by_type(placeables, type_):
    for p in placeables:
        if p.name == type_:
            return p
    return None

def random_subtile_in_rectangle(rect_placeable, map_density):
    import random
    # rect_placeable.x, rect_placeable.y, rect_placeable.width, rect_placeable.height in tile coords
    sub_left = int(rect_placeable.x * map_density)
    sub_top = int(rect_placeable.y * map_density)
    sub_w = int(rect_placeable.width * map_density)
    sub_h = int(rect_placeable.height * map_density)

    gx = random.randint(sub_left, sub_left + sub_w - 1)
    gy = random.randint(sub_top, sub_top + sub_h - 1)
    return (gx, gy)

def decide_next_target(agent, placeables, current_time, map_density):
    """
    Decide where the agent wants to go next:
      - If it's the first time, maybe pick back_hotspot or seat
      - If it's break, pick back_hotspot or seat
      - If agent has no seat yet, pick a seat
      - etc.
    Returns (gx, gy) in sub-tile coords, or None
    """
    # Example logic: if we haven't sat yet, go to our assigned chair
    # We assume chairs is a list of "Circle" placeables with type="Chair"
    # index in that list = agent.id
    # But you can adapt as needed
    hour = current_time.hour
    minute = current_time.minute
    if minute >= 50:
        # break => possibly go to "BackHotspot"
        hotspot = find_placeable_by_type(placeables, "BackHotspot")
        if hotspot:
            return random_subtile_in_rectangle(hotspot, map_density)
        else:
            return None
    else:
        # go to assigned chair
        chair = get_chair_for_agent(placeables, agent.chair_index)
        if chair:
            # place the agent in center => (x + radius/2, y + radius/2)
            # but actually we store it as a rectangle for pathing
            sub_left = int(chair.x * map_density)
            sub_top = int(chair.y * map_density)
            # or you can aim for the center if it's a circle
            # For simplicity, we aim for the top-left
            return sub_left, sub_top
    return None

def get_chair_for_agent(placeables, index):
    # Suppose you have a list of all chairs in sorted order
    chairs = [p for p in placeables if p.type == "Chair"]
    if index < len(chairs):
        return chairs[index]
    return None
