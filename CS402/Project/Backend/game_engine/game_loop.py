import time
import logging
import json
from pathlib import Path

from config import (
    STARTING_FEN, HUMAN_COLOR,
    VISION_CONFIDENCE_MIN, VISION_RECOVERY_FRAMES,
    VISION_STABILITY_WINDOW, VISION_STABILITY_REQUIRED, VISION_POLL_INTERVAL,
    VISION_MIN_STABLE_SECONDS, VISION_STABILITY_MODE,
)
from board_state import BoardState
from game_state import GameStateMachine, GameState, TurnManager
from move_detector import MoveDetector
from move_validator import MoveValidator
from stockfish_engine import StockfishEngine
from game_over_detector import GameOverDetector
from vision_interface import VisionInterface
from robot_interface import write_move_command
from fen_utils import validate_fen_structure, validate_fen_semantics, get_piece_placement, placements_match_with_vision_tolerance
from fen_history import FenHistory

logger = logging.getLogger(__name__)

_ENGINE_DIR = Path(__file__).resolve().parent
_ROBOT_STATUS_PATH = _ENGINE_DIR.parent / "shared" / "queue" / "robot_status.json"


# Set the loop interval of the gameloop
LOOP_INTERVAL      = 0.05
# Waititme for the vision to start up
VISION_STARTUP_WAIT = 3.0
STOCKFISH_FALLBACK = True
# Puzzle: allow slow camera / stability filter to settle before defaulting
PUZZLE_CALIBRATION_TIMEOUT_S = 90.0
PUZZLE_LOCK_TIMEOUT_S = 45.0

