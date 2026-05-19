import mujoco as mj
import mujoco.viewer
import numpy as np
import multiprocessing as mp
import os
import json
import time
from pathlib import Path
from ur10e_controller import UR10eController, GRIPPER_OPEN

_SHARED = Path(__file__).resolve().parent.parent / "shared" / "queue"
_ROBOT_STATUS_PATH = _SHARED / "robot_status.json"
_STATE_PATH = _SHARED / "robot_joint_state.json"

_QPOS_TO_NAME = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

_STATE_WRITE_HZ = 10

TIME_STEP = 0.002
KP_JOINTS = np.array([450, 370, 135, 150, 100, 144])
KD_JOINTS = np.array([3.5, 30.36, 26.4375, 35, 3.9, 2.86])
KP_GRIPPER = 17.8
KD_GRIPPER = 2.0

def pd_control(desired, current, vel, kp, kd):
    return kp*(desired-current) + kd*(-vel)

class SimExecutor:
    """Execute arm + gripper smoothly with PD control, holding last target if no new command."""
    def __init__(self, model, data, planner: UR10eController):
        self.model = model
        self.data = data
        self.planner = planner
        self.current_command = None
        self.start_time = 0.0
        self.initial_qpos = None
        self.last_target_qpos = data.qpos.copy()  # Hold last target indefinitely

    def is_idle(self):
        """True when no commands in progress - move queue is empty."""
        return (
            self.current_command is None
            and not self.planner.command_queue
            and not self.planner.intent_queue
        )

    def step(self):
        # Request new command if we don't have one
        if self.current_command is None:
            # Second arg was historically unused by _solve_next_intent; kept for API compatibility.
            cmd = self.planner.get_next_command(self.data.qpos, self.data.qpos[0])
            if cmd is not None:
                self.current_command = cmd
                self.start_time = self.data.time
                self.initial_qpos = self.data.qpos.copy()
                self.last_target_qpos = cmd.target_qpos.copy()
            # If cmd is None, keep holding last_target_qpos
        
        # Compute interpolation if we have a current command
        if self.current_command is not None:
            elapsed = self.data.time - self.start_time
            alpha = min(elapsed / self.current_command.duration, 1.0)
            smooth = 3*alpha**2 - 2*alpha**3
            desired_qpos = self.initial_qpos + smooth*(self.current_command.target_qpos - self.initial_qpos)

            # If finished, clear current_command but still hold last_target_qpos
            if alpha >= 1.0:
                self.current_command = None
                self.initial_qpos = desired_qpos.copy()  # Ensure smooth continuation
                self.last_target_qpos = desired_qpos.copy()
        else:
            # No new command, hold last target
            desired_qpos = self.last_target_qpos.copy()

        # --- PD Control ---
        # Arm
        torques = pd_control(desired_qpos[:6], self.data.qpos[:6], self.data.qvel[:6], KP_JOINTS, KD_JOINTS)
        self.data.ctrl[:6] = torques

        # Gripper: same indexing as pre-refactor (joint id == qpos index == actuator index for this 7-DOF model).
        # PD on top of the interpolated setpoint matches the previous working behavior.
        g_id = self.planner.gripper_joint_id
        g_ctrl = pd_control(
            desired_qpos[g_id],
            self.data.qpos[g_id],
            self.data.qpos[g_id],
            KP_GRIPPER,
            KD_GRIPPER,
        )
        self.data.ctrl[g_id] = desired_qpos[g_id] + g_ctrl * TIME_STEP

