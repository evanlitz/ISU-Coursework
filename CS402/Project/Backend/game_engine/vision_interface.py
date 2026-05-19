import time
import logging
from fen_reader import FenReader
from fen_stability import FenStabilityFilter

# This is a class that wraps the FenReader and FenStabilityFilter into a single object that the game loop can then call and utlize.
# Vision --> Engine input module
# Game loop will call vi = VisionInterface() and vi.start()
# fen = vi.poll()
# vi.confirm_move()


logger = logging.getLogger(__name__)

# Module for vision to game engine input module.
# Polls the vision JSON files, filters for stability, and has API for the game loop
class VisionInterface:

    # Stability window = # of frames to keep in filter buffer
    # Stability_required = Frames that must match to confirm
    # Confidence_min = Mininum vision confidence to accept the positon
    # poll_interval = seconds between file read
    def __init__(
        self,
        stability_window=5,
        stability_required=3,
        stability_mode="per_square",
        confidence_min=0.6,
        poll_interval=0.2,
        recovery_frames=3,
        min_stable_seconds=1.0,
        fen_history=None,
    ):
        self.poll_interval = poll_interval

        self._reader = FenReader(confidence_threshold=confidence_min)
        self._filter = FenStabilityFilter(
            window=stability_window,
            required=stability_required,
            mode=stability_mode,
            confidence_threshold=confidence_min,
            recovery_frames=recovery_frames,
            min_stable_seconds=min_stable_seconds,
            fen_history=fen_history,
        )

        self._last_confirmed_fen = None # This is the FEN that was told to the game_engine last
        self._last_poll_time     = 0.0
        self._started            = False
        self._total_polls        = 0

        logger.info(
            f"VisionInterface: mode={stability_mode}, stability={stability_required}/{stability_window}, "
            f"confidence_min={confidence_min}, recovery_frames={recovery_frames}, "
            f"min_stable={min_stable_seconds}s, poll_interval={poll_interval}s"
        )

    # This is called once before the game loop begins
    def start(self):
        self._filter.reset()
        self._last_confirmed_fen = None
        self._reader.begin_engine_session()
        self._started = True
        logger.info("VisionInterface started")

    # Called when the game loop ends
    def stop(self):
        self._started = False
        logger.info("VisionInterface stopped")

    @staticmethod
    def _placement(fen):
        """Return the piece-placement field of a FEN, or empty string if None."""
        return fen.split()[0] if fen else ""

    # Check for new stable FEN from the vision module
    # Call this in game lloop whenever and return FEN string only when a new stable FEN is detected that is different from the last confirmed FEN
    def poll(self):
        now = time.time()
        if now - self._last_poll_time < self.poll_interval:
            return None

        self._last_poll_time = now
        self._total_polls += 1

        # Check whether the vision JSON has actually changed since the last poll.
        # is_new_frame() reads the timestamp field — False means the vision pipeline
        # hasn't written a new frame yet (jitter, slow inference, etc.).
        is_new = self._reader.is_new_frame()

        # Here it reads the latest FEN from vision module and gets confidence too
        fen, confidence = self._reader.get_current_fen()

        # Feed FEN and confidence into the stability filter.
        # is_new gates buffer voting; hand detection inside update() always fires.
        new_stable = self._filter.update(fen, confidence, is_new_frame=is_new)

        # Compare piece placement only — vision always pads side-to-move as "w",
        # but the internal board alternates. A full-string compare would falsely
        # treat the same position as new after every Black move.
        if new_stable and self._placement(new_stable) != self._placement(self._last_confirmed_fen):
            logger.info(f"New stable FEN detected: {new_stable}")
            return new_stable

        return None

    # Call this after the game engine has processed a FEN. THis prevents retriggering on the same position. FEN just processed is passed in as argument
    def confirm_move(self, fen):
        # Store placement only so the comparison in poll() is never tripped by
        # side-to-move field differences between vision output and board state.
        self._last_confirmed_fen = self._placement(fen)
        self._filter.reset()
        logger.info(f"Move confirmed. Filter reset. Waiting for next change...")

    def mark_stable_seen_as_invalid(self, fen: str):
        """After rejecting a stable FEN (e.g. empty board), advance last_confirmed so poll()
        does not return the same stable repeatedly without a filter reset."""
        if fen:
            self._last_confirmed_fen = fen

    # Check if the vision module is running
    def is_vision_running(self):
        return self._reader.is_vision_active()

    # Get the raw FEN fron the vision
    def get_current_fen(self):
        fen, confidence = self._reader.get_current_fen()
        return fen

    def get_current_fen_for_confirm(self):
        """Get FEN without confidence threshold - for robot-move confirmation when vision may report low conf."""
        return self._reader.get_current_fen_ignore_confidence()

    def get_new_frame_for_confirm(self):
        """For robot-move confirmation only. Returns (fen, is_new_frame) where is_new_frame
        is False if the vision file timestamp hasn't changed since the last call.
        Callers must check is_new_frame before counting toward a confirmation threshold —
        otherwise the same physical camera frame can be counted multiple times per second
        because the game loop runs faster than the camera."""
        is_new = self._reader.is_new_frame()
        fen = self._reader.get_current_fen_ignore_confidence()
        return fen, is_new

    # Get the stable FEN (if any has been confirmed by filter)
    def get_stable_fen(self):
        return self._filter.get_stable()

    # Stats getter function for debugging
    def get_stats(self):
        return {
            "total_polls":        self._total_polls,
            "vision_running":     self.is_vision_running(),
            "current_raw_fen":    self.get_current_fen(),
            "current_stable_fen": self.get_stable_fen(),
            "last_confirmed_fen": self._last_confirmed_fen,
            "filter_buffer":      self._filter.buffer_contents(),
        }

    def __repr__(self):
        return (
            f"VisionInterface(polls={self._total_polls}, "
            f"stable={self._filter.is_stable()}, "
            f"vision_running={self.is_vision_running()})"
        )


