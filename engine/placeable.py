from itertools import starmap

import pygame as pg


class Placeable:
    """
    Base class for static objects in the simulation.
    """
    def __init__(self, name, x, y, color, collision=True):
        """
        :param name: Identifier for the object.
        :param x: Relative X coordinate.
        :param y: Relative Y coordinate.
        :param color: RGB color tuple.
        :param collision: Whether this object causes collisions.
        """
        self._name = name
        self._x = x
        self._y = y
        self._color = color
        self._collision = collision

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def color(self):
        return self._color

    @property
    def collision(self):
        return self._collision

    def draw(self, screen, screen_width, screen_height, tile_size):
        """
        Draw the object on the screen.
        """
        pass


class Rectangle(Placeable):
    """
    A class that stores the coordinates and the color of the rectangle.
    """
    def __init__(self, name, x, y, width, height, color=(0, 0, 0), collision=True):
        super().__init__(name, x, y, color, collision)
        self.width = width
        self.height = height

    def draw(self, screen, screen_width, screen_height, tile_size):
        # Check for valid positions
        if self.x * tile_size > screen_width or self.y * tile_size > screen_height:
            raise ValueError("Invalid coordinates for rectangle.")
        abs_x = int(self.x * tile_size)
        abs_y = int(self.y * tile_size)
        abs_width = int(self.width * tile_size)
        abs_height = int(self.height * tile_size)
        pg.draw.rect(screen, self.color, (abs_x, abs_y, abs_width, abs_height))

class Polygon(Placeable):
    """
    A class that stores the coordinates and the color of the polygon.
    """
    def __init__(self, name, points, color=(0, 0, 0), collision=True):
        super().__init__(name, 0, 0, color, collision)
        self.points = points

    def draw(self, screen, screen_width, screen_height, tile_size):
        processed_points = list(starmap(lambda x, y: (x * tile_size, y * tile_size), self.points))
        pg.draw.polygon(screen, self.color, processed_points)

class Circle(Placeable):
    """
    A class that stores the coordinates and the color of the circle.
    """
    def __init__(self, name, x, y, color=(0, 0, 0), collision=False):
        super().__init__(name, x, y, color, collision)

    def draw(self, screen, screen_width, screen_height, tile_size):
        abs_x = int(self.x * tile_size + tile_size / 2)
        abs_y = int(self.y * tile_size + tile_size / 2)
        abs_radius = tile_size / 2.5

        pg.draw.circle(screen, self.color, (abs_x, abs_y), abs_radius)