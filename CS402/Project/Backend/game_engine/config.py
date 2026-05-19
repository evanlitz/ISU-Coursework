import os
from pathlib import Path
import numpy as np
import sys

# Path constants -- MIGHT NEED TO BE CHANGED 
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEPLOY_MUJOCO_DIR = PROJECT_ROOT / "deploy_mujoco"
VISION_MODULE_DIR = PROJECT_ROOT / "vision_module"
MUJOCO_MODEL_PATH = "ur10e/ur10e_custom_gripper_scene.xml"
sys.path.insert(0, str(DEPLOY_MUJOCO_DIR))


# Stockfish paths for smart chess moves
STOCKFISH_PATHS = [
    "stockfish",
    "stockfish.exe",
    r"C:\Users\15157\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe",   # EDIT THIS WITH WHERE YOU DOWNLOAD STOCKFISH.EXE
    r"C:\Program Files\Stockfish\stockfish.exe",            # EDIT THIS WHERE YOU KEEP THE STOCKFISH.EXE FILE
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    "/usr/games/stockfish",
    "/opt/homebrew/bin/stockfish",
]

# Stockfish settings 
STOCKFISH_SKILL_LEVEL = 20  # similar to the chess bot settings in chess.com?
STOCKFISH_TIME_LIMIT = 2.0 # Time limit for setting moves 
STOCKFISH_DEPTH = None # Skill level like chess.com rating ??

# Starting FEN and human is opponent (for now)
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  
HUMAN_COLOR = "white"
ROBOT_COLOR = "black"

# If vision cannot match any legal opponent move to the new FEN, still advance the game by
# trusting piece placement from vision and setting side-to-move to the robot (when FEN is valid).
VISION_SYNC_ON_MOVE_MISMATCH = True
# If True, only sync when validate_fen_semantics passes (rejects e.g. duplicate kings).
VISION_SYNC_REQUIRE_SEMANTICS = True

# --- Vision / Stability buffer tuning ---
# Confidence from YOLO below this value is treated as a hand over the board;
# the stability buffer is paused and no frames are accepted until recovery.
VISION_CONFIDENCE_MIN     = 0.6
# Number of consecutive high-confidence frames required after a hand withdraws
# before the stability buffer resumes. At poll_interval=0.4s, 3 frames = 1.2s.
VISION_RECOVERY_FRAMES    = 3
# Sliding window size (number of recent polls kept in the buffer).
VISION_STABILITY_WINDOW   = 5
# How many of those window frames must show the same FEN to declare it stable.
VISION_STABILITY_REQUIRED = 3
# Seconds between vision JSON reads. Set to match the vision pipeline's output
# rate (~2.5 fps = 0.4s/frame) so each poll sees a genuinely new camera frame.
# Polling faster than the vision rate causes the same frame to be fed to the
# stability filter twice, inflating vote counts without adding new information.
VISION_POLL_INTERVAL      = 0.4
# Minimum wall-clock seconds the candidate FEN must be continuously observed
# before stability is declared. Acts as a second condition alongside frame count.
# At poll_interval=0.4s with recovery_frames=3: total hand-to-detection minimum
# is roughly recovery (1.2s) + this value.
VISION_MIN_STABLE_SECONDS = 0.7
# Stability filter mode: "per_square" (recommended), "majority", or "strict".
# per_square votes on each board square independently — immune to piece-type flicker.
# majority/strict require the exact FEN string to repeat, which breaks on flicker.
VISION_STABILITY_MODE     = "per_square"

# Pull from deploy.pu
try:
    from deploy import (
        KP_JOINTS, KD_JOINTS,
        KP_GRIPPER, KD_GRIPPER,
        GRIPPER_OPEN, GRIPPER_CLOSED as GRIPPER_CLOSE,
    )
except ImportError:
    # Fallback if deploy.py can't be imported
    KP_JOINTS = [450, 370, 135, 150, 100, 144]
    KD_JOINTS = [3.5, 30.36, 26.4375, 35, 3.9, 2.86]
    KP_GRIPPER = 17.8
    KD_GRIPPER = 2.0
    GRIPPER_OPEN = 1.5
    GRIPPER_CLOSE = -0.17453

BOARD_ORIGIN = np.array([0.0, 0.0, 0.0])
SQUARE_SIZE = 0.05
PIECE_HEIGHT = 0.15
APPROACH_HEIGHT = 0.10
# Hardcoding these for now, will fix later.
