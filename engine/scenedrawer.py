import pygame as pg


class SceneDrawer:
    def __init__(self, screen, placeables, actors, orchestrator=None):
        """
        :param orchestrator: Optional reference to SceneOrchestrator so we can show time/week info
        """
        self.screen = screen
        self.placeables = placeables
        self.actors = actors
        self.orchestrator = orchestrator

        # Create a font
        self.font = pg.font.Font(None, 24)

    def draw_scene(self, tile_size):
        # 1) Draw placeables
        for placeable in self.placeables:
            placeable.draw(self.screen, self.screen.get_width(), self.screen.get_height(), tile_size)

        # 2) Draw actors

        # 3) Draw the time/week in top-left corner if orchestrator is available
        if self.orchestrator:
            info_text = (
                f"Week {self.orchestrator.get_current_week()}, "
                f"{self.orchestrator.get_day_of_week_str()} "
                f"{self.orchestrator.get_time_str()}"
            )
            text_surface = self.font.render(info_text, True, (255, 255, 255))  # white color
            self.screen.blit(text_surface, (10, 10))

        pg.display.flip()
