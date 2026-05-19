import chess
from dataclasses import dataclass
from typing import Optional
import logging


# Data class for move info needed for game logic and robot execution
@dataclass
class MoveInfo:
    uci: str                                # Move in UCI format (e.g. "e2e4")
    from_square: str                        # Where the robot picks up the piece
    to_square: str                          # Where the robot places the piece
    piece: str                              # Moving piece in FEN notation (e.g. "P" = white pawn)
    special: Optional[str] = None          # "en_passant" | "castle_wk" | "castle_bk" | "castle_wq" | "castle_bq" | None
    captured_piece: Optional[str] = None   # Piece being captured (None if no capture)
    promotion_piece: Optional[str] = None  # Piece to promote to (None if not a promotion)

class MoveValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_move(self, fen, uci_move):
        # Build the board from the FEN, if the FEN is a failure then return Value Error
        # Note if the vision module is spotty here, then may need to adjust this logic. Currently give it no leeway.
        try:
            board = chess.Board(fen)
        except ValueError:
            return (False, "~~~~~~~~~~Invalid FEN~~~~~~~~~~~~~")
            
        # Parse the UCI string here
        # So move like "e2e4" becomes a chess.Move object. If an illegal move input is entered here, then it catches it
        try:
            move = chess.Move.from_uci(uci_move)
        except ValueError:
            return (False, "Invalid UCI format")
            
        # Check if the parsed move is in the board's legal moves. python-chess computes all legal moves considering checks, pins, and everything
        if move not in board.legal_moves:
            # King is in check and illegal move was made not considering itSS
            if board.is_check():
                return (False, "Illegal move: king is in check and must either move, block the check, or capture the checking piece.")
            # Illegal move
            return (False, f"Illegal move: {uci_move} is not legal in this position")
            # Legal move return
        
        return (True, "Legal move")
        

    def classify_move(self, fen, uci_move):
        # Parse the FEN and move, bail if either is invalid
        try:
            board = chess.Board(fen)
            move = chess.Move.from_uci(uci_move)
        
        except ValueError:
            return None
        
        # Check legality of the mobe by using the board's current legal moves
        if move not in board.legal_moves:
            return None
        
        # This converts the python-chess library's internal square # to the actual name like e2
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)
        # Returns the piece object on square
        piece = board.piece_at(move.from_square)
        # This gives the correct casing and letter type of the piece
        piece_symbol = piece.symbol() if piece else "?"

        special = None
        captured_piece = None
        promotion_piece = None

        if board.is_castling(move):
            if move.to_square in (chess.G1, chess.G8):
                special = "castle_wk" if move.to_square == chess.G1 else "castle_bk"
            else:
                special = "castle_wq" if move.to_square == chess.C1 else "castle_bq"

        elif board.is_en_passant(move):
            special = "en_passant"
            captured_piece = "p" if board.turn == chess.WHITE else "P"

        # Promotion check !!!!!! DEF NEED TO CHANGE LATER !!!!!!!!
        # Move.promotion is only not None for promoting moves
        # Robot needs to remove the pawn, then place a different piece on the destination
        elif move.promotion is not None:
            promotion_piece = chess.piece_symbol(move.promotion).lower()
            if board.piece_at(move.to_square) is not None:
                captured_piece = board.piece_at(move.to_square).symbol()

        elif board.is_capture(move):
            captured_piece = board.piece_at(move.to_square).symbol()

        return MoveInfo(
            uci=uci_move,
            from_square=from_sq,
            to_square=to_sq,
            piece=piece_symbol,
            special=special,
            captured_piece=captured_piece,
            promotion_piece=promotion_piece,
        )