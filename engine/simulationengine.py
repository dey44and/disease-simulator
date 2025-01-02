import os

import pygame as pg
import logging

from interaction.sceneorchestrator import SceneOrchestrator
from loader.scene_loader import load_scene_from_yaml
from loader.engine_loader import load_engine_from_yaml
from engine.scenedrawer import SceneDrawer


class SimulationEngine(object):
    """
    A class to manage the pygame engine lifecycle, including:
    - Initialization of pygame.
    - Collision between pygame objects.
    - Main game loop.
    - Update the scene.
    - Resolution and frame rate management.
    """
    def __init__(self,
                 width=800,
                 height=600,
                 tile_size=5,
                 map_file='config/map.yaml',
                 engine_file='config/engine.yaml'):
        """
        Initialize the pygame engine.
        :param width: Width of the pygame window.
        :param height: Height of the pygame window.
        :param map_file: Path to the yaml configuration file.
        """
        if not os.path.exists(map_file):
            raise FileNotFoundError(f"File {map_file} not found.")
        if width % tile_size != 0 or height % tile_size != 0:
            raise ValueError("Width and height must be divisible by tile_size.")

        pg.init()
        self.__height = height
        self.__width = width
        self.__tile_size = tile_size
        self.__screen = pg.display.set_mode((self.__width, self.__height))
        pg.display.set_caption('COVID-19 Agent-Based Simulator')

        self.__running = True
        self.__clock = pg.time.Clock()

        # Load scene configuration
        self.__placeables = load_scene_from_yaml(map_file)
        self.__agents = []  # Add actor instantiation later

        # Load engine configuration
        engine_config = load_engine_from_yaml(engine_file)
        self.__start_time_str = engine_config["engine"]["start_time"]  # e.g. "07:30"
        self.__end_time_str = engine_config["engine"]["end_time"]  # e.g. "13:50"
        self.__infection_prob = engine_config["engine"]["infection_prob"] # e.g. 0.021
        self.__num_weeks = engine_config["engine"]["num_weeks"]  # e.g. 2

        # Discrete stepping / speed config
        self.__time_step_sec = engine_config["engine"]["time_step_seconds"]  # e.g. 5
        self.__speed_x = engine_config["engine"]["speed_x"]  # e.g. 1 (can be changed)

        self.__orchestrator = SceneOrchestrator(
            agents=self.__agents,
            start_time=self.__start_time_str,
            end_time=self.__end_time_str,
            num_weeks=self.__num_weeks,
            time_step_seconds=self.__time_step_sec
        )

        self.__drawer = SceneDrawer(self.__screen, self.__placeables, self.__agents, self.__orchestrator)

    def run(self):
        import time
        logging.info("Starting simulation engine ...")

        self.__running = True

        # The real time between steps depends on speed_x.
        while self.__running:
            # 1. Handle events (so we can quit, etc.)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__running = False

            # 2. Advance the simulation by one discrete step (5 seconds, etc.)
            self.__orchestrator.simulate_once()

            # 3. If finished, break out
            if self.__orchestrator.is_finished():
                logging.info("Simulation reached the end (all weeks).")
                self.__running = False
                continue

            # 4. Draw the scene
            self.__screen.fill((0, 0, 0))  # Clear screen
            self.__drawer.draw_scene(self.__tile_size)
            pg.display.flip()

            # 5. Wait in real time depending on speed
            # If speed_x=2 => 0.5 seconds per step
            real_sleep = 1.0 / self.__speed_x
            time.sleep(real_sleep)

        self.quit()

    def quit(self):
        """
        Clean up the pygame engine and quit.
        """
        pg.quit()
        logging.info('Quitting the simulator engine.')
