import math

from engine.placeable import *


def build_collision_grid(placeables, width, height, tile_size, map_density):
    """
    :return: 2D list [row][col] of booleans: True if blocked
    """
    # number of tiles horizontally & vertically
    num_tiles_x = width // tile_size
    num_tiles_y = height // tile_size

    grid_width = num_tiles_x * map_density
    grid_height = num_tiles_y * map_density

    # Initialize all free
    collision_grid = [[False for _ in range(grid_width)]
                                 for _ in range(grid_height)]

    for p in placeables:
        if not p.collision:
            continue

        if isinstance(p, Rectangle):
            sub_left = int(p.x * map_density)
            sub_top = int(p.y * map_density)
            sub_w = int(p.width * map_density)
            sub_h = int(p.height * map_density)

            for row in range(sub_top, sub_top + sub_h):
                for col in range(sub_left, sub_left + sub_w):
                    if 0 <= row < grid_height and 0 <= col < grid_width:
                        collision_grid[row][col] = True

        elif isinstance(p, Circle):
            # Circle center = (p.x, p.y) in tile coords. radius in tile coords
            # Suppose radius is sub_r (in tile units).
            # Convert to sub-tile coords:
            center_x = p.x * map_density
            center_y = p.y * map_density
            sub_r = (tile_size / 2.5) * map_density

            # bounding box
            min_row = int(center_y - sub_r)
            max_row = int(center_y + sub_r)
            min_col = int(center_x - sub_r)
            max_col = int(center_x + sub_r)

            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    if 0 <= row < grid_height and 0 <= col < grid_width:
                        # distance from center
                        dist = math.sqrt((col - center_x)**2 + (row - center_y)**2)
                        if dist <= sub_r:
                            collision_grid[row][col] = True

        elif isinstance(p, Polygon):
            scaled_points = []
            for (px, py) in p.points:
                scaled_points.append((px * map_density, py * map_density))

                for row in range(0, int(grid_height)):
                    for col in range(0, int(grid_width)):
                        if not point_in_polygon((col, row), scaled_points):
                            # TODO: In the future
                            # collision_grid[row][col] = True
                            pass

    return collision_grid


def point_in_polygon(cell, polygon):
    """
    Check if point is inside polygon.
    :param cell: Cell represents a 2D coordinate
    :param polygon: List of (x, y) vertices that represent polygon
    :return: True if point is inside polygon, False otherwise
    """
    px, py = cell
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i+1) % n]

        # Check if the horizontal line at py crosses this edge
        intersects = ((y1 > py) != (y2 > py))
        if intersects:
            # x coordinate of intersection at y=py
            x_at_py = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x_at_py > px:
                inside = not inside
    return inside