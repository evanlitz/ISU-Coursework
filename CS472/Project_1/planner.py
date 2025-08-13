import os
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import heapq
import scipy

##
## @Author Evan Litzer
## March 7th, 2025
## CS 472
##

def a_star(grid, start, end):
    count = 0 
    
    rows = len(grid)
    cols = len(grid[0])

    open_set = []
    heapq.heappush(open_set, (0, start[0], start[1], [start]))

    grid_cost = {start: 0}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  

    while open_set :
        cost, x, y, path = heapq.heappop(open_set)

        current_cost = cost

        if (x, y) == end:
            return path, grid_cost[(x, y)]
        
        for dx, dy in directions:
            newX = x + dx
            newY = y + dy

            if grid[newX][newY] == 0 and 0 <= newX < rows and 0 <= newY < cols :
                new_cost = grid_cost[(x, y)] + 1  
                if (newX, newY) not in grid_cost or new_cost < grid_cost[(newX, newY)]:
                    grid_cost[(newX, newY)] = new_cost
                    j = max(abs(end[0] - newX), abs(end[1] - newY))
                    total_cost = new_cost + j
                    heapq.heappush(open_set, (total_cost, newX, newY, path + [(newX, newY)]))  
    return None, None                


def plan_path(world: np.ndarray, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[np.ndarray]:
    """
    Computes a path from the start position to the end position 
    using a certain planning algorithm (DFS is provided as an example).

    Parameters:
    - world (np.ndarray): A 2D numpy array representing the grid environment.
      - 0 represents a walkable cell.
      - 1 represents an obstacle.
    - start (Tuple[int, int]): The (row, column) coordinates of the starting position.
    - end (Tuple[int, int]): The (row, column) coordinates of the goal position.

    Returns:
    - np.ndarray: A 2D numpy array where each row is a (row, column) coordinate of the path.
      The path starts at 'start' and ends at 'end'. If no path is found, returns None.
    """
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    world_list: List[List[int]] = world.tolist()
    path, cost = a_star(world_list, start, end)

    if path :
        return np.array(path)
    else :
        return None


def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, "data", "grid_tasks.csv")
    grid_folder = os.path.join(base_path, "data", "grid_files")

    tasks = pd.read_csv(csv_path)

    for index in range(100) :
        grid_filename = os.path.join(grid_folder, f"grid_{index}.npy")

        if os.path.exists(grid_filename):
            grid = np.load(grid_filename)
        else:
            print(f"Warning: {grid_filename} not found!")
            continue 

        start = (tasks.iloc[index]["StartX"], tasks.iloc[index]["StartY"])
        end = (tasks.iloc[index]["EndX"], tasks.iloc[index]["EndY"])

        print(f"Processing: {grid_filename}, Start: {start}, End: {end}")

        path = plan_path(grid, start, end)

        if path is not None:
            print(f"Path found for {grid_filename}!")
        else:
            print(f"No path found for {grid_filename}.")

if __name__ == "__main__":
    main()



