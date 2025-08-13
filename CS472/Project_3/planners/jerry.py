import numpy as np
import random
from typing import Tuple, Optional
from collections import defaultdict

DIRECTIONS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1],
                       [-1, -1], [-1, 1], [1, -1], [1, 1]])

def valid(pos, world):
    r, c = pos
    return 0 <= r < world.shape[0] and 0 <= c < world.shape[1] and world[r][c] == 0

def predict_spike_next_step(world, spike, tom):
    best_dist = float('inf')
    best_next = spike  
    for d in DIRECTIONS:
        next_pos = spike + d
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

def evaluate(jerry, spike, tom, world):
    if np.array_equal(jerry, spike):
        return 10000
    if np.array_equal(jerry, tom):
        return -10000

    dist_to_spike = a_star_length(world, tuple(jerry), tuple(spike))
    dist_from_tom = np.sum(np.abs(jerry - tom))

    mobility = sum(valid(jerry + d, world) for d in DIRECTIONS)
    spike_mobility = sum(valid(spike + d, world) for d in DIRECTIONS)

    near_wall = (jerry[0] in [0, world.shape[0] - 1]) or (jerry[1] in [0, world.shape[1] - 1])
    line_threat = (jerry[0] == tom[0] or jerry[1] == tom[1])

    dead_end_penalty = max(0, 3 - mobility) * 8.0

    return (-4.0 * dist_to_spike +2.0 * dist_from_tom + 1.2 * mobility - 1.0 * spike_mobility - 10.0 * line_threat - 5.0 * near_wall - dead_end_penalty)

