#!/usr/bin/env python3
"""
Organize captured tiles into the training dataset using FEN notation.

Takes a capture session (folder of a1.jpg...h8.jpg) and a FEN string,
copies each tile to the correct class folder. Uses Windows-safe folder
names (p_b, n_b, etc.) to avoid case-insensitive filesystem collision.

Usage:
  cd Backend/vision_module
  python data/chess_dataset/tools/organize_captured_tiles.py <capture_id> <FEN> [--no-empty]

Example:
  python data/chess_dataset/tools/organize_captured_tiles.py 20250212_143022 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

FEN format: piece placement only (no game state). Use standard FEN:
  - Uppercase = white (P,N,B,R,Q,K)
  - Lowercase = black (p,n,b,r,q,k)
  - Numbers = consecutive empty squares
  - / = row separator
  - Rank 8 first (top of board), Rank 1 last (bottom)
"""

import argparse
import shutil
import sys
from pathlib import Path

# Add vision src for class_folders import
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "src"))
from vision.piece_classifier.class_folders import FEN_TO_FOLDER, FOLDER_NAMES

CAPTURE_DIR = Path(__file__).resolve().parents[1] / "capture_for_labeling"
SQUARE_DATASET = Path(__file__).resolve().parents[1] / "square_dataset"
FILES = "abcdefgh"
RANKS = "87654321"


def parse_fen_to_piece_map(fen: str) -> dict:
    """
    Parse FEN piece placement (first part, no game state) into square -> piece map.
    """
    piece_map = {}
    rows = fen.split("/")
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


def main():
    parser = argparse.ArgumentParser(
        description="Organize captured tiles into training dataset using FEN"
    )
    parser.add_argument("capture_id", help="Timestamp folder name (e.g. 20250212_143022)")
    parser.add_argument("fen", help="FEN piece placement (e.g. rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR)")
    parser.add_argument("--target", default=str(SQUARE_DATASET / "train"),
                        help="Target dir (train or val)")
    parser.add_argument("--prefix", default="cap_", help="Filename prefix")
    parser.add_argument("--no-empty", action="store_true",
                        help="Skip empty squares (only copy piece tiles)")
    args = parser.parse_args()

    src_dir = CAPTURE_DIR / args.capture_id
    if not src_dir.exists():
        print(f"Error: Capture folder not found: {src_dir}")
        return 1

    try:
        piece_map = parse_fen_to_piece_map(args.fen.strip().split()[0])
    except Exception as e:
        print(f"Error parsing FEN: {e}")
        return 1

    target = Path(args.target)
    for folder in FOLDER_NAMES:
        (target / folder).mkdir(parents=True, exist_ok=True)

    count = 0
    for square, piece in piece_map.items():
        if args.no_empty and piece == "empty":
            continue
        src_file = src_dir / f"{square}.jpg"
        if not src_file.exists():
            print(f"Warning: {square}.jpg not found in {src_dir}")
            continue
        folder = FEN_TO_FOLDER[piece] if piece != "empty" else "empty"
        dest_name = f"{args.prefix}{args.capture_id}_{square}.jpg"
        dest_file = target / folder / dest_name
        shutil.copy2(src_file, dest_file)
        count += 1

    print(f"Organized {count} tiles into {target}")
    print("Run train_transfer_learning.py to train on the dataset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
