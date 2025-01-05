import heapq


class PathFinder(object):
    """
    Class that contains implementation of path finding algorithm.
    """
    @staticmethod
    def astar_pathfinding(collision_grid, start, goal, in_bounds, heuristic):
        """
        Finds the shortest path from start to goal using A* algorithm.
        :param heuristic: Heuristic function used to compute the cost
        :param in_bounds: Method used to detect the limits on grid
        :param collision_grid: 2D array of booleans (true/false)
        :param start: starting position represented as tuple (x, y)
        :param goal: goal position represented as tuple (x, y)
        :return: list of coordinates represented as tuple (x, y)
        """
        # Check if the starting point or the goal are in a restricted cell
        if not in_bounds(collision_grid, start) or not in_bounds(collision_grid, goal):
            return []
        if collision_grid[start[0]][start[1]] or collision_grid[goal[0]][goal[1]]:
            return []

        open_set = []
        heapq.heappush(open_set, (0, start))  # Each entry in the list is represented as (f_score, (r, c))

        came_from = {}
        g_score = {start: 0}

        while open_set:
            # Get the smallest element from the heap
            _, current = heapq.heappop(open_set)
            # If the destination has been reached, reconstruct the path
            if current == goal:
                return PathFinder.reconstruct_path(came_from, current)

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr = current[0] + dr
                nc = current[1] + dc
                neighbor = (nr, nc)
                if in_bounds(collision_grid, neighbor) and not collision_grid[nr][nc]:
                    # Compute the cost
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, goal)
                        came_from[neighbor] = current
                        heapq.heappush(open_set, (f_score, neighbor))
        return []  # no path found

    @staticmethod
    def reconstruct_path(came_from, current):
        """
        Returns a list of coordinates represented as tuple (x, y)
        :param came_from: Dictionary of current node to its parent
        :param current: Current position represented as tuple (x, y)
        :return: path from start to goal stored as a list of tuples (x, y)
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
