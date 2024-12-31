import pygame as pg

class SceneDrawer:
    """
    Handles drawing all static and dynamic elements on the screen.
    """
    def __init__(self, screen, placeables, actors):
        self.screen = screen
        self.placeables = placeables  # List of Placeable objects
        self.actors = actors  # List of Actor objects

    def draw_scene(self):
        """
        Draw all elements in the scene.
        """
        for placeable in self.placeables:
            placeable.draw(self.screen, self.screen.get_width(), self.screen.get_height())
        for actor in self.actors:
            actor.draw(self.screen)
        pg.display.flip()