class RunSim(mp.Process):
    def __init__(self, pipe_conn):
        super().__init__()
        self.pipe = pipe_conn
        self.daemon = True

    def run(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        xml_path = os.path.join(cur_dir, "ur10e", "ur10e_custom_gripper_scene.xml")

        # Load model
        model = mj.MjModel.from_xml_path(xml_path)
        data = mj.MjData(model)
        model.opt.timestep = TIME_STEP
        data.qpos[:6] = np.array([-1.5708, -2.5708, 1.2708, -2.0, 1.5708, 0.0])
        _gj = mj.mj_name2id(model, mj.mjtObj.mjOBJ_JOINT, "gripper")
        _ga = mj.mj_name2id(model, mj.mjtObj.mjOBJ_ACTUATOR, "gripper")
        data.qpos[model.jnt_qposadr[_gj]] = GRIPPER_OPEN
        data.ctrl[_ga] = GRIPPER_OPEN
        mj.mj_forward(model, data)

        # Controller / planner (same initial pose including open gripper)
        planner_model = mj.MjModel.from_xml_path(xml_path)
        planner_data = mj.MjData(planner_model)
        planner_data.qpos[:6] = np.array([-1.5708, -2.5708, 1.2708, -2.0, 1.5708, 0.0])
        _gj_p = mj.mj_name2id(planner_model, mj.mjtObj.mjOBJ_JOINT, "gripper")
        planner_data.qpos[planner_model.jnt_qposadr[_gj_p]] = GRIPPER_OPEN
        mj.mj_forward(planner_model, planner_data)

        planner = UR10eController(planner_model, planner_data, "attachment_site", verbose=True)

        # Demo positions
        rest = np.array([0.5,0.5,0.5])
        hover = np.array([0.8925,-0.2625,0.5])
        lower = np.array([0.8925,-0.2625,0.15])
        R = np.array([[-1,0,0],[0,1,0],[0,0,-1]])


        # Function to enqueue demo intents
        def enqueue_sequence(sequence):
            for command in sequence:
                if (command[3] == 1):
                    planner.grip()
                elif (command[3] == 1):
                    planner.release()
                else:
                    planner.move_to(np.round(command[:3], 4), R)
            #print("[Main] Sequence enqueued")
            planner.move_to(rest, R)


        # Enqueue initial sequence
        #enqueue_sequence()
        planner.move_to(rest, R)

        # Executor
        executor = SimExecutor(model, data, planner)
        was_busy = False
        received_game_command = False
        move_complete_flag = False  # Stays True until next command (so game engine can poll it)
        last_state_write = 0.0

        def write_robot_status(state: str, move_complete: bool = False):
            try:
                _ROBOT_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(_ROBOT_STATUS_PATH, "w") as f:
                    json.dump({
                        "state": state,
                        "move_complete": move_complete,
                        "timestamp": time.time(),
                    }, f, indent=2)
            except OSError:
                pass

        def _sim_tick():
            """One simulation tick — step physics, update executor, handle pipe + status."""
            nonlocal was_busy, received_game_command, move_complete_flag, last_state_write

            mj.mj_step(model, data)
            executor.step()

            try:
                if self.pipe.poll():
                    command_sequence = self.pipe.recv()
                    if command_sequence is None:
                        return False  # stop signal
                    received_game_command = True
                    move_complete_flag = False
                    enqueue_sequence(command_sequence)
            except (EOFError, BrokenPipeError):
                return False

            is_idle = executor.is_idle()
            if was_busy and is_idle and received_game_command:
                move_complete_flag = True
            was_busy = not is_idle

            write_robot_status("idle" if is_idle else "moving", move_complete=move_complete_flag)

            now = time.monotonic()
            if now - last_state_write >= (1.0 / _STATE_WRITE_HZ):
                last_state_write = now
                try:
                    _SHARED.mkdir(parents=True, exist_ok=True)
                    with open(_STATE_PATH, "w") as f:
                        json.dump(
                            {
                                "timestamp": data.time,
                                "joints": {
                                    name: float(data.qpos[i])
                                    for i, name in enumerate(_QPOS_TO_NAME)
                                },
                            },
                            f,
                            indent=2,
                        )
                except OSError:
                    pass

            return True  # keep running

        # --- Simulation loop ---
        has_display = bool(os.environ.get("DISPLAY"))
        if has_display:
            try:
                with mujoco.viewer.launch_passive(model, data) as viewer:
                    while viewer.is_running():
                        if not _sim_tick():
                            break
                        viewer.sync()
            except Exception:
                has_display = False  # fall through to headless

        if not has_display:
            while True:
                if not _sim_tick():
                    break
                time.sleep(TIME_STEP)
