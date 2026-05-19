import chess
from typing import Tuple, Optional, Dict

# Assign the arguments of the FEN algorithm to the right fields, subdividing it so can be used later.
def parse_fen_fields(fen: str) -> Tuple[str, str, str, int, int]:
    fields = fen.strip().split()
   # if fields.contains
    if len(fields) != 6:
        print("FEN does not have 6 VALUES!!!!!!")
        raise ValueError(f"FEN needs 6 fields, has {len(fields)}")
    
    placement, turn, castling_rights, en_passant, halfmove, fullmove = fields
    return (placement, turn, castling_rights, en_passant, int(halfmove), int(fullmove))

# Validate the fen so that the assigned fields are correct. Otherwise return an error.
def validate_fen_structure(fen: str) -> Tuple[bool, str]:
    fields = fen.strip().split()
    if len(fields) != 6:
        return (False, f"{len(fields)} fields when it should be = 6")
    
    placement, turn, castling_rights, en_passant, halfmove, fullmove = fields

    # Split the ranks into their individual values
    ranks = placement.split("/")
    if len(ranks) != 8:
        return (False, f"{len(ranks)} ranks, need 8 ranks")
    
    # Check each of the ranks for any invalid pieces or digits, if found return an error.
    # Also sum the ranks and check if equal to 8
    valid_pieces = set("rnbqkpRNBQKP")
    valid_digits = set("12345678")

    for i, rank in enumerate(ranks):
        rank_sum = 0
        for ch in rank:
            if ch in valid_pieces:
                rank_sum += 1
            elif ch in valid_digits:
                rank_sum += int(ch)
            else:
                return (False, f"'{ch}' is invalid character in rank {i + 1}" )
        if rank_sum != 8:
            return (False, f"Rank {i+1} adds to {rank_sum}, need 8!")
    
    # Check turn value for either w or b
    if turn not in ("w", "b"):
        return (False, "Turn must be set to w or b")
    
    # Check castling_rights for anything unusual, not set to KQkq.
    if castling_rights != "-":
        valid_castling = "KQkq"
        seen = set()
        last_index = -1
        for ch in castling_rights:
            if ch not in valid_castling:
                return (False, f"Invalid castling char '{ch}'")
            if ch in seen:
                return(False, f"duped castling char '{ch}'")
            index = valid_castling.index(ch)
            if index < last_index:
                return (False, "Castling chars out of order")
            last_index = index
            seen.add(ch)

    # En_passant validity checks, can only be in ranks 3-6 inclusive
    if en_passant != "-":
        if len(en_passant) != 2:
            return (False, f"Invalid en passant '{en_passant}'")
        if en_passant[0] not in "abcdefgh":
            return (False, f"Invalid en passant file '{en_passant[0]}'")
        if en_passant[1] not in ("3", "6"):
            return (False, f"En passant rank is in invalid range, currently '{en_passant[1]}'")
    
    # Check half and full move values for irregular range.
    try:
        hm = int(halfmove)
        if hm < 0:
            return (False, "Halfmove clock is negative")
    except ValueError:
        return (False, f"halfmove clock '{halfmove}' is not an integer")
    
    try:
        fm = int(fullmove)
        if fm < 1:
            return (False, "Fullmove number must be bigger than one")
    except ValueError:
        return (False, f"Hm clock '{halfmove}' is not an int")
    
    return (True, "OK")

