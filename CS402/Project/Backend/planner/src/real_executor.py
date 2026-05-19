"""
Receives waypoint sequences from MotionPlanner via pipe (same protocol as
RunSim), solves IK, batches consecutive arm moves into single
FollowJointTrajectory action calls (one per arm segment between
grip/release), and drives the gripper directly via the Feetech bus.

Subscribes to /joint_states and writes robot_joint_state.json at 10 Hz.
Writes robot_status.json matching RunSim's format so the game loop is
unchanged.
"""

from __future__ import annotations

import json
import multiprocessing as mp
from multiprocessing.connection import Connection
import os
import time
from pathlib import Path

import sys
import mujoco as mj
import numpy as np
from scipy.spatial.transform import Rotation as R

# ROS Noetic installs its Python packages under the system Python path.
# When conda's Python is active (PATH=/opt/conda/bin:...) those packages are
# not on sys.path automatically, so we add them explicitly before importing.
_ROS_PYTHON_PATH = "/opt/ros/noetic/lib/python3/dist-packages"
_CATKIN_PYTHON_PATH = "/catkin_ws/devel/lib/python3/dist-packages"
for _p in (_ROS_PYTHON_PATH, _CATKIN_PYTHON_PATH):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_ROS_IMPORT_ERROR: str | None = None
try:
    import rospy
    from control_msgs.msg import FollowJointTrajectoryActionGoal
    from trajectory_msgs.msg import JointTrajectoryPoint
    from sensor_msgs.msg import JointState
    _ROS_AVAILABLE = True
except Exception as _e:
    _ROS_AVAILABLE = False
    _ROS_IMPORT_ERROR = f"{type(_e).__name__}: {_e}"

from ur10e_controller import UR10eController

### Paths
_HERE = Path(__file__).resolve().parent
_XML_PATH = str(_HERE / "ur10e" / "ur10e_custom_gripper_scene.xml")
_SHARED = _HERE.parent.parent / "shared" / "queue"
_STATUS_PATH = _SHARED / "robot_status.json"
_STATE_PATH = _SHARED / "robot_joint_state.json"

### ROS config
_ACTION_NS = "/scaled_pos_joint_traj_controller/follow_joint_trajectory"

