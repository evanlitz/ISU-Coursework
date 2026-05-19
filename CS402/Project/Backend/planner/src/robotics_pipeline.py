import argparse
import json
import multiprocessing as mp
import time
import os
from pathlib import Path

from motion_planner import MotionPlanner
from run_sim import RunSim
from real_executor import RealExecutor

_HERE = Path(__file__).resolve().parent
_CMD_PATH = _HERE.parent.parent / "shared" / "queue" / "robot_commands.json"
_POLL_INTERVAL = 0.1  # seconds between file checks


def run_pipeline(auto=False, real=False):
    # 1. Setup Communication Channels
    main_to_planner_send, planner_recv = mp.Pipe()
    planner_to_executor_send, executor_recv = mp.Pipe()

    # 2. Instantiate Classes
    planner = MotionPlanner(planner_recv, planner_to_executor_send)
    executor = RealExecutor(executor_recv) if real else RunSim(executor_recv)

    # 3. Start Processes
    planner.start()
    executor.start()

    print("--- Pipeline Active ---\n")
    try:
        print(f"auto? {auto}")
        if auto:
            # Launched by orchestrator: poll robot_commands.json for moves
            try:
                os.makedirs(os.path.dirname(_CMD_PATH), exist_ok=True)
                with open(_CMD_PATH, "w") as f:
                    print(f"{_CMD_PATH} created/cleared")
            except Exception as e:
                print(f"An error occured: {e}")

            last_mtime = _CMD_PATH.stat().st_mtime
            while True:
                time.sleep(_POLL_INTERVAL)
                if not _CMD_PATH.exists():
                    continue
                try:
                    mtime = _CMD_PATH.stat().st_mtime
                except OSError:
                    continue
                if mtime <= last_mtime:
                    continue
                try:
                    with open(_CMD_PATH) as f:
                        cmd = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue
                last_mtime = mtime
                print(
                    f"Sending: {cmd.get('from_sq')}{cmd.get('to_sq')} ({cmd.get('special') or 'normal'})"
                )
                main_to_planner_send.send(cmd)
        else:
            # Manual testing: accept move strings from stdin
            print(
                "Input move (e.g. e2e4/P///  or  e5d6/P/p//en_passant), or 'q' to quit:\n"
            )
            while True:
                cmd = input("> ")
                if cmd.lower() == "q":
                    break
                main_to_planner_send.send(cmd)
    except KeyboardInterrupt:
        pass
    finally:
        # 4. Clean Shutdown
        try:
            main_to_planner_send.send("STOP")
        except (EOFError, BrokenPipeError):
            pass  # Planner may have already exited
        try:
            planner_to_executor_send.send(None)
        except (EOFError, BrokenPipeError):
            pass  # Executor or planner may have already closed pipe
        planner.join()
        executor.join()
        print("Pipeline closed.")


if __name__ == "__main__":
    # CRITICAL: This guard is required for multi-file multiprocessing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Poll robot_commands.json (used when launched by the orchestrator)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use RealExecutor (real UR10e via ROS) instead of RunSim",
    )
    args = parser.parse_args()
    run_pipeline(auto=args.auto, real=args.real)
