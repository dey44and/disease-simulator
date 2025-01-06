from engine.placeable import Placeable
from interaction.utilities import *


class Agent(object):
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