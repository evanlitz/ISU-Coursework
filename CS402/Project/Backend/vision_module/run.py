#!/usr/bin/env python3
"""
Chess Vision Detection Runner - Enhanced Fixed Version (updated)

- Manual corner calibration only (no CV board detection)
- Two-panel UI: Bird's Eye View | Piece Classification, FEN + commands bar at bottom (900x600 panels, resizable)
- Live hotkeys:
    [ ] -> decrease/increase confidence threshold (0.50 .. 0.90)
    c   -> toggle corner overlay
    p   -> toggle piece overlay
    d   -> toggle debug file generation (images, results.txt, etc.)
    s   -> snapshot full artifact bundle
    q/ESC -> quit

@author Abhay Prasanna Rao
"""

import sys
import os
import cv2
import logging
import time
import json
from pathlib import Path
import argparse
import numpy as np
from datetime import datetime
import gc
import traceback
from collections import deque

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Vision components (manual corner calibration only - no CV board detection)
from vision.enhanced_homography_transformer import EnhancedHomographyTransformer
from vision.enhanced_calibration_system import EnhancedCalibrationSystem

from vision.vision_config import (
    BOARD_OUTPUT_SIZE,
    BOARD_TOP_MARGIN,
    BOARD_SIDE_MARGIN,
    undistort_and_orient_frame,
)

# Game state tracking moved to Backend/game_engine (reads from latest_frame_data.json)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _frame_for_corner_overlay(processor, frame):
    """Same undistort + optional 180° as bird's-eye pipeline so corners align on screen."""
    cs = processor.calibration_system
    if cs is None:
        return undistort_and_orient_frame(frame, None, None)
    return undistort_and_orient_frame(frame, cs.camera_matrix, cs.dist_coeffs)


