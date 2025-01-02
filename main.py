import logging

import engine.simulationengine as simengine

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    simEngine = simengine.SimulationEngine(width=1200,
                                           height=720,
                                           tile_size=60,
                                           map_file="config/map.yaml",
                                           engine_file="config/engine.yaml")
    simEngine.run()