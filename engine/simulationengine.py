import pygame as pg
import logging

from engine.loader import load_scene_from_yaml
from engine.scenedrawer import SceneDrawer


class SimulationEngine:
    """
    A class to manage the pygame engine lifecycle, including:
    - Initialization of pygame.
    - Collision between pygame objects.
    - Main game loop.
    - Update the scene.
    - Resolution and frame rate management.
    """
    def __init__(self, width=800, height=600, frame_rate=30, config_file='config.yaml'):
        """
        Initialize the pygame engine.
        :param width: Width of the pygame window.
        :param height: Height of the pygame window.
        :param frame_rate: Frame rate of the pygame window.
        :param config_file: Path to the yaml configuration file.
        """
        pg.init()
        self.__height = height
        self.__width = width
        self.__fps = frame_rate
        self.__screen = pg.display.set_mode((self.__width, self.__height))
        pg.display.set_caption('COVID-19 Agent-Based Simulator')

        self.__running = True
        self.__clock = pg.time.Clock()

        # Load scene configuration
        self.__placeables = load_scene_from_yaml(config_file)
        self.__actors = []  # Add actor instantiation later
        self.__drawer = SceneDrawer(self.__screen, self.__placeables, self.__actors)

    def run(self):
        """
        Start the main simulation loop.
        """
        logging.info('Starting simulator engine ...')
        while self.__running:
            self.__clock.tick(self.__fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__running = False
            self.__drawer.draw_scene()
        self.quit()

    def quit(self):
        """
        Clean up the pygame engine and quit.
        """
        pg.quit()
        logging.info('Quitting the simulator engine.')
