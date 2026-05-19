#!/usr/bin/env python3
"""
Check square_dataset structure for transfer learning training.

Validates that train/ (and optionally val/) exist with Windows-safe class folders.
Reports counts per class and suggests fixes.

Expected structure:
  square_dataset/
    train/empty/, train/P/, train/p_b/, train/N/, train/n_b/, ...
    val/empty/, val/P/, ... (optional)

Class folder names must match class_folders.FOLDER_NAMES:
  empty, P, p_b, N, n_b, B, b_b, R, r_b, Q, q_b, K, k_b

Usage:
  cd Backend/vision_module
  python data/chess_dataset/tools/check_square_dataset.py
"""

import sys
from pathlib import Path

DS_DIR = Path(__file__).resolve().parents[1]
SQUARE_DATASET = DS_DIR / "square_dataset"

# Import FOLDER_NAMES for validation
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from vision.piece_classifier.class_folders import FOLDER_NAMES

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def count_images(folder: Path) -> int:
    """Count image files in a folder."""
    if not folder.is_dir():
        return 0
    return sum(1 for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTS)


def main():
    print("Checking square_dataset structure...")
    print(f"Path: {SQUARE_DATASET}\n")

    train_dir = SQUARE_DATASET / "train"
    val_dir = SQUARE_DATASET / "val"

    if not train_dir.exists():
        print("ERROR: train/ folder not found.")
        print("Create square_dataset/train/ with class subfolders.")
        print("Use organize_captured_tiles.py or batch_organize_from_fen.py to build from captures.")
        return 1

    # Check for unexpected folders (common mistakes: p instead of p_b on Windows)
    train_folders = [d.name for d in train_dir.iterdir() if d.is_dir()]
    expected = set(FOLDER_NAMES)
    found = set(train_folders)
    unexpected = found - expected
    missing = expected - found

    if unexpected:
        print("WARNING: Unexpected folder names (may cause issues on Windows):")
        for u in sorted(unexpected):
            print(f"  - {u}")
        print("\nExpected names:", ", ".join(sorted(FOLDER_NAMES)))
        print("(Use p_b, n_b, b_b, r_b, q_b, k_b for black pieces to avoid case collision.)\n")

    train_counts = {}
    for name in FOLDER_NAMES:
        cnt = count_images(train_dir / name)
        if cnt > 0 or name in found:
            train_counts[name] = cnt
    total_train = sum(train_counts.values())

    print("Train/ class counts:")
    for name in sorted(train_counts.keys()):
        print(f"  {name}: {train_counts[name]}")
    print(f"  Total train: {total_train}")

    if val_dir.exists():
        val_counts = {}
        for name in FOLDER_NAMES:
            cnt = count_images(val_dir / name)
            if cnt > 0:
                val_counts[name] = cnt
        total_val = sum(val_counts.values())
        print(f"\nVal/ total: {total_val}")
    else:
        print("\nVal/ not found. train_transfer_learning.py will use 80/20 split from train/.")

    if total_train < 10:
        print("\nWARNING: Very few images. Consider capturing more board positions.")
        print("Use 't' in live mode to capture tiles, then organize with batch_organize_from_fen.py")

    if total_train > 0:
        print("\nReady for training. Run:")
        print("  python data/chess_dataset/tools/train_transfer_learning.py [--epochs 10]")
    else:
        print("\nNo images found. Add images to train/<class>/ folders.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
