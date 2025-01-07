import pygame as pg

from engine.colors import WHITE


class SceneDrawer:
    """
    Draws the scene on the screen.
    """
    def __init__(self, screen, orchestrator=None):
        """
        Constructor for SceneDrawer class.
        :param orchestrator: Reference to SceneOrchestrator so we can extract scene details.
        """
        self.__screen = screen
        self.__orchestrator = orchestrator

    @property
    def screen(self):
        return self.__screen

    @property
    def orchestrator(self):
        return self.__orchestrator

    def draw_scene(self, tile_size):
        """
        Draws the scene on the screen scaled by tile_size.
        :param tile_size: The size of the tile.
        """
        # 1) Draw placeables
        for placeable in self.orchestrator.placeables:
            placeable.draw(self.screen, self.screen.get_width(), self.screen.get_height(), tile_size)

        # 2) Draw actors
        for agent in self.orchestrator.agents:
            agent.draw(self.screen, self.screen.get_width(), self.screen.get_height(),
                       tile_size / self.orchestrator.agents_prop("map_density"))
        self.orchestrator.teacher.draw(self.screen, self.screen.get_width(), self.screen.get_height(),
                                       tile_size / self.orchestrator.agents_prop("map_density"))

        # 3) Draw the time/week in top-left corner
        font = pg.font.Font(None, 24)
        info_text = (
            f"Week {self.orchestrator.timer.current_week}, "
            f"{self.orchestrator.timer.day_of_week_str} "
            f"{self.orchestrator.timer.time_str}"
        )
        text_surface = font.render(info_text, True, WHITE)  # white color
        self.screen.blit(text_surface, (10, 10))

        # 4) Update the entire display
        pg.display.flip()
