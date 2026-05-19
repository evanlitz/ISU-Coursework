import time
import logging
from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class FenSnapshot:
    fen: str
    source: str            # "start" | "opponent_move" | "vision_sync"
    move: Optional[str]    # UCI move that produced this FEN; None for the start position
    timestamp: float


class FenHistory:
    """
    Tracks confirmed board positions across a game for two purposes:

    1. Per-square vote tiebreaker: when the stability filter is split between two
       piece types on a square, the last confirmed FEN breaks the tie. A piece that
       was confirmed there last move is very likely still there if the vote is close.

    2. Recovery baseline: if Stockfish rejects a position, the caller can roll back
       to last_confirmed_fen() rather than accepting a bad board state.

    Two-tier model
    --------------
    _confirmed  deque of FenSnapshots that have been accepted into the game record.
                Each entry was produced by a legal move or the verified starting position.
    _pending    A single FenSnapshot for the position the engine is currently evaluating
                (i.e. while in ROBOT_THINKING). Promoted to confirmed on success,
                discarded on rejection.
    """

    SUSPECT_THRESHOLD = 4   # consecutive failed detections before a square is locked

    def __init__(self, maxlen: int = 30):
        self._confirmed: deque = deque(maxlen=maxlen)
        self._pending: Optional[FenSnapshot] = None
        # Square-to-piece cache for the last confirmed position — rebuilt on demand.
        self._piece_cache: Optional[Dict[int, str]] = None
        # Tracks how many consecutive failed detections each square has caused.
        # When a square's count hits SUSPECT_THRESHOLD, resolve_square() locks it
        # to the confirmed piece regardless of vote margin.
        self._suspect_squares: Dict[int, int] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def seed(self, fen: str) -> None:
        """Seed history with the starting position. Call once before the game loop begins."""
        self._confirmed.append(FenSnapshot(fen=fen, source="start", move=None, timestamp=time.time()))
        self._piece_cache = None
        logger.info(f"FenHistory seeded: {fen}")

    def set_pending(self, fen: str, source: str = "opponent_move") -> None:
        """
        Record a candidate FEN when the system transitions to ROBOT_THINKING.
        The position is not yet confirmed — Stockfish must accept it first.
        """
        self._pending = FenSnapshot(fen=fen, source=source, move=None, timestamp=time.time())
        logger.debug(f"FenHistory pending set: {fen[:40]}...")

    def confirm(self, move_uci: str) -> None:
        """
        Promote the pending snapshot to confirmed after Stockfish finds a legal move.
        Call this before transitioning to ROBOT_MOVING.
        """
        if self._pending is None:
            logger.warning("FenHistory.confirm() called but no pending snapshot exists")
            return
        self._pending.move = move_uci
        self._confirmed.append(self._pending)
        self._pending = None
        self._piece_cache = None   # invalidate square cache
        logger.debug(f"FenHistory confirmed: move={move_uci}")

    def reject(self) -> None:
        """
        Discard the pending snapshot when Stockfish rejects the position.
        last_confirmed_fen() remains the valid recovery baseline.
        """
        if self._pending:
            logger.warning(f"FenHistory: pending FEN rejected ({self._pending.fen[:40]}...)")
            self._pending = None

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def last_confirmed_fen(self) -> Optional[str]:
        """Return the most recently confirmed FEN, or None if history is empty."""
        return self._confirmed[-1].fen if self._confirmed else None

    def get_history(self) -> List[FenSnapshot]:
        """Return confirmed history oldest-first (copy)."""
        return list(self._confirmed)

    # ------------------------------------------------------------------
    # Per-square tiebreaker — primary integration point with FenStabilityFilter
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Suspect square tracking
    # ------------------------------------------------------------------

    def record_failed_detection(self, vision_fen: str) -> None:
        """
        Called each time a stable FEN from vision fails legal move matching.
        Compares vision_fen against the last confirmed position square by square:
          - Squares where confirmed has a piece but vision disagrees → count incremented.
          - Squares that agree → count reset (vision corrected itself for that square).
        Once a square's count reaches SUSPECT_THRESHOLD it is locked in resolve_square().
        """
        confirmed = self.last_confirmed_fen()
        if confirmed is None:
            return

        confirmed_map = _fen_to_index_map(confirmed)
        vision_map    = _fen_to_index_map(vision_fen)
        all_squares   = set(confirmed_map.keys()) | set(vision_map.keys())

        for sq in all_squares:
            confirmed_piece = confirmed_map.get(sq)
            vision_piece    = vision_map.get(sq)

            if confirmed_piece is not None and confirmed_piece != vision_piece:
                # Confirmed piece exists but vision disagrees — potential misclassification
                prev = self._suspect_squares.get(sq, 0)
                self._suspect_squares[sq] = prev + 1
                if self._suspect_squares[sq] == self.SUSPECT_THRESHOLD:
                    logger.warning(
                        f"Square {_index_to_algebraic(sq)} flagged SUSPECT after "
                        f"{self.SUSPECT_THRESHOLD} failed detections "
                        f"(confirmed={confirmed_piece}, vision={vision_piece})"
                    )
            else:
                # Square agrees — vision is correct here, reset its count
                if sq in self._suspect_squares:
                    del self._suspect_squares[sq]

    def is_suspect(self, square_index: int) -> bool:
        """Return True if this square has been persistently misclassified."""
        return self._suspect_squares.get(square_index, 0) >= self.SUSPECT_THRESHOLD

    def clear_suspect_squares(self) -> None:
        """
        Called after a successful move detection. A real board change means the
        confirmed reference has advanced — prior suspect flags are stale.
        """
        if self._suspect_squares:
            names = [_index_to_algebraic(s) for s in self._suspect_squares
                     if self._suspect_squares[s] >= self.SUSPECT_THRESHOLD]
            if names:
                logger.info(f"Suspect squares cleared after successful detection: {names}")
        self._suspect_squares.clear()

    # ------------------------------------------------------------------
    # Per-square tiebreaker — primary integration point with FenStabilityFilter
    # ------------------------------------------------------------------

    def resolve_square(
        self,
        square_index: int,
        piece_votes: Dict[Optional[str], int],
        required: int,
    ) -> Optional[str]:
        """
        Resolve the piece on a square given a vote dict from the stability filter.

        piece_votes  {piece_char_or_None: frame_count}
                     None means the square was seen as empty in that frame.
        required     The minimum vote count a piece must reach (VISION_STABILITY_REQUIRED).

        Decision logic
        --------------
        0. If the square is SUSPECT (repeatedly misclassified across failed detections),
             ignore votes entirely and lock to the confirmed piece.
        1. If no candidate meets `required` → return None (square uncertain, excluded).
        2. If the winning candidate leads by >= 2 votes → trust the votes outright.
        3. If the margin is 0 or 1 (close vote):
             a. Look up the last confirmed piece on this square.
             b. If the confirmed piece is one of the top-two candidates → return it.
             c. Otherwise (piece moved here since last confirmation) → trust vote plurality.
        4. If the winning piece is a pawn on rank 1 or rank 8 (chess-impossible):
             return the last confirmed piece on that square instead.
        """
        # --- Suspect override: vision has proven unreliable for this square ---
        if self.is_suspect(square_index):
            confirmed_piece = self._get_piece_at_index(square_index)
            if confirmed_piece is not None:
                logger.debug(
                    f"  sq={_index_to_algebraic(square_index)}: SUSPECT — "
                    f"overriding all votes with confirmed piece {confirmed_piece}"
                )
                return confirmed_piece

        if not piece_votes:
            return None

        # Separate piece candidates from empty votes; empty is handled below.
        candidates = {p: c for p, c in piece_votes.items() if p is not None}
        if not candidates:
            return None   # All frames saw this square as empty

        sorted_by_count = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        best_piece, best_count = sorted_by_count[0]

        if best_count < required:
            return None   # No candidate reaches the required threshold

        # Only one candidate — no ambiguity
        if len(sorted_by_count) == 1:
            return self._pawn_rank_override(square_index, best_piece)

        second_piece, second_count = sorted_by_count[1]
        margin = best_count - second_count

        # Clear majority — no need to consult history
        if margin >= 2:
            return self._pawn_rank_override(square_index, best_piece)

        # Close vote: consult the last confirmed position
        confirmed_piece = self._get_piece_at_index(square_index)

        if confirmed_piece in (best_piece, second_piece):
            logger.debug(
                f"  sq={_index_to_algebraic(square_index)}: close vote "
                f"({best_piece}:{best_count} vs {second_piece}:{second_count}), "
                f"history={confirmed_piece} → tiebreak to history"
            )
            return confirmed_piece

        # History piece is neither candidate (piece moved to/from this square).
        # The vote plurality is the best available signal.
        return self._pawn_rank_override(square_index, best_piece)

    def _pawn_rank_override(self, square_index: int, piece: Optional[str]) -> Optional[str]:
        """If `piece` is a pawn on rank 1 or rank 8 (chess-impossible), return the last
        confirmed piece on that square instead. Otherwise return `piece` unchanged.

        When no confirmed history exists (e.g. puzzle calibration before seeding), the
        illegal pawn is returned as-is so validate_fen_semantics can reject the whole FEN
        and calibration keeps waiting for a clean frame."""
        if piece is None or piece.lower() != 'p':
            return piece
        rank = square_index // 8  # 0 = rank 1, 7 = rank 8
        if rank not in (0, 7):
            return piece
        confirmed = self._get_piece_at_index(square_index)
        if confirmed is None:
            if not self._confirmed:
                # No history yet (puzzle calibration before seeding) — let the illegal
                # pawn through so validate_fen_semantics rejects the FEN and calibration
                # keeps waiting for a clean frame.
                return piece
            # History exists but square is confirmed empty (piece moved off this rank).
            # Treat the pawn vote as noise and report the square as empty.
            return None
        logger.debug(
            f"  sq={_index_to_algebraic(square_index)}: voted pawn on rank {rank + 1} "
            f"(illegal) — substituting confirmed={confirmed!r}"
        )
        return confirmed

    def delta_from_last(self, new_fen: str) -> int:
        """
        Count how many squares differ between new_fen and the last confirmed FEN.
        Returns -1 when there is no confirmed FEN to compare against.

        A legal chess move touches 2–4 squares. More than 6 differing squares
        is a strong signal of vision noise rather than a real board change.
        """
        last = self.last_confirmed_fen()
        if last is None:
            return -1
        new_map  = _fen_to_index_map(new_fen)
        last_map = _fen_to_index_map(last)
        all_indices = set(new_map.keys()) | set(last_map.keys())
        return sum(1 for idx in all_indices if new_map.get(idx) != last_map.get(idx))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_piece_at_index(self, square_index: int) -> Optional[str]:
        """Return the piece at a square index in the last confirmed position."""
        if not self._confirmed:
            return None
        if self._piece_cache is None:
            self._piece_cache = _fen_to_index_map(self._confirmed[-1].fen)
        return self._piece_cache.get(square_index)

    def __len__(self) -> int:
        return len(self._confirmed)

    def __repr__(self) -> str:
        last_move = self._confirmed[-1].move if self._confirmed else None
        return (
            f"FenHistory(confirmed={len(self._confirmed)}, "
            f"pending={'yes' if self._pending else 'no'}, "
            f"last_move={last_move!r})"
        )


# ------------------------------------------------------------------
# Module-level helpers (shared with FenStabilityFilter via import)
# ------------------------------------------------------------------

def _fen_to_index_map(fen: str) -> Dict[int, str]:
    """Parse FEN placement into {square_index: piece_char}. Empty squares absent.
    square_index = rank * 8 + file  where rank 7 = rank 8 on the board (same
    convention used by FenStabilityFilter._fen_to_square_dict)."""
    placement = fen.split()[0]
    squares: Dict[int, str] = {}
    rank, file_idx = 7, 0
    for ch in placement:
        if ch == '/':
            rank -= 1
            file_idx = 0
        elif ch.isdigit():
            file_idx += int(ch)
        else:
            squares[rank * 8 + file_idx] = ch
            file_idx += 1
    return squares


def _index_to_algebraic(index: int) -> str:
    """Convert a square index (rank*8+file) to algebraic notation e.g. 'e4'."""
    file_idx = index % 8
    rank     = index // 8
    return "abcdefgh"[file_idx] + str(rank + 1)