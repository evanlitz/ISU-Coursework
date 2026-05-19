from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time
import logging
from fen_utils import validate_fen_structure
from config import VISION_SYNC_ON_MOVE_MISMATCH

logger = logging.getLogger(__name__)


# Enum class where robot is always in one of these five states. Use enum number not string
class GameState(Enum):
    IDLE = "idle"   # Pregame state or pause state if we need one.
    WAITING_FOR_OPPONENT = "waiting_for_opponent"   # Waiting for the other robot to move, so do nothing besides wait until move detected
    ROBOT_THINKING = "robot_thinking"   # Vision module --> Engine calculating a move --> Receive move from engine
    ROBOT_MOVING = "robot_moving"      # Certain movements are programmed based on the type of move and where to move from and place, and if capture/castle/etc
    GAME_OVER = "game_over"         # Game ended (checkmate/draw/etc.); engine idles until user stops the process


@dataclass
class GameInfo:
    state: GameState
    current_fen: str
    turn: str
    move_number: int
    last_move: Optional[str] = None
    pending_robot_move: Optional[str] = None
    evaluation: Optional[dict] = None
    is_check: bool = False
    game_result: Optional[str] = None
    message: str = ""

class GameStateMachine:

    def __init__(self):
        self.state = GameState.IDLE
        self.transition_history = []

        self.valid_transitions = {
            GameState.IDLE: [GameState.WAITING_FOR_OPPONENT, GameState.ROBOT_THINKING],
            GameState.WAITING_FOR_OPPONENT: [GameState.ROBOT_THINKING, GameState.GAME_OVER, GameState.IDLE],
            GameState.ROBOT_THINKING: [GameState.ROBOT_MOVING, GameState.WAITING_FOR_OPPONENT, GameState.GAME_OVER, GameState.IDLE],
            GameState.ROBOT_MOVING: [GameState.WAITING_FOR_OPPONENT, GameState.GAME_OVER, GameState.IDLE],
            GameState.GAME_OVER: [GameState.IDLE],
        }

    # Transitioning to states, all of them happen with this function. This ensures that the system only stays in one state. 
    def transition_to(self, new_state):
        if new_state in self.valid_transitions[self.state]:
            old_state = self.state
            self.state = new_state
            self.transition_history.append({
                "from": old_state.value,
                "to": new_state.value,
                "timestamp": time.time()
            })

            logger.info(f"State: {old_state.value} -> {new_state.value}")
            return True
        
        else:
            logger.warning(f"Transition FALIED from {self.state.value} to {new_state.value}")
            return False

    def get_state(self):
        return self.state
    
    def validate_transition(self, target):
        return target in self.valid_transitions[self.state]
    
    def force_reset(self):
        logger.warning(f"Reset the game, so go from whatever state to IDLE (pregame)")
        self.state = GameState.IDLE
        self.transition_history.append({
            "from": "force_reset",
            "to": "idle",
            "timestamp": time.time()
        })

    def get_transition_history(self):
        return self.transition_history
    
class TurnManager:
    
    # Board_state is the known chess position as BoardState instance
    # State_machine refers to GameStateMachine instance
    # Last_processed_fen refers to last FEN string that has handled.
    # Consecutive_same_count is how many times in a row the same FEN has been observed. This is a band-aid solution for now.
    def __init__(self, board_state, state_machine, puzzle_mode=False):
        self.board_state = board_state
        self.state_machine = state_machine
        self.puzzle_mode = puzzle_mode
        self.last_processed_fen = None
        self.consecutive_same_count = 0

    def process_new_fen(self, fen):
        # Duplicate the check, update the consectuive FEN count if the same
        if fen == self.last_processed_fen:
            self.consecutive_same_count += 1
            return {"action": "no_change"}
        
        # Validate the FEN to see if board position is legal
        is_valid, error = validate_fen_structure(fen)
        if not is_valid:
            return {"action": "no_change"}

        # Detect a turn change between robot and opponent
        turn_info = self.board_state.detect_turn_change(fen)

        # Update the FEN tracking as a new FEN has been saved and consecutive FEN updates needs to be set to 0
        self.last_processed_fen = fen
        self.consecutive_same_count = 0

        # When turn change happens, update the board with the matched move and transition to Robot thinking
        if turn_info["turn_changed"] and turn_info["opponent_just_moved"]:
            matched_move = turn_info.get("matched_move")
            if matched_move:
                self.board_state.push_move(matched_move)
            else:
                # Fallback: reconstruct FEN from vision (may fail on invalid ep/halfmove)
                current_fields = self.board_state.get_fen().split()
                vision_placement = fen.split()[0]
                new_turn = "b" if current_fields[1] == "w" else "w"
                corrected_fen = f"{vision_placement} {new_turn} {current_fields[2]} {current_fields[3]} {current_fields[4]} {current_fields[5]}"
                self.board_state.update_from_fen(corrected_fen)
            self.state_machine.transition_to(GameState.ROBOT_THINKING)
            return {"action": "opponent_moved", "matched_move": matched_move}

        # Vision changed the board on the opponent's turn but no legal move matched (misclassification).
        # Optionally adopt vision placement so the game continues with the robot to move.
        # Puzzle mode never uses this — glitches must not skip waiting for a real human move.
        if (
            not self.puzzle_mode
            and VISION_SYNC_ON_MOVE_MISMATCH
            and turn_info["turn_changed"]
            and not turn_info["opponent_just_moved"]
            and turn_info["previous_turn"] == self.board_state.opponent_color
        ):
            if self.board_state.try_sync_from_vision_after_opponent_move(fen):
                self.state_machine.transition_to(GameState.ROBOT_THINKING)
                return {"action": "opponent_moved", "matched_move": None}

        # IF there was no turn change, then still waiting and return
        return {"action": "waiting", "turn": turn_info["current_turn"]}

    # After robot arm makes a move, this method notifies the system that robot is done and return to waiting for opponent. Transition to waiting state
    def confirm_robot_moved(self):
        if self.state_machine.get_state() == GameState.ROBOT_MOVING:
            return self.state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
        return False
    