# Joint order expected by the UR driver (alphabetical)
_UR_JOINT_ORDER = [
    "elbow_joint",
    "shoulder_lift_joint",
    "shoulder_pan_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

### Gripper config (env vars match docker-compose)
# Read at run() time so importing this module in sim mode doesn't crash.
_GRIPPER_PORT     = os.getenv("GRIPPER_PORT",      "/dev/ttyACM0")
_GRIPPER_BAUD     = int(os.getenv("GRIPPER_BAUD",  "1000000"))
_GRIPPER_MOTOR_ID = int(os.getenv("GRIPPER_MOTOR_ID", "1"))

# STS3215 register addresses
_STS_ADDR_TORQUE_ENABLE   = 40
_STS_ADDR_GOAL_POSITION   = 42
_STS_ADDR_PRESENT_POSITION = 56


class _GripperBus:
    """
    Minimal serial driver for the STS3215 gripper servo.
    Uses pyserial directly.
    """

    _INST_WRITE = 0x03

    def __init__(self, port: str, motor_id: int):
        self._id = motor_id
        self._port_name = port
        self._serial = None  # type: ignore[var-annotated]

    def connect(self) -> None:
        import serial
        self._serial = serial.Serial(self._port_name, baudrate=_GRIPPER_BAUD, timeout=0.1)

    def _write_reg(self, address: int, data: bytes) -> None:
        params = bytes([address]) + data
        length = len(params) + 2  # instruction byte + checksum byte
        header = bytes([self._id, length, self._INST_WRITE]) + params
        checksum = (~sum(header)) & 0xFF
        self._serial.reset_input_buffer()
        self._serial.write(b'\xff\xff' + header + bytes([checksum]))
        # Drain the status response the servo always sends back (6 bytes)
        self._serial.read(6)

    def read_present_position(self) -> int | None:
        motor_id = self._id
        length, inst = 4, 0x02
        header = bytes([motor_id, length, inst, _STS_ADDR_PRESENT_POSITION, 2])
        checksum = (~sum(header)) & 0xFF
        self._serial.reset_input_buffer()
        self._serial.write(b'\xff\xff' + header + bytes([checksum]))
        resp = self._serial.read(8)
        if len(resp) < 8 or resp[0] != 0xFF or resp[1] != 0xFF:
            return None
        return resp[5] | (resp[6] << 8)

    def enable_torque(self) -> None:
        self._write_reg(_STS_ADDR_TORQUE_ENABLE, b'\x01')

    def enable_torque_hold(self) -> None:
        """Enable torque but first sync Goal_Position to present position so servo doesn't lurch."""
        pos = self.read_present_position()
        if pos is not None:
            self._write_reg(_STS_ADDR_GOAL_POSITION, bytes([pos & 0xFF, (pos >> 8) & 0xFF]))
        self._write_reg(_STS_ADDR_TORQUE_ENABLE, b'\x01')

    def disable_torque(self) -> None:
        self._write_reg(_STS_ADDR_TORQUE_ENABLE, b'\x00')

    def write_position(self, pos: int) -> None:
        self._write_reg(_STS_ADDR_GOAL_POSITION, bytes([pos & 0xFF, (pos >> 8) & 0xFF]))

    def disconnect(self) -> None:
        try:
            if self._serial and self._serial.is_open:
                self._serial.close()
        except Exception:
            pass

rot_vec = np.array([2.158, -2.211, -0.045])
r_pendant = R.from_rotvec(rot_vec).as_matrix()
r_base = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
_R = r_base @ r_pendant

# MuJoCo joint index to UR joint name (positional order in qpos[0:6])
_QPOS_TO_NAME = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

_STATE_WRITE_HZ = 10


def _write_status(state: str, move_complete: bool = False) -> None:
    try:
        _SHARED.mkdir(parents=True, exist_ok=True)
        with open(_STATUS_PATH, "w") as f:
            json.dump(
                {
                    "state": state,
                    "move_complete": move_complete,
                    "timestamp": time.time(),
                },
                f,
                indent=2,
            )
    except OSError:
        pass


class RealExecutor(mp.Process):
    """Drop-in replacement for RunSim, real UR10e via ROS."""

    def __init__(self, pipe_conn: Connection):
        super().__init__()
        self.pipe = pipe_conn
        self.daemon = True

    ### Gripper

    def _gripper(self, action: str | float) -> None:
        """
        Send a gripper command.
          action = "open" | "close" , convenience endpoints
          action = float 0.0–1.0    , fractional grip (0=open, 1=closed)
        """
        if self._gripper_bus is None:
            rospy.logwarn(f"[RealExecutor] Gripper {action!r} skipped, bus not connected")
            return
        try:
            if isinstance(action, float):
                value = max(0.0, min(1.0, action))
                raw = int(round(self._gripper_open + value * (self._gripper_close - self._gripper_open)))
            elif action == "open":
                raw = self._gripper_open
            else:
                raw = self._gripper_close
            self._gripper_bus.write_position(raw)
        except Exception as e:
            rospy.logwarn(f"[RealExecutor] Gripper {action!r} failed: {e}")

    _JOINT_ABBREV = {
        "shoulder_pan_joint": "pan",
        "shoulder_lift_joint": "lift",
        "elbow_joint":         "elbow",
        "wrist_1_joint":       "w1",
        "wrist_2_joint":       "w2",
        "wrist_3_joint":       "w3",
    }

    ### Waypoint publisher

    def _send_waypoint(self, qpos6: np.ndarray, duration: float) -> None:
        """
        Publish a single-point trajectory goal and sleep until the robot should
        have reached it.  Mirrors joint_publisher.py's approach exactly.
        """
        positions = [float(qpos6[_QPOS_TO_NAME.index(j)]) for j in _UR_JOINT_ORDER]
        rospy.loginfo(
            f"[RealExecutor] Waypoint (duration={duration:.2f}s)  "
            + "  ".join(f"{self._JOINT_ABBREV[j]}={p:.3f}" for j, p in zip(_UR_JOINT_ORDER, positions))
        )

        pt = JointTrajectoryPoint()
        pt.positions = positions
        pt.time_from_start = rospy.Duration(duration)

        msg = FollowJointTrajectoryActionGoal()
        now = rospy.Time.now()
        msg.header.stamp = now
        msg.goal_id.stamp = now
        msg.goal_id.id = f"real_executor_{now.to_nsec()}"
        msg.goal.trajectory.joint_names = _UR_JOINT_ORDER
        msg.goal.trajectory.points = [pt]

        self._goal_pub.publish(msg)
        rospy.sleep(duration)

    ### Sequence execution

    def _execute_sequence(
        self, sequence: list, planner: UR10eController, data: mj.MjData
    ) -> None:
        """
        Convert a raw MotionPlanner sequence into trajectory/gripper segments
        and execute each one. Consecutive arm moves are batched into a single
        trajectory action call.
        """
        planner.clear_intents()
        current_qpos = data.qpos.copy()

        for cmd in sequence:
            if cmd[3] == 1:
                # Grip command — cmd[0] is 0.0 (open) to 1.0 (fully closed).
                grip_value = float(cmd[0])
                rospy.sleep(0.25)
                rospy.loginfo(f"[RealExecutor] Gripper {grip_value:.2f}")
                self._gripper(grip_value)
                rospy.sleep(0.25)
            else:
                # Arm move — run IK then send each resulting waypoint individually.
                planner.move_to(np.round(cmd[:3], 4), _R)
                while planner.intent_queue:
                    ik_cmd = planner.get_next_command(current_qpos, current_qpos[0])
                    if ik_cmd is None:
                        break
                    arm_moved = not np.allclose(
                        ik_cmd.target_qpos[:6], current_qpos[:6], atol=1e-6
                    )
                    if arm_moved:
                        self._send_waypoint(ik_cmd.target_qpos[:6], ik_cmd.duration)
                    else:
                        rospy.logwarn("[RealExecutor] IK returned same position, skipping waypoint")
                    current_qpos = ik_cmd.target_qpos.copy()
                    data.qpos[: len(current_qpos)] = current_qpos
                    mj.mj_forward(self._model, data)

    ### Joint state subscriber

    def _joint_state_cb(self, msg: JointState) -> None:
        self._latest_joints = dict(zip(msg.name, msg.position))
        now = time.monotonic()
        if now - self._last_state_write < (1.0 / _STATE_WRITE_HZ):
            return
        self._last_state_write = now
        try:
            _SHARED.mkdir(parents=True, exist_ok=True)
            with open(_STATE_PATH, "w") as f:
                joints = self._latest_joints
                json.dump(
                    {
                        "timestamp": msg.header.stamp.to_sec(),
                        "joints": {
                            j: joints[j] for j in _UR_JOINT_ORDER if j in joints
                        },
                    },
                    f,
                    indent=2,
                )
        except OSError:
            pass

    def get_joint_state(self) -> dict | None:
        """Return the latest cached joint positions (keyed by joint name)."""
        return getattr(self, "_latest_joints", None)

    ### Process entry point

    def run(self) -> None:
        if not _ROS_AVAILABLE:
            raise RuntimeError(
                "RealExecutor requires ROS (rospy, control_msgs), "
                "run inside the Docker container or a ROS-enabled environment.\n"
                f"  Import error was: {_ROS_IMPORT_ERROR}\n"
                f"  sys.path: {sys.path}"
            )

        # Gripper positions, must be set in env (docker-compose provides them)
        self._gripper_open  = int(os.environ["GRIPPER_OPEN_POS"])
        self._gripper_close = int(os.environ["GRIPPER_CLOSE_POS"])

        # ROS, init node first so wait_for_message works
        rospy.init_node("chess_real_executor", anonymous=False)

        self._latest_joints = {}
        self._last_state_write = 0.0
        rospy.Subscriber(
            "/joint_states", JointState, self._joint_state_cb, queue_size=1
        )

        # MuJoCo - IK only, no viewer; seed qpos from live robot state
        self._model = mj.MjModel.from_xml_path(_XML_PATH)
        data = mj.MjData(self._model)
        self._model.opt.timestep = 0.002

        rospy.loginfo("[RealExecutor] Waiting for first /joint_states message...")
        first_js = rospy.wait_for_message("/joint_states", JointState)
        for name, pos in zip(first_js.name, first_js.position):
            if name in _QPOS_TO_NAME:
                data.qpos[_QPOS_TO_NAME.index(name)] = pos
        mj.mj_forward(self._model, data)
        rospy.loginfo("[RealExecutor] Seeded MuJoCo qpos from live joint states.")

        planner = UR10eController(self._model, data, "attachment_site", verbose=False)

        # Gripper
        self._gripper_bus = _GripperBus(_GRIPPER_PORT, _GRIPPER_MOTOR_ID)
        try:
            self._gripper_bus.connect()
            self._gripper_bus.disable_torque()
            self._gripper_bus.enable_torque_hold()
        except Exception as e:
            rospy.logwarn(f"[RealExecutor] Gripper connect failed: {e}, gripper disabled")
            self._gripper_bus = None

        _GOAL_TOPIC = _ACTION_NS + "/goal"
        self._goal_pub = rospy.Publisher(
            _GOAL_TOPIC, FollowJointTrajectoryActionGoal, queue_size=1
        )
        rospy.loginfo(f"[RealExecutor] Waiting for controller to subscribe on {_GOAL_TOPIC}...")
        start = rospy.Time.now()
        while (self._goal_pub.get_num_connections() == 0
               and (rospy.Time.now() - start).to_sec() < 10.0
               and not rospy.is_shutdown()):
            rospy.sleep(0.05)
        if self._goal_pub.get_num_connections() == 0:
            rospy.logwarn("[RealExecutor] No subscribers on goal topic — is the UR driver running?")
        else:
            rospy.loginfo("[RealExecutor] Controller connected. Ready, waiting for commands.")

        _write_status("idle")

        while not rospy.is_shutdown():
            try:
                if not self.pipe.poll(timeout=0.1):
                    continue
                sequence = self.pipe.recv()
            except (EOFError, BrokenPipeError):
                break

            if sequence is None:
                break

            rospy.loginfo(f"[RealExecutor] Received sequence ({len(sequence)} steps)")
            _write_status("moving")
            self._execute_sequence(sequence, planner, data)
            _write_status("idle", move_complete=True)
            rospy.loginfo("[RealExecutor] Move complete.")

        if self._gripper_bus is not None:
            try:
                self._gripper_bus.disable_torque()
                self._gripper_bus.disconnect()
            except Exception:
                pass
