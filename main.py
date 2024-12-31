import engine.simulationengine as simengine

if __name__ == "__main__":
    simEngine = simengine.SimulationEngine(width=1280, height=720, frame_rate=60, config_file="config/map.yaml")
    simEngine.run()