import math


class SpreadSimulator:
    """
    Simulates the spreading of droplet particles and represents the environment as a grid.
    """
    def __init__(self, rows: int, cols: int, max_load: float = 16000.0,
                 decay_const: float = 0.1, diffusion_coeff: float = 0.02):
        """
        Constructor for the SpreadSimulator class.
        :param rows: Row size of the simulation.
        :param cols: Column size of the simulation.
        :param max_load: Max number of particles in each cell.
        :param decay_const: Parameter to control the decay of the spread.
        :param diffusion_coeff: Parameter to control the diffusion coefficient.
        """
        self.__rows = rows
        self.__cols = cols
        self.__max_load = max_load

        self.__decay_const = decay_const
        self.__diffusion_coeff = diffusion_coeff

        self.__grid = [[0.0 for _ in range(cols)] for _ in range(rows)]

    def reset_grid(self):
        """
        Resets the grid of cells to zero.
        """
        for r in range(self.__rows):
            for c in range(self.__cols):
                self.__grid[r][c] = 0.0

    def add_source(self, row: int, col: int, amount: float):
        """
        Adds a source of particles to the grid.
        :param row: Row index of the source.
        :param col: Column index of the source.
        :param amount: Amount of particles to add.
        """
        if 0 <= row < self.__rows and 0 <= col < self.__cols:
            self.__grid[row][col] += amount
            if self.__grid[row][col] > self.__max_load:
                self.__grid[row][col] = self.__max_load

    def get_rate(self, row: int, col: int) -> float:
        """
        Returns the spreading rate of the particle [A number between 0 and 1].
        :param row: Row index of the source.
        :param col: Column index of the source.
        :return: The spreading rate of the particle.
        """
        if 0 <= row < self.__rows and 0 <= col < self.__cols:
            return self.__grid[row][col]
        return 0.0

    def _get_neighbors(self, row: int, col: int) -> list:
        """
        Returns the neighbors of the cell.
        :param row: Row index of the source.
        :param col: Column index of the source.
        :return: List of neighbors represented as 2D coordinates.
        """
        neighbors = []
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        for x, y, in zip(dx, dy):
            if 0 <= row + x < self.__rows and 0 <= col + y < self.__cols:
                neighbors.append((row + x, col + y))
        return neighbors

    def _apply_decay(self):
        """
        Apply the decay on the particles amount.
        """
        decay_factor = math.exp(-self.__decay_const)
        for r in range(self.__rows):
            for c in range(self.__cols):
                self.__grid[r][c] *= decay_factor
                if self.__grid[r][c] < 0:
                    self.__grid[r][c] = 0.0

    def _apply_diffusion(self):
        """
        Apply the diffusion on the particles amount.
        """
        temp_grid = [[0.0 for _ in range(self.__cols)] for _ in range(self.__rows)]

        for r in range(self.__rows):
            for c in range(self.__cols):
                val = self.__grid[r][c]
                outflow = self.__diffusion_coeff * val
                remain = val - outflow

                # Add remain to the cell in temp grid
                temp_grid[r][c] += remain

                # Spread outflow among neighbors
                neighbors = self._get_neighbors(r, c)
                if neighbors:
                    portion = outflow / len(neighbors)
                    for (nr, nc) in neighbors:
                        temp_grid[nr][nc] += portion

        # Copy the new values
        for r in range(self.__rows):
            for c in range(self.__cols):
                if temp_grid[r][c] > self.__max_load:
                    temp_grid[r][c] = self.__max_load
                self.__grid[r][c] = temp_grid[r][c]

    def update(self):
        """
        Advance one simulation tick:
          1) Decay the droplets in each cell
          2) Diffuse droplets among neighboring cells
        """
        # 1) Decay
        self._apply_decay()

        # 2) Diffusion
        self._apply_diffusion()

    def draw(self, screen, screen_width, screen_height):
        """
        Draw the particles on the screen.
        :param screen: Reference to the screen object.
        :param screen_width: Screen width.
        :param screen_height: Screen height.
        """
        import pygame as pg
        alpha_max = int(0.8 * 255)  # At max leve of infection, still keep a 20% level of transparency

        for r in range(self.__rows):
            for c in range(self.__cols):
                load = self.__grid[r][c]
                if load > 0:
                    fraction = load / self.__max_load
                    # alpha from 0 to alpha_max
                    alpha_val = int(alpha_max * fraction)

                    # Only draw if there's some infection
                    if alpha_val > 0:
                        x = c * screen_width // self.__cols
                        y = r * screen_height // self.__rows
                        # Create a surface with per-pixel alpha
                        surf = pg.Surface((screen_width // self.__cols, screen_height // self.__rows), pg.SRCALPHA)
                        surf.fill((255, 0, 0, alpha_val))
                        # Blit onto main screen
                        screen.blit(surf, (x, y))