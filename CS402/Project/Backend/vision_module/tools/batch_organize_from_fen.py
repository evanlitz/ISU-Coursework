#!/usr/bin/env python3
"""
Batch organize captured board positions into the training dataset.

Accepts a list of capture directory names (e.g. from capture_for_labeling/).
For each directory:
  1. Finds FEN.txt
  2. Parses the FEN to get square -> piece mapping
  3. Copies each tile (a1.jpg ... h8.jpg) into square_dataset/train/<class>/
     or square_dataset/val/<class>/ for transfer learning training

Expected structure per capture directory:
  capture_for_labeling/<capture_id>/
    FEN.txt          # FEN string (piece placement only; full FEN ok, first token used)
    a1.jpg, a2.jpg, ... h8.jpg   # 64 tile images (or .png)

Output structure (matches train_transfer_learning.py):
  square_dataset/
    train/empty/, train/P/, train/p_b/, train/N/, ... (13 classes)
  Uses Windows-safe folder names (p->p_b, n->n_b, etc.) to avoid case collision.

Usage:
  cd Backend/vision_module
  python data/chess_dataset/tools/batch_organize_from_fen.py 20260214_195556 20260214_131745
  python data/chess_dataset/tools/batch_organize_from_fen.py 20260214_*  # shell glob
  python data/chess_dataset/tools/batch_organize_from_fen.py --dirs-from file.txt

Example dirs-from file (one capture_id per line):
  20260214_195556
  20260214_131745
  20260214_131751
"""

import argparse
import random
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
TILE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def parse_fen_to_piece_map(fen: str) -> dict:
    """
    Parse FEN piece placement (first part, no game state) into square -> piece map.
    Full FEN strings are ok; only the first token (piece placement) is used.
    """
    piece_map = {}
    # Take first token only (piece placement); ignore turn, castling, etc.
    placement = fen.strip().split()[0] if fen.strip() else fen.strip()
    rows = placement.split("/")
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


def find_fen_file(capture_dir: Path) -> Path | None:
    """Find FEN.txt in the capture directory."""
    fen_path = capture_dir / "FEN.txt"
    if fen_path.exists():
        return fen_path
    return None


def find_tile_path(capture_dir: Path, square: str) -> Path | None:
    """Find tile image for square (a1..h8); supports .jpg, .jpeg, .png."""
    for ext in TILE_EXTENSIONS:
        p = capture_dir / f"{square}{ext}"
        if p.exists():
            return p
    return None


def organize_capture(
    capture_id: str,
    src_dir: Path,
    target_base: Path,
    split: str,
    prefix: str,
    val_ratio: float,
) -> tuple[int, int]:
    """
    Organize one capture directory into train/val.
    Returns (train_count, val_count).
    """
    fen_path = find_fen_file(src_dir)
    if not fen_path:
        raise FileNotFoundError(f"FEN.txt not found in {src_dir}")

    fen_text = fen_path.read_text(encoding="utf-8").strip()
    piece_map = parse_fen_to_piece_map(fen_text)

    # Determine train vs val for this capture (optional random split)
    use_val = val_ratio > 0 and random.random() < val_ratio
    target = target_base / ("val" if use_val else "train")

    for folder in FOLDER_NAMES:
        (target / folder).mkdir(parents=True, exist_ok=True)

    count = 0
    for square, piece in piece_map.items():
        if piece == "empty":
            continue  # Skip empty squares - don't add to training images
        src_file = find_tile_path(src_dir, square)
        if not src_file:
            continue
        folder = FEN_TO_FOLDER[piece]
        dest_name = f"{prefix}{capture_id}_{square}{src_file.suffix}"
        dest_file = target / folder / dest_name
        shutil.copy2(src_file, dest_file)
        count += 1

    return (0, count) if use_val else (count, 0)


def main():
    parser = argparse.ArgumentParser(
        description="Batch organize capture directories using FEN.txt into training dataset"
    )
    parser.add_argument(
        "capture_ids",
        nargs="*",
        help="Capture directory names (e.g. 20260214_195556). Omit if using --dirs-from.",
    )
    parser.add_argument(
        "--dirs-from",
        type=str,
        metavar="FILE",
        help="Read capture IDs from file (one per line). Overrides positional args if given.",
    )
    parser.add_argument(
        "--target",
        default=str(SQUARE_DATASET),
        help="Base directory for square_dataset (default: data/chess_dataset/square_dataset)",
    )
    parser.add_argument(
        "--capture-root",
        default=str(CAPTURE_DIR),
        help="Root directory for capture_for_labeling",
    )
    parser.add_argument(
        "--prefix",
        default="cap_",
        help="Filename prefix for copied tiles",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.0,
        metavar="R",
        help="Fraction of captures to put in val/ (0–1). Default 0 = all to train.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for train/val split (default 42)",
    )
    args = parser.parse_args()

    # Resolve capture IDs
    capture_ids = list(args.capture_ids)
    if args.dirs_from:
        p = Path(args.dirs_from)
        if not p.exists():
            print(f"Error: File not found: {p}")
            return 1
        capture_ids = [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]

    if not capture_ids:
        print("Error: No capture directories specified.")
        print("Usage: batch_organize_from_fen.py <capture_id> [...]")
        print("   or: batch_organize_from_fen.py --dirs-from list.txt")
        return 1

    capture_root = Path(args.capture_root)
    target_base = Path(args.target)
    random.seed(args.seed)

    total_train, total_val = 0, 0
    ok, skip, err = 0, 0, 0

    for capture_id in capture_ids:
        src_dir = capture_root / capture_id
        if not src_dir.is_dir():
            print(f"[SKIP] Not a directory: {src_dir}")
            skip += 1
            continue

        try:
            tr, va = organize_capture(
                capture_id,
                src_dir,
                target_base,
                "train",
                args.prefix,
                args.val_ratio,
            )
            total_train += tr
            total_val += va
            n = tr + va
            dest = "val" if va else "train"
            if n == 0:
                print(f"[WARN] {capture_id}: no tile images found (expected a1.jpg ... h8.jpg)")
            else:
                print(f"[OK] {capture_id}: {n} tiles -> {dest}/")
            ok += 1
        except FileNotFoundError as e:
            print(f"[SKIP] {capture_id}: {e}")
            skip += 1
        except Exception as e:
            print(f"[ERROR] {capture_id}: {e}")
            err += 1

    print()
    print(f"Summary: {ok} organized, {skip} skipped, {err} errors")
    print(f"Tiles: train={total_train}, val={total_val}")
    print(f"Output: {target_base}/train/ and {target_base}/val/")
    print("Run train_transfer_learning.py to train the transfer learning model.")

    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
