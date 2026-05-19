import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vision_interface import VisionInterface
from board_state import BoardState
from move_detector import MoveDetector
from move_validator import MoveValidator
from fen_utils import validate_fen_structure

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
POLL_SECONDS = 5.0
STABILITY_WINDOW = 3

board_state = BoardState(fen=STARTING_FEN)
detector    = MoveDetector()
validator   = MoveValidator()
vi          = VisionInterface(
    stability_window=STABILITY_WINDOW,
    stability_required=STABILITY_WINDOW - 1,
    poll_interval=0.2,
)

print("=" * 60)
print("  VISION PIPELINE TEST")
print("=" * 60)
print()
print("This test simulates the vision → game engine pipeline.")
print("You will manually update the vision JSON files to simulate")
print("what the camera would see after a chess move.")
print()
print(f"JSON files to edit:")
print(f"  shared/queue/game_state.json")
print(f"  shared/queue/latest_frame_data.json")
print()
print("Starting board position:")
print(board_state.board)
print()


_SHARED_QUEUE = Path(__file__).resolve().parent.parent.parent / "shared" / "queue"


def set_vision_fen(fen, confidence=0.9):
    game_state_path = _SHARED_QUEUE / "game_state.json"
    if game_state_path.exists():
        try:
            with open(game_state_path) as f:
                data = json.load(f)
        except Exception:
            data = {}
        data["fen"] = fen
        data["last_detected_fen"] = fen
        data["timestamp"] = time.time()
        data["game_active"] = True
        with open(game_state_path, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print(f"  [WARN] game_state.json not found at {game_state_path}")

    frame_path = _SHARED_QUEUE / "latest_frame_data.json"
    frame_data = {
        "timestamp": time.time(),
        "vision_results": {
            "success": True,
            "fen": fen,
            "confidence": confidence,
            "method_used": "test_simulation",
            "fallback_active": False,
            "error_message": "",
        },
        "frame_path": "test",
        "capture_type": "test",
    }
    with open(frame_path, "w") as f:
        json.dump(frame_data, f, indent=2)

    print(f"  [Simulated vision]: {fen[:50]}...")


def poll_for_change(description, expected_fen, timeout=15.0):
    print(f"\n[Polling] {description}...")
    start = time.time()
    while True:
        result = vi.poll()
        if result:
            print(f"  [DETECTED] {result[:50]}...")
            return result
        elapsed = time.time() - start
        if elapsed > timeout:
            print(f"  [TIMEOUT] Did not detect change within {timeout}s")
            return None
        time.sleep(0.1)


print("STEP 1: Set starting position in vision files")
set_vision_fen(STARTING_FEN)
vi.start()
for _ in range(10):
    vi.poll()
    time.sleep(0.15)
vi.confirm_move(STARTING_FEN)
print(f"  Starting FEN confirmed.")
print()

print("STEP 2: Simulate human plays e2e4")
print("  (Auto-updating vision JSON to the new position...)")
time.sleep(1.0)

fen_after_e2e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

print("  Injecting a glitch frame...")
set_vision_fen("GLITCH_FEN_DO_NOT_ACT_ON_THIS", confidence=0.3)
time.sleep(0.3)
print("  Now sending correct FEN...")
set_vision_fen(fen_after_e2e4, confidence=0.95)

detected = poll_for_change("Waiting for e2e4 to be detected...", fen_after_e2e4)

if detected:
    print()
    print("  Validating detected FEN...")
    is_valid, msg = validate_fen_structure(detected)
    print(f"  FEN valid: {is_valid} — {msg}")

    print()
    print("  Detecting what move was played...")
    detected_move, is_legal = detector.detect_move_validated(STARTING_FEN, detected)
    print(f"  Detected move: {detected_move}")
    print(f"  Is legal:      {is_legal}")

    if detected_move:
        move_info = validator.classify_move(STARTING_FEN, detected_move)
        if move_info:
            print(f"  Move type:  {move_info.special or 'normal'}")
            print(f"  From → To:  {move_info.from_square} → {move_info.to_square}")
            print(f"  Piece:      {move_info.piece}")

    vi.confirm_move(detected)
    board_state.update_from_fen(detected)

print()
print("=" * 60)
print("  Test complete.")
print()
print("  If MoveDetector correctly identified e2e4, the pipeline works.")
print("  If not, check:")
print("  1. Are both JSON files being updated?")
print("  2. Is the confidence above the threshold (0.6)?")
print("  3. Does the detected FEN differ from the starting FEN?")
print("=" * 60)
