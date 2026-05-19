"""
Verify FEN against detected board and save misclassified tile images to the training set.

Compares expected (ground truth) FEN with classifier output. For each square where
detected != expected, extracts the tile image and saves it to the correct class folder,
so it becomes training data for the true label.

Can be used from run.py (v key) or standalone.
"""

import sys
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

# vision_module root
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "src"))

from vision.piece_classifier.class_folders import FEN_TO_FOLDER, FOLDER_NAMES
from vision.piece_classifier.board_splitter import split_board_into_tiles, square_to_row_col

FILES = "abcdefgh"
RANKS = "87654321"
SQUARE_DATASET = Path(__file__).resolve().parents[1] / "square_dataset"
TRAIN_DIR = SQUARE_DATASET / "train"
VAL_DIR = SQUARE_DATASET / "val"


def parse_fen_to_piece_map(fen: str) -> dict:
    """Parse FEN piece placement into square -> piece map. Raises on invalid."""
    piece_map = {}
    # Use first part only (piece placement)
    fen_part = fen.strip().split()[0] if fen else ""
    rows = fen_part.split("/")
    if len(rows) != 8:
        raise ValueError(f"FEN must have 8 rows, got {len(rows)}")

    for rank_idx, row in enumerate(rows):
        rank = RANKS[rank_idx]
        col_idx = 0
        for char in row:
            if char.isdigit():
                n = int(char)
                for _ in range(n):
                    file_char = FILES[col_idx]
                    piece_map[f"{file_char}{rank}"] = "empty"
                    col_idx += 1
            elif char in "PRNBQKprnbqk":
                file_char = FILES[col_idx]
                piece_map[f"{file_char}{rank}"] = char
                col_idx += 1
            else:
                raise ValueError(f"Invalid FEN character: {char}")
        if col_idx != 8:
            raise ValueError(f"Row {rank} has {col_idx} squares, expected 8")
    return piece_map


def validate_fen(fen_str: str) -> Tuple[bool, Optional[dict], str]:
    """
    Validate FEN accounts for all 64 squares.
    Returns (valid, piece_map, message).
    """
    if not fen_str or not fen_str.strip():
        return False, None, "FEN is empty"
    try:
        piece_map = parse_fen_to_piece_map(fen_str)
        if len(piece_map) != 64:
            return False, None, f"FEN must describe 64 squares, got {len(piece_map)}"
        return True, piece_map, "Valid"
    except Exception as e:
        return False, None, str(e)


def verify_and_save_misclassified(
    warped_board,
    detected_piece_map: dict,
    expected_fen_str: str,
    board_top_margin: int = 225,
    board_side_margin: int = 35,
    top_overlap_px: int = 60,
    tile_size: int = 128,
    target_dir: Optional[Path] = None,
    board_orientation: int = 0,
    tile_scale: float = 0.5,
) -> Tuple[bool, str, int]:
    """
    Compare expected FEN with detected; save misclassified tile images to training set.

    Args:
        warped_board: Bird's-eye view image
        detected_piece_map: {square: piece} from classifier (empty squares omitted)
        expected_fen_str: Ground truth FEN
        board_top_margin, board_side_margin, top_overlap_px: Board split params
        tile_size: Output tile size
        target_dir: Where to save (default: square_dataset/train)

    Returns:
        (success, message, count of tiles saved)
    """
    import cv2

    valid, expected_map, msg = validate_fen(expected_fen_str)
    if not valid:
        return False, f"Invalid FEN: {msg}", 0

    target = target_dir or TRAIN_DIR
    for folder in FOLDER_NAMES:
        (target / folder).mkdir(parents=True, exist_ok=True)

    tiles = split_board_into_tiles(
        warped_board,
        top_overlap_px=top_overlap_px,
        tile_size=tile_size,
        board_top_margin=board_top_margin,
        board_side_margin=board_side_margin,
        tile_scale=tile_scale,
    )
    # tiles are in order (row, col); use orientation to map square -> tile
    def get_tile_for_square(sq: str):
        row, col = square_to_row_col(sq, board_orientation)
        idx = row * 8 + col
        return tiles[idx] if 0 <= idx < 64 else None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    count = 0
    for square, expected_piece in expected_map.items():
        detected_piece = detected_piece_map.get(square, "empty")
        if detected_piece != expected_piece:
            tile = get_tile_for_square(square)
            if tile is None:
                continue
            folder = FEN_TO_FOLDER[expected_piece]
            dest_name = f"verify_{timestamp}_{square}.jpg"
            dest_path = target / folder / dest_name
            cv2.imwrite(str(dest_path), tile.image)
            count += 1

    return True, f"Saved {count} misclassified tiles to {target}", count


def sort_all_tiles(
    warped_board,
    expected_fen_str: str,
    board_top_margin: int = 225,
    board_side_margin: int = 35,
    top_overlap_px: int = 60,
    tile_size: int = 128,
    target_dir: Optional[Path] = None,
    board_orientation: int = 0,
    include_empty: bool = True,
    tile_scale: float = 0.5,
) -> Tuple[bool, str, int]:
    """
    Save all tile images into class folders based on expected FEN.

    Unlike verify_and_save_misclassified, this saves every square regardless of
    whether it was misclassified. Use for building training data from known positions.

    Args:
        warped_board: Bird's-eye view image
        expected_fen_str: Ground truth FEN
        include_empty: If True, save empty squares too; if False, skip them
        (other args same as verify_and_save_misclassified)

    Returns:
        (success, message, count of tiles saved)
    """
    import cv2

    valid, expected_map, msg = validate_fen(expected_fen_str)
    if not valid:
        return False, f"Invalid FEN: {msg}", 0

    target = target_dir or TRAIN_DIR
    for folder in FOLDER_NAMES:
        (target / folder).mkdir(parents=True, exist_ok=True)

    tiles = split_board_into_tiles(
        warped_board,
        top_overlap_px=top_overlap_px,
        tile_size=tile_size,
        board_top_margin=board_top_margin,
        board_side_margin=board_side_margin,
        tile_scale=tile_scale,
    )
    def get_tile_for_square(sq: str):
        row, col = square_to_row_col(sq, board_orientation)
        idx = row * 8 + col
        return tiles[idx] if 0 <= idx < 64 else None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    count = 0
    for square, expected_piece in expected_map.items():
        if not include_empty and expected_piece == "empty":
            continue
        tile = get_tile_for_square(square)
        if tile is None:
            continue
        folder = FEN_TO_FOLDER[expected_piece]
        dest_name = f"sort_{timestamp}_{square}.jpg"
        dest_path = target / folder / dest_name
        cv2.imwrite(str(dest_path), tile.image)
        count += 1

    empty_status = "including" if include_empty else "excluding"
    return True, f"Saved {count} tiles ({empty_status} empty) to {target}", count
