# Piece Classifier Training Guide

This document explains how to collect training data, organize it into the correct format, train the piece classifier model, and how the vision pipeline uses it.

---

## Overview

The vision system uses a **per-square classification** approach instead of object detection (YOLO). For each of the 64 chess squares, a small CNN predicts one of 13 classes:

| Class                        | Description                                            |
| ---------------------------- | ------------------------------------------------------ |
| `empty`                      | No piece on the square                                 |
| `P`, `N`, `B`, `R`, `Q`, `K` | White pieces                                           |
| `p`, `n`, `b`, `r`, `q`, `k` | Black pieces (stored as `p_b`, `n_b`, etc. on Windows) |

The pipeline: **Camera → Board detection → Homography (bird's-eye) → Split into 64 tiles → CNN per tile → FEN assembly**

---

## Step 1: Capture Training Images

### During Live Detection

1. **Calibrate** the camera and board first:

   ```bash
   cd Backend/vision_module
   python run.py --calibrate
   or
   delete old config files in config/calibration and run program
    as normal and press y in the console to start calibration
   ```

2. **Start live detection:**

   ```bash
   python run.py --live --camera 0
   ```

3. **Set up a board position** on your physical board.

4. **Press `t`** when the board is detected and the bird's-eye view looks correct.
   - A message like `[TRAINING] Saved 64 tiles to ...` confirms capture.
   - If you see `[TRAINING] No valid board - detect board first`, wait for a successful detection (green corners) before pressing `t`.

5. Each press of `t` creates a new timestamped folder in:
   ```
   data/chess_dataset/capture_for_labeling/<YYYYMMDD_HHMMSS>/
   ```

### Output per Capture

Each capture folder contains:

| File                 | Description                     |
| -------------------- | ------------------------------- |
| `a1.jpg` … `h8.jpg`  | 64 tile images (one per square) |
| `grid_reference.jpg` | 8×8 montage with square labels  |
| `README.txt`         | Instructions for the next step  |

**Distortion balancing:** Tiles in files a–d (left half) are flipped horizontally before saving. This mirrors camera lens distortion so pieces that lean one way near the left edge appear to lean the opposite way in training data—you effectively get both orientations from fewer captures.

---

## Step 2: Label and Organize the Data

Each capture must be labeled with the board position in **FEN notation** (piece placement only).

### FEN Format Quick Reference

- **Uppercase** = White (P, N, B, R, Q, K)
- **Lowercase** = Black (p, n, b, r, q, k)
- **Digits** = Empty squares in a row (e.g. `4` = 4 empty)
- **`/`** = Row separator
- **Order** = Rank 8 first (top), Rank 1 last (bottom)

Example starting position:

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
```

### Organizing a Single Capture

Use `organize_captured_tiles.py` when you have one capture and know its FEN:

```bash
cd Backend/vision_module
python data/chess_dataset/tools/organize_captured_tiles.py <capture_id> "<FEN>"
```

Example:

```bash
python data/chess_dataset/tools/organize_captured_tiles.py 20260214_195556 "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
```

- By default, copies all 64 tiles into `square_dataset/train/<class>/` (including empty squares).
- Add `--no-empty` to skip empty squares and only copy piece tiles.
- Uses Windows-safe folder names (`p_b`, `n_b`, etc.) automatically.

```bash
# Include empty squares (default)
python data/chess_dataset/tools/organize_captured_tiles.py 20260214_195556 "<FEN>"

# Exclude empty squares (pieces only)
python data/chess_dataset/tools/organize_captured_tiles.py 20260214_195556 "<FEN>" --no-empty
```

To put tiles in the validation set instead:

```bash
python data/chess_dataset/tools/organize_captured_tiles.py 20260214_195556 "<FEN>" --target data/chess_dataset/square_dataset/val
```

### Batch Organizing Multiple Captures

If you have many captures and a `FEN.txt` file in each folder:

1. Create `FEN.txt` in each capture folder:

   ```
   data/chess_dataset/capture_for_labeling/20260214_195556/FEN.txt
   ```

   Contents: the FEN string for that board position (e.g. `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR`).

2. Run the batch script:

   ```bash
   cd Backend/vision_module
   python data/chess_dataset/tools/batch_organize_from_fen.py 20260214_195556 20260214_200112 20260214_201533
   ```

3. Optional train/val split:
   ```bash
   python data/chess_dataset/tools/batch_organize_from_fen.py 20260214_* --val-ratio 0.2
   ```
   Puts ~20% of captures into `val/` for validation.

**Note:** `batch_organize_from_fen.py` only organizes piece squares (skips empty). For empty-square examples, use `organize_captured_tiles.py` or add empty images manually.

### Expected Dataset Structure

After organizing:

```
square_dataset/
  train/
    empty/    ← empty squares
    P/       ← white pawn
    p_b/     ← black pawn (Windows-safe)
    N/
    n_b/
    B/
    b_b/
    R/
    r_b/
    Q/
    q_b/
    K/
    k_b/
  val/       ← optional
    (same structure)
```

### Verify the Dataset

```bash
python data/chess_dataset/tools/check_square_dataset.py
```

This prints counts per class and warns about structure issues.

---

## Step 3: Train the Model

```bash
cd Backend/vision_module
python data/chess_dataset/tools/train_transfer_learning.py [--epochs 20]
```

### Common Options

| Option         | Default         | Description                                            |
| -------------- | --------------- | ------------------------------------------------------ |
| `--epochs`     | 20              | Number of training epochs                              |
| `--batch-size` | 32              | Batch size (reduce to 8 if out of memory)              |
| `--model`      | efficientnet_b0 | `efficientnet_b0`, `resnet18`, or `mobilenet_v3_small` |
| `--tile-size`  | 64              | Input size (must match inference)                      |
| `--device`     | cuda/cpu        | Device to train on                                     |

### Examples

**Standard run:**

```bash
python data/chess_dataset/tools/train_transfer_learning.py --epochs 20
```

**Small dataset / quick test:**

```bash
python data/chess_dataset/tools/train_transfer_learning.py --epochs 5 --batch-size 8
```

**Lighter model (MobileNet):**

```bash
python data/chess_dataset/tools/train_transfer_learning.py --model mobilenet_v3_small --epochs 15
```

### Output

- Best model saved to `Model/piece_classifier.pt`
- If `val/` does not exist, an 80/20 split from `train/` is used for validation

---

## Architecture and Pipeline

### Vision Pipeline Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Camera Frame   │───▶│ Board Detection  │────▶│   Homography    │
└─────────────────┘     │ (4 corners)      │     │ (bird's-eye)    │
                        └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  FEN Notation   │◀────│ Piece Classifier │◀────│Board Splitter  │
│  (output)       │     │ (64 predictions) │     │  (64 tiles)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

1. **Board detection** – Finds the 4 board corners in the camera image.
2. **Homography** – Warps the view to a square bird's-eye image (a8 top-left, h1 bottom-right).
3. **Board splitter** – Cuts the bird's-eye view into 64 tiles with slight overlap, especially on the top, so piece tops aren’t cut off.
4. **Piece classifier** – Each tile is classified as empty or one of 12 piece types.
5. **FEN assembly** – The 64 classifications are turned into FEN notation and stored in the latest_frame_data.json

### Model Architecture (Transfer Learning)

- **Base:** Pre-trained ImageNet backbone (EfficientNet-B0 by default).
- **Head:** Final layer replaced with 13 outputs (one per class).
- **Input:** 64×64 RGB tiles, normalized for ImageNet.
- **Output:** Class probabilities per tile; argmax gives the piece (or empty).

### Board Splitter (Overlap)

- Each tile overlaps slightly upward into the square above.
- Avoids cutting off piece tops at square boundaries.
- Parameters: `top_overlap` (e.g. 0.2), `tile_size` (64), `board_top_margin` for homography.

### Data Augmentation (Training)

- Random resized crop
- Random horizontal flip
- Random rotation (±10°)
- Color jitter (brightness, contrast, saturation)

---

## Using the Trained Model

Once `Model/piece_classifier.pt` exists:

```bash
python run.py --live --camera 0
```

The pipeline automatically loads the classifier and uses it instead of any legacy detection. No extra configuration is needed.

---

## Troubleshooting

| Issue                       | Possible fix                                                                   |
| --------------------------- | ------------------------------------------------------------------------------ |
| `[TRAINING] No valid board` | Wait for board detection (green corners) before pressing `t`                   |
| No calibration              | Run `python run.py --calibrate` first                                          |
| Few images per class        | Capture more board positions; variety helps (pieces, empty, different squares) |
| Low validation accuracy     | Add more data, train longer, or try another model (`--model resnet18`)         |
| Out of memory               | Use `--batch-size 8`                                                           |
| Wrong class mapping         | Ensure folder names match `class_folders` (e.g. `p_b`, not `p` on Windows)     |