def validate_fen_semantics(fen: str) -> Tuple[bool, str]:
    is_valid, error = validate_fen_structure(fen)
    if not is_valid:
        return (False, error)
    
    placement = fen.split()[0]
    castling_rights = fen.split()[2]

    white_kings = placement.count("K")
    black_kings = placement.count("k")

    if white_kings != 1:
        return (False, f"{white_kings} total white kings, when it should be 1")
    if black_kings != 1:
        return (False, f"{black_kings} total black kings, when it should be 1")
    


    ranks = placement.split("/")
    rank_8 = ranks[0]
    rank_1 = ranks[7]

    # Check if pawns on outer ranks which should not be possible. But what is the promotion logic?
    # PROMOTION MIGHT CAUSE ERRORS
    if "p" in rank_8 or "P" in rank_8:
        return (False, "Pawns cannot be on rank 8")
    if "p" in rank_1 or "P" in rank_1:
        return (False, "Pawns cannot be on rank 1")
    
    white_count = sum(1 for ch in placement if ch.isupper())
    black_count = sum(1 for ch in placement if ch.islower())
    if white_count > 16:
        return (False, f"White has {white_count} pieces and that is more than 16")
    if black_count > 16:
        return (False, f"Black has {black_count} pieces and is more than 16")
    
    white_pawns = placement.count("P")
    black_pawns = placement.count("p")
    if white_pawns > 8:
        return (False, f"White has {white_pawns} pawns and is more than 8")
    if black_pawns > 8:
        return (False, f"Black has {black_pawns} pawns and is more than 8")
    
    pieces = get_piece_placement(fen)

    if "K" in castling_rights and (pieces.get("e1") != "K" or pieces.get("h1") != "R"):
        return (False, f"Kingside castling but it is inelgible. (K)")
    if "Q" in castling_rights and (pieces.get("e1") != "K" or pieces.get("a1") != "R"):
        return (False, "Queenside castling but not elgible (Q)")
    if "k" in castling_rights and (pieces.get("e8") != "k" or pieces.get("h8") != "r"):
        return (False, "Kingside castling but not eligible (k)")
    if "q" in castling_rights and (pieces.get("e8") != "k" or pieces.get("a8") != "r"):
        return (False, "Queenside castling but not elgible (q)")
    
    return (True, "OK")

def get_turn_from_fen(fen: str) -> str :
    fields = fen.strip().split()
    return "white" if fields[1] == "w" else "black"

def get_piece_placement(fen: str) -> Dict[str, str]:
    placement = fen.strip().split()[0]
    ranks = placement.split("/")
    pieces = {}

    for rank_idx, rank in enumerate(ranks):
        file_idx = 0
        board_rank = 8 - rank_idx
        for ch in rank :
            if ch.isdigit():
                file_idx += int(ch)
            else :
                file_letter = "abcdefgh"[file_idx]
                square = f"{file_letter}{board_rank}"
                pieces[square] = ch
                file_idx += 1

    return pieces

def compare_positions(fen1: str, fen2: str) -> Dict:
    pieces1 = get_piece_placement(fen1)
    pieces2 = get_piece_placement(fen2)

    all_squares = set(list(pieces1.keys()) + list(pieces2.keys()))

    added = {}
    removed = {}
    changed = {}
    unchanged = 0

    for square in all_squares:
        p1 = pieces1.get(square)
        p2 = pieces2.get(square)

        if p1 == p2:
            unchanged += 1
        elif p1 is None and p2 is not None:
            added[square] = p2
        elif p1 is not None and p2 is None:
            removed[square] = p1
        else :
            changed[square] = {"from": p1, "to": p2}

    all_board_squares = {f"{f}{r}" for f in "abcdefgh" for r in range(1, 9)}
    empty_both = all_board_squares - set(pieces1.keys()) - set(pieces2.keys())
    unchanged += len(empty_both)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged_count": unchanged,
    }


def placements_match_with_vision_tolerance(pieces1: dict, pieces2: dict) -> bool:
    """Match placements, allowing swaps (common vision confusion e.g. K/Q, N/B).
    Does NOT treat piece moves (e.g. e7->e5) as matches — only true swaps where
    both squares have pieces in both placements."""
    if pieces1 == pieces2:
        return True
    differing = [(sq, pieces1.get(sq), pieces2.get(sq)) for sq in set(pieces1.keys()) | set(pieces2.keys())
                 if pieces1.get(sq) != pieces2.get(sq)]
    if len(differing) == 0:
        return True
    # Check if all differences form swap pairs (A on s1, B on s2 -> B on s1, A on s2)
    # A MOVE (piece from sq A to sq B) has (A, piece, None) and (B, None, piece) — reject those.
    used = set()
    for i, (s1, p1a, p1b) in enumerate(differing):
        if i in used:
            continue
        if p1a is None or p1b is None:
            return False  # Move or structural change, not a swap
        for j, (s2, p2a, p2b) in enumerate(differing[i + 1:], i + 1):
            if j in used:
                continue
            if p2a is None or p2b is None:
                continue  # Skip, try another pair
            if p1a == p2b and p2a == p1b:
                used.add(i)
                used.add(j)
                break
        else:
            return False  # No matching swap for this difference
    return True