#!/usr/bin/env python3
"""
Pre-flight hardware check.

Polls all required devices in a live checklist until they are all reachable,
then automatically proceeds. Press Enter at any time to bypass and continue
with whatever is available.

Device config via environment variables (same ones docker-compose passes):
  CAMERA_INDEX    -- OpenCV camera index   (default: 1)
  GRIPPER_PORT    -- gripper serial port   (default: /dev/ttyACM0)
  ROBOT_IP        -- UR10e IP address      (default: 192.168.1.100)
  ROBOT_PORT      -- UR10e port (used for route check, default: 29999)
"""

import glob
import os
import socket
import sys
import threading
import time

# ANSI
_GREEN  = "\033[92m"
_RED    = "\033[91m"
_YELLOW = "\033[93m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"
_CLR    = "\033[K"  # clear to end of line

_CHECK = f"{_GREEN}+{_RESET}"
_CROSS = f"{_RED}x{_RESET}"
_WAIT  = f"{_YELLOW}?{_RESET}"

_RETRY_INTERVAL = 3.0


# Individual checks

def check_camera(index: int) -> tuple:
    video_devs = sorted(glob.glob("/dev/video*"))
    if not video_devs:
        return False, "no /dev/video* devices found"
    try:
        import cv2
        cap = cv2.VideoCapture(index)
        ok = cap.isOpened()
        cap.release()
        if ok:
            return True, f"index {index} opened ({len(video_devs)} device(s) visible)"
        return False, f"{len(video_devs)} device(s) found but index {index} failed to open"
    except Exception as e:
        return False, f"cv2 error: {e}"


def check_gripper(port: str) -> tuple:
    if not os.path.exists(port):
        return False, f"{port} not found"
    if not os.access(port, os.R_OK | os.W_OK):
        return False, f"{port} found but not accessible (permissions?)"
    return True, port


def check_host_network(ip: str, port: int) -> tuple:
    """
    Verify our host has a network route to the robot's IP without
    requiring the robot to be on. A UDP 'connect' resolves the local
    interface that would be used — no packets are sent.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, port))
        local_ip = s.getsockname()[0]
        s.close()
        return True, f"host interface {local_ip} → {ip}"
    except OSError as e:
        return False, f"no route to {ip} -- {e}"


# Rendering

def _render(states: list, status: str, first: bool) -> None:
    n_lines = len(states) + 1
    if not first:
        sys.stdout.write(f"\033[{n_lines}A")

    for ok, name, detail in states:
        if ok is True:
            icon = _CHECK
        elif ok is False:
            icon = _CROSS
        else:
            icon = _WAIT
        line = f"  [{icon}] {name}"
        if detail:
            line += f"  {_YELLOW}{detail}{_RESET}"
        sys.stdout.write(f"{line}{_CLR}\n")

    sys.stdout.write(f"  {status}{_CLR}\n")
    sys.stdout.flush()


# Runner

def run() -> bool:
    """
    Poll all hardware checks in a live loop until all pass or the user bypasses.
    Returns True if all passed, False if bypassed with failures.
    """
    camera_index = int(os.getenv("CAMERA_INDEX", "1"))
    gripper_port = os.getenv("GRIPPER_PORT",  "/dev/ttyACM0")
    robot_ip     = os.getenv("ROBOT_IP",       "192.168.1.100")
    robot_port   = int(os.getenv("ROBOT_PORT", "29999"))

    checks = [
        ("USB Camera",       lambda: check_camera(camera_index)),
        ("Gripper USB",      lambda: check_gripper(gripper_port)),
        ("UR10e Network",    lambda: check_host_network(robot_ip, robot_port)),
    ]

    _bypass = threading.Event()

    def _listen():
        try:
            sys.stdin.readline()
            _bypass.set()
        except Exception:
            pass

    threading.Thread(target=_listen, daemon=True).start()

    print(f"\n{_BOLD}  Pre-flight check{_RESET}  "
          f"{_YELLOW}(press Enter to bypass){_RESET}")
    print("  " + "-" * 44)

    states = [(None, name, "") for name, _ in checks]
    _render(states, f"{_YELLOW}Checking...{_RESET}", first=True)

    while not _bypass.is_set():
        states = [(fn(), name) for name, fn in checks]
        states = [(ok, name, detail) for (ok, detail), name in states]

        all_ok = all(ok for ok, _, _ in states)

        if all_ok:
            _render(states, f"{_GREEN}All checks passed -- starting.{_RESET}", first=False)
            print()
            return True

        failed = sum(1 for ok, _, _ in states if not ok)
        status = (
            f"{_RED}{failed} check(s) failed.{_RESET}  "
            f"{_YELLOW}Retrying in {_RETRY_INTERVAL:.0f}s... (Enter to bypass){_RESET}"
        )
        _render(states, status, first=False)

        deadline = time.monotonic() + _RETRY_INTERVAL
        while time.monotonic() < deadline and not _bypass.is_set():
            time.sleep(0.1)

    failed_names = [name for ok, name, _ in states if not ok]
    msg = (
        f"{_YELLOW}Bypassed -- proceeding with failures: "
        f"{', '.join(failed_names)}{_RESET}"
        if failed_names
        else f"{_GREEN}All checks passed.{_RESET}"
    )
    _render(states, msg, first=False)
    print()
    return len(failed_names) == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
