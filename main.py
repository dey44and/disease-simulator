import logging

import engine.simulation_engine as simengine

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    simEngine = simengine.SimulationEngine(width=1200, height=720, tile_size=60)
    simEngine.run()