import logging
import time
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fen_history import FenHistory

logger = logging.getLogger(__name__)


"""
This class is built to filter out the noisy FEN readings that come from the vision model. For now I have two modes it can turn on.

Strict: FEN must appear an N amount of consecutive times 
    - This is the default mode 
Majority: FEN must appear in at least M of the last N frames

Also has a reset function.

I use a concept in this class called SLIDING WINDOW FILTERING. So keep buffer of last N FEN detection. If same FEN appears in majority of them, report it as the stable FEN. Since the frames are so fast (I hope) and the 
opponent needs time to make a move, this works.



"""
class FenStabilityFilter:

    MODE_STRICT     = "strict"
    MODE_MAJORITY   = "majority"
    MODE_PER_SQUARE = "per_square"

    # Intiialize the FenStabilityFilter object.
    # confidence_threshold: frames below this are treated as hand-present (buffer paused)
    # recovery_frames: number of consecutive high-confidence frames required after a hand
    #                  withdraws before the buffer resumes accepting frames
    # min_stable_seconds: minimum wall-clock time the candidate FEN must hold before firing.
    #                     Acts as a second condition alongside the frame-count requirement.
    def __init__(self, window=5, required=3, mode="per_square",
                 confidence_threshold=0.6, recovery_frames=3, min_stable_seconds=0.7,
                 fen_history=None):
        if required > window:
            raise ValueError(f"required ({required}) cannot exceed window ({window})")

        # Window is the number of recent frames to keep in the buffer
        self.window = window
        # Required is the number of time the same FEN must appear in the window.
        self.required = required
        # Strict (consecutive) or majority (required of window frames)
        self.mode = mode
        # Confidence below this signals a hand is over the board
        self.confidence_threshold = confidence_threshold
        # How many high-confidence frames must follow a hand before buffer resumes
        self.recovery_frames = recovery_frames
        # Minimum seconds the candidate FEN must be continuously observed before firing
        self.min_stable_seconds = min_stable_seconds
        # Optional FenHistory reference for per-square vote tiebreaking
        self._fen_history = fen_history

        # Store the recent FEN strings
        self._buffer = deque(maxlen=window)
        # This is the last FEN that is reported as stable
        self._last_stable = None
        # Consecutive count for strict mode
        self._consecutive = 0
        # Hand-presence state
        self._hand_present = False
        self._recovery_count = 0
        # Candidate FEN being timed — clock starts when a new FEN first appears
        self._candidate_fen = None
        self._candidate_first_seen = None

    # Feed a new FEN and its vision confidence to the filter.
    # Returns a stable FEN string if one has been confirmed, otherwise None.
    def update(self, fen, confidence=1.0, is_new_frame=True):

        # --- Hand detection: always runs, even on duplicate frames ---
        # A hand over the board must be caught on every poll. Waiting for a new
        # frame before detecting low confidence would add up to one full vision
        # cycle (~0.4s) of blind time while the buffer is being corrupted.
        if confidence < self.confidence_threshold:
            if not self._hand_present:
                logger.info(
                    f"Hand detected (conf={confidence:.2f} < {self.confidence_threshold:.2f})"
                    " — stability buffer paused"
                )
            self._hand_present = True
            self._recovery_count = 0
            self._consecutive = 0  # Reset strict-mode streak
            self._candidate_fen = None  # Invalidate any candidate being timed
            self._candidate_first_seen = None
            self._buffer.clear()  # Discard stale frames so post-move frames start fresh
            return None

        # --- Duplicate frame gate ---
        # Recovery counting and buffer voting only run on genuinely new frames.
        # Feeding the same camera frame twice inflates vote counts without adding
        # information — a 3v2 split would actually represent 1.5 frames vs 1,
        # not 3 independent observations vs 2.
        if not is_new_frame:
            return None

        # --- Recovery: require N clean frames after hand leaves ---
        if self._hand_present:
            self._recovery_count += 1
            if self._recovery_count < self.recovery_frames:
                logger.debug(
                    f"Post-hand recovery: {self._recovery_count}/{self.recovery_frames} "
                    f"clean frames (conf={confidence:.2f})"
                )
                return None
            logger.info(
                f"Hand withdrawn — buffer resuming after {self._recovery_count} "
                f"recovery frame(s)"
            )
            self._hand_present = False
            self._recovery_count = 0

        # --- Normal operation: add to buffer and check frame-count stability ---
        self._buffer.append(fen)

        if self.mode == self.MODE_STRICT:
            frame_stable = self._check_strict(fen)
            clock_key = fen
        elif self.mode == self.MODE_MAJORITY:
            frame_stable = self._check_majority(fen)
            clock_key = fen
        else:  # MODE_PER_SQUARE
            frame_stable = self._check_per_square()
            # Track the clock on the consensus FEN, not the raw noisy input.
            # The consensus is already smoothed by per-square voting, so a single
            # flickering square won't reset the clock on every frame.
            clock_key = frame_stable

        # --- Candidate clock: reset when the trackable key changes ---
        if clock_key is not None and clock_key != self._candidate_fen:
            self._candidate_fen = clock_key
            self._candidate_first_seen = time.time()
            logger.debug("New candidate FEN — dwell clock started")

        if frame_stable is None:
            return None

        # --- Time gate: frame count passed, now check minimum dwell ---
        elapsed = time.time() - self._candidate_first_seen
        if elapsed < self.min_stable_seconds:
            logger.debug(
                f"Frame-stable but dwell insufficient: {elapsed:.2f}s "
                f"/ {self.min_stable_seconds}s required"
            )
            return None

        # --- Both conditions met: report stable FEN ---
        if frame_stable != self._last_stable:
            self._last_stable = frame_stable
            logger.info(
                f"Stable FEN confirmed (frames + {elapsed:.2f}s dwell): {frame_stable}"
            )
            return frame_stable

        return None
        
    # Returns the FEN if the strict (consecutive) frame condition is met, else None.
    # Does not set _last_stable — that is handled by update() after the time gate.
    def _check_strict(self, fen):
        if fen is None:
            self._consecutive = 0
            return None

        if len(self._buffer) >= 2 and self._buffer[-2] == fen:
            self._consecutive += 1
        else:
            self._consecutive = 1

        if self._consecutive >= self.required:
            return fen

        return None

    # Returns the FEN if the majority frame condition is met, else None.
    # Does not set _last_stable — that is handled by update() after the time gate.
    def _check_majority(self, fen):
        if len(self._buffer) < self.window:
            return None

        counts = {}
        for f in self._buffer:
            if f is not None:
                counts[f] = counts.get(f, 0) + 1

        best_fen = max(counts, key=counts.get) if counts else None
        best_count = counts.get(best_fen, 0)

        if best_count >= self.required:
            return best_fen
        return None
    
    # Build a consensus FEN by voting per square across all frames in the buffer.
    # Each square independently elects the piece seen most often across the window.
    # A square that flickers between two piece types resolves to the plurality winner
    # rather than invalidating the whole FEN — this is the key advantage over majority mode.
    # Returns None if the buffer is not yet full.
    def _check_per_square(self):
        if len(self._buffer) < self.window:
            return None

        frame_dicts = [self._fen_to_square_dict(f) for f in self._buffer if f is not None]
        if not frame_dicts:
            return None

        # Collect all squares seen in any frame
        all_squares = set()
        for fd in frame_dicts:
            all_squares.update(fd.keys())

        consensus = {}
        for sq in all_squares:
            # Tally votes: piece char or None (empty) for each frame
            piece_votes = {}
            for fd in frame_dicts:
                piece = fd.get(sq)  # None means the square was empty this frame
                piece_votes[piece] = piece_votes.get(piece, 0) + 1

            # Resolve the piece for this square.
            # When FenHistory is attached and the vote is close (margin <= 1),
            # the last confirmed position breaks the tie — e.g. a K/Q split
            # resolves to whichever was confirmed there last move.
            if self._fen_history is not None:
                resolved = self._fen_history.resolve_square(sq, piece_votes, self.required)
            else:
                best_piece = max(piece_votes, key=piece_votes.get)
                best_count = piece_votes[best_piece]
                resolved = best_piece if (best_piece is not None and best_count >= self.required) else None

            if resolved is not None:
                consensus[sq] = resolved

        placement = self._square_dict_to_fen(consensus)
        return placement + " w KQkq - 0 1"

    @staticmethod
    def _fen_to_square_dict(fen):
        """Parse a FEN string into {square_index: piece_char}. Empty squares are absent."""
        if not fen:
            return {}
        placement = fen.split()[0]
        squares = {}
        rank, file = 7, 0
        for ch in placement:
            if ch == '/':
                rank -= 1
                file = 0
            elif ch.isdigit():
                file += int(ch)
            else:
                squares[rank * 8 + file] = ch
                file += 1
        return squares

    @staticmethod
    def _square_dict_to_fen(squares):
        """Reconstruct a FEN piece-placement string from {square_index: piece_char}."""
        ranks = []
        for rank in range(7, -1, -1):
            empty = 0
            rank_str = ""
            for file in range(8):
                sq = rank * 8 + file
                if sq in squares:
                    if empty:
                        rank_str += str(empty)
                        empty = 0
                    rank_str += squares[sq]
                else:
                    empty += 1
            if empty:
                rank_str += str(empty)
            ranks.append(rank_str)
        return "/".join(ranks)

    # Return the most recent confirmed stable FEN
    def get_stable(self):
        return self._last_stable
    
    # Clear the buffer and reset state. This is called at game start and end.
    def reset(self):
        self._buffer.clear()
        self._last_stable = None
        self._consecutive = 0
        self._hand_present = False
        self._recovery_count = 0
        self._candidate_fen = None
        self._candidate_first_seen = None
        logger.debug("Fen Stability Filter is reset.")

    # Check if the given FEN or current buffer content is stable
    def is_stable(self, fen=None):

        if fen is None:
            return self._last_stable is not None
        return self._last_stable == fen
    
    # Return a copy of the current bufffer for debugging
    def buffer_contents(self):
        return list(self._buffer)
    
    def __repr__(self):
        elapsed = (
            f"{time.time() - self._candidate_first_seen:.2f}s"
            if self._candidate_first_seen else "n/a"
        )
        return (
            f"FenStabilityFilter(window={self.window}, required={self.required}, "
            f"mode={self.mode!r}, min_stable={self.min_stable_seconds}s, "
            f"conf_threshold={self.confidence_threshold}, "
            f"recovery_frames={self.recovery_frames}, "
            f"hand_present={self._hand_present}, recovery_count={self._recovery_count}, "
            f"consecutive={self._consecutive}, candidate_dwell={elapsed}, "
            f"stable={'yes' if self._last_stable else 'no'})"
        )