def _visualize_corners(image, corners):
    """Draw corner overlay on image (replaces detector.visualize_corners)."""
    vis = image.copy()
    if corners and len(corners) == 4:
        names = ['a8', 'h8', 'h1', 'a1']
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
        for (corner, name, color) in zip(corners, names, colors):
            x, y = int(corner[0]), int(corner[1])
            cv2.circle(vis, (x, y), 10, color, -1)
            cv2.circle(vis, (x, y), 12, (255, 255, 255), 2)
            label_pos = (x + 15, y - 15) if y > 30 else (x + 15, y + 30)
            cv2.putText(vis, name, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        pts = np.array(corners, dtype=np.int32)
        cv2.polylines(vis, [pts], True, (255, 255, 255), 3)
    return vis


class FrameProcessor:
    """Fixed frame processor with improved stability, plus adaptive hooks."""

    def __init__(self, piece_classifier=None):
        self.piece_classifier = piece_classifier
        self.transformer = EnhancedHomographyTransformer(
            output_size=BOARD_OUTPUT_SIZE,
            output_top_margin=BOARD_TOP_MARGIN,
            output_side_margin=BOARD_SIDE_MARGIN,
        )
        self.calibration_system = EnhancedCalibrationSystem(output_size=BOARD_OUTPUT_SIZE)
        self.calibration_data = None

        # Tile scale for piece capture (adjustable via key in live mode; >1 = taller pieces)
        self.tile_scale = 0.5

        # State
        self.last_successful_result = None
        self.consecutive_failures = 0
        self.processing_count = 0

        # Performance
        self.fps_counter = deque(maxlen=30)
        
        # Load existing calibration data
        self._load_calibration_data()

    def _load_calibration_data(self):
        """Load existing calibration data."""
        if self.calibration_system.load_calibration_data():
            # Apply camera calibration data to transformer
            if self.calibration_system.camera_matrix is not None and self.calibration_system.dist_coeffs is not None:
                self.transformer.set_camera_params(
                    self.calibration_system.camera_matrix,
                    self.calibration_system.dist_coeffs
                )
                logger.info("Applied camera calibration data to transformer")
            
            # Apply homography calibration data to transformer
            if self.calibration_system.board_corners:
                # Set the homography matrix directly instead of calibrating with None image
                self.transformer.homography_matrix = self.calibration_system.homography_matrix
                self.transformer.inverse_homography_matrix = np.linalg.inv(self.calibration_system.homography_matrix) if self.calibration_system.homography_matrix is not None else None
                self.transformer.has_homography = self.calibration_system.homography_matrix is not None
                self.transformer.is_calibrated = self.calibration_system.is_calibrated
                self.transformer.last_corners = self.calibration_system.board_corners
                self.transformer.label_orientation_offset = getattr(self.calibration_system, "label_orientation_offset", 0)
                logger.info("Loaded existing homography calibration data")
            else:
                logger.info("No board corners found in calibration data")
        else:
            logger.info("No existing calibration data found")
    
    def _refine_corners(self, image, corners):
        """Refine detected corners for better accuracy using sub-pixel corner detection."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Convert corners to numpy array
            corners_array = np.array(corners, dtype=np.float32)
            
            # Define criteria for sub-pixel corner detection
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            
            # Refine corners with sub-pixel accuracy
            refined_corners = cv2.cornerSubPix(gray, corners_array, (5, 5), (-1, -1), criteria)
            
            # Convert back to list of tuples
            refined_corners_list = [(float(x), float(y)) for x, y in refined_corners]
            
            logger.debug(f"Refined corners: {refined_corners_list}")
            return refined_corners_list
            
        except Exception as e:
            logger.warning(f"Corner refinement failed: {e}")
            return corners

    def set_calibration(self, calibration_data):
        """Set camera calibration data."""
        self.calibration_data = calibration_data
        if calibration_data:
            self.transformer.set_camera_params(
                calibration_data['camera_matrix'],
                calibration_data['dist_coeffs']
            )
    
    def process_frame(
        self,
        image,
        output_dir=None,
        save_files=True,
        confidence_threshold: float = 0.50,
    ):
        """Process a single frame using manual calibration only."""
        results = {
            'success': False,
            'corners': None,
            'warped_board': None,
            'detected_pieces': [],
            'piece_fen': None,
            'piece_map': {},
            'error_message': '',
            'processing_time': 0,
            'detection_method': None
        }

        start_time = time.time()

        try:
            # Validate
            if image is None or image.size == 0:
                results['error_message'] = "Invalid input image"
                return results

            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif len(image.shape) != 3 or image.shape[2] != 3:
                results['error_message'] = f"Invalid image shape: {image.shape}"
                return results

            # ---- Step 1: Board corners (manual calibration only) ----
            logger.info("Using board corners...")
            if not (self.calibration_system.board_corners and self.calibration_system.is_calibrated):
                results['error_message'] = "No calibration. Run corner calibration (k key) or recalibrate (r key)."
                self.consecutive_failures += 1
                if save_files and output_dir:
                    self._save_failed_frame(image, results, output_dir)
                return results

            corners = self.calibration_system.board_corners
            results['detection_method'] = 'saved_calibration'

            if corners is None or len(corners) != 4:
                results['error_message'] = f"Corner detection failed: {len(corners) if corners else 0} corners"
                self.consecutive_failures += 1
                if save_files and output_dir:
                    self._save_failed_frame(image, results, output_dir)
                return results

            results['corners'] = corners
            # Detection method is now set in the corner detection logic above

            # ---- Step 2: Homography ----
            logger.info("Using saved homography calibration...")
            self.transformer.homography_matrix = self.calibration_system.homography_matrix
            self.transformer.inverse_homography_matrix = np.linalg.inv(self.calibration_system.homography_matrix)
            self.transformer.has_homography = True
            self.transformer.is_calibrated = True
            self.transformer.last_corners = corners
            self.transformer.label_orientation_offset = getattr(self.calibration_system, "label_orientation_offset", 0)

            # ---- Step 3: Bird's-eye ----
            logger.info("Generating bird's eye view...")
            warped = self.transformer.transform_to_birdseye(image)
            if warped is None:
                results['error_message'] = "Bird's eye transformation failed"
                self.consecutive_failures += 1
                if save_files and output_dir:
                    self._save_failed_frame(image, results, output_dir)
                return results
            results['warped_board'] = warped

            # ---- Step 4: Piece classification (per-square CNN) ----
            logger.info("Running piece classification...")
            try:
                from vision.piece_classifier import fen_from_classifier

                board_size = self.transformer.output_size[0] if isinstance(self.transformer.output_size, tuple) else self.transformer.output_size
                board_orientation = getattr(
                    self.calibration_system, 'board_orientation', 0
                ) % 4
                pipeline_results = fen_from_classifier(
                    warped,
                    self.piece_classifier,
                    top_overlap_px=60,
                    tile_size=128,
                    confidence_threshold=float(confidence_threshold),
                    board_top_margin=BOARD_TOP_MARGIN,
                    board_side_margin=BOARD_SIDE_MARGIN,
                    board_orientation=board_orientation,
                    tile_scale=self.tile_scale,
                )
                results.update(pipeline_results)
                results['board_orientation'] = board_orientation
                results['piece_fen'] = pipeline_results['fen']
                results['detected_pieces'] = pipeline_results.get('detections', [])
                logger.info(f"Detected {len(results['detected_pieces'])} pieces")

                self.last_frame_data = {
                    'image': warped,
                    'corners': corners,
                    'detections': results['detected_pieces'],
                    'timestamp': time.time()
                }
            except Exception as e:
                logger.warning(f"Piece classification failed: {e}")
                results['detected_pieces'] = []
                results['piece_fen'] = "8/8/8/8/8/8/8/8"

            # Success
            results['success'] = True
            self.consecutive_failures = 0
            self.last_successful_result = results.copy()

            if save_files and output_dir:
                self._save_successful_frame(image, results, output_dir)

        except Exception as e:
            results['error_message'] = f"Processing failed: {str(e)[:100]}"
            logger.error(f"Processing error: {e}")
            logger.error(traceback.format_exc())
            self.consecutive_failures += 1
            if save_files and output_dir:
                self._save_failed_frame(image, results, output_dir)
        finally:
            results['processing_time'] = time.time() - start_time
            self.processing_count += 1
            if self.processing_count % 50 == 0:
                gc.collect()

        return results

    def _save_successful_frame(self, image, results, output_dir):
        """Save successful frame outputs."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            corners = results.get('corners')
            if corners is not None and len(corners) >= 4:
                overlay_base = _frame_for_corner_overlay(self, image)
                corner_viz = _visualize_corners(overlay_base, corners)
                cv2.imwrite(str(output_dir / "01_corners_detected.jpg"), corner_viz)

            if results['warped_board'] is not None:
                cv2.imwrite(str(output_dir / "02_birdseye_view.jpg"), results['warped_board'])
                try:
                    board_ort = results.get('board_orientation', getattr(self.calibration_system, 'board_orientation', 0))
                    grid_overlay = self.transformer.draw_precise_grid(results['warped_board'].copy(), board_orientation=board_ort)
                    cv2.imwrite(str(output_dir / "03_grid_overlay.jpg"), grid_overlay)
                except Exception as e:
                    logger.warning(f"Grid overlay failed to save: {e}")

            # Enhanced results file with FEN summary and board mapping
            with open(str(output_dir / "04_results.txt"), 'w') as f:
                f.write("Chess Board Analysis Results\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Status: SUCCESS\n")
                f.write(f"Detection Method: {results.get('detection_method', 'Unknown')}\n")
                f.write(f"Corners: 4\n")
                f.write(f"Pieces Detected: {len(results['detected_pieces'])}\n")
                f.write(f"FEN: {results.get('piece_fen', 'Not generated')}\n")
                f.write(f"Processing Time: {results.get('processing_time', 0):.3f}s\n")
                
                if results['detected_pieces']:
                    f.write("\nDetected Pieces:\n")
                    for i, (label, bbox, conf) in enumerate(results['detected_pieces'], 1):
                        x1, y1, x2, y2 = [int(c) for c in bbox]
                        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                        f.write(f"  {i}. {label} (conf: {conf:.3f}) at ({center_x}, {center_y})\n")
            
            # Create enhanced FEN summary and board mapping file
            with open(str(output_dir / "05_fen_board_mapping.txt"), 'w') as f:
                f.write("FEN SUMMARY & BOARD MAPPING\n")
                f.write("=" * 50 + "\n\n")
                
                # FEN Analysis
                fen = results.get('piece_fen', '8/8/8/8/8/8/8/8')
                f.write(f"FEN String: {fen}\n")
                f.write(f"Board State: {'Empty Board' if fen == '8/8/8/8/8/8/8/8' else 'Pieces Present'}\n\n")
                
                # Board mapping visualization
                f.write("BOARD MAPPING (8x8 Chess Board):\n")
                f.write("   a  b  c  d  e  f  g  h\n")
                f.write("  " + "-" * 24 + "\n")
                
                # Parse FEN to create board visualization
                fen_rows = fen.split('/')
                for rank_idx, fen_row in enumerate(fen_rows):
                    rank = 8 - rank_idx  # Chess ranks go 8,7,6,5,4,3,2,1
                    f.write(f"{rank} |")
                    
                    file_idx = 0
                    for char in fen_row:
                        if char.isdigit():
                            # Empty squares
                            for _ in range(int(char)):
                                f.write(" . ")
                                file_idx += 1
                        else:
                            # Piece
                            f.write(f" {char} ")
                            file_idx += 1
                    f.write("|\n")
                f.write("  " + "-" * 24 + "\n")
                f.write("   a  b  c  d  e  f  g  h\n\n")
                
                # Piece mapping to squares
                if results['detected_pieces']:
                    f.write("PIECE LOCATIONS:\n")
                    f.write("-" * 20 + "\n")
                    for i, (label, bbox, conf) in enumerate(results['detected_pieces'], 1):
                        x1, y1, x2, y2 = [int(c) for c in bbox]
                        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                        
                        # Try to map to chess square if transformer is available
                        square_info = "Unknown square"
                        if hasattr(self, 'transformer') and self.transformer.is_calibrated:
                            try:
                                # This would need the transformer to have a method to convert pixel to square
                                square_info = f"Pixel ({center_x}, {center_y})"
                            except:
                                square_info = f"Pixel ({center_x}, {center_y})"
                        
                        f.write(f"{i}. {label} - {square_info} (conf: {conf:.3f})\n")
                else:
                    f.write("No pieces detected on the board.\n")

            # Piece detection visualization (use warped board - bboxes are in that space)
            # Use explicit is not None - "or" would trigger "truth value of array ambiguous" on numpy arrays
            wb = results.get('warped_board')
            piece_viz = (wb if wb is not None else image).copy()
            
            if results['detected_pieces']:
                # Draw detected pieces
                for i, (label, bbox, conf) in enumerate(results['detected_pieces'], 1):
                    try:
                        x1, y1, x2, y2 = [int(c) for c in bbox]
                        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                        
                        # Color coding: FEN uppercase=white, lowercase=black
                        if label and label.isupper():
                            color = (255, 255, 255)  # White
                            text_color = (0, 0, 0)   # Black text
                        elif label and label.islower():
                            color = (0, 0, 0)        # Black
                            text_color = (255, 255, 255)  # White text
                        else:
                            color = (0, 255, 0)      # Green for unknown
                            text_color = (255, 255, 255)
                        
                        # Draw bounding box
                        cv2.rectangle(piece_viz, (x1, y1), (x2, y2), color, 3)
                        
                        # Draw center point
                        cv2.circle(piece_viz, (center_x, center_y), 5, (0, 0, 255), -1)
                        
                        # Draw piece number
                        cv2.circle(piece_viz, (x1 + 15, y1 + 15), 12, color, -1)
                        cv2.putText(piece_viz, str(i), (x1 + 10, y1 + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
                        
                        # Draw label and confidence
                        label_text = f"{label}: {conf:.7f}"
                        cv2.putText(piece_viz, label_text, (x1, y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                    except Exception as e:
                        logger.warning(f"Error drawing piece {i}: {e}")
                        pass
                
                # Add detection summary
                pieces_count = len(results['detected_pieces'])
                cv2.putText(piece_viz, f"Detected: {pieces_count} pieces", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            else:
                # No pieces detected - add "no detection" overlay
                cv2.putText(piece_viz, "Detected: 0 pieces", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.putText(piece_viz, "No chess pieces found", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Always save piece detection output
            cv2.imwrite(str(output_dir / "05_piece_detection.jpg"), piece_viz)
            
            # Enhanced piece detection visualization (if pieces detected)
            if results['detected_pieces']:
                cv2.imwrite(str(output_dir / "06_piece_detection.jpg"), piece_viz)
                
                # Bird's eye view with piece detection (if available)
                if results['warped_board'] is not None:
                    try:
                        birdseye_pieces = results['warped_board'].copy()
                        # Add grid overlay
                        if hasattr(self, 'transformer') and self.transformer.is_calibrated:
                            board_ort = results.get('board_orientation', getattr(self.calibration_system, 'board_orientation', 0))
                            birdseye_pieces = self.transformer.draw_precise_grid(birdseye_pieces, board_orientation=board_ort)
                        
                        # Note: This would need warped piece coordinates, which requires additional processing
                        # For now, just save the grid overlay as a reference
                        cv2.imwrite(str(output_dir / "07_board_mapping_visual.jpg"), birdseye_pieces)
                        
                    except Exception as e:
                        logger.warning(f"Error creating board mapping visual: {e}")
            
            else:
                # Create empty board visualization even if no pieces detected
                if results['warped_board'] is not None:
                    try:
                        empty_board = results['warped_board'].copy()
                        if hasattr(self, 'transformer') and self.transformer.is_calibrated:
                            board_ort = results.get('board_orientation', getattr(self.calibration_system, 'board_orientation', 0))
                            empty_board = self.transformer.draw_precise_grid(empty_board, board_orientation=board_ort)
                        cv2.imwrite(str(output_dir / "06_empty_board_mapping.jpg"), empty_board)
                    except Exception as e:
                        logger.warning(f"Error creating empty board visual: {e}")

            logger.info(f"Saved successful frame outputs to {output_dir}")

        except Exception as e:
            logger.error(f"Error saving outputs: {e}")

    def _save_failed_frame(self, image, results, output_dir):
        """Save failed frame for debugging."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            cv2.imwrite(str(output_dir / "00_raw_image.jpg"), image)
            with open(str(output_dir / "00_failure_report.txt"), 'w') as f:
                f.write("FRAME PROCESSING FAILURE\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Error: {results.get('error_message', 'Unknown')}\n")
                corners_val = results.get('corners')
                f.write(f"Corners Detected: {len(corners_val) if corners_val is not None else 0}\n")
                f.write(f"Processing Time: {results.get('processing_time', 0):.3f}s\n")
                f.write(f"Consecutive Failures: {self.consecutive_failures}\n")
                f.write(f"\nImage Info:\n")
                f.write(f"  Shape: {image.shape}\n")
                f.write(f"  Type: {image.dtype}\n")
                f.write(f"  Min/Max: {image.min()}/{image.max()}\n")

            if corners_val is not None and len(corners_val) > 0:
                overlay_base = _frame_for_corner_overlay(self, image)
                corner_viz = _visualize_corners(overlay_base, results['corners'])
                cv2.imwrite(str(output_dir / "01_partial_corners.jpg"), corner_viz)

            logger.info(f"Saved failed frame to {output_dir}")
        except Exception as e:
            logger.error(f"Error saving failed frame: {e}")


def get_all_classifier_paths():
    """Return ordered list of available classifier paths for cycling with 'm' key.
    Default model: mobilenet_v3_small (preferred), then piece_classifier.pt, then others."""
    model_dir = Path(__file__).parent / "Model"
    paths = []
    # Prefer v3_small as default when available
    v3_small = model_dir / "40_inch_heightpiece_classifier_mobilenet_v3_small.pt"
    if v3_small.exists():
        paths.append(str(v3_small))
    default_path = model_dir / "piece_classifier.pt"
    if default_path.exists() and str(default_path) not in paths:
        paths.append(str(default_path))
    arch_specific = sorted(model_dir.glob("*.pt")) if model_dir.exists() else []
    for p in arch_specific:
        if str(p) not in paths:
            paths.append(str(p))
    return paths


def find_piece_classifier_path():
    """Find piece classifier model in the project (first in get_all_classifier_paths)."""
    paths = get_all_classifier_paths()
    if not paths:
        logger.warning("No piece classifier found - run train_transfer_learning.py to train one")
        return None
    logger.info(f"Found piece classifier: {paths[0]}")
    return paths[0]


def load_calibration():
    """Load the most recent camera calibration data."""
    calibration_dir = Path(__file__).parent / "test_results" / "camera_calibration"
    if not calibration_dir.exists():
        return None
    calibration_files = list(calibration_dir.glob("calibration_*.npz"))
    if not calibration_files:
        return None
    latest_file = max(calibration_files, key=lambda x: x.stat().st_mtime)
    try:
        data = np.load(str(latest_file))
        calibration_data = {
            'camera_matrix': data['camera_matrix'],
            'dist_coeffs': data['dist_coeffs'],
            'mean_error': float(data['mean_error']),
            'num_images': int(data['num_images']),
            'timestamp': str(data['timestamp'])
        }
        logger.info(f"Loaded calibration from {latest_file}")
        return calibration_data
    except Exception as e:
        logger.warning(f"Failed to load calibration: {e}")
        return None


def enumerate_available_cameras(max_cameras=10):
    """Enumerate available cameras and test their availability (fixed to avoid GStreamer errors).

    Tests every index from 0 through max_cameras inclusive so Linux nodes like /dev/video1
    are not skipped (the previous even-only list missed many USB setups).
    """
    import platform
    import os
    
    available_cameras = []
    print("Scanning for available cameras...")
    
    if platform.system() == "Linux":
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    
    for camera_id in range(max_cameras + 1):
        cap = None
        try:
            cap = initialize_camera(camera_id)
            if cap is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                camera_name = f"Camera {camera_id} ({width}x{height} @ {fps:.1f}fps)"
                available_cameras.append((camera_id, True, camera_name))
                logger.info(f"Found available camera: {camera_name}")
                cap.release()
        except Exception as e:
            logger.debug(f"Camera {camera_id} test failed: {e}")
            if cap:
                cap.release()

    if not available_cameras:
        logger.warning("No cameras found")
        print("No cameras detected. Make sure your external webcam is connected.")
    return available_cameras


def initialize_camera(camera_id=0, width=None, height=None):
    """Initialize camera connection (4K-friendly: MSMF, MJPEG, resolution presets)."""
    from vision.camera_utils import initialize_camera_robust

    cap = initialize_camera_robust(camera_id, width=width, height=height)
    if cap is None:
        print(f"Failed to open camera {camera_id}")
    return cap


def show_verify_fen_dialog(
    last_results: dict,
    board_top_margin: int,
    board_side_margin: int,
    board_orientation: int = 0,
    tile_scale: float = 0.5,
) -> None:
    """
    Show Tkinter dialog: FEN text box, Fill from detected, Verify.
    Verify validates FEN, finds misclassified squares, saves those tile images to training set.
    Uses board_orientation from last_results when available so sorting matches the rotated camera view.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError:
        print("[VERIFY] Tkinter not available - install python3-tk")
        return

    tools_dir = str(Path(__file__).parent / "data" / "chess_dataset" / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)

    try:
        from verify_fen_to_training import validate_fen, verify_and_save_misclassified, sort_all_tiles, VAL_DIR
    except ImportError as e:
        print(f"[VERIFY] Failed to import verify_fen_to_training: {e}")
        return

    root = tk.Tk()
    root.title("Verify FEN - Save Misclassified to Training")
    root.geometry("820x260")
    root.resizable(True, True)

    fen_var = tk.StringVar()
    result_var = tk.StringVar(value="Enter FEN and click Verify")

    def on_fill():
        fen = last_results.get("piece_fen") or ""
        fen_placement = fen.strip().split()[0] if fen.strip() else "8/8/8/8/8/8/8/8"
        fen_var.set(fen_placement)

    def on_verify():
        fen_text = fen_var.get().strip()
        if not fen_text:
            messagebox.showwarning("Verify FEN", "Please enter a FEN string first.")
            return
        valid, _, msg = validate_fen(fen_text)
        if not valid:
            messagebox.showerror("Invalid FEN", msg)
            return
        warped = last_results.get("warped_board")
        piece_map = last_results.get("piece_map") or {}
        if warped is None:
            messagebox.showerror("Verify", "No board image available. Detect board first.")
            return
        # Use orientation from the frame that produced this warped_board (handles rotated calibration)
        board_ort = last_results.get("board_orientation", board_orientation)
        success, message, count = verify_and_save_misclassified(
            warped,
            piece_map,
            fen_text,
            board_top_margin=board_top_margin,
            board_side_margin=board_side_margin,
            top_overlap_px=60,
            board_orientation=board_ort,
            tile_scale=tile_scale,
        )
        result_var.set(message)
        if success:
            messagebox.showinfo("Verify Complete", message)
        else:
            messagebox.showerror("Verify Failed", message)

    def on_sort_all(include_empty: bool, target_val: bool = False):
        fen_text = fen_var.get().strip()
        if not fen_text:
            messagebox.showwarning("Sort All", "Please enter a FEN string first.")
            return
        valid, _, msg = validate_fen(fen_text)
        if not valid:
            messagebox.showerror("Invalid FEN", msg)
            return
        warped = last_results.get("warped_board")
        if warped is None:
            messagebox.showerror("Sort All", "No board image available. Detect board first.")
            return
        # Use orientation from the frame that produced this warped_board (handles rotated calibration)
        board_ort = last_results.get("board_orientation", board_orientation)
        target_dir = VAL_DIR if target_val else None  # None => use default TRAIN_DIR
        success, message, count = sort_all_tiles(
            warped,
            fen_text,
            board_top_margin=board_top_margin,
            board_side_margin=board_side_margin,
            top_overlap_px=60,
            board_orientation=board_ort,
            include_empty=include_empty,
            target_dir=target_dir,
        )
        result_var.set(message)
        if success:
            messagebox.showinfo("Sort Complete", message)
        else:
            messagebox.showerror("Sort Failed", message)

    # FEN label + entry
    frm = ttk.Frame(root, padding=10)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text="FEN (piece placement):").pack(anchor=tk.W)
    entry = ttk.Entry(frm, textvariable=fen_var, width=80)
    entry.pack(fill=tk.X, pady=(0, 8))

    # Buttons
    btn_frm = ttk.Frame(frm)
    btn_frm.pack(fill=tk.X, pady=8)
    ttk.Button(btn_frm, text="Fill from detected", command=on_fill).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frm, text="Verify", command=on_verify).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frm, text="Sort All (with empty)", command=lambda: on_sort_all(include_empty=True)).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frm, text="Sort All (no empty)", command=lambda: on_sort_all(include_empty=False)).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frm, text="Add to Validation", command=lambda: on_sort_all(include_empty=True, target_val=True)).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frm, text="Close", command=root.destroy).pack(side=tk.LEFT)

    ttk.Label(frm, textvariable=result_var, foreground="gray").pack(anchor=tk.W, pady=(4, 0))

    root.mainloop()


def create_multi_panel_display(
    frame,
    results,
    transformer,
    show_corners=True,
    show_pieces=True,
    panel1_raw_camera=False,
    tile_scale=0.5,
    last_process_time=0.0,
    fps=0.0,
    ui_method="auto",
    ui_conf=0.50,
    calibration_system=None,
    auto_capture_enabled=False,
    save_debug_files=True,
    current_classifier=None,
):
    """Create a two-panel display: Bird's Eye View | Piece Classification, with FEN + commands bar at bottom."""
    try:
        # Large panels for readability - two sections plus bottom bar
        margin = 16
        bar_height = 145  # FEN + gap + 3 rows of key bindings
        panel_width = 900
        panel_height = 600

        canvas_width = panel_width * 2 + margin * 3
        canvas_height = panel_height + bar_height + margin * 2
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:] = (30, 30, 30)

        # ---------- Panel 1: Bird's Eye View or Raw Camera ----------
        if panel1_raw_camera and frame is not None:
            # Raw camera input (no transforms)
            panel1 = frame.copy()
            panel1_label = "Raw Camera"
        elif results['success'] and results.get('warped_board') is not None:
            panel1 = results['warped_board'].copy()
            if transformer and getattr(transformer, "has_homography", False):
                try:
                    board_ort = results.get('board_orientation', getattr(calibration_system, 'board_orientation', 0) if calibration_system else 0)
                    panel1 = transformer.draw_precise_grid(panel1, board_orientation=board_ort)
                except Exception:
                    pass
            panel1_label = "Bird's Eye View"
        else:
            panel1 = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
            panel1[:] = (20, 20, 20)
            cv2.putText(panel1, "Waiting for detection", (panel_width//2 - 120, panel_height//2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (128, 128, 128), 2)
            panel1_label = "Bird's Eye View"

        cv2.putText(panel1, panel1_label, (12, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        status_color = (0, 255, 0) if results['success'] else (0, 0, 255)
        status_text = "DETECTED" if results['success'] else "SEARCHING"
        cv2.putText(panel1, status_text, (12, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, status_color, 3)
        homography_status = "READY" if transformer and getattr(transformer, "has_homography", False) else "NO"
        cv2.putText(panel1, f"H: {homography_status}", (12, 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0) if homography_status == "READY" else (0, 0, 255), 3)

        panel1_resized = cv2.resize(panel1, (panel_width, panel_height))
        canvas[margin:margin+panel_height, margin:margin+panel_width] = panel1_resized

        # ---------- Panel 2: Piece Classification ----------
        _FEN_TO_DISPLAY = {
            "P": "White Pawn", "p": "Black Pawn",
            "N": "White Knight", "n": "Black Knight",
            "B": "White Bishop", "b": "Black Bishop",
            "R": "White Rook", "r": "Black Rook",
            "Q": "White Queen", "q": "Black Queen",
            "K": "White King", "k": "Black King",
        }
        if results['success'] and results.get('warped_board') is not None and results.get('detected_pieces') and show_pieces:
            panel2 = results['warped_board'].copy()
            for label, bbox, conf in results['detected_pieces']:
                try:
                    x1, y1, x2, y2 = [int(c) for c in bbox]
                    cv2.rectangle(panel2, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green boxes
                    piece_name = _FEN_TO_DISPLAY.get(str(label), str(label))
                    label_text = f"{piece_name}"
                    text_y = max(24, y1 - 8)
                    cv2.putText(panel2, label_text, (x1, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
                except Exception:
                    pass
        elif results['success'] and results.get('warped_board') is not None:
            panel2 = results['warped_board'].copy()
        else:
            panel2 = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
            panel2[:] = (20, 20, 20)
            cv2.putText(panel2, "Waiting for detection", (panel_width//2 - 120, panel_height//2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (128, 128, 128), 2)

        panel2_resized = cv2.resize(panel2, (panel_width, panel_height))
        canvas[margin:margin+panel_height, margin*2+panel_width:margin*2+panel_width*2] = panel2_resized

        # ---------- Bottom bar: FEN + Key bindings (multi-row) ----------
        bar_y = margin + panel_height + 8
        bar_h = bar_height - 16
        bar_x_left = margin
        bar_w = canvas_width - margin * 2
        line_height = 22
        fen_to_commands_gap = 18  # Extra space between FEN and key bindings

        # Draw bar background
        cv2.rectangle(canvas, (bar_x_left, bar_y), (bar_x_left + bar_w, bar_y + bar_h), (45, 45, 45), -1)
        cv2.rectangle(canvas, (bar_x_left, bar_y), (bar_x_left + bar_w, bar_y + bar_h), (80, 80, 80), 1)

        # FEN line
        fen = results.get('piece_fen') or "(no FEN yet)"
        fen_display = fen if len(fen) <= 95 else fen[:92] + "..."
        cv2.putText(canvas, f"FEN: {fen_display}", (bar_x_left + 12, bar_y + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 220, 220), 2)

        # Detection labels + key bindings (multiple rows, with gap below FEN)
        y_cmd = bar_y + 26 + line_height + fen_to_commands_gap
        pieces_count = len(results.get('detected_pieces', []))
        model_label = f"Model: {current_classifier}" if current_classifier else "Model: (none)"
        auto_status = "Auto: ON" if auto_capture_enabled else "Auto: OFF"
        cmd_rows = [
            f"Piece Classification | {model_label} | Pieces: {pieces_count} | Conf: {ui_conf:.2f} | Scale: {tile_scale:.1f} | {auto_status}",
            "q quit | s capture | d debug | t tiles | a auto | v verify FEN | p pieces | f raw camera | m swap model",
            "r recalibrate | k corners | [ ] conf | + - tile scale | f swap panel 1",
        ]

        for i, row_text in enumerate(cmd_rows):
            cv2.putText(canvas, row_text, (bar_x_left + 12, y_cmd + i * line_height),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 160), 1)

        return canvas

    except Exception as e:
        logger.error(f"Display error: {e}")
        error_frame = frame.copy()
        cv2.putText(error_frame, "Display Error", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return error_frame


def run_live_camera_detection(
    camera_id=0,
    multi_panel=True,
    save_debug=True,
    width=None,
    height=None,
    headless=False,
):
    """Run live camera detection with real-time processing.
    
    Args:
        save_debug: If True, save debug artifacts (images, results.txt, fen_board_mapping.txt)
                   when capturing frames. If False, only JSON gameplay data is saved.
        width, height: Optional capture size (try first, then built-in presets). None = auto.
        headless: If True, skip OpenCV windows and keyboard handling; still runs the vision
            loop and writes gameplay_data/latest_frame_data.json when auto-capture is enabled.
            Stop with Ctrl+C. Requires calibration files (no interactive setup in this mode).
    """
    print("\n" + "="*60)
    print("    LIVE CAMERA DETECTION - FIXED")
    print("="*60)
    print("Starting live camera detection with piece classification...")
    print("Hotkeys: q quit | s capture | d debug | t tiles | a auto | v verify FEN | p pieces | f raw camera")
    print("         r recalibrate | k corners | [ ] conf | + - tile scale")
    print()

    # Camera
    cap = initialize_camera(camera_id, width=width, height=height)
    if cap is None:
        return

    # Piece classifier
    classifier_path = find_piece_classifier_path()
    piece_classifier = None
    if classifier_path:
        try:
            from vision.piece_classifier import PieceClassifier
            piece_classifier = PieceClassifier(classifier_path, tile_size=128)
            if piece_classifier.is_available:
                logger.info("Piece classifier loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load piece classifier: {e}")

    # Processor
    processor = FrameProcessor(piece_classifier)

    # Calibration is now handled before calling this function
    # No need to check calibration here as it's already ensured
    # Legacy calibration loading removed - using EnhancedCalibrationSystem instead
    
    # No chess game in run.py - use gameplay.py for chess functionality
    classifier_paths = get_all_classifier_paths()
    current_classifier_idx = 0 if classifier_paths else -1
    current_classifier_name = Path(classifier_paths[0]).stem if classifier_paths else "none"

    print("\n" + "="*60)
    print("    LIVE DETECTION MODE")
    print("="*60)
    print("Starting live detection mode.")
    print(f"Classifier: {current_classifier_name} (press 'm' to swap)")
    print("Use 's' to capture and process frames.")
    print("Run 'python3 gameplay.py' in another terminal for chess gameplay.")
    print()

    # UI flags/state
    show_corners = True
    show_pieces = True
    panel1_raw_camera = False  # Toggle with 'f' - panel 1 shows raw camera vs bird's eye
    save_debug_files = save_debug  # Toggle with 'd' - controls generation of debug images/text files
    frame_count = 0
    display_window_initialized = False  # Only resize window on first frame so user resizing is preserved

    # Confidence threshold (manual calibration only - no detection method switching)
    conf_threshold = 0.50

    # Loop timing & fps
    last_process_time = 0
    last_results = {
        'success': False,
        'error_message': 'Initializing...',
        'corners': None,
        'warped_board': None,
        'detected_pieces': [],
        'piece_fen': None,
        'processing_time': 0
    }
    fps_counter = deque(maxlen=30)
    
    # Auto capture: when enabled, write to JSON on every successful frame (runs at display processing rate)
    auto_capture_enabled = True

    def write_frame_data_to_json(results, frame_path="", capture_type="live"):
        """Write vision results to latest_frame_data.json for game_engine."""
        def convert_numpy_types(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.float32, np.float64, np.floating)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64, np.integer)):
                return int(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            elif obj is None:
                return None
            return obj

        vision_results = {
            'success': results['success'],
            'fen': results.get('piece_fen'),
            'confidence': 0.8 if results['success'] else 0.0,
            'method_used': results.get('detection_method', 'calibration'),
            'detected_pieces': convert_numpy_types(results.get('detected_pieces', [])),
            'corners': convert_numpy_types(results.get('corners')),
            'error_message': results.get('error_message', '')
        }
        gameplay_data = {
            'timestamp': time.time(),
            'vision_results': vision_results,
            'frame_path': frame_path,
            'capture_type': capture_type
        }
        gameplay_dir = Path(__file__).parent.parent / "shared" / "queue"
        gameplay_dir.mkdir(exist_ok=True)
        target_path = gameplay_dir / "latest_frame_data.json"
        temp_path = target_path.with_suffix(".json.tmp")
        with open(temp_path, 'w') as f:
            json.dump(gameplay_data, f, indent=2)
        try:
            temp_path.replace(target_path)
        except OSError:
            pass  # Skip this frame if replace fails (reader may have file open); next frame will retry

    def save_frame_for_processing(frame, processor, save_files=True, is_auto=False):
        """Save frame and process it for gameplay."""
        # Write latest raw frame for debugging (atomic replace)
        _queue_dir = Path(__file__).parent.parent / "shared" / "queue"
        _queue_dir.mkdir(exist_ok=True)
        _tmp_jpg = _queue_dir / "latest_frame.jpg.tmp"
        cv2.imwrite(str(_tmp_jpg), frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        try:
            _tmp_jpg.replace(_queue_dir / "latest_frame.jpg")
        except OSError:
            pass

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness
        capture_type = "auto" if is_auto else "manual"
        save_dir = Path(__file__).parent / "test_results" / "live_detection" / f"frame_{capture_type}_{timestamp}"
        
        results = processor.process_frame(
            frame, save_dir, save_files=save_files,
            confidence_threshold=conf_threshold,
        )
        
        if results['success']:
            if is_auto:
                logger.debug(f"[AUTO-CAPTURE] Frame saved to: {save_dir}")
            else:
                print(f"[SAVED] Frame saved to: {save_dir}")

            # Write to latest_frame_data.json for game_engine
            write_frame_data_to_json(results, frame_path=str(save_dir), capture_type=capture_type)

            if not is_auto:
                print("[SENT] Frame data sent to gameplay.py")
                print("[INFO] Run 'python3 gameplay.py' in another terminal to process this frame")
            
            return True
        else:
            if not is_auto:
                print(f"[ERROR] Failed to save frame: {results['error_message']}")
            return False

    try:
        if headless:
            print("Camera feed starting (headless). Press Ctrl+C to stop.")
        else:
            print("Camera feed starting... Press 'q' to quit.")
        if auto_capture_enabled:
            print("[AUTO-CAPTURE] Enabled - sending frames to game engine continuously")
        else:
            print("[AUTO-CAPTURE] Disabled - press 'a' to enable")
        print(f"[DEBUG] Save debug files: {'ON' if save_debug_files else 'OFF'} (press 'd' to toggle)")
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning("Failed to read frame from camera, retrying...")
                time.sleep(0.1)
                continue

            frame_count += 1

            # FPS
            now = time.time()
            fps_counter.append(now)
            if len(fps_counter) > 1:
                fps = len(fps_counter) / (fps_counter[-1] - fps_counter[0])
            else:
                fps = 0.0


            try:
                results = processor.process_frame(
                    frame,
                    save_files=False,
                    confidence_threshold=conf_threshold,
                )
                last_process_time = now
                last_results = results
                status = "SUCCESS" if results['success'] else "FAILED"
                logger.info(f"Processing result: {status} (time: {results.get('processing_time', 0):.3f}s)")
                if results.get('detection_method'):
                    logger.info(f"Detection method: {results['detection_method']}")

                # When auto capture enabled, update latest_frame_data.json for game_engine (every successful frame)
                if results['success'] and auto_capture_enabled:
                    write_frame_data_to_json(results, frame_path="", capture_type="live")
                
                # Web interface integration removed (vision-only mode)
            except Exception as e:
                logger.error(f"Processing error: {e}")
                last_results = {
                    'success': False,
                    'error_message': str(e)[:50],
                    'corners': None,
                    'warped_board': None,
                    'detected_pieces': [],
                    'piece_fen': None,
                    'processing_time': 0
                }

            if headless:
                time.sleep(0.005)
                if frame_count % 100 == 0:
                    gc.collect()
                continue

            # Compose display
            if multi_panel:
                display_image = create_multi_panel_display(
                    frame, last_results, processor.transformer,
                    show_corners, show_pieces,
                    panel1_raw_camera=panel1_raw_camera,
                    tile_scale=processor.tile_scale,
                    fps=fps,
                    ui_method="calibration",
                    ui_conf=conf_threshold,
                    calibration_system=processor.calibration_system,
                    auto_capture_enabled=auto_capture_enabled,
                    save_debug_files=save_debug_files,
                    current_classifier=current_classifier_name,
                )
                window_name = 'Live Chess Detection - Multi Panel View'
            else:
                display_frame = frame.copy()
                if last_results['success']:
                    if show_corners and last_results['corners']:
                        overlay_base = _frame_for_corner_overlay(processor, frame)
                        display_frame = _visualize_corners(overlay_base, last_results['corners'])
                    if show_pieces and last_results['detected_pieces']:
                        _DISPLAY_NAMES = {
                            "P": "W-Pawn", "p": "B-Pawn",
                            "N": "W-Knight", "n": "B-Knight",
                            "B": "W-Bishop", "b": "B-Bishop",
                            "R": "W-Rook", "r": "B-Rook",
                            "Q": "W-Queen", "q": "B-Queen",
                            "K": "W-King", "k": "B-King",
                        }
                        for label, bbox, conf in last_results['detected_pieces']:
                            x1, y1, x2, y2 = [int(c) for c in bbox]
                            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            piece_name = _DISPLAY_NAMES.get(str(label), str(label))
                            cv2.putText(display_frame, piece_name, (x1, max(24, y1 - 8)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                    if last_results.get('piece_fen'):
                        fen_text = last_results['piece_fen'][:60] + ("..." if len(last_results['piece_fen']) > 60 else "")
                        cv2.putText(display_frame, f"FEN: {fen_text}", (10, 35),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                else:
                    cv2.putText(display_frame, f"Detection failed: {last_results['error_message']}", (10, 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, display_frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                cv2.putText(display_frame, f"Model: {current_classifier_name} | m=swap", (10, display_frame.shape[0] - 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2)
                display_image = display_frame
                window_name = 'Live Chess Detection'

            # Show (resize only on first frame so user can resize and it stays)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            if not display_window_initialized:
                H, W = display_image.shape[:2]
                cv2.resizeWindow(window_name, min(W, 2560), min(H, 1440))
                display_window_initialized = True
            cv2.imshow(window_name, display_image)
            
            # Force window to stay on top and visible (Linux fix)
            try:
                import platform
                if platform.system() == "Linux":
                    # On Linux, ensure window stays visible
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 0)
            except Exception:
                pass

            # Keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # q or ESC
                break
            elif key == ord('s'):
                # Manual frame capture - save current frame bundle and send data to gameplay.py
                save_frame_for_processing(frame, processor, save_files=save_debug_files, is_auto=False)
            elif key == ord('d'):
                # Toggle debug file generation (images, results.txt, fen_board_mapping.txt)
                save_debug_files = not save_debug_files
                status = "ON" if save_debug_files else "OFF"
                print(f"[DEBUG] Save debug files: {status}")
            elif key == ord('a'):
                # Toggle automatic frame capture (sending to game engine)
                auto_capture_enabled = not auto_capture_enabled
                status = "ENABLED" if auto_capture_enabled else "DISABLED"
                print(f"[AUTO-CAPTURE] {status}")
            elif key == ord('c'):
                show_corners = not show_corners
                print(f"Corner visualization: {'ON' if show_corners else 'OFF'}")
            elif key == ord('p'):
                show_pieces = not show_pieces
                print(f"Piece overlay: {'ON' if show_pieces else 'OFF'}")
            elif key == ord('f'):
                panel1_raw_camera = not panel1_raw_camera
                status = "Raw camera" if panel1_raw_camera else "Bird's eye"
                print(f"[PANEL 1] {status}")
            elif key == ord('r'):
                print("Recalibrating...")
                success = processor.calibration_system.run_full_calibration(
                    camera_id, width=width, height=height
                )
                if success:
                    print("Recalibration successful!")
                    # Load calibration from disk and apply to transformer
                    processor._load_calibration_data()
                    processor.detector.last_corners = processor.calibration_system.board_corners
                    # Force using saved calibration
                    force_method_override = False
                    selected_method = "auto"
                else:
                    print("Recalibration failed!")
            elif key == ord('k'):
                print("Starting corner mapping...")
                # Capture current frame for corner mapping
                ret, frame = cap.read()
                if ret:
                    # Pre-load previous corners if available (so user can just rotate)
                    prev_corners = processor.calibration_system.board_corners if getattr(
                        processor.calibration_system, 'board_corners', None
                    ) else None
                    success = processor.calibration_system.select_board_corners_interactive_from_frame(
                        frame, initial_corners=prev_corners
                    )
                    if success:
                        # Update the transformer with new corners and homography
                        processor.transformer.homography_matrix = processor.calibration_system.homography_matrix
                        processor.transformer.inverse_homography_matrix = np.linalg.inv(
                            processor.calibration_system.homography_matrix
                        ) if processor.calibration_system.homography_matrix is not None else None
                        processor.transformer.has_homography = True
                        processor.transformer.is_calibrated = True
                        processor.transformer.last_corners = processor.calibration_system.board_corners
                        print("Corner mapping successful! Using new corners for detection")
                        print(f"New corners: {processor.calibration_system.board_corners}")
                    else:
                        print("Corner mapping cancelled or failed!")
                else:
                    print("Failed to capture frame for corner mapping!")
            elif key == ord('['):
                conf_threshold = max(0.20, conf_threshold - 0.05)
                print(f"Confidence: {conf_threshold:.2f}")
            elif key == ord(']'):
                conf_threshold = min(0.90, conf_threshold + 0.05)
                print(f"Confidence: {conf_threshold:.2f}")
            elif key == ord('=') or key == ord('+'):
                processor.tile_scale = min(1.5, processor.tile_scale + 0.1)
                print(f"Tile scale: {processor.tile_scale:.1f} (taller pieces)")
            elif key == ord('-'):
                processor.tile_scale = max(0.5, processor.tile_scale - 0.1)
                print(f"Tile scale: {processor.tile_scale:.1f} (shorter pieces)")
            elif key == ord('t'):
                # Reload vision modules so edits take effect without restart (grid, splitter, etc.)
                import importlib
                import vision.enhanced_homography_transformer as _ht_mod
                importlib.reload(_ht_mod)
                processor.transformer.draw_precise_grid = (
                    lambda img, board_orientation=None: _ht_mod.EnhancedHomographyTransformer.draw_precise_grid(
                        processor.transformer, img,
                        board_orientation if board_orientation is not None else getattr(processor.calibration_system, 'board_orientation', 0)
                    )
                )
                # Capture 64 tiles for training data - reloads capture_training_data too
                if last_results.get('success') and last_results.get('warped_board') is not None:
                    try:
                        import importlib
                        import sys
                        tools_dir = str(Path(__file__).parent / "data" / "chess_dataset" / "tools")
                        if tools_dir not in sys.path:
                            sys.path.insert(0, tools_dir)
                        import capture_training_data as _cap_mod
                        importlib.reload(_cap_mod)
                        capture_dir = Path(__file__).parent / "data" / "chess_dataset" / "capture_for_labeling"
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        out_dir = capture_dir / ts
                        _cap_mod.capture_tiles_to_dir(
                            last_results['warped_board'],
                            out_dir,
                            tile_size=128,
                            top_overlap_px=20,
                            board_top_margin=BOARD_TOP_MARGIN,
                            board_side_margin=BOARD_SIDE_MARGIN,
                        )
                        with open(out_dir / "FEN.txt", "w") as f:
                            f.write(f"{ts} <FEN>\n")
                        print(f"[TRAINING] Saved 64 tiles to {out_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to save training tiles: {e}")
                        print(f"[ERROR] {e}")
                else:
                    print("[TRAINING] No valid board - detect board first (wait for success)")
            elif key == ord('v'):
                # Verify FEN: dialog with text box, Fill from detected, Verify (saves misclassified to training)
                board_ort = getattr(
                    processor.calibration_system, "board_orientation", 0
                ) % 4
                show_verify_fen_dialog(
                    last_results,
                    board_top_margin=BOARD_TOP_MARGIN,
                    board_side_margin=BOARD_SIDE_MARGIN,
                    board_orientation=board_ort,
                    tile_scale=processor.tile_scale,
                )
            elif key == ord('m'):
                # Swap classifier (cycle through available models)
                if classifier_paths:
                    current_classifier_idx = (current_classifier_idx + 1) % len(classifier_paths)
                    path = classifier_paths[current_classifier_idx]
                    try:
                        from vision.piece_classifier import PieceClassifier
                        new_classifier = PieceClassifier(path, tile_size=128)
                        processor.piece_classifier = new_classifier
                        current_classifier_name = Path(path).stem
                        print(f"[MODEL] Swapped to: {current_classifier_name}")
                    except Exception as e:
                        logger.warning(f"Failed to load classifier {path}: {e}")
                        print(f"[MODEL] Failed to load {path}")
                else:
                    print("[MODEL] No classifiers found in Model/")

            time.sleep(0.005)

            if frame_count % 100 == 0:
                gc.collect()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\nLive detection stopped.")


def run_automatic_capture(camera_id=0, duration_minutes=5, width=None, height=None):
    """Run automatic image capture with processing."""
    print("\n" + "="*60)
    print("    AUTOMATIC IMAGE CAPTURE")
    print("="*60)
    print(f"Starting automatic capture for {duration_minutes} minutes...")
    print("Images will be captured and processed every 5 seconds")
    print("Press 'q' to quit early")
    print()

    cap = initialize_camera(camera_id, width=width, height=height)
    if cap is None:
        return

    classifier_path = find_piece_classifier_path()
    piece_classifier = None
    if classifier_path:
        try:
            from vision.piece_classifier import PieceClassifier
            piece_classifier = PieceClassifier(classifier_path, tile_size=128)
            if piece_classifier.is_available:
                logger.info("Piece classifier loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load piece classifier: {e}")

    processor = FrameProcessor(piece_classifier)

    # Calibration is handled by FrameProcessor's EnhancedCalibrationSystem
    # Calibration system handles loading automatically

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    capture_interval = 5  # seconds
    last_capture_time = 0
    frame_count = 0

    try:
        while time.time() < end_time:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                break

            current_time = time.time()
            if current_time - last_capture_time >= capture_interval:
                frame_count += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness
                output_dir = Path(__file__).parent / "test_results" / "automatic_capture" / f"frame_{frame_count:03d}_{timestamp}"

                results = processor.process_frame(
                    frame, output_dir, save_files=True,
                    detection_method="auto",
                    confidence_threshold=0.50
                )

                if results['success']:
                    pieces_count = len(results['detected_pieces'])
                    print(f"  Frame {frame_count}: SUCCESS - {pieces_count} pieces")
                    if results.get('detection_method'):
                        print(f"    Method: {results['detection_method']}")
                else:
                    print(f"  Frame {frame_count}: FAILED - {results['error_message']}")

                last_capture_time = current_time
                elapsed = current_time - start_time
                remaining = end_time - current_time
                print(f"    Progress: {elapsed/60:.1f}min elapsed, {remaining/60:.1f}min remaining")

            display_frame = frame.copy()
            next_capture = max(0, capture_interval - (current_time - last_capture_time))
            cv2.putText(display_frame, f"Frame: {frame_count}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Next capture in: {next_capture:.1f}s", (10, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            cv2.namedWindow('Automatic Capture', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Automatic Capture', 1440, 1080)
            cv2.imshow('Automatic Capture', display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nEarly termination requested by user")
                break

        print(f"\nAutomatic capture completed!")
        print(f"Total frames captured: {frame_count}")
        print(f"Results saved to: test_results/automatic_capture/")

    finally:
        cap.release()
        cv2.destroyAllWindows()


def run_static_image_processing():
    """Process static test images."""
    print("\n" + "="*60)
    print("    STATIC IMAGE PROCESSING")
    print("="*60)

    test_images = [
        "data/yolo_datasets/our_custom_dataset/IMG_7180.JPG",
        "data/yolo_datasets/our_custom_dataset/IMG_7178.JPG",
        "data/yolo_datasets/our_custom_dataset/IMG_7179.JPG",
        "data/yolo_datasets/our_custom_dataset/IMG_7312.JPG"
    ]

    classifier_path = find_piece_classifier_path()
    piece_classifier = None
    if classifier_path:
        try:
            from vision.piece_classifier import PieceClassifier
            piece_classifier = PieceClassifier(classifier_path, tile_size=128)
            if piece_classifier.is_available:
                logger.info("Piece classifier loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load piece classifier: {e}")

    processor = FrameProcessor(piece_classifier)

    print(f"Processing {len(test_images)} test images...\n")
    successful_detections = 0

    for i, image_path in enumerate(test_images, 1):
        full_path = str(Path(__file__).parent / image_path)
        if not Path(full_path).exists():
            logger.warning(f"Image not found: {full_path}")
            continue

        print(f"Processing image {i}/{len(test_images)}: {Path(image_path).name}")

        image = cv2.imread(full_path)
        if image is None:
            logger.error(f"Failed to load image: {full_path}")
            continue

        output_dir = Path(__file__).parent / "test_results" / "run_output" / f"image_{i}"

        results = processor.process_frame(
            image, output_dir, save_files=True,
            detection_method="auto",
            confidence_threshold=0.50
        )

        if results['success']:
            successful_detections += 1
            pieces_count = len(results['detected_pieces'])
            print(f"  SUCCESS - {pieces_count} pieces detected")
            if results.get('detection_method'):
                print(f"  Method: {results['detection_method']}")
            print(f"  Output saved to: {output_dir}")
        else:
            print(f"  FAILED - {results['error_message']}")

    print(f"\nProcessing complete!")
    print(f"Successful detections: {successful_detections}/{len(test_images)}")
    print(f"Results saved to: test_results/run_output/")


def calibrate_camera(camera_id=0, num_images=20, width=None, height=None):
    """Run camera calibration."""
    import os
    import platform
    
    if platform.system() == "Linux":
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    
    print("\n" + "="*60)
    print("    CAMERA CALIBRATION")
    print("="*60)
    print(f"Starting camera calibration with {num_images} images...")
    print("Press SPACE to capture, 'q' to quit\n")

    cap = initialize_camera(camera_id, width=width, height=height)
    if cap is None:
        return

    patterns = [(7, 7), (6, 6), (5, 5), (8, 8), (9, 9)]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objpoints = []
    imgpoints = []
    successful_pattern = None
    captured_count = 0

    try:
        while captured_count < num_images:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            best_pattern = None
            best_corners = None
            for pattern_size in patterns:
                ret_corners, chess_corners = cv2.findChessboardCorners(
                    gray, pattern_size,
                    cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                )
                if ret_corners:
                    best_pattern = pattern_size
                    best_corners = chess_corners
                    break

            display_frame = frame.copy()
            cv2.putText(display_frame, f"Captured: {captured_count}/{num_images}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            corners2 = None
            if best_pattern and best_corners is not None:
                cv2.putText(display_frame, f"Pattern: {best_pattern[0]}x{best_pattern[1]}", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                cv2.putText(display_frame, "Chessboard detected! Press SPACE to capture", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                corners2 = cv2.cornerSubPix(gray, best_corners, (11, 11), (-1, -1), criteria)
                cv2.drawChessboardCorners(display_frame, best_pattern, corners2, True)

                if successful_pattern is None:
                    successful_pattern = best_pattern
                    objp = np.zeros((best_pattern[0] * best_pattern[1], 3), np.float32)
                    objp[:, :2] = np.mgrid[0:best_pattern[0], 0:best_pattern[1]].T.reshape(-1, 2)
            else:
                cv2.putText(display_frame, "No chessboard pattern detected", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.namedWindow('Camera Calibration', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Camera Calibration', 1920, 1440)
            cv2.imshow('Camera Calibration', display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space
                if best_pattern and corners2 is not None:
                    objpoints.append(objp)
                    imgpoints.append(corners2)
                    captured_count += 1
                    print(f"Captured image {captured_count}/{num_images}")
                else:
                    print("No chessboard pattern detected in current frame!")
            elif key == ord('q'):
                print("Calibration cancelled by user")
                break

        if captured_count < 10:
            print(f"Not enough images captured ({captured_count}). Need at least 10.")
            return None

        print(f"Calibrating camera with {captured_count} images...")

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )

        if ret:
            total_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                total_error += error
            mean_error = total_error / len(objpoints)

            print("Calibration successful!")
            print(f"Mean reprojection error: {mean_error:.3f} pixels")

            calibration_data = {
                'camera_matrix': camera_matrix,
                'dist_coeffs': dist_coeffs,
                'mean_error': mean_error,
                'num_images': captured_count,
                'pattern_size': successful_pattern,
                'timestamp': datetime.now().isoformat()
            }

            calibration_dir = Path(__file__).parent / "test_results" / "camera_calibration"
            calibration_dir.mkdir(parents=True, exist_ok=True)
            calibration_file = calibration_dir / f"calibration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.npz"
            np.savez(str(calibration_file), **calibration_data)
            print(f"Calibration data saved to: {calibration_file}")
            return calibration_data
        else:
            print("Calibration failed!")
            return None

    finally:
        cap.release()
        cv2.destroyAllWindows()


def interactive_camera_selection():
    """Interactive camera selection."""
    print("\n" + "="*60)
    print("    CAMERA SELECTION")
    print("="*60)

    available_cameras = enumerate_available_cameras()
    if not available_cameras:
        print("No cameras detected. Using default camera 0.")
        return 0

    print("\nAvailable cameras:")
    for i, (camera_id, is_available, camera_name) in enumerate(available_cameras, 1):
        status = "Available" if is_available else "Unavailable"
        print(f"{i}. {camera_name} - {status}")

    try:
        choice = int(input(f"Select camera option (1-{len(available_cameras)}): ").strip())
        if 1 <= choice <= len(available_cameras):
            selected_camera = available_cameras[choice - 1]
            camera_id, is_available, camera_name = selected_camera
            if is_available:
                print(f"Selected: {camera_name}")
                return camera_id
            else:
                print("Selected camera is not available, using default (0)")
                return 0
        else:
            print("Invalid choice, using default camera")
            return 0
    except ValueError:
        print("Invalid input, using default camera")
        return 0


def run_corner_mapping_live(frame, calibration_system):
    """
    Run corner mapping during live detection.
    
    Args:
        frame: Current camera frame
        calibration_system: Calibration system instance
        
    Returns:
        bool: True if corner mapping was successful
    """
    print("\n" + "="*60)
    print("    CORNER MAPPING - LIVE DETECTION")
    print("="*60)
    print("Instructions:")
    print("1. Click on the four corners of the chessboard in this order:")
    print("   - Top-Left corner")
    print("   - Top-Right corner") 
    print("   - Bottom-Right corner")
    print("   - Bottom-Left corner")
    print("2. Press ENTER to confirm the corners")
    print("3. Press ESC to cancel")
    print("="*60)
    
    try:
        success = calibration_system.select_board_corners_interactive(frame)
        if success:
            print("\n[SUCCESS] Corner mapping completed!")
            print(f"New corners: {calibration_system.board_corners}")
            
            # Save the calibration data
            calibration_system.save_calibration_data()
            print("Corner mapping saved to calibration files.")
            return True
        else:
            print("\n[INFO] Corner mapping cancelled.")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Corner mapping failed: {e}")
        return False


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Chess Vision Detection Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --live
  python run.py --live --camera 1
  python run.py --live --camera 0 --width 3840 --height 2160   # 4K USB camera
  python run.py --live --no-save-debug   # Disable debug file generation
  python run.py --live --headless        # No GUI; updates gameplay_data/latest_frame_data.json
  python run.py --static
  python run.py --auto --duration 10
  python run.py --calibrate
        """
    )

    # Modes
    parser.add_argument('--live', action='store_true', help='Run live camera detection')
    parser.add_argument('--static', action='store_true', help='Run static image processing')
    parser.add_argument('--auto', action='store_true', help='Run automatic image capture')
    parser.add_argument('--calibrate', action='store_true', help='Run camera calibration')

    # Camera options
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID (default: 0)')
    parser.add_argument(
        '--width',
        type=int,
        default=0,
        metavar='W',
        help='Capture width (0=auto: tries 4K, QHD, 1080p, …). Use with --height to lock a mode.',
    )
    parser.add_argument(
        '--height',
        type=int,
        default=0,
        metavar='H',
        help='Capture height (0=auto). Example for 4K: --width 3840 --height 2160',
    )

    # Options
    parser.add_argument('--duration', type=int, default=5, help='Duration in minutes for automatic capture (default: 5)')
    parser.add_argument('--cal-images', type=int, default=20, help='Number of images for calibration (default: 20)')
    parser.add_argument('--no-save-debug', action='store_true',
                        help='Disable saving debug files (images, results.txt) when capturing in live mode')
    parser.add_argument(
        '--headless',
        action='store_true',
        help='With --live only: no OpenCV windows; vision loop still writes gameplay_data/latest_frame_data.json (Ctrl+C to quit)',
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    cam_w = args.width if args.width > 0 else None
    cam_h = args.height if args.height > 0 else None

    print("="*80)
    print("    CHESS VISION DETECTION RUNNER - FIXED (updated)")
    print("    Board Detection + Piece Classification + FEN Generation")
    print("="*80)

    try:
        if args.calibrate:
            calibrate_camera(args.camera, args.cal_images, width=cam_w, height=cam_h)
        elif args.auto:
            run_automatic_capture(args.camera, args.duration, width=cam_w, height=cam_h)
        elif args.live:
            if args.headless:
                os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            # Force calibration before live detection
            print("\n" + "="*60)
            print("    CALIBRATION REQUIRED FOR LIVE DETECTION")
            print("="*60)
            print("Live detection requires calibration for stable board detection.")
            print("This ensures consistent corner detection without fluctuation.")
            
            # Check if calibration already exists
            from vision.enhanced_calibration_system import EnhancedCalibrationSystem
            calibration_system = EnhancedCalibrationSystem(output_size=BOARD_OUTPUT_SIZE)
            has_calibration = calibration_system.load_calibration_data()
            
            if has_calibration:
                print(f"\n[SUCCESS] Existing calibration found!")
                print(f"Board corners: {calibration_system.board_corners}")
                print(f"Camera calibration error: {calibration_system.calibration_error:.3f}px")
                print("Using existing calibration for live detection.")
            else:
                print("\n[ERROR] No calibration data found.")
                print("Calibration is required for live detection.")
                if args.headless:
                    print("Headless mode cannot prompt for calibration. Run once with GUI to calibrate, then retry.")
                    sys.exit(1)
                response = input("Do you want to calibrate now? (y/n): ").strip().lower()
                if response == 'y':
                    print("Starting calibration...")
                    success = calibration_system.run_full_calibration(
                        args.camera, width=cam_w, height=cam_h
                    )
                    if not success:
                        print("Calibration failed. Exiting.")
                        sys.exit(1)
                    print("Calibration completed successfully!")
                else:
                    print("Calibration is required for live detection. Exiting.")
                    sys.exit(1)
            
            # Now start live detection
            print("\n" + "="*60)
            print("    STARTING LIVE DETECTION")
            print("="*60)
            run_live_camera_detection(
                args.camera,
                save_debug=not args.no_save_debug,
                width=cam_w,
                height=cam_h,
                headless=args.headless,
            )
        elif args.static:
            run_static_image_processing()
        else:
            # Interactive menu
            print("\nChoose detection mode:")
            print("1. Live camera detection (real-time)")
            print("2. Static image processing (test images)")
            print("3. Automatic image capture (every 5 seconds)")
            print("4. Camera calibration\n")

            choice = input("Select mode (1-4): ").strip()

            if choice == "1":
                camera_id = interactive_camera_selection()
                
                # Force calibration before live detection
                print("\n" + "="*60)
                print("    CALIBRATION REQUIRED FOR LIVE DETECTION")
                print("="*60)
                print("Live detection requires calibration for stable board detection.")
                print("This ensures consistent corner detection without fluctuation.")
                
                # Check if calibration already exists
                from vision.enhanced_calibration_system import EnhancedCalibrationSystem
                calibration_system = EnhancedCalibrationSystem(output_size=BOARD_OUTPUT_SIZE)
                has_calibration = calibration_system.load_calibration_data()
                
                if has_calibration:
                    print(f"\n[SUCCESS] Existing calibration found!")
                    print(f"Board corners: {calibration_system.board_corners}")
                    print(f"Camera calibration error: {calibration_system.calibration_error:.3f}px")
                    
                    response = input("\nDo you want to use existing calibration or recalibrate? (u/r): ").strip().lower()
                    if response == 'r':
                        print("Starting recalibration...")
                        success = calibration_system.run_full_calibration(camera_id)
                        if not success:
                            print("Recalibration failed. Exiting.")
                            sys.exit(1)
                        print("Recalibration completed successfully!")
                    else:
                        print("Using existing calibration.")
                else:
                    print("\n[ERROR] No calibration data found.")
                    print("Calibration is required for live detection.")
                    
                    response = input("Do you want to calibrate now? (y/n): ").strip().lower()
                    if response == 'y':
                        print("Starting calibration...")
                        success = calibration_system.run_full_calibration(camera_id)
                        if not success:
                            print("Calibration failed. Exiting.")
                            sys.exit(1)
                        print("Calibration completed successfully!")
                    else:
                        print("Calibration is required for live detection. Exiting.")
                        sys.exit(1)
                
                # Now start live detection
                print("\n" + "="*60)
                print("    STARTING LIVE DETECTION")
                print("="*60)
                run_live_camera_detection(camera_id)
            elif choice == "2":
                run_static_image_processing()
            elif choice == "3":
                camera_id = interactive_camera_selection()
                try:
                    duration = int(input("Enter duration in minutes (default 5): ").strip() or "5")
                except ValueError:
                    duration = 5
                run_automatic_capture(camera_id, duration)
            elif choice == "4":
                camera_id = interactive_camera_selection()
                
                # Use EnhancedCalibrationSystem for proper calibration with manual corner selection
                from vision.enhanced_calibration_system import EnhancedCalibrationSystem
                calibration_system = EnhancedCalibrationSystem(output_size=BOARD_OUTPUT_SIZE)
                
                print("\n" + "="*60)
                print("    ENHANCED CAMERA CALIBRATION")
                print("="*60)
                print("This will calibrate the camera and allow you to manually select board corners.")
                print("The manual corner selection ensures accurate board detection.")
                print()
                
                success = calibration_system.run_full_calibration(camera_id)
                if success:
                    print("\n[SUCCESS] Calibration completed successfully!")
                    print("You can now use live detection with accurate board detection.")
                else:
                    print("\n[ERROR] Calibration failed. Please try again.")
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()