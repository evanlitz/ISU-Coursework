import numpy as np
import random
from typing import Tuple, Optional
from collections import defaultdict

DIRECTIONS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [-1, 1], [1, -1], [1, 1]])


def valid(pos, world):
    r, c = pos
    return 0 <= r < world.shape[0] and 0 <= c < world.shape[1] and world[r][c] == 0


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


def evaluate(tom, jerry, spike, world):
    if np.array_equal(tom, jerry):
        return 10000
    if np.array_equal(tom, spike):
        return -10000

    dist_to_jerry = np.linalg.norm(tom - jerry)

    dist_from_spike = np.linalg.norm(tom - spike)

    mobility = sum(valid(tom + d, world) for d in DIRECTIONS)

    spike_mobility = sum(valid(spike + d, world) for d in DIRECTIONS)

    near_wall = (tom[0] in [0, world.shape[0] - 1]) or (tom[1] in [0, world.shape[1] - 1])

    line_threat = (tom[0] == spike[0] or tom[1] == spike[1])

    dead_end_penalty = max(0, 3 - mobility) * 8.0

    return (-5.2 * dist_to_jerry + 2.0 * dist_from_spike + 1.2 * mobility - 1.0 * spike_mobility - 10.0 * line_threat - 5.0 * near_wall - dead_end_penalty)


class PlannerAgent:
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=0.1):
        self.q_table = defaultdict(lambda: np.zeros(len(DIRECTIONS)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def state_key(self, tom, jerry, spike):
        return (tuple(tom), tuple(jerry), tuple(spike))

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.randint(0, len(DIRECTIONS) - 1)
        
        return int(np.argmax(self.q_table[state_key]))

    def update(self, state_key, action, reward, next_state_key):
        old_q = self.q_table[state_key][action]
        future = np.max(self.q_table[next_state_key])
        self.q_table[state_key][action] += self.alpha * (reward + self.gamma * future - old_q)

    def get_dynamic_probs(self, tom, spike):
        dist_to_spike = np.linalg.norm(tom - spike)
        uncertainty = np.clip(1.0 / (dist_to_spike + 1e-5), 0.1, 1.0)
        p_straight = max(0.2, 1.0 - uncertainty)
        p_side = (1.0 - p_straight) / 2.0
        return (p_side, p_straight, p_side)

    def get_reward(self, tom, jerry, spike):
        if np.array_equal(tom, jerry):
            return 500
        if np.array_equal(tom, spike):
            return -500
        dist_to_jerry = np.linalg.norm(tom - jerry)
        dist_to_spike = np.linalg.norm(tom - spike)
        near_jerry = dist_to_jerry <= 1.5
        near_spike = dist_to_spike <= 1.5
        reward = 0.0
        reward += max(0, 200 - 20 * dist_to_jerry)
        if near_spike and not near_jerry:
            reward -= 100
        if dist_to_jerry <= 1.0:
            reward += 50
        reward += -4.0 * dist_to_jerry + 2.0 * dist_to_spike
        return reward

    def train(self, world, tom, jerry, spike, episodes=500):
        for _ in range(episodes):
            state = (np.copy(tom), np.copy(jerry), np.copy(spike))
            for _ in range(100):
                s_key = self.state_key(*state)
                action_idx = self.choose_action(s_key)


                intended_move = DIRECTIONS[action_idx]
                probs = self.get_dynamic_probs(state[0], state[2])
                move = None
                for rotation, p in zip(['left', 'straight', 'right'], probs):
                    if random.random() < p:
                        move = rotate_direction(intended_move, rotation)
                        break
                if move is None:
                    continue
                next_tom = state[0] + move
                if not valid(next_tom, world):
                    continue
                next_jerry = state[1]
                next_spike = state[2]
                reward = self.get_reward(next_tom, next_jerry, next_spike)
                next_state = (next_tom, next_jerry, next_spike)
                self.update(s_key, action_idx, reward, self.state_key(*next_state))
                if np.array_equal(next_tom, next_jerry):
                    break
                state = next_state

    def plan_action(self, world, tom, jerry, spike):
        key = self.state_key(tom, jerry, spike)
        q_values = self.q_table[key]
        probs = self.get_dynamic_probs(tom, spike)
        directions_with_rotation = ['left', 'straight', 'right']
        for action_idx in np.argsort(-q_values):
            intended = DIRECTIONS[action_idx]

            for rotation, prob in zip(directions_with_rotation, probs):

                if random.random() < prob:
                    move = rotate_direction(intended, rotation)
                    new_pos = tom + move
                    if valid(new_pos, world):
                        return move
        return np.array([0, 0])