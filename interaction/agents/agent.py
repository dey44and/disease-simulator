import pygame as pg

from engine.colors import *
from engine.placeable import Placeable
from interaction.traverse_algorithms.random_block import random_subtile_in_rectangle
from interaction.utilities import *


def find_placeable_by_type(placeables, type):
    """
    Filter the placeables list to find the placeable by type. If there are multiple placeables of specified type,
    the first occurence is returned.
    :param placeables: List of placeables.
    :param type: Type of the placeable represented as string
    :return: the placeable with the specified type.
    """
    for p in placeables:
        if p.name == type:
            return p
    return None


def decide_next_target(agent, placeables, current_time, map_density):
    """
    Choose next target coordinates based on the current time and state of the agents.
    :param agent: A reference to the agents.
    :param placeables: A list of placeables.
    :param current_time: The current time.
    :param map_density: The density of the standard tile.
    :return: A tuple that represents the next target coordinates.
    """
    if agent.place in [Place.DESK, Place.TEACHER_DESK]:
        chair = None
        # Generate the position of the chair
        if agent.place == Place.DESK:
            chair = get_chair_for_agent(placeables, agent.get_chair_index())
        elif agent.place == Place.TEACHER_DESK:
            chair = find_placeable_by_type(placeables, "Armchair")
        if chair:
            sub_left = int(chair.x * map_density)
            sub_top = int(chair.y * map_density)
            return sub_left, sub_top

    hotspot = None
    if agent.place == Place.ENTRANCE:
        # Generate a random position on the entrance
        hotspot = find_placeable_by_type(placeables, "Entrance")
    elif agent.place == Place.BACKSPOT:
        # Generate a random position on the BackHotspot
        hotspot = find_placeable_by_type(placeables, "BackHotspot")
    return random_subtile_in_rectangle(hotspot, map_density) if hotspot else None


def get_chair_for_agent(placeables, index):
    """
    Return the chair associated with the given index.
    :param placeables: List of placeables.
    :param index: Index of the chair.
    :return: Chair associated with the given index.
    """
    # Filter the placeables and keep only the 'Chair' type
    chairs = [p for p in placeables if p.name == "Chair"]
    if index < len(chairs):
        return chairs[index]
    return None


def draw_circle(screen, px, py, text, tile_size, map_density):
    """
    Draw a circle on the screen.
    :param screen: Reference to the screen object.
    :param px: X coordinate of the center of the circle.
    :param py: Y coordinate of the center of the circle.
    :param text: Text to be drawn in the circle.
    :param tile_size: Size of the tile.
    :param map_density: The density of the standard tile.
    """
    if map_density:
        tx = int(px * map_density)
        ty = int(py * map_density)

        abs_x = int(tx * tile_size + tile_size / 2)
        abs_y = int(ty * tile_size + tile_size / 2)
        abs_radius = tile_size / 2.5

        pg.draw.circle(screen, WHITE, (abs_x, abs_y), abs_radius)
        pg.draw.circle(screen, BLACK, (abs_x, abs_y), abs_radius, width=3)
        # Create a font
        font = pg.font.Font(None, 24)
        text_surface = font.render(text, True, BLACK)  # black color
        screen.blit(text_surface, (abs_x - abs_radius / 2, abs_y - abs_radius / 2))

class Agent:
    def __init__(self, id, schedule, style="lazy", behaviour="quiet", mask="no-mask", vaccine="no-vax"):
        """
        Constructor for Agent class.
        :param id: The id of the agents.
        :param schedule: The schedule of the agents.
        :param style: The style of the agents (lazy, smart, neutral).
        :param behaviour: The behaviour of the agents (quiet, active).
        :param mask: The mask of the agents.
        :param vaccine: The vaccine.
        """
        if style not in style_probabilities.keys():
            raise ValueError("Invalid agents style")
        if behaviour not in behaviour_probabilities.keys():
            raise ValueError("Invalid agents behaviour")
        if mask not in mask_protection_probabilities.keys():
            raise ValueError("Invalid agents mask")
        if vaccine not in vaccine_protection_probabilities.keys():
            raise ValueError("Invalid agents vaccine")
        self.id = id
        self.schedule = schedule
        self.style = style
        self.behaviour = behaviour
        self.mask = mask
        self.vaccine = vaccine

        # Agent attributes
        self.__map_density = None
        self.__gx = None
        self.__gy = None

    def act(self, current_time: str, placeables: list[Placeable], agent_props):
        """
        Called each simulation 'tick'. Manages daily logic:
          - If OUTSIDE and it's time to arrive, spawn in entrance
          - If MOVING, follow path
          - If IDLE, check break times or leaving times
        """
        pass

    def draw(self, screen, screen_width, screen_height, tile_size):
        """
        Draws the character on the screen.
        :param screen: Reference to the screen to draw on.
        :param screen_width: Width of the screen.
        :param screen_height: Height of the screen.
        :param tile_size: Size of the tile.
        """
        pass