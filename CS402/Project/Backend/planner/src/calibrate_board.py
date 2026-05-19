#!/usr/bin/env python3
"""
Standalone board calibration script.

Connects to the UR10e via ROS, loads the MuJoCo model for forward kinematics,
and guides the user to manually position the robot arm at each calibration
waypoint. Saves the result to board_calibration.json.

Usage (inside the Docker container with ROS active):
    python calibrate_board.py

Ensure the robot is in Remote Control mode on the UR tablet and the URCap
program is running before starting. Enable Freedrive on the pendant when
prompted so the arm can be moved by hand.

Waypoints collected:
    a1    — gripper tip at corner A1 of the board (near-left)
    h1    — gripper tip at corner H1 of the board (near-right)
    a8    — gripper tip at corner A8 of the board (far-left)
    h8    — gripper tip at corner H8 of the board (far-right)
    hover — gripper tip at hover height above the centre of the board
    lower — gripper tip lowered to piece-grasp height above the centre
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import mujoco as mj
import numpy as np

# ── ROS Python paths (mirrors real_executor.py) ───────────────────────────────
_ROS_PYTHON_PATH    = "/opt/ros/noetic/lib/python3/dist-packages"
_CATKIN_PYTHON_PATH = "/catkin_ws/devel/lib/python3/dist-packages"
for _p in (_ROS_PYTHON_PATH, _CATKIN_PYTHON_PATH):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import rospy
    from sensor_msgs.msg import JointState
except ImportError as e:
    sys.exit(
        "ROS not available — run this script inside the Docker container.\n"
        f"  Import error: {e}"
    )

# ── Paths (mirrors motion_planner.py) ─────────────────────────────────────────
_HERE        = Path(__file__).resolve().parent
_XML_PATH    = _HERE / "ur10e" / "ur10e_custom_gripper_scene.xml"
_SHARED_ROOT = (
    Path("/shared")
    if Path("/shared").exists()
    else _HERE.parent.parent / "shared"
)
_CALIB_OUT = _SHARED_ROOT / "calibrations" / "board_calibration.json"

# ── MuJoCo qpos index → UR joint name (matches real_executor._QPOS_TO_NAME) ──
_QPOS_TO_NAME = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

# ── Waypoints to collect, in order ───────────────────────────────────────────
_WAYPOINTS = [
    (
        "a1",
        "Corner A1  (file A, rank 1 — near-left corner of the board)\n"
        "     Place the gripper thumb on the lowest corner of a1 (absolute corner).",
    ),
    (
        "h1",
        "Corner H1  (file H, rank 1 — near-right corner of the board)\n"
        "     Place the gripper thumb on the lowest corner of h1 (absolute corner).",
    ),
    (
        "a8",
        "Corner A8  (file A, rank 8 — far-left corner of the board)\n"
        "     Place the gripper thumb on the lowest corner of a8 (absolute corner).",
    ),
    (
        "h8",
        "Corner H8  (file H, rank 8 — far-right corner of the board)\n"
        "     Place the gripper thumb on the lowest corner of h8 (absolute corner).",
    ),
    (   "a1grip",
        "Grip area (a1), place the thumb to the side enough to properly\n"
        "     grip any piece."
    ),
    (
        "hover",
        "Hover height  (centre of board, gripper at the height used to\n"
        "     travel between squares — typically ~5–8 cm above a piece).",
    ),
    (
        "lower",
        "Lower height  (centre of board, gripper lowered to the lowest\n"
        "     height that clears all pieces).",
    ),
    (
        "pawn",
        "Pawn height  (place gripper at height to grip a pawn)."
    ),
    (
        "knight",
        "knight height  (place gripper at height to grip a knight)."
    ),
    (
        "bishop",
        "bishop height  (place gripper at height to grip a bishop)."
    ),
    (
        "rook",
        "rook height  (place gripper at height to grip a rook)."
    ),
    (
        "queen",
        "queen height  (place gripper at height to grip a queen)."
    ),
    (
        "king",
        "king height  (place gripper at height to grip a king)."
    ),
]

# ── Latest joint state (filled by ROS subscriber callback) ───────────────────
_latest_joints: dict[str, float] = {}


def _joint_cb(msg: JointState) -> None:
    global _latest_joints
    _latest_joints = dict(zip(msg.name, msg.position))


def _get_qpos6() -> np.ndarray | None:
    """Build MuJoCo qpos[0:6] from the latest ROS /joint_states message."""
    if not _latest_joints:
        return None
    try:
        return np.array([_latest_joints[name] for name in _QPOS_TO_NAME])
    except KeyError as missing:
        rospy.logwarn(f"[calibrate_board] Joint missing from /joint_states: {missing}")
        return None


def _fk(
    model: mj.MjModel,
    data: mj.MjData,
    qpos6: np.ndarray,
    site_id: int,
) -> np.ndarray:
    """
    Set arm joints, run mj_forward, and return the attachment_site position.
    The gripper joint (index 6) is left at its current value.
    """
    data.qpos[:6] = qpos6
    mj.mj_forward(model, data)
    return data.site_xpos[site_id].copy()


def main() -> None:
    print("\n" + "=" * 60)
    print("  UR10e Board Calibration")
    print("=" * 60)
    print(f"  MuJoCo model : {_XML_PATH}")
    print(f"  Output       : {_CALIB_OUT}")
    print()

    # ── Load MuJoCo model ─────────────────────────────────────────────────────
    if not _XML_PATH.exists():
        sys.exit(f"ERROR: MuJoCo XML not found:\n  {_XML_PATH}")

    model   = mj.MjModel.from_xml_path(str(_XML_PATH))
    data    = mj.MjData(model)
    site_id = mj.mj_name2id(model, mj.mjtObj.mjOBJ_SITE, "attachment_site")
    if site_id == -1:
        sys.exit("ERROR: 'attachment_site' not found in MuJoCo model.")

    print("  MuJoCo model loaded OK.")

    # ── ROS init and /joint_states subscriber ─────────────────────────────────
    rospy.init_node("board_calibrator", anonymous=False)
    rospy.Subscriber("/joint_states", JointState, _joint_cb, queue_size=1)

    print("  Subscribed to /joint_states — waiting for first message (10 s)...")
    deadline = time.monotonic() + 10.0
    while not _latest_joints and time.monotonic() < deadline:
        time.sleep(0.05)

    if not _latest_joints:
        sys.exit(
            "\nERROR: No /joint_states received within 10 s.\n"
            "  → Confirm the UR ROS driver is running.\n"
            "  → Confirm ROS_MASTER_URI points at the correct host."
        )

    print(f"  Receiving joint states for: {list(_latest_joints.keys())}\n")

    # ── Instructions ──────────────────────────────────────────────────────────
    print("─" * 60)
    print("  INSTRUCTIONS")
    print("─" * 60)
    print("  1. Enable Freedrive on the UR tablet so you can move the arm.")
    print("  2. For each waypoint, physically guide the gripper tip to the")
    print("     described position.")
    print("  3. Press ENTER to record — the script reads /joint_states and")
    print("     uses MuJoCo FK to compute the end-effector xyz in the world")
    print("     frame.")
    print("  4. Confirm or redo each recording before moving on.")
    print("  5. Ctrl-C at any time to abort without saving.")
    print("─" * 60)
    input("\n  Press ENTER to begin calibration...\n")

    results: dict[str, list[float]] = {}

    for key, description in _WAYPOINTS:
        while True:
            print(f"\n  [{key.upper()}]  {description}")
            input("  → Position the arm, then press ENTER to record... ")

            qpos6 = _get_qpos6()
            if qpos6 is None:
                print("  [!] No joint state available yet — retrying...")
                time.sleep(0.3)
                qpos6 = _get_qpos6()
                if qpos6 is None:
                    print("  [!] Still no joint state — please check ROS driver.")
                    continue

            pos = _fk(model, data, qpos6, site_id)
            print(f"\n  Recorded position  (world frame, attachment_site):")
            print(f"    x = {pos[0]: .4f} m")
            print(f"    y = {pos[1]: .4f} m")
            print(f"    z = {pos[2]: .4f} m")
            print(f"  Joint angles (rad): {np.round(qpos6, 4).tolist()}")

            ans = input("\n  Accept this recording? [Y/n]: ").strip().lower()
            if ans in ("", "y", "yes"):
                results[key] = pos.tolist()
                print(f"  Saved {key}.")
                break
            else:
                print("  Redoing this waypoint...")

    # ── Write calibration file ────────────────────────────────────────────────
    _CALIB_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(_CALIB_OUT, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("  Calibration complete!")
    print(f"  Saved to: {_CALIB_OUT}")
    print("=" * 60)
    print("\n  Summary:")
    for key, val in results.items():
        print(f"    {key:6s}: {[round(v, 4) for v in val]}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted — calibration NOT saved.\n")
        sys.exit(1)
