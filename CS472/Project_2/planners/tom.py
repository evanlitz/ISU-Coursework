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

def evaluate(tom, jerry, spike, world):
    if np.array_equal(tom, jerry):
        return 10000

    dist_to_jerry = a_star_length(world, tuple(tom), tuple(jerry))
    dist_from_spike = np.sum(np.abs(tom - spike))
    mobility = sum(valid(tom + d, world) for d in DIRECTIONS)
    danger_penalty = 10 / (dist_from_spike + 1)**2

    return -3.0 * dist_to_jerry + 1.2 * dist_from_spike - 1.5 * danger_penalty + 1.5 * mobility

def alpha_beta(world, tom, jerry, spike, depth, alpha, beta, maximizing):
    if depth == 0:
        return evaluate(tom, jerry, spike, world)

    if maximizing:
        max_eval = -np.inf
        for move in DIRECTIONS:
            new_tom = tom + move
            if not valid(new_tom, world):
                continue
            eval = alpha_beta(world, new_tom, jerry, spike, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in DIRECTIONS:
            new_spike = spike + move
            if not valid(new_spike, world):
                continue
            eval = alpha_beta(world, tom, jerry, new_spike, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def best_move(world, tom, jerry, spike, depth=2):
    best_score = -np.inf
    move_choice = np.array([0, 0])
    for move in DIRECTIONS:
        new_tom = tom + move
        if not valid(new_tom, world):
            continue
        score = alpha_beta(world, new_tom, jerry, spike, depth - 1, -np.inf, np.inf, False)
        if score > best_score:
            best_score = score
            move_choice = move
    return move_choice

class PlannerAgent:
    def __init__(self):
        self.depth = 2

    def plan_action(
        self, world: np.ndarray,
        current: Tuple[int, int],     # Tom
        pursued: Tuple[int, int],     # Jerry
        pursuer: Tuple[int, int]      # Spike
    ) -> Optional[np.ndarray]:
        return best_move(world, np.array(current), np.array(pursued), np.array(pursuer), self.depth)
