import json
import logging
from pathlib import Path
from move_validator import MoveInfo

logger = logging.getLogger(__name__)

_ENGINE_DIR = Path(__file__).resolve().parent
ROBOT_COMMANDS_DIR = _ENGINE_DIR.parent / "shared" / "queue"
ROBOT_COMMANDS_PATH = ROBOT_COMMANDS_DIR / "robot_commands.json"
ROBOT_STATUS_PATH = ROBOT_COMMANDS_DIR / "robot_status.json"


def _clear_move_complete_in_status():
    """So the game loop does not see the previous move's move_complete before the sim clears it."""
    try:
        payload = {
            "state": "pending",
            "move_complete": False,
        }
        if ROBOT_STATUS_PATH.exists():
            try:
                with open(ROBOT_STATUS_PATH, "r", encoding="utf-8") as f:
                    prev = json.load(f)
                if isinstance(prev, dict):
                    payload = {**prev, **payload}
            except (json.JSONDecodeError, OSError):
                pass
        ROBOT_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ROBOT_STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass

def write_move_command(move_info: MoveInfo, path=None):
    out_path = Path(path or ROBOT_COMMANDS_PATH)

    command = {
        "from_sq":        move_info.from_square,
        "to_sq":          move_info.to_square,
        "moved_piece":    move_info.piece,
        "captured_piece": move_info.captured_piece,
        "promotion_piece": move_info.promotion_piece,
        "special":        move_info.special,
    }

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _clear_move_complete_in_status()
        with open(out_path, "w") as f:
            json.dump(command, f, indent=2)
        logger.info(f"Robot command written: {move_info.uci} ({move_info.special or 'normal'})")
    except OSError as e:
        logger.error(f"Failed to write robot command: {e}")
