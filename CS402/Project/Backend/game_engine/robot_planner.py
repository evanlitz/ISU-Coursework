from move_validator import MoveInfo

def build_move_command(move_info: MoveInfo) -> dict:
    return {
        "from_sq":        move_info.from_square,
        "to_sq":          move_info.to_square,
        "moved_piece":    move_info.piece,
        "captured_piece": move_info.captured_piece,
        "promotion_piece": move_info.promotion_piece,
        "special":        move_info.special,
    }


