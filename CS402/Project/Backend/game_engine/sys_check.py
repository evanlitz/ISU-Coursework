import sys
import os
from pathlib import Path

print("=" * 50)
print("  CHESS ROBOT SYSTEM CHECK")
print("=" * 50)
print()

# ── Test 1: Python-chess ────────────────────────────────
try:
    import chess
    print(f"[OK] python-chess  v{chess.__version__}")
except ImportError:
    print("[FAIL] python-chess not installed.")
    print("       Run: pip install chess")
    sys.exit(1)

# ── Test 2: NumPy ───────────────────────────────────────
try:
    import numpy as np
    print(f"[OK] numpy         v{np.__version__}")
except ImportError:
    print("[FAIL] numpy not installed. Run: pip install numpy")

# ── Test 3: Game Engine Modules ─────────────────────────
print()
print("--- Game Engine Modules ---")

modules = [
    "config",
    "fen_utils",
    "board_state",
    "game_state",
    "move_detector",
    "move_validator",
    "robot_actions",
    "robot_planner",
    "stockfish_engine",
    "game_over_detector",
]

all_ok = True
for mod in modules:
    try:
        __import__(mod)
        print(f"[OK] {mod}")
    except ImportError as e:
        print(f"[FAIL] {mod}: {e}")
        all_ok = False
    except Exception as e:
        print(f"[WARN] {mod}: {e}")

# ── Test 4: Vision JSON Files ───────────────────────────
print()
print("--- Vision Module JSON Output ---")

shared_queue = Path(__file__).resolve().parent.parent / "shared" / "queue"
game_state_path = shared_queue / "game_state.json"
frame_data_path = shared_queue / "latest_frame_data.json"

if game_state_path.exists():
    print(f"[OK] game_state.json found")
else:
    print(f"[WARN] game_state.json not found at:")
    print(f"       {game_state_path}")
    print(f"       Vision module must run first to create this file.")

if frame_data_path.exists():
    print(f"[OK] latest_frame_data.json found")
else:
    print(f"[WARN] latest_frame_data.json not found")
    print(f"       Vision module must run first to create this file.")

# ── Test 5: Deploy MuJoCo ───────────────────────────────
print()
print("--- Deploy MuJoCo ---")

deploy_dir = project_root / "deploy_mujoco"
motion_planner_path = deploy_dir / "motion_planner.py"
ur10e_controller_path = deploy_dir / "ur10e_controller.py"

if motion_planner_path.exists():
    print(f"[OK] motion_planner.py found (empty class — will fill in Prompt 06)")
else:
    print(f"[FAIL] motion_planner.py not found")

if ur10e_controller_path.exists():
    print(f"[OK] ur10e_controller.py found")
else:
    print(f"[FAIL] ur10e_controller.py not found")

# ── Test 6: Stockfish ───────────────────────────────────
print()
print("--- Stockfish ---")

import shutil
stockfish_found = shutil.which("stockfish")
if stockfish_found:
    print(f"[OK] stockfish on PATH: {stockfish_found}")
else:
    # Check the hardcoded path from config
    try:
        from config import STOCKFISH_PATHS
        found = False
        for path in STOCKFISH_PATHS:
            if os.path.isfile(path):
                print(f"[OK] stockfish at: {path}")
                found = True
                break
        if not found:
            print("[WARN] Stockfish not found. Update STOCKFISH_PATHS in config.py")
    except Exception:
        print("[WARN] Could not check Stockfish paths")

# ── Summary ─────────────────────────────────────────────
print()
print("=" * 50)
if all_ok:
    print("  All game engine modules loaded OK.")
else:
    print("  Some modules failed. Fix before continuing.")
print("=" * 50)