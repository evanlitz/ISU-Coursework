import numpy as np
from typing import Tuple, Optional

DIRECTIONS = np.array([[0, 0], [-1, 0], [1, 0], [0, -1], [0, 1],
                       [-1, -1], [-1, 1], [1, -1], [1, 1]])

def valid(pos, world):
    r, c = pos
    return 0 <= r < world.shape[0] and 0 <= c < world.shape[1] and world[r][c] == 0

def a_star_length(world, start, goal):
    from queue import PriorityQueue
    visited = set()
    q = PriorityQueue()
    q.put((0, start))
    cost = {start: 0}

    while not q.empty():
        _, curr = q.get()
        if curr == goal:
            return cost[curr]

        for d in DIRECTIONS:
            next_pos = (curr[0] + d[0], curr[1] + d[1])
            if not valid(np.array(next_pos), world):
                continue
            new_cost = cost[curr] + 1
            if next_pos not in cost or new_cost < cost[next_pos]:
                cost[next_pos] = new_cost
                visited.add(next_pos)
                priority = new_cost + np.linalg.norm(np.array(next_pos) - np.array(goal))
                q.put((priority, next_pos))
    return float('inf')

def evaluate(spike, tom, jerry, world):
    if np.array_equal(spike, tom):
        return 10000

    dist_to_tom = a_star_length(world, tuple(spike), tuple(tom))
    dist_from_jerry = np.sum(np.abs(spike - jerry))
    mobility = sum(valid(spike + d, world) for d in DIRECTIONS)
    danger_penalty = 10 / (dist_from_jerry + 1)**2

    return -2.8 * dist_to_tom + 2.0 * dist_from_jerry - 2.0 * danger_penalty + 1.0 * mobility

def alpha_beta(world, spike, tom, jerry, depth, alpha, beta, maximizing):
    if depth == 0:
        return evaluate(spike, tom, jerry, world)

    if maximizing:
        max_eval = -np.inf
        for move in DIRECTIONS:
            new_spike = spike + move
            if not valid(new_spike, world):
                continue
            eval = alpha_beta(world, new_spike, tom, jerry, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in DIRECTIONS:
            new_jerry = jerry + move
            if not valid(new_jerry, world):
                continue
            eval = alpha_beta(world, spike, tom, new_jerry, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def best_move(world, spike, tom, jerry, depth=2):
    best_score = -np.inf
    move_choice = np.array([0, 0])
    for move in DIRECTIONS:
        new_spike = spike + move
        if not valid(new_spike, world):
            continue
        score = alpha_beta(world, new_spike, tom, jerry, depth - 1, -np.inf, np.inf, False)
        if score > best_score:
            best_score = score
            move_choice = move
    return move_choice

class PlannerAgent:
    def __init__(self):
        self.depth = 2

    def plan_action(
        self, world: np.ndarray,
        current: Tuple[int, int],     # Spike
        pursued: Tuple[int, int],     # Tom
        pursuer: Tuple[int, int]      # Jerry
    ) -> Optional[np.ndarray]:
        return best_move(world, np.array(current), np.array(pursued), np.array(pursuer), self.depth)
