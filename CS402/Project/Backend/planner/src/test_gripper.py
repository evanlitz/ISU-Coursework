"""
Gripper test script — arm is never touched.

Run inside the Docker container:
    python3 /chess/test_gripper.py

Connects without enabling torque — gripper stays limp until you type 'hold'.

Commands:
    read        → print current encoder position
    free        → disable torque so you can move gripper by hand
    hold        → enable torque (holds current position, won't lurch)
    open        → move to configured open position
    close       → move to configured close position
    0.0 – 1.0   → fractional position (0=open, 1=closed)
    q / exit    → disable torque and quit
"""

import os
import sys

_GRIPPER_PORT     = os.getenv("GRIPPER_PORT",      "/dev/ttyACM0")
_GRIPPER_BAUD     = int(os.getenv("GRIPPER_BAUD",  "1000000"))
_GRIPPER_MOTOR_ID = int(os.getenv("GRIPPER_MOTOR_ID", "1"))
_GRIPPER_OPEN_POS  = int(os.environ["GRIPPER_OPEN_POS"])
_GRIPPER_CLOSE_POS = int(os.environ["GRIPPER_CLOSE_POS"])

sys.path.insert(0, "/chess")
from real_executor import _GripperBus


def main() -> None:
    bus = _GripperBus(_GRIPPER_PORT, _GRIPPER_MOTOR_ID)
    try:
        bus.connect()
    except Exception as e:
        print(f"[ERROR] Could not connect to gripper on {_GRIPPER_PORT}: {e}")
        sys.exit(1)

    # Disable torque on connect — servo stays limp, won't lurch
    bus.disable_torque()
    torque_on = False

    pos = bus.read_present_position()
    print(f"Gripper connected on {_GRIPPER_PORT} (motor {_GRIPPER_MOTOR_ID})")
    print(f"  current position = {pos if pos is not None else '(no response)'}")
    print(f"  configured open={_GRIPPER_OPEN_POS}  close={_GRIPPER_CLOSE_POS}")
    print("  torque is OFF — type 'hold' to enable")
    print("Commands: read | free | hold | open | close | 0.0-1.0 | q\n")

    try:
        while True:
            try:
                raw = input("gripper> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break

            if raw in ("q", "quit", "exit", ""):
                break

            elif raw == "read":
                val = bus.read_present_position()
                if val is None:
                    print("  ! no response from servo")
                else:
                    print(f"  position = {val}")
                continue

            elif raw == "free":
                bus.disable_torque()
                torque_on = False
                print("  torque disabled — move gripper by hand, then type 'read'")
                continue

            elif raw == "hold":
                bus.enable_torque_hold()
                torque_on = True
                print("  torque enabled (holding current position)")
                continue

            elif raw == "open":
                pos = _GRIPPER_OPEN_POS
                print(f"  → open ({pos})")
            elif raw == "close":
                pos = _GRIPPER_CLOSE_POS
                print(f"  → close ({pos})")
            else:
                try:
                    frac = float(raw)
                    if not (0.0 <= frac <= 1.0):
                        print("  ! value must be between 0.0 and 1.0")
                        continue
                    pos = int(round(_GRIPPER_OPEN_POS + frac * (_GRIPPER_CLOSE_POS - _GRIPPER_OPEN_POS)))
                    print(f"  → {frac:.2f} ({pos})")
                except ValueError:
                    print("  ! unrecognised command")
                    continue

            if not torque_on:
                bus.enable_torque_hold()
                torque_on = True
                print("  (torque auto-enabled to execute move)")

            try:
                bus.write_position(pos)
            except Exception as e:
                print(f"  ! write failed: {e}")
    finally:
        print("\nDisabling torque and disconnecting.")
        try:
            bus.disable_torque()
            bus.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()
