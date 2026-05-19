import mujoco as mj
import numpy as np
from dataclasses import dataclass
from generic_ik_solver import IKSolver

# Arm IK / positioning moves: base / multiplier gives nominal sim-time per segment; SIM_SPEEDUP scales wall-clock feel.
_ARM_MOVE_BASE_DURATION_S = 2
ARM_MOVE_SPEED_MULTIPLIER = 1
# ~2× faster arm segments vs previous defaults (also halve gripper below).
SIM_SPEEDUP = 3.0
ARM_MOVE_DURATION = _ARM_MOVE_BASE_DURATION_S / ARM_MOVE_SPEED_MULTIPLIER / SIM_SPEEDUP

REAL_ARM_MOVE_DURATION = 5.0

GRIPPER_DURATION = 0.25
# Must stay within ur10e_custom_gripper.xml gripper joint ctrlrange (-0.17453, 1.74533).
GRIPPER_OPEN = 0.5
GRIPPER_CLOSED = -0.17453

@dataclass
class Command:
    target_qpos: np.ndarray   # full DOF vector: 6 arm + 1 gripper
    duration: float

@dataclass
class Intent:
    pos: np.ndarray | None = None
    rot: np.ndarray | None = None
    grip: float | None = None
    wait: float | None = None

class UR10eController:
    """Planner/controller decoupled from executor, with separate gripper joint."""
    def __init__(self, planner_model: mj.MjModel, planner_data: mj.MjData, site_name: str, verbose=False):
        self.model = planner_model
        self.data = planner_data
        self.site_name = site_name
        self.verbose = verbose

        self.gripper_joint_id = mj.mj_name2id(planner_model, mj.mjtObj.mjOBJ_JOINT, "gripper")
        self.gripper_qpos_adr = int(self.model.jnt_qposadr[self.gripper_joint_id])
        self.gripper_actuator_id = mj.mj_name2id(
            planner_model, mj.mjtObj.mjOBJ_ACTUATOR, "gripper"
        )

        self.intent_queue: list[Intent] = []
        self.command_queue: list[Command] = []

        self.current_qpos = self.data.qpos.copy()  # full DOF
        self.paused = False

    def move_to(self, pos: np.ndarray, rot: np.ndarray):
        self.intent_queue.append(Intent(pos=pos, rot=rot))
        if self.verbose:
            print(f"[Intent] move_to: pos={pos}, rot=\n{rot}")

    def grip(self):
        self.intent_queue.append(Intent(grip=0.0))
        if self.verbose:
            print(f"[Intent] grip -> {0.0}")

    def release(self):
        self.intent_queue.append(Intent(grip=1.0))
        if self.verbose:
            print(f"[Intent] release -> {1.0}")

    def wait(self, duration: float):
        self.intent_queue.append(Intent(wait=duration))
        if self.verbose:
            print(f"[Intent] wait -> {duration}s")

    def clear_intents(self):
        self.intent_queue.clear()
        self.command_queue.clear()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def solve_ik(self, seed_qpos, target_pos, target_rot):
        saved_qpos = self.data.qpos[:6].copy()
        self.data.qpos[:6] = seed_qpos[:6]
        mj.mj_forward(self.model, self.data)

        solver = IKSolver(self.model, self.data, n_dof=6, verbose=False)
        result = solver.solve_ik(
            target_pos=target_pos,
            target_rot_matrix=target_rot,
            site_name=self.site_name,
            max_steps=100000,
            tol=1e-8,
            regularization_strength=3e-2
        )
        self.data.qpos[:6] = saved_qpos
        mj.mj_forward(self.model, self.data)
        qpos_full = seed_qpos.copy()
        qpos_full[:6] = result["qpos"][:6]
        return qpos_full

    def _solve_next_intent(self, current_qpos, gripper_state):
        if self.paused or not self.intent_queue:
            return
        intent = self.intent_queue.pop(0)
        qpos = current_qpos.copy()

        # Arm movement
        if intent.pos is not None and intent.rot is not None:
            qpos = self.solve_ik(current_qpos, intent.pos, intent.rot)

        # Gripper movement
        if intent.grip is not None:
            qpos[self.gripper_joint_id] = intent.grip

        # Determine duration
        if intent.wait is not None:
            duration = intent.wait
        elif intent.pos is not None:
            duration = REAL_ARM_MOVE_DURATION
        else:
            duration = GRIPPER_DURATION

        self.command_queue.append(Command(target_qpos=qpos, duration=duration))
        self.current_qpos = qpos.copy()

        if self.verbose:
            print(f"[Command generated] duration={duration}")
            print(f"Target qpos: {qpos}")

    def get_next_command(self, current_qpos, gripper_state):
        if self.command_queue:
            cmd = self.command_queue.pop(0)
            if self.verbose:
                print(f"[Command sent] duration={cmd.duration}")
                print(f"Target qpos: {cmd.target_qpos}")
            return cmd
        self._solve_next_intent(current_qpos, gripper_state)
        if self.command_queue:
            cmd = self.command_queue.pop(0)
            if self.verbose:
                print(f"[Command sent] duration={cmd.duration}")
                print(f"Target qpos: {cmd.target_qpos}")
            return cmd
        return None
