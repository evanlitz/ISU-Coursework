#!/usr/bin/env python3
"""
Load one square-dataset training image and stitch the original plus N random
augmentations (same pipeline as train_transfer_learning.get_train_transforms).

Usage (from vision_module):
  python data/chess_dataset/tools/visualize_train_augmentations.py
  python data/chess_dataset/tools/visualize_train_augmentations.py --image path/to/tile.jpg
  python data/chess_dataset/tools/visualize_train_augmentations.py --variations 5 --out aug_preview.png
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from train_transfer_learning import DS_DIR, get_train_augment_pil_transforms


def _pick_sample_image(data_dir: Path) -> Path:
    train = data_dir / "train"
    if not train.is_dir():
        raise FileNotFoundError(f"Missing {train} — use --image or build square_dataset/train/")
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    files = [p for p in train.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    if not files:
        raise FileNotFoundError(f"No images under {train}")
    return random.choice(files)


def _default_out_path() -> Path:
    here = Path(__file__).resolve().parent
    return here / "train_augment_preview.png"


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview train augmentations on one tile.")
    parser.add_argument("--data", type=str, default=str(DS_DIR / "square_dataset"))
    parser.add_argument("--image", type=str, default="", help="PIL-readable image path (default: random from train/)")
    parser.add_argument("--variations", type=int, default=5, help="Number of augmented panels (default: 5)")
    parser.add_argument("--tile-size", type=int, default=128)
    parser.add_argument("--no-strong-lighting", action="store_true")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible crops/colors")
    parser.add_argument("--out", type=str, default="", help="Output PNG path")
    parser.add_argument("--gap", type=int, default=4, help="Pixels between panels")
    args = parser.parse_args()

    data_dir = Path(args.data)
    if args.seed is not None:
        random.seed(args.seed)

    src = Path(args.image) if args.image else _pick_sample_image(data_dir)
    if not src.is_file():
        raise FileNotFoundError(src)

    pil_aug = get_train_augment_pil_transforms(
        args.tile_size, strong_lighting=not args.no_strong_lighting
    )
    base = Image.open(src).convert("RGB")

    # Match training: augment from full image (ImageFolder -> same pipeline).
    panels: list[tuple[str, Image.Image]] = [("original", base)]
    for i in range(args.variations):
        panels.append((f"aug {i + 1}", pil_aug(base)))

    gap = max(0, args.gap)
    tw, th = args.tile_size, args.tile_size
    label_h = 22
    n = len(panels)
    total_w = n * tw + (n - 1) * gap
    total_h = th + label_h
    canvas = Image.new("RGB", (total_w, total_h), (32, 32, 32))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()

    x = 0
    for label, im in panels:
        im = im.resize((tw, th), Image.Resampling.BILINEAR)
        canvas.paste(im, (x, 0))
        draw.text((x + 4, th + 4), label, fill=(220, 220, 220), font=font)
        x += tw + gap

    out = Path(args.out) if args.out else _default_out_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(f"Saved {n} panels ({panels[0][0]} + {args.variations} variations) -> {out}")
    print(f"Source: {src}")


if __name__ == "__main__":
    main()
