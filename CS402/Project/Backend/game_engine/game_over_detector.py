import chess
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import logging



# Class that tracks the reason of why chess game has ended. Probably the least necesscary thing I have made so far, but alas this needs to be tracked and displayed when a game ends
class GameEndReason(Enum):
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    FIFTY_MOVE_RULE = "fifty_move_rule"     # Tying rule where after 50 moves, draw can be taken when no piece is captured and no pawn is pushed
    THREEFOLD_REPETITION = "threefold_repetition"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    SEVENTY_FIVE_MOVES = "seventy_five_moves"   # This is where the game MUST end if in a seventy five move span, no pawn is pushed and no piece is captured. Upper limit
    RESIGNATION = "resignation"
    DRAW_AGREEMENT = "draw_agreement"
    NOT_OVER = "not_over"


@dataclass
class GameResult:
    is_over: bool   # Tracks if game is over or still going
    reason: GameEndReason   # Why the game ended. The reason
    winner: Optional[str]   # The winner of the game
    score: str          # The score of the game, so 1-0 if white wins, 0-1 if black wins, 1/2-1/2 if there is a draw, and * if still going
    message: str        # String for logging for game result


# Game Over Detector class, how we differentiate between all of the endgame situations
class GameOverDetector:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Core function, returns the proper GameResult fields for each of the possible ways a game can end
    # Pass in the board and the logger
    def check(self, board):

        # If its a CHECKMATE, then whoever's turn is the winner and return the reason and score.
        if board.is_checkmate():
            winner = "black" if board.turn == chess.WHITE else "white"
            return GameResult(
                is_over=True,
                reason=GameEndReason.CHECKMATE,
                winner=winner,
                score="0-1" if winner == "black" else "1-0",
                message=f"Checkmate --> {winner.capitalize()} wins."
            )
        
        # Stalemate GameResult formatting
        if board.is_stalemate():
            return GameResult(
                is_over=True,
                reason=GameEndReason.STALEMATE,
                winner=None,
                score="1/2-1/2",
                message="Stalemate --> draw"
            )

        # Insufficient material GR formatting
        if board.is_insufficient_material():
            return GameResult(
                is_over=True,
                reason=GameEndReason.INSUFFICIENT_MATERIAL,
                winner=None,
                score="1/2-1/2",
                message="Draw --> insufficient material"
            )
        
        # Fivefold repetition GR formatting
        if board.is_fivefold_repetition():
            return GameResult(
                is_over = True,
                reason = GameEndReason.FIVEFOLD_REPETITION,
                winner=None,
                score="1/2-1/2",
                message="Draw --> fivefold repetition"
            )

        # 75 move GR formatting
        if board.is_seventyfive_moves():
            return GameResult(
                is_over = True,
                reason = GameEndReason.SEVENTY_FIVE_MOVES,
                winner=None,
                score="1/2-1/2",
                message="Draw --> seventy-five move rule."
            )
        
        # Threefold repetition GR formatting
        if board.can_claim_threefold_repetition():
            return GameResult(
                is_over = True,
                reason = GameEndReason.THREEFOLD_REPETITION,
                winner=None,
                score="1/2-1/2",
                message = "Draw --> threefold repetition"
            )
        
        # Insufficient material GR formatting
        if board.can_claim_fifty_moves():
            return GameResult(
                is_over=True,
                reason=GameEndReason.FIFTY_MOVE_RULE,
                winner=None,
                score="1/2-1/2",
                message="Draw --> fifty move rule"
            )

        # The game is not over GR formatting
        return GameResult(
            is_over=False,
            reason=GameEndReason.NOT_OVER,
            winner=None,
            score="*",
            message=""
        )
    
    # Use this when we want to force a resignation. For user to then start a new game. Our robot is a role model, it never gives up on its own.
    def force_resignation(self, resigning_color):
        winner = "black" if resigning_color == "white" else "white"
        return GameResult(
            is_over = True,
            reason = GameEndReason.RESIGNATION,
            winner=winner,
            score="0-1" if resigning_color == "white" else "1-0",
            message=f"{resigning_color.capitalize()} resigned. {winner.capitalize()} wins"
        )
    
    # This is a debugging method to force a draw. Robot will never ask for a draw on its own.
    def force_draw(self):
        return GameResult(
            is_over = True,
            reason = GameEndReason.DRAW_AGREEMENT,
            winner=None,
            score="1/2-1/2",
            message="Draw by agreement."
        )