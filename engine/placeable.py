import pygame as pg
from itertools import starmap

class Placeable:
    """
    Base class for static objects in the simulation.
    """
    def __init__(self, name, x, y, color, collision=True):
        """
        :param name: Identifier for the object.
        :param x: Relative X coordinate (0-1).
        :param y: Relative Y coordinate (0-1).
        :param color: RGB color tuple.
        :param collision: Whether this object causes collisions.
        """
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.collision = collision

    def draw(self, screen, screen_width, screen_height):
        """
        Draw the object on the screen.
        """
        pass


class Rectangle(Placeable):
    def __init__(self, name, x, y, width, height, color=(0, 0, 0), collision=True):
        super().__init__(name, x, y, color, collision)
        self.width = width
        self.height = height

    def draw(self, screen, screen_width, screen_height):
        abs_x = int(self.x * screen_width)
        abs_y = int(self.y * screen_height)
        abs_width = int(self.width * screen_width)
        abs_height = int(self.height * screen_height)
        pg.draw.rect(screen, self.color, (abs_x, abs_y, abs_width, abs_height))

class Polygon(Placeable):
    def __init__(self, name, points, color=(0, 0, 0), collision=True):
        self.x, self.y = 0.5, 0.5
        super().__init__(name, self.x, self.y, color, collision)
        self.points = points

    def draw(self, screen, screen_width, screen_height):
        processed_points = list(starmap(lambda x, y: (x * screen_width, y * screen_height), self.points))
        pg.draw.polygon(screen, self.color, processed_points)

class Circle(Placeable):
    def __init__(self, name, x, y, radius, color=(0, 0, 0), collision=False):
        super().__init__(name, x, y, color, collision)
        self.radius = radius

    def draw(self, screen, screen_width, screen_height):
        abs_x = int(self.x * screen_width)
        abs_y = int(self.y * screen_height)
        abs_radius = int(self.radius * screen_width)
        pg.draw.circle(screen, self.color, (abs_x, abs_y), abs_radius)