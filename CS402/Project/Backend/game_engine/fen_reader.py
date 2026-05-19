import json
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Reject latest_frame_data.json rows older than (session_start - this) so a file on disk
# from a previous run cannot seed puzzle calibration; allow a small skew for test order
# (set vision JSON, then vi.start()) and vision writing just before the engine starts.
_SESSION_FRESH_SLACK_S = 2.0

_ENGINE_DIR = Path(__file__).resolve().parent
_SHARED_QUEUE = _ENGINE_DIR.parent / "shared" / "queue"

GAME_STATE_PATH = _SHARED_QUEUE / "game_state.json"
FRAME_DATA_PATH = _SHARED_QUEUE / "latest_frame_data.json"

DEFAULT_CONFIDENCE_THRESHOLD = 0.6

class FenReader:



    def __init__(
        self,
        game_state_path = None,
        frame_data_path = None,
        confidence_threshold = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        
        self.game_state_path = Path(game_state_path or GAME_STATE_PATH)
        self.frame_data_path = Path(frame_data_path or FRAME_DATA_PATH)
        self.confidence_threshold = confidence_threshold
        
        self._last_frame_timestamp = None
        # Set in begin_engine_session(); frames with older JSON timestamps are ignored.
        self._min_allowed_json_timestamp = None
        
        logger.debug(f"FenReader: game_state -> {self.game_state_path}")
        logger.debug(f"FenReader: frame_data -> {self.frame_data_path}")

    def begin_engine_session(self):
        """Call when the game engine starts. Ignores stale latest_frame_data.json from prior runs."""
        self._min_allowed_json_timestamp = time.time() - _SESSION_FRESH_SLACK_S
        logger.info(
            "FenReader: engine session started — using only live latest_frame_data.json "
            f"(timestamp >= {_SESSION_FRESH_SLACK_S}s before this moment); no game_state fallback"
        )


    # Read the JSON file (retries on Windows when vision is briefly writing)
    def _read_json(self, path, retries=3):
        for attempt in range(retries):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except FileNotFoundError:
                logger.debug(f"File not found: {path}")
                return None
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error in {path}: {e}")
                return None
            except (OSError, PermissionError) as e:
                if attempt < retries - 1:
                    time.sleep(0.02)
                    continue
                logger.warning(f"OS error reading {path}: {e}")
                return None
        return None
    
    # Read the persistent game state json file in the vision module.
    # Then return dict with the keys (fen, last_detected_fen, game_active, etc (from json)) or None if missing or corrupt
    def read_game_state(self):
        return self._read_json(self.game_state_path)
    
    # Read the per frame latest frame data json file and return the dict with the keys the json file contains, including timestamp, vision_results that contain fen, confidence, and success. Otherwise return none.
    def read_frame_data(self):
        return self._read_json(self.frame_data_path)
    
    # Get the best available FEN and the confidence score related to it.
    # Uses latest_frame_data.json only (after begin_engine_session); game_state.json is not used
    # for FEN so persisted last_detected_fen cannot override the live camera after a restart.
    def _pad_fen(self, fen):
        """Vision usually returns piece placement (1 field). Pad to a full FEN.
        If a full 6-field FEN is already present, return it unchanged.
        In puzzle mode the game engine may override side to move from --to_move."""
        if fen and len(fen.strip().split()) == 1:
            return fen.strip() + " w KQkq - 0 1"
        return fen

    def _frame_is_fresh_for_session(self, frame: dict) -> bool:
        """True if this snapshot is not from before the current engine run (disk can hold old JSON)."""
        if self._min_allowed_json_timestamp is None:
            return True
        ts = frame.get("timestamp")
        if ts is None:
            return False
        return float(ts) >= self._min_allowed_json_timestamp

    def get_current_fen(self):
        # Only latest_frame_data.json — never game_state.json (last_detected_fen persists across runs).
        frame = self.read_frame_data()
        if frame is not None:
            if not self._frame_is_fresh_for_session(frame):
                return (None, 0.0)
            results = frame.get("vision_results", {})
            if results.get("success", False):
                fen = self._pad_fen(results.get("fen"))
                confidence = results.get("confidence", 0.0)
                if fen:
                    # Always return the actual confidence so the stability filter
                    # can detect hand presence from a confidence drop. Gating
                    # on the threshold here would mask low-confidence frames with
                    # a stale game_state fallback, defeating the hand-detection logic.
                    return (fen, confidence)

        # Only fall back to game_state when frame data is entirely unavailable.
        # Return 0.0 confidence so the filter treats it as unreliable.
        state = self.read_game_state()
        if state is not None:
            fen = self._pad_fen(state.get("last_detected_fen") or state.get("fen"))
            if fen:
                logger.debug("Using FEN from game_state.json (fallback)")
                return (fen, 0.0)
        return (None, 0.0)

    def get_current_fen_ignore_confidence(self):
        """Return FEN from latest frame if success=true, regardless of confidence. For robot-move confirmation."""
        frame = self.read_frame_data()
        if frame is not None:
            if not self._frame_is_fresh_for_session(frame):
                return None
            results = frame.get("vision_results", {})
            if results.get("success", False):
                fen = self._pad_fen(results.get("fen"))
                if fen:
                    return fen
        return None
            
    # Check if a new frame has arrived since the last call/read of the json file. 
    # Returns true if the timestamp in the json file is different than the last call
    def is_new_frame(self):
        frame = self.read_frame_data()
        if frame is None:
            return False
        
        ts = frame.get("timestamp")
        if ts != self._last_frame_timestamp:
            self._last_frame_timestamp = ts
            return True
        return False
    
    # Check if the vision system is running
    # Returns true if the game_state json file says game_active, or if frame_data has been updated within the last 10 seconds (very generous here, but it makes sense?)
    def is_vision_active(self):
        state = self.read_game_state()
        if state is not None and state.get("game_active", False):
            return True
        
        frame = self.read_frame_data()
        if frame is not None:
            ts = frame.get("timestamp", 0)
            age = time.time() - ts
            if age < 10.0:
                return True
            
        return False
    
    # Helper function to get the confidence threshold for the reading of the FEN in current frame/state
    def get_confidence_threshold(self):
        return self.confidence_threshold
    
    # Function to set the confidence threshold. Not sure how I call this yet. Maybe a settings panel? Not a bad shout. I have to make it though, ._.
    def set_confidence_threshold(self, threshold):
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold:.2f}")