def stochastic_alpha_beta(world, jerry, spike, tom, depth, alpha, beta, maximizing, probs=(0.3, 0.4, 0.3)):
    if depth == 0:
        return evaluate(jerry, spike, tom, world)

    directions_with_rotation = ['left', 'straight', 'right']
    
    if maximizing:
        max_eval = -np.inf
        for move in DIRECTIONS:
            exp_val = 0.0
            for rot, p in zip(directions_with_rotation, probs):
                rotated = rotate_direction(move, rot)
                new_jerry = jerry + rotated
                if not valid(new_jerry, world):
                    continue
                eval = stochastic_alpha_beta(world, new_jerry, spike, tom, depth - 1, alpha, beta, False, probs)
                exp_val += p * eval
            max_eval = max(max_eval, exp_val)
            alpha = max(alpha, exp_val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in DIRECTIONS:
            new_tom = tom + move
            if not valid(new_tom, world):
                continue
            eval = stochastic_alpha_beta(world, jerry, spike, new_tom, depth - 1, alpha, beta, True, probs)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def best_move(world, jerry, spike, tom, depth=2, probs=(0.3, 0.4, 0.3)):
    best_score = -np.inf
    move_choice = None
    valid_moves = []

    directions_with_rotation = ['left', 'straight', 'right']

    for move in DIRECTIONS:
        total_score = 0.0
        any_valid = False

        for rot, p in zip(directions_with_rotation, probs):
            rotated = rotate_direction(move, rot)
            new_jerry = jerry + rotated
            if not valid(new_jerry, world):
                continue
            any_valid = True
            score = stochastic_alpha_beta(world, new_jerry, spike, tom, depth - 1, -np.inf, np.inf, False, probs)
            total_score += p * score

        if any_valid:
            valid_moves.append(move)
            if total_score > best_score:
                best_score = total_score
                move_choice = move

    # Final safety: ensure chosen move is still valid
    if move_choice is not None and valid(jerry + move_choice, world):
        return move_choice

    # If no best move or it leads to obstacle, try any valid move
    if move_choice is None or not valid(jerry + move_choice, world):
        safe_moves = [m for m in DIRECTIONS if valid(jerry + m, world)]
        if safe_moves:
            return max(safe_moves, key=lambda m: evaluate(jerry + m, spike, tom, world))
        return np.array([0, 0])

    # If truly no move is valid, stay still
    return np.array([0, 0])

class PlannerAgent:
    def __init__(self, probs=(0.3, 0.4, 0.3)):
        self.depth = 2
        self.probs = probs  
    def plan_action(self, world: np.ndarray, current: Tuple[int, int], pursued: Tuple[int, int], pursuer: Tuple[int, int]) -> Optional[np.ndarray]:
        jerry = np.array(current)
        tom = np.array(pursuer)

        dist_to_tom = np.linalg.norm(jerry - tom)
        adaptive_depth = 3 if dist_to_tom < 4 else 2  # deeper if Tom is close
        
        dist_to_tom = np.linalg.norm(jerry - tom)
        uncertainty = np.clip(1.0 / (dist_to_tom + 1e-5), 0.1, 1.0)

        p_straight = max(0.2, 1.0 - uncertainty)
        p_side = (1.0 - p_straight) / 2.0
        dynamic_probs = (p_side, p_straight, p_side)

        return best_move(world, jerry, np.array(pursued), tom, adaptive_depth, dynamic_probs)

class QTableJerryAgent:
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=0.1, p=(0.1, 0.8, 0.1)):
        self.q_table = defaultdict(lambda: np.zeros(len(DIRECTIONS)))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.p = p

    def state_key(self, jerry, spike, tom):
        return (tuple(jerry), tuple(spike), tuple(tom))

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.randint(0, len(DIRECTIONS) - 1)
        return int(np.argmax(self.q_table[state_key]))

    def update(self, state_key, action, reward, next_state_key):
        old_q = self.q_table[state_key][action]
        future = np.max(self.q_table[next_state_key])
        self.q_table[state_key][action] += self.alpha * (reward + self.gamma * future - old_q)

    def train(self, world, jerry, spike, tom, episodes=500):
        for _ in range(episodes):
            state = (np.copy(jerry), np.copy(spike), np.copy(tom))
            for _ in range(100):  # max steps
                s_key = self.state_key(*state)
                action_idx = self.choose_action(s_key)
                intended_move = DIRECTIONS[action_idx]
                found_valid_move = False
                for rotation in ['left', 'straight', 'right']:
                    actual_move = rotate_direction(intended_move, rotation)
                    next_jerry = state[0] + actual_move
                    if valid(next_jerry, world):
                        found_valid_move = True
                        break
                if not found_valid_move:
                    continue

            # Simulate spike and tom moves (simple policies or fixed)
                next_spike = predict_spike_next_step(world, state[1], state[2])  # heuristic move
                next_tom = state[2]  # keep static, or implement if you want realism

                reward = self.get_reward(next_jerry, next_spike, next_tom)
                next_state = (next_jerry, next_spike, next_tom)
                s_key_next = self.state_key(*next_state)
                self.update(s_key, action_idx, reward, s_key_next)

                if np.array_equal(next_jerry, next_spike):
                    break
                state = next_state

    def get_reward(self, jerry, spike, tom):
        if np.array_equal(jerry, spike):
            return 500  # Huge reward for catching Spike

        if np.array_equal(jerry, tom):
            return -500  # Immediate loss if caught by Tom

    # Distances
        dist_to_spike = np.linalg.norm(jerry - spike)
        dist_to_tom = np.linalg.norm(jerry - tom)
        near_spike = dist_to_spike <= 1.5
        near_tom = dist_to_tom <= 1.5

        reward = 0.0

        reward += max(0, 200 - 20 * dist_to_spike)

    # Strong penalty for stepping close to Tom (unless very close to Spike)
        if near_tom and not near_spike:
            reward -= 100

        if dist_to_spike <= 1.0:
            reward += 50
    
    # Encourage being aggressive toward Spike and cautious with Tom
        reward += -4.0 * dist_to_spike + 2.0 * dist_to_tom       # Encourage staying away from Tom)

        return reward


    def plan_action(self, world, jerry, spike, tom):
        key = self.state_key(jerry, spike, tom)
        q_values = self.q_table[key]

        best_action_idx = int(np.argmax(q_values))
        move = DIRECTIONS[best_action_idx]

        return move 