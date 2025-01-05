import pygame as pg

from engine.colors import WHITE


class SceneDrawer:
    def __init__(self, screen, orchestrator=None):
        """
        :param orchestrator: Reference to SceneOrchestrator so we can extract scene details.
        """
        self.screen = screen
        self.orchestrator = orchestrator

        # Create a font
        self.font = pg.font.Font(None, 24)

    def draw_scene(self, tile_size):
        # 1) Draw placeables
        for placeable in self.orchestrator.get_placeables():
            placeable.draw(self.screen, self.screen.get_width(), self.screen.get_height(), tile_size)

        # 2) Draw actors
        for actor in self.orchestrator.get_agents():
            actor.draw(self.screen, self.screen.get_width(), self.screen.get_height(),
                       tile_size / self.orchestrator.get_agents_prop("map_density"))

        # 3) Draw the time/week in top-left corner
        info_text = (
            f"Week {self.orchestrator.get_timer().get_current_week()}, "
            f"{self.orchestrator.get_timer().get_day_of_week_str()} "
            f"{self.orchestrator.get_timer().get_time_str()}"
        )
        text_surface = self.font.render(info_text, True, WHITE)  # white color
        self.screen.blit(text_surface, (10, 10))

        # 4) Update the entire display
        pg.display.flip()
