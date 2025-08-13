import numpy as np
import random
from typing import Tuple, Optional
from collections import defaultdict

DIRECTIONS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1],
                       [-1, -1], [-1, 1], [1, -1], [1, 1]])

def valid(pos, world):
    r, c = pos
    return 0 <= r < world.shape[0] and 0 <= c < world.shape[1] and world[r][c] == 0

def predict_jerry_next_step(world, jerry, tom):
    best_dist = float('inf')
    best_next = jerry  
    for d in DIRECTIONS:
        next_pos = jerry + d
        if not valid(next_pos, world):
            continue
        dist = np.linalg.norm(next_pos - tom)
        if dist < best_dist:
            best_dist = dist
            best_next = next_pos
    return best_next

def rotate_direction(direction: np.ndarray, rotation: str) -> np.ndarray:
    cardinal_dirs = [np.array([-1, 0]), np.array([1, 0]), np.array([0, -1]), np.array([0, 1])]
    if not any(np.array_equal(direction, d) for d in cardinal_dirs):
        return direction
    idx = next(i for i, d in enumerate(cardinal_dirs) if np.array_equal(direction, d))
    if rotation == 'left':
        return cardinal_dirs[(idx - 1) % 4]
    elif rotation == 'right':
        return cardinal_dirs[(idx + 1) % 4]
    return direction

def sample_probabilistic_move(base_move: np.ndarray, p: Tuple[float, float, float]) -> np.ndarray:
    choice = np.random.choice(['left', 'straight', 'right'], p=p)
    return rotate_direction(base_move, choice)

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
    return -3 * dist_to_tom + 1.35 * dist_from_jerry - 1.5 * danger_penalty + 1.4 * mobility  

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
    def plan_action(self, world: np.ndarray, current: Tuple[int, int], pursued: Tuple[int, int], pursuer: Tuple[int, int]) -> Optional[np.ndarray]:
        return best_move(world, np.array(current), np.array(pursued), np.array(pursuer), self.depth)

class QTableSpikeAgent:
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=0.1, p=(0.1, 0.8, 0.1)):
        self.q_table = defaultdict(lambda: np.zeros(len(DIRECTIONS)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.p = p

    def state_key(self, spike, tom, jerry):
        return (tuple(spike), tuple(tom), tuple(jerry))

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.randint(0, len(DIRECTIONS) - 1)
        return int(np.argmax(self.q_table[state_key]))

    def update(self, state_key, action, reward, next_state_key):
        old_q = self.q_table[state_key][action]
        future = np.max(self.q_table[next_state_key])
        self.q_table[state_key][action] += self.alpha * (reward + self.gamma * future - old_q)

    def train(self, world, spike, tom, jerry, episodes=500):
        for _ in range(episodes):
            state = (np.copy(spike), np.copy(tom), np.copy(jerry))
            for _ in range(100):  # max steps
                s_key = self.state_key(*state)
                action_idx = self.choose_action(s_key)
                intended_move = DIRECTIONS[action_idx]
                found_valid_move = False
                for rotation in ['left', 'straight', 'right']:
                    actual_move = rotate_direction(intended_move, rotation)
                    next_spike = state[0] + actual_move
                    if valid(next_spike, world):
                        found_valid_move = True
                        break
                if not found_valid_move:
                    continue

                next_jerry = predict_jerry_next_step(world, state[2], state[1])
                next_tom = state[1]

                reward = self.get_reward(next_spike, next_tom, next_jerry)
                next_state = (next_spike, next_tom, next_jerry)
                s_key_next = self.state_key(*next_state)
                self.update(s_key, action_idx, reward, s_key_next)

                if np.array_equal(next_spike, next_tom):
                    break
                state = next_state

    def get_reward(self, spike, tom, jerry):
        if np.array_equal(spike, tom):
            return 500  # Reward for catching Tom
        if np.array_equal(spike, jerry):
            return -500  # Loss if caught by Jerry

        dist_to_tom = np.linalg.norm(spike - tom)
        dist_to_jerry = np.linalg.norm(spike - jerry)
        near_tom = dist_to_tom <= 1.5
        near_jerry = dist_to_jerry <= 1.5

        reward = 0.0
        reward += max(0, 200 - 20 * dist_to_tom)

        if near_jerry and not near_tom:
            reward -= 100

        if dist_to_tom <= 1.0:
            reward += 50

        reward += -4.0 * dist_to_tom + 2.0 * dist_to_jerry

        return reward

    def plan_action(self, world, spike, tom, jerry):
        key = self.state_key(spike, tom, jerry)
        q_values = self.q_table[key]
        directions_with_rotation = ['left', 'straight', 'right']
        for action_idx in np.argsort(-q_values):
            intended = DIRECTIONS[action_idx]
            for rotation in directions_with_rotation:
                move = rotate_direction(intended, rotation)
                new_pos = spike + move
                if valid(new_pos, world):
                    return move
        return np.array([0, 0])