# Simulate a game of chess through a game loop
class GameLoop:

    def __init__(
        self,
        starting_fen=None,
        human_color=None,
        puzzle_mode=False,
        to_move="auto",
    ):
        self.human_color = human_color or HUMAN_COLOR
        self.puzzle_mode = puzzle_mode
        # Puzzle: "auto" | "white" | "black" — who has the move (side to move in FEN)
        self.to_move = to_move if puzzle_mode else "auto"
        # Puzzle: position comes only from vision; ignore any CLI starting FEN.
        if puzzle_mode:
            self.starting_fen = STARTING_FEN
        else:
            self.starting_fen = starting_fen if starting_fen is not None else STARTING_FEN

        self.board_state   = BoardState(fen=self.starting_fen, opponent_color=self.human_color)
        self.state_machine = GameStateMachine()
        self.turn_manager  = TurnManager(
            self.board_state, self.state_machine, puzzle_mode=self.puzzle_mode
        )
        self.detector      = MoveDetector()
        self.validator     = MoveValidator()
        self.game_over     = GameOverDetector()
        self.stockfish     = StockfishEngine()
        self.fen_history   = FenHistory()
        self.vision        = VisionInterface(
            stability_window=VISION_STABILITY_WINDOW,
            stability_required=VISION_STABILITY_REQUIRED,
            stability_mode=VISION_STABILITY_MODE,
            confidence_min=VISION_CONFIDENCE_MIN,
            poll_interval=VISION_POLL_INTERVAL,
            recovery_frames=VISION_RECOVERY_FRAMES,
            min_stable_seconds=VISION_MIN_STABLE_SECONDS,
            fen_history=self.fen_history,
        )

        self.running    = False
        self.move_count = 0
        self.last_fen   = self.starting_fen
        self._robot_confirm_count = 0
        # Puzzle: True once we have a real placement from the camera (not default start after timeout)
        self._puzzle_board_from_camera = False

    @staticmethod
    def _is_empty_board_placement(placement: str) -> bool:
        return all(p == "8" for p in placement.split("/"))

    def _puzzle_stm_letter(self) -> str:
        if self.to_move == "auto":
            return "w" if self.human_color == "white" else "b"
        return "w" if self.to_move == "white" else "b"

    def _derive_castling_rights(self, placement: str) -> str:
        """Derive castling rights from piece positions in the FEN placement string.
        A side can castle if and only if its king and the relevant rook are still
        on their starting squares (e1/a1/h1 for white, e8/a8/h8 for black)."""
        pieces = {}
        rank, file = 7, 0
        for ch in placement:
            if ch == '/':
                rank -= 1
                file = 0
            elif ch.isdigit():
                file += int(ch)
            else:
                pieces[rank * 8 + file] = ch
                file += 1

        # Square indices: a1=0 e1=4 h1=7 / a8=56 e8=60 h8=63
        rights = ""
        if pieces.get(4) == 'K':
            if pieces.get(7) == 'R':
                rights += 'K'
            if pieces.get(0) == 'R':
                rights += 'Q'
        if pieces.get(60) == 'k':
            if pieces.get(63) == 'r':
                rights += 'k'
            if pieces.get(56) == 'r':
                rights += 'q'
        return rights if rights else "-"

    def _normalize_puzzle_fen(self, fen: str, quiet: bool = True) -> str:
        """Piece placement from vision; side to move from --to_move (or auto from human side).
        Castling rights are derived from king/rook positions rather than taken from vision,
        since vision always pads with KQkq which fails semantic validation for mid-game positions."""
        parts = fen.strip().split()
        placement = parts[0]
        stm = self._puzzle_stm_letter()
        castling = self._derive_castling_rights(placement)
        out = f"{placement} {stm} {castling} - 0 1"
        if not quiet:
            if self.to_move == "auto":
                src = f"auto (human {self.human_color} → side-to-move {stm})"
            else:
                src = f"--to_move {self.to_move}"
            logger.info(f"PUZZLE MODE: side to move {stm}, castling {castling} ({src})")
        return out

    def _apply_puzzle_starting_fen(self, fen_norm: str) -> bool:
        """Apply a normalized puzzle FEN to board state. Sets _puzzle_board_from_camera on success."""
        is_valid, _ = validate_fen_semantics(fen_norm)
        if not is_valid:
            return False
        self.starting_fen = fen_norm
        self.last_fen = fen_norm
        self.board_state = BoardState(fen=fen_norm, opponent_color=self.human_color)
        self.turn_manager = TurnManager(
            self.board_state, self.state_machine, puzzle_mode=self.puzzle_mode
        )
        self._puzzle_board_from_camera = True
        return True

    def _calibrate_from_vision(self, timeout=None):
        """Puzzle mode: block until vision gives a stable FEN, then use it as the
        starting position. Rejects empty boards and invalid stables so poll() can advance."""
        if timeout is None:
            timeout = PUZZLE_CALIBRATION_TIMEOUT_S
        logger.info("PUZZLE MODE: Waiting for vision to detect board position...")
        print("\n  [PUZZLE] Detecting board position from vision — please wait...")

        start = time.time()
        while time.time() - start < timeout:
            fen = self.vision.poll()
            if fen:
                norm = self._normalize_puzzle_fen(fen, quiet=True)
                if self._is_empty_board_placement(norm.split()[0]):
                    self.vision.mark_stable_seen_as_invalid(fen)
                    time.sleep(0.05)
                    continue
                if self._apply_puzzle_starting_fen(norm):
                    self._normalize_puzzle_fen(fen, quiet=False)
                    logger.info(f"PUZZLE MODE: Starting position locked in: {norm}")
                    print(f"  [PUZZLE] Starting position: {norm}\n")
                    return True
                self.vision.mark_stable_seen_as_invalid(fen)
            time.sleep(0.05)

        logger.warning("PUZZLE MODE: Timed out waiting for vision — falling back to default FEN")
        print("  [PUZZLE] Vision timeout — using default starting position\n")
        return False

    def _try_adopt_puzzle_board_from_stable(self, stable: str) -> bool:
        """If calibration timed out, adopt the first valid non-empty stable FEN from vision."""
        if self._puzzle_board_from_camera or not stable:
            return False
        norm = self._normalize_puzzle_fen(stable, quiet=True)
        if self._is_empty_board_placement(norm.split()[0]):
            self.vision.mark_stable_seen_as_invalid(stable)
            return False
        if not self._apply_puzzle_starting_fen(norm):
            self.vision.mark_stable_seen_as_invalid(stable)
            return False
        self.vision.confirm_move(self.board_state.get_fen())
        self._normalize_puzzle_fen(stable, quiet=False)
        logger.info(
            f"PUZZLE MODE: Adopted board from vision after calibration timeout: {self.starting_fen}"
        )
        print(f"  [PUZZLE] Board from camera (late lock): {self.starting_fen}\n")
        return True

    def _wait_for_puzzle_vision_lock_on_board(self, timeout=None):
        """After confirm_move resets the filter, wait until vision stabilizes on the physical board.
        If calibration used the default start, adopts a valid stable FEN when it appears."""
        if timeout is None:
            timeout = PUZZLE_LOCK_TIMEOUT_S
        robot_first = self.board_state.is_robot_turn()
        logger.info(
            "PUZZLE MODE: Waiting for stable vision to match physical board "
            f"({'robot' if robot_first else 'human'} moves first)..."
        )
        if robot_first:
            print("\n  [PUZZLE] Locking vision on the board before robot thinks — hold steady...")
        else:
            print("\n  [PUZZLE] Locking vision on the starting position — make no moves yet...")

        start = time.time()
        while time.time() - start < timeout:
            self.vision.poll()
            stable = self.vision.get_stable_fen()
            if stable:
                if not self._puzzle_board_from_camera:
                    self._try_adopt_puzzle_board_from_stable(stable)
                try:
                    board_placement = self.board_state.get_fen().split()[0]
                    stable_placement = stable.split()[0]
                    if self._is_empty_board_placement(stable_placement):
                        self.vision.mark_stable_seen_as_invalid(stable)
                        time.sleep(0.05)
                        continue
                    expected = get_piece_placement(
                        board_placement + " w KQkq - 0 1"
                    )
                    seen = get_piece_placement(stable_placement + " w KQkq - 0 1")
                    if placements_match_with_vision_tolerance(seen, expected):
                        if self.board_state.is_robot_turn():
                            logger.info(
                                "PUZZLE MODE: Stable vision matches board — robot may move."
                            )
                            print("  [PUZZLE] Vision locked — robot thinking.\n")
                        else:
                            logger.info(
                                "PUZZLE MODE: Stable vision matches board — waiting for your move."
                            )
                            print("  [PUZZLE] Ready — play when you are.\n")
                        return True
                except (ValueError, IndexError):
                    pass
            time.sleep(0.05)

        logger.warning(
            "PUZZLE MODE: Timed out waiting for stable vision before play — proceeding anyway"
        )
        print("  [PUZZLE] Vision lock-on timeout — proceeding anyway.\n")
        return False

    def setup(self):
        logger.info("=== Game Loop Setup ===")

        ok = self.stockfish.start()
        if not ok:
            logger.warning("Stockfish failed to start — will use fallback moves")

        self.vision.start()

        if self.puzzle_mode:
            self._calibrate_from_vision()

        # Seed the confirmed FEN so the stability filter doesn't fire immediately
        # on the starting position (puzzle or standard). Vision must see something
        # *different* from the starting position before a human move is reported.
        self.vision.confirm_move(self.starting_fen)

        # Seed FEN history with the verified starting position so the per-square
        # tiebreaker has a reference from the very first poll onward.
        self.fen_history.seed(self.starting_fen)

        # Puzzle: confirm_move resets the stability filter; wait until vision agrees with the
        # physical board (adopts camera position if calibration fell back to default).
        if self.puzzle_mode:
            self._wait_for_puzzle_vision_lock_on_board()

        if self.board_state.is_robot_turn():
            self.state_machine.transition_to(GameState.ROBOT_THINKING)
        else:
            self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)

        logger.info(f"Starting FEN: {self.starting_fen}")
        logger.info(f"Human color:  {self.human_color}")
        logger.info("Waiting for vision...")
        time.sleep(VISION_STARTUP_WAIT)
        logger.info("Ready.")

    def run(self):
        self.running = True
        logger.info("=== Game Loop Running ===")

        try:
            while self.running:
                try:
                    self._tick()
                except Exception as e:
                    logger.warning(f"Tick error (skipping): {e}", exc_info=True)
                time.sleep(LOOP_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        finally:
            self.running = False

    def shutdown(self):
        logger.info("=== Shutdown ===")
        self.stockfish.stop()
        self.vision.stop()

    def _tick(self):
        state = self.state_machine.get_state()

        if state == GameState.WAITING_FOR_OPPONENT:
            self._handle_waiting()
        elif state == GameState.ROBOT_THINKING:
            self._handle_thinking()
        elif state == GameState.ROBOT_MOVING:
            self._handle_robot_moving()
        elif state == GameState.GAME_OVER:
            # Keep vision/stockfish running until the user stops the process (no auto-exit).
            pass

    def _handle_waiting(self):
        new_fen = self.vision.poll()
        if new_fen is None:
            return

        is_valid, err = validate_fen_structure(new_fen)
        if not is_valid:
            logger.warning(f"Invalid FEN from vision: {err}")
            return

        result = self.turn_manager.process_new_fen(new_fen)

        if result["action"] == "opponent_moved":
            matched = result.get("matched_move", "")
            logger.info(f"Human move detected: {matched or 'from vision'} — robot thinking")
            self.vision.confirm_move(new_fen)
            self.last_fen = new_fen
            # Record the new board state as pending in history. It will be promoted
            # to confirmed once Stockfish accepts it, or discarded on rejection.
            self.fen_history.set_pending(self.board_state.get_fen())
            # Successful detection — any suspect square flags are now stale since
            # the confirmed reference has advanced to the new board position.
            self.fen_history.clear_suspect_squares()

        elif result["action"] == "waiting":
            # A new stable FEN was seen but no legal move matched. Record which
            # squares differ from the confirmed position so that persistently
            # misclassified squares can be identified and locked (suspect override).
            self.fen_history.record_failed_detection(new_fen)
            if self.puzzle_mode:
                self._puzzle_sync_fallback(new_fen)

    def _puzzle_sync_fallback(self, new_fen: str) -> bool:
        """Puzzle-mode fallback when both primary and diff-based move detection fail.

        If the stable vision FEN differs from the confirmed board by 2-6 squares
        (consistent with a single legal move plus at most a couple of artifacts),
        adopt vision's placement as the opponent's move. The delta gate replaces
        the noise protection that VISION_SYNC_ON_MOVE_MISMATCH's 'not puzzle_mode'
        guard was providing.

        try_sync_from_vision_after_opponent_move runs validate_fen_semantics
        internally, so semantically impossible positions are still rejected."""
        delta = self.fen_history.delta_from_last(new_fen)
        if not (2 <= delta <= 6):
            return False
        if not self.board_state.try_sync_from_vision_after_opponent_move(new_fen):
            return False
        logger.warning(
            f"Puzzle: no legal move matched (delta={delta}) — "
            f"adopted vision FEN as opponent move"
        )
        self.vision.confirm_move(new_fen)
        self.last_fen = new_fen
        self.fen_history.set_pending(self.board_state.get_fen())
        self.fen_history.clear_suspect_squares()
        self.state_machine.transition_to(GameState.ROBOT_THINKING)
        return True

    def _handle_robot_moving(self):
        """Wait for sim to signal move complete (empty queue) or vision to match expected."""
        # 1. Check robot_status.json from MuJoCo sim - authoritative when sim is running
        try:
            if _ROBOT_STATUS_PATH.exists():
                with open(_ROBOT_STATUS_PATH, "r") as f:
                    status = json.load(f)
                if status.get("move_complete", False):
                    logger.info("Sim signalled move complete — waiting for human for ten seconds")
                    time.sleep(10.0)
                    self.vision.confirm_move(self.board_state.get_fen())
                    self.last_fen = self.board_state.get_fen()
                    self._robot_confirm_count = 0
                    self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
                    return
        except (OSError, json.JSONDecodeError):
            pass

        # 2. Fallback: vision confirmation (for --no-sim or if status file missing).
        # Do not call poll() here — it runs the stable-FEN filter; mid-move frames would
        # corrupt stability and waste work while the arm is moving.
        # is_new_frame guards against counting the same camera frame twice — the game loop
        # runs at 20Hz but vision may only update at 10-15fps.
        fen, is_new_frame = self.vision.get_new_frame_for_confirm()
        if not fen or not is_new_frame:
            return
        try:
            expected_placement = self.board_state.get_fen().split()[0]
            vision_placement = fen.split()[0]
            if len(vision_placement.split("/")) != 8:
                self._robot_confirm_count = 0
                return
            expected_pieces = get_piece_placement(expected_placement + " w KQkq - 0 1")
            vision_pieces = get_piece_placement(vision_placement + " w KQkq - 0 1")
        except (ValueError, IndexError):
            self._robot_confirm_count = 0
            return
        if placements_match_with_vision_tolerance(vision_pieces, expected_pieces):
            self._robot_confirm_count += 1
            if self._robot_confirm_count >= 2:
                logger.info("Vision confirmed robot move — waiting for human for ten seconds")
                time.sleep(10.0)
                self.vision.confirm_move(self.board_state.get_fen())
                self.last_fen = self.board_state.get_fen()
                self._robot_confirm_count = 0
                self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
        else:
            self._robot_confirm_count = 0

    def _reset_robot_status(self):
        """Write move_complete: false before entering ROBOT_MOVING so a stale True
        from the previous move is never read on the first tick of the next move."""
        try:
            _ROBOT_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_ROBOT_STATUS_PATH, "w") as f:
                json.dump({"move_complete": False}, f)
        except OSError as e:
            logger.warning(f"Could not reset robot_status.json: {e}")

    def _rollback_board(self) -> None:
        """Restore board state to the last confirmed FEN when a bad position is detected.
        Ensures the internal board stays consistent with FenHistory's ground truth
        after a semantic validation failure or a Stockfish rejection."""
        fallback = self.fen_history.last_confirmed_fen()
        if fallback and fallback != self.board_state.get_fen():
            logger.warning(f"Board rolled back to last confirmed: {fallback[:40]}...")
            self.board_state.update_from_fen(fallback)

    def _handle_thinking(self):
        logger.info("Robot thinking...")
        current_fen = self.board_state.get_fen()

        ok, err = validate_fen_semantics(current_fen)
        if not ok:
            logger.error(
                f"Illegal board position before Stockfish: {err} — "
                f"rolling back to last confirmed and waiting for clean vision"
            )
            self._rollback_board()
            self.fen_history.reject()
            self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
            return

        # Check for game over before asking Stockfish (handles stalemate/checkmate
        # on the robot's turn where there are no legal moves to return).
        pre_result = self.game_over.check(self.board_state.board)
        if pre_result.is_over:
            logger.info(f"Game over (detected before robot move): {pre_result.message}")
            self.state_machine.transition_to(GameState.GAME_OVER)
            return

        best_move = self._get_stockfish_move(current_fen)
        if best_move is None:
            logger.error("No move from Stockfish — rolling back to last confirmed")
            self._rollback_board()
            self.fen_history.reject()
            self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
            return

        logger.info(f"Stockfish plays: {best_move}")

        move_info = self.validator.classify_move(current_fen, best_move)
        if move_info is None:
            logger.error(f"Could not classify move {best_move}")
            self.fen_history.reject()
            self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
            return

        move_type = move_info.special or "normal"
        logger.info(f"Move type: {move_type} | Piece: {move_info.piece}")

        write_move_command(move_info)
        logger.info(f"Sent move to robot: {best_move}")

        # The robot now has the command and may already be moving. Any exception
        # from here must NOT leave the state in ROBOT_THINKING — that would cause
        # a retry on the next tick and send a second command to the arm.
        try:
            self.board_state.push_move(best_move)
            self.move_count += 1

            result = self.game_over.check(self.board_state.board)
            if result.is_over:
                logger.info(f"Game over: {result.message}")
                self.fen_history.confirm(best_move)
                self.state_machine.transition_to(GameState.GAME_OVER)
                return

            # Promote pending to confirmed — history tiebreaker is now based on
            # the post-move board state for all subsequent vision polls.
            self.fen_history.confirm(best_move)
            self._robot_confirm_count = 0
            self._reset_robot_status()
            self.state_machine.transition_to(GameState.ROBOT_MOVING)
        except Exception:
            logger.error(
                "Exception after write_move_command — robot already has the command. "
                "Transitioning to ROBOT_MOVING to prevent retry.",
                exc_info=True,
            )
            self.fen_history.confirm(best_move)
            self._robot_confirm_count = 0
            self._reset_robot_status()
            self.state_machine.transition_to(GameState.ROBOT_MOVING)

    def _get_stockfish_move(self, fen):
        try:
            if self.stockfish.is_available():
                result = self.stockfish.get_best_move_with_info(fen)
                move = result.get("best_move")
                if move:
                    return move
        except Exception as e:
            logger.warning(f"Stockfish error: {e}")

        if STOCKFISH_FALLBACK:
            legal = self.board_state.get_legal_moves()
            if legal:
                logger.warning(f"Fallback: playing {legal[0]}")
                return legal[0]

        return None