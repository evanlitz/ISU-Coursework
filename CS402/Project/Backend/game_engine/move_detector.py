import chess
from fen_utils import get_piece_placement, compare_positions
from typing import Optional, Tuple
import logging

class MoveDetector:

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    # Build the chess.Board from the before-move FEN passed into the method
    # Then get piece placement of the after-move FEN, the target that is being matched to
    # For each legal move, copy the board, push the move on the copy, get the resulting piece placement, and if matches target fen_after the nit is the move
    # Move returned in UCI format e2e4
    # Fallback to difference method
    def detect_move(self, fen_before, fen_after):
        # Try all legal moves and see which one produces the after FEN
        try:
            board = chess.Board(fen_before)
            after_pieces = get_piece_placement(fen_after)

            for move in board.legal_moves:
                test_board = board.copy()
                # *********************************************
                # Push method is very important. 
                test_board.push(move)
                test_pieces = get_piece_placement(test_board.fen())

                if test_pieces == after_pieces:
                    return move.uci()
                
        except Exception as e:
            self.logger.warning(f"Legal move matching failed: {e}")
        
        # IF other method fails, then fall 
        # back to the detect by difference move.
        return self._detect_by_diff(fen_before, fen_after)
    
    #
    def _detect_by_diff(self, fen_before, fen_after):
        diff = compare_positions(fen_before, fen_after) # Compare positons method compares the fens before and after moves, constructs square array
        removed = diff["removed"] # Squares that had piece on it before but is empty now
        added = diff["added"]   # Squares that were empty before but now have a piece on it
        changed = diff["changed"]   # Squares where the piece type changed

        if len(removed) == 1 and len(added) == 1:
            from_sq = list(removed.keys())[0]
            to_sq = list(added.keys())[0]
            uci = from_sq + to_sq 

            removed_piece = removed[from_sq]
            added_piece = added[to_sq]
            if removed_piece.lower() == 'p' and to_sq[1] in ('1', '8'):
                uci += added_piece.lower()


            return uci
        
        # Capture handling -- attacking piece replaces the defending piece -- compare_positions sees that one square became empty (removed) and one square changed its piece (changed)
        # from represents the removed square and the to represents the changed square
        if len(removed) == 1 and len(added) == 0 and len(changed) == 1:
            from_sq = list(removed.keys())[0]
            to_sq = list(changed.keys())[0]
            return from_sq + to_sq
        
        # King and rook move in castling so the diff shows that theere were 2 removed squares and 2 added squares
        # Find which one of the squares is the king (K/k) and then return the kings move.
        if len(removed) == 2 and len(added) == 2:
            king_from = None
            king_to = None
            for sq, piece in removed.items():
                if piece.lower() == 'k':
                    king_from = sq
            for sq, piece in added.items():
                if piece.lower() == 'k':
                    king_to = sq
            if king_from is not None and king_to is not None:
                return king_from + king_to
        
        # Attacking pawn moves diagonally but captured pawn is on different sqaure. 2 removals and 1 addition.
        # Find the removed square whose file differs from the added square, whcih will then represent the pawn that moved.
        if len(removed) == 2 and len(added) == 1:
            added_sq = list(added.keys())[0]
            for sq in removed:
                if sq[0] != added_sq[0]:
                    return sq + added_sq
        
        # Return nothing if everything else fails 
        self.logger.warning(f"Could not detect the move from the diff: removed = {removed}, added = {added}, changed = {changed}")
        return None
    

    # This method takes the dectected move and double checks it with the list of legal moves available from the position
    # Caller gets a tuple with the move string and a boolean indicating legality.
    def detect_move_validated(self, fen_before, fen_after):
        move = self.detect_move(fen_before, fen_after)

        if move is None:
            return (None, False)
        
        try:
            board = chess.Board(fen_before)
            chess_move = chess.Move.from_uci(move)
            is_legal = chess_move in board.legal_moves
            return (move, is_legal)
        except Exception:
            return (move, False)
        

