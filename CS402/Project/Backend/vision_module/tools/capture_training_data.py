#!/usr/bin/env python3
"""
Capture bird's-eye board tiles for manual labeling and training.

Runs live camera with calibration. When you press 'c', captures the current
bird's-eye view, splits it into 64 tiles (with overlap), and saves them for
you to label. Set up board positions, capture, then use organize_captured_tiles.py
with the FEN for each capture to build your training dataset.

Usage:
  cd Backend/vision_module
  cd Backend/vision_module
  PYTHONPATH=src python data/chess_dataset/tools/capture_training_data.py [--camera 0]

  Or during live detection (run.py --live): press 't' to capture current board.

Hotkeys:
  c - Capture 64 tiles for current board position
  q - Quit

Output: data/chess_dataset/capture_for_labeling/<timestamp>/
  - a1.jpg, a2.jpg, ... h8.jpg  (64 tile images)
  - labeled_grid.jpg             (8x8 visual with square labels)
  - README.txt                  (instructions for labeling)
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# vision_module root: tools -> chess_dataset -> data -> vision_module
ROOT = Path(__file__).resolve().parents[3]
src_path = str(ROOT / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# Bypass bytecode cache so edits to vision modules take effect without restart
sys.dont_write_bytecode = True

import cv2
import numpy as np

CAPTURE_DIR = Path(__file__).resolve().parents[1] / "capture_for_labeling"
TILE_SIZE = 128  # Match training pipeline
TOP_OVERLAP_PX = 20  # Base overlap above each square; plus rank-dependent bottom crop (6–20 px) shifted to top


def capture_tiles_to_dir(
    warped_board,
    out_dir: Path,
    tile_size: int = 128,
    top_overlap_px: int = 20,
    board_top_margin: int = 0,
    board_side_margin: int = 0,
    fen: str = "",
) -> None:
    """Split warped board into tiles, save to out_dir. Callable from run.py (t key) or standalone."""
    from vision.piece_classifier import split_board_into_tiles
    from vision.vision_config import BOARD_TOP_MARGIN, BOARD_SIDE_MARGIN

    top_margin = board_top_margin or BOARD_TOP_MARGIN
    side_margin = board_side_margin or BOARD_SIDE_MARGIN

    tiles = split_board_into_tiles(
        warped_board,
        top_overlap_px=top_overlap_px,
        tile_size=tile_size,
        board_top_margin=top_margin,
        board_side_margin=side_margin,
    )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for tile in tiles:
        img = tile.image
        path = out_dir / f"{tile.square}.jpg"
        cv2.imwrite(str(path), img)

    # Grid reference: 8x8 montage with labels
    cell_h, cell_w = tiles[0].image.shape[:2]
    grid_img = np.zeros((cell_h * 8, cell_w * 8, 3), dtype=np.uint8)
    for tile in tiles:
        r, c = tile.row, tile.col
        y1, y2 = r * cell_h, (r + 1) * cell_h
        x1, x2 = c * cell_w, (c + 1) * cell_w
        img = tile.image
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        grid_img[y1:y2, x1:x2] = img
        cv2.putText(grid_img, tile.square, (x1 + 2, y1 + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    cv2.imwrite(str(out_dir / "labeled_grid.jpg"), grid_img)

    if fen:
        with open(out_dir / "FEN.txt", "w") as f:
            f.write(fen)


def main():
    # Run from vision_module so config/calibration paths resolve
    import os
    os.chdir(ROOT)

    parser = argparse.ArgumentParser(description="Capture board tiles for training data")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--tile-size", type=int, default=128)
    args = parser.parse_args()

    from vision.enhanced_chessboard_detector import EnhancedChessBoardDetector
    from vision.enhanced_homography_transformer import EnhancedHomographyTransformer
    from vision.enhanced_calibration_system import EnhancedCalibrationSystem
    from vision.piece_classifier import split_board_into_tiles
    from vision.vision_config import BOARD_OUTPUT_SIZE, BOARD_TOP_MARGIN, BOARD_SIDE_MARGIN
    from vision.camera_utils import initialize_camera_robust

    cap = initialize_camera_robust(args.camera)
    if cap is None:
        print(f"Failed to open camera {args.camera}")
        return 1

    # Detector + calibration (use same BOARD_OUTPUT_SIZE/BOARD_TOP_MARGIN as run.py)
    detector = EnhancedChessBoardDetector()
    transformer = EnhancedHomographyTransformer(
        output_size=BOARD_OUTPUT_SIZE,
        output_top_margin=BOARD_TOP_MARGIN,
        output_side_margin=BOARD_SIDE_MARGIN,
    )
    calibration = EnhancedCalibrationSystem(output_size=BOARD_OUTPUT_SIZE)
    calibration.load_calibration_data()

    if calibration.camera_matrix is not None:
        transformer.set_camera_params(calibration.camera_matrix, calibration.dist_coeffs)
    if calibration.board_corners and calibration.homography_matrix is not None:
        transformer.homography_matrix = calibration.homography_matrix
        transformer.inverse_homography_matrix = np.linalg.inv(calibration.homography_matrix)
        transformer.has_homography = True
        transformer.is_calibrated = True
        transformer.last_corners = calibration.board_corners
        print("Loaded saved calibration")
    else:
        print("No calibration found. Run: python run.py --calibrate")
        print("Then run this script again.")
        cap.release()
        return 1

    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    print("\n" + "=" * 60)
    print("  CAPTURE TRAINING DATA")
    print("=" * 60)
    print("Press 'c' to capture 64 tiles from current board view")
    print("Press 'q' to quit")
    print("Output:", CAPTURE_DIR)
    print("=" * 60 + "\n")

    last_warped = None
    last_corners = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect corners (or use saved)
        corners = calibration.board_corners if calibration.board_corners else None
        if corners is None or len(corners) != 4:
            corners = detector.detect_board_corners(frame, method='auto')

        if corners and len(corners) == 4:
            if not transformer.calibrate(frame, corners):
                pass  # keep previous
            warped = transformer.transform_to_birdseye(frame)
            if warped is not None:
                last_warped = warped
                last_corners = corners
                # Draw grid on display
                board_ort = getattr(calibration, 'board_orientation', 0)
                grid = transformer.draw_precise_grid(warped.copy(), board_orientation=board_ort) if transformer.is_calibrated else warped
            else:
                grid = frame
        else:
            grid = frame
            cv2.putText(grid, "No board detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # Show
        display = cv2.resize(grid, (640, 640))
        cv2.putText(display, "c=capture | q=quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Capture Training Data", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            if last_warped is None:
                print("[SKIP] No valid bird's-eye view - detect board first")
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = CAPTURE_DIR / timestamp
            capture_tiles_to_dir(
                last_warped,
                out_dir,
                tile_size=args.tile_size,
                top_overlap_px=TOP_OVERLAP_PX,
                board_top_margin=BOARD_TOP_MARGIN,
                board_side_margin=BOARD_SIDE_MARGIN,
            )
            fen = input("FEN for this position (or Enter to skip): ").strip()
            if fen:
                with open(out_dir / "FEN.txt", "w") as f:
                    f.write(fen)
            print(f"[SAVED] {out_dir} (64 tiles)")

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    main()
