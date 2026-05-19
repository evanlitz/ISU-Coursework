import chess
import logging
from config import STARTING_FEN, VISION_SYNC_REQUIRE_SEMANTICS

logger = logging.getLogger(__name__)

# Wrapper around chess.board that tracks the game current position and methods for engine to use
# Tracking FEN and move history -- might need it for position validation from vision glitches. Either way there is
# not much latency doing it
class BoardState:
    # Constructor
    def __init__(self, fen=None, opponent_color="white"):
        self.board = chess.Board(fen or STARTING_FEN)
        self.move_history = []
        self.fen_history = []
        self.opponent_color = opponent_color
        self.robot_color = "black" if opponent_color== "white" else "white"
        self.last_known_turn = None

# Update the board with the fen from vision. This is where vision validation will need to be implemented.
    def update_from_fen(self, fen):
        try:
            self.board = chess.Board(fen)   # Update board
            self.fen_history.append(fen)    # Update the fen history
            return True
        except ValueError:
            return False

    def try_sync_from_vision_after_opponent_move(self, vision_fen: str) -> bool:
        """When no legal move explains the new vision FEN, optionally adopt vision placement
        with side-to-move set to the robot so the game can continue."""
        from fen_utils import validate_fen_structure, validate_fen_semantics

        ok_struct, err = validate_fen_structure(vision_fen)
        if not ok_struct:
            logger.warning(f"Vision sync: invalid structure ({err})")
            return False

        parts = vision_fen.split()
        placement = parts[0]
        hm = parts[4] if len(parts) > 4 else "0"
        fm = parts[5] if len(parts) > 5 else "1"
        robot_letter = "w" if self.robot_color == "white" else "b"
        # Castling / EP unknown from vision; cleared so python-chess accepts most positions.
        candidate = f"{placement} {robot_letter} - - {hm} {fm}"

        sem_ok, sem_err = validate_fen_semantics(candidate)
        if not sem_ok:
            if VISION_SYNC_REQUIRE_SEMANTICS:
                logger.warning(f"Vision sync: semantics rejected ({sem_err})")
                return False
            logger.warning(f"Vision sync: semantics failed but trying anyway ({sem_err})")

        if self.update_from_fen(candidate):
            self.move_history.append("vision_sync")
            logger.warning("Board synced from vision (no UCI match); robot to move")
            return True
        return False

    # Get the fen from board
    def get_fen(self):
        return self.board.fen()
    
    # Get the turn, either white or black
    def get_turn(self):
        return "white" if self.board.turn == chess.WHITE else "black"
    
    # Returns true false based on opponent turn
    def is_opponent_turn(self):
        return self.get_turn() == self.opponent_color

    # Return true false based on robot turn check
    def is_robot_turn(self):
        return self.get_turn() == self.robot_color

    def _find_opponent_move_matching_vision(self, vision_placement):
        """Return the opponent's legal move that produces the vision position, or None."""
        from fen_utils import get_piece_placement, placements_match_with_vision_tolerance
        vision_pieces = get_piece_placement(vision_placement + " w KQkq - 0 1")
        for move in self.board.legal_moves:
            try:
                test_board = self.board.copy()
                test_board.push(move)
                engine_placement = test_board.fen().split()[0]
                engine_pieces = get_piece_placement(engine_placement + " w KQkq - 0 1")
                if placements_match_with_vision_tolerance(vision_pieces, engine_pieces):
                    return move.uci()
            except (ValueError, TypeError):
                continue
        return None

    def detect_turn_change(self, new_fen):
        from fen_utils import compare_positions, get_piece_placement

        old_turn = self.get_turn()

        # Vision can't tell us whose turn it is — the padded FEN always says "w".
        # Instead, detect a move by comparing piece placements before and after.
        diff = compare_positions(self.get_fen(), new_fen)
        pieces_changed = (
            len(diff["removed"]) > 0 or
            len(diff["added"]) > 0 or
            len(diff["changed"]) > 0
        )

        # Only treat as opponent move if vision position is reachable by a legal move.
        # This filters vision noise (e.g. K/Q misclassification) that would otherwise
        # trigger a false "human moved" when the board hasn't changed.
        opponent_just_moved = False
        matched_move = None
        if pieces_changed and old_turn == self.opponent_color:
            vision_placement = new_fen.split()[0]
            current_placement = self.get_fen().split()[0]
            from fen_utils import get_piece_placement, placements_match_with_vision_tolerance
            vision_pieces = get_piece_placement(vision_placement + " w KQkq - 0 1")
            current_pieces = get_piece_placement(current_placement + " w KQkq - 0 1")
            # If vision matches current position, opponent hasn't moved (e.g. robot just played, vision lags)
            if placements_match_with_vision_tolerance(vision_pieces, current_pieces):
                opponent_just_moved = False
            else:
                matched_move = self._find_opponent_move_matching_vision(vision_placement)

                # Fallback: if no legal move matches the vision placement exactly,
                # use diff-based detection (looks at which squares gained/lost pieces,
                # ignoring piece type misclassification from bad lighting).
                if matched_move is None:
                    from move_detector import MoveDetector
                    candidate = MoveDetector().detect_move(self.get_fen(), new_fen)
                    if candidate:
                        try:
                            if chess.Move.from_uci(candidate) in self.board.legal_moves:
                                matched_move = candidate
                                logger.warning(f"Vision placement mismatch — diff-based fallback accepted: {matched_move}")
                        except Exception:
                            pass

                opponent_just_moved = matched_move is not None

        new_turn = ("black" if old_turn == "white" else "white") if pieces_changed else old_turn

        return {
            "turn_changed": pieces_changed,
            "previous_turn": old_turn,
            "current_turn": new_turn,
            "opponent_just_moved": opponent_just_moved,
            "robot_should_move": opponent_just_moved,
            "matched_move": matched_move,
        }

    # Return the legal moves found through the uci function from chess library
    def get_legal_moves(self):
        return [move.uci() for move in self.board.legal_moves]
    
    # Checks for legality before pushing the move to the board and addiding the move to the move history.
    def push_move(self, uci_move):
        move = chess.Move.from_uci(uci_move)
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(uci_move)
            return True
        return False
    
    # Checks if the game is over using the chess library is game over funciton
    def is_game_over(self):
        return self.board.is_game_over()
    
    # Returns the result of the game if it is over, otherwise returns *
    def get_result(self):
        if self.board.is_game_over():
            return self.board.result()
        return "*"
    
    # Look up squares by parsing the board object.
    def piece_at(self, square_name):
        square = chess.parse_square(square_name)
        return self.board.piece_at(square)
    
    # Reset the game/board when user prompts to or when game is over. 
    def reset(self, fen=None):
        self.board = chess.Board(fen or STARTING_FEN)
        self.move_history = []
        self.fen_history = []

    