#!/usr/bin/env python3
"""
Enhanced Camera and Board Calibration System
Combines camera calibration with manual board corner selection and persistent storage.

@author Abhay Prasanna Rao
"""

import cv2
import numpy as np
import json
import logging
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.enhanced_homography_transformer import EnhancedHomographyTransformer
from vision.vision_config import undistort_and_orient_frame

logger = logging.getLogger(__name__)


class EnhancedCalibrationSystem:
    """
    Enhanced calibration system that combines camera calibration with manual board corner selection.
    """
    
    def __init__(self, output_size=800):
        """
        Initialize the calibration system.
        
        Args:
            output_size: Size for bird's eye view output
        """
        self.output_size = output_size
        self.transformer = EnhancedHomographyTransformer(output_size)
        
        # Calibration data storage
        self.calibration_dir = Path("config/calibration")
        self.calibration_dir.mkdir(parents=True, exist_ok=True)
        
        # Camera calibration data
        self.camera_matrix = None
        self.dist_coeffs = None
        self.calibration_error = None
        
        # Board corner data
        self.board_corners = None
        self.homography_matrix = None
        self.is_calibrated = False
        # Board orientation: 0=TL=a8, 1=90°CW, 2=180°, 3=270°CW (set during calibration with 'r' key)
        self.board_orientation = 0
        # Add to orientation for grid labels when warp convention differs (0 or 2; set in board_corners.json)
        self.label_orientation_offset = 0

        # Interactive selection state (no corner labels - user picks any 4 corners)
        self.corners = []
        self.current_corner = 0
        self.colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
    
    def load_calibration_data(self) -> bool:
        """
        Load existing calibration data from storage.
        
        Returns:
            True if calibration data was loaded successfully
        """
        try:
            # Load camera calibration
            camera_file = self.calibration_dir / "camera_calibration.json"
            if camera_file.exists():
                with open(camera_file, 'r') as f:
                    camera_data = json.load(f)
                    self.camera_matrix = np.array(camera_data['camera_matrix'])
                    self.dist_coeffs = np.array(camera_data['dist_coeffs'])
                    self.calibration_error = camera_data.get('mean_error', 0.0)
                    logger.info(f"Loaded camera calibration (error: {self.calibration_error:.3f}px)")
            
            # Load board corners
            corners_file = self.calibration_dir / "board_corners.json"
            if corners_file.exists():
                with open(corners_file, 'r') as f:
                    corners_data = json.load(f)
                    self.board_corners = [tuple(corner) for corner in corners_data['corners']]
                    self.homography_matrix = np.array(corners_data.get('homography_matrix', []))
                    self.is_calibrated = corners_data.get('is_calibrated', False)
                    self.board_orientation = int(corners_data.get('board_orientation', 0)) % 4
                    # Add 2 to fix a8<->h8, a1<->a8 label swap when warp/corner convention differs
                    self.label_orientation_offset = int(corners_data.get('label_orientation_offset', 0))
                    logger.info(f"Loaded board corners: {self.board_corners}, orientation: {self.board_orientation}")
            
            return self.is_calibrated
            
        except Exception as e:
            logger.error(f"Failed to load calibration data: {e}")
            return False
    
    def save_calibration_data(self) -> bool:
        """
        Save calibration data to storage.
        
        Returns:
            True if data was saved successfully
        """
        try:
            # Save camera calibration
            if self.camera_matrix is not None and self.dist_coeffs is not None:
                camera_data = {
                    'camera_matrix': self.camera_matrix.tolist(),
                    'dist_coeffs': self.dist_coeffs.tolist(),
                    'mean_error': self.calibration_error,
                    'timestamp': datetime.now().isoformat()
                }
                camera_file = self.calibration_dir / "camera_calibration.json"
                with open(camera_file, 'w') as f:
                    json.dump(camera_data, f, indent=2)
                logger.info(f"Saved camera calibration to {camera_file}")
            
            # Save board corners
            if self.board_corners is not None:
                corners_data = {
                    'corners': self.board_corners,
                    'homography_matrix': self.homography_matrix.tolist() if self.homography_matrix is not None else [],
                    'is_calibrated': self.is_calibrated,
                    'board_orientation': self.board_orientation,
                    'label_orientation_offset': getattr(self, 'label_orientation_offset', 0),
                    'timestamp': datetime.now().isoformat()
                }
                corners_file = self.calibration_dir / "board_corners.json"
                with open(corners_file, 'w') as f:
                    json.dump(corners_data, f, indent=2)
                logger.info(f"Saved board corners to {corners_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save calibration data: {e}")
            return False
    
    def calibrate_camera(self, camera_id=0, droidcam_ip=None, num_images=15, width=None, height=None) -> bool:
        """
        Perform camera calibration using chessboard patterns.
        
        Args:
            camera_id: Camera device ID
            droidcam_ip: DroidCam IP address
            num_images: Number of calibration images to capture
            
        Returns:
            True if calibration was successful
        """
        print("\n" + "="*60)
        print("    CAMERA CALIBRATION")
        print("="*60)
        print(f"Starting camera calibration with {num_images} images...")
        print("Press SPACE to capture, 'q' to quit")
        print("Move the chessboard to different positions and angles\n")
        
        # Initialize camera
        cap = self._initialize_camera(camera_id, width=width, height=height)
        if cap is None:
            return False
        
        # Calibration parameters
        patterns = [(7, 7), (6, 6), (5, 5), (8, 8), (9, 9)]
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        objpoints = []
        imgpoints = []
        captured_count = 0
        
        try:
            while captured_count < num_images:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                
                # Undistort + optional 180° if we have previous calibration
                if self.camera_matrix is not None and self.dist_coeffs is not None:
                    frame = undistort_and_orient_frame(
                        frame, self.camera_matrix, self.dist_coeffs
                    )
                
                # Try to detect chessboard pattern
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
                
                # Display frame with status
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Captured: {captured_count}/{num_images}", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
                if best_corners is not None:
                    # Refine corners
                    refined_corners = cv2.cornerSubPix(
                        gray, best_corners, (11, 11), (-1, -1), criteria
                    )
                    
                    # Draw detected pattern
                    cv2.drawChessboardCorners(display_frame, best_pattern, refined_corners, True)
                    cv2.putText(display_frame, f"Pattern: {best_pattern}", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Press SPACE to capture", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # Prepare object points
                    objp = np.zeros((best_pattern[0] * best_pattern[1], 3), np.float32)
                    objp[:, :2] = np.mgrid[0:best_pattern[0], 0:best_pattern[1]].T.reshape(-1, 2)
                else:
                    cv2.putText(display_frame, "No chessboard detected", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(display_frame, "Move chessboard and try again", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show frame
                cv2.namedWindow('Camera Calibration', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Camera Calibration', 1280, 720)
                cv2.imshow('Camera Calibration', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space
                    if best_corners is not None:
                        objpoints.append(objp)
                        imgpoints.append(refined_corners)
                        captured_count += 1
                        print(f"Captured image {captured_count}/{num_images}")
                    else:
                        print("No chessboard pattern detected in current frame!")
                elif key == ord('q'):
                    print("Calibration cancelled by user")
                    break
            
            if captured_count < 10:
                print(f"Not enough images captured ({captured_count}). Need at least 10.")
                return False
            
            print(f"Calibrating camera with {captured_count} images...")
            
            # Perform calibration with conservative distortion modeling
            # Use only k1, k2 (radial distortion) and p1, p2 (tangential distortion)
            # This prevents extreme distortion coefficients
            flags = cv2.CALIB_FIX_K3  # Fix k3 to 0 to prevent extreme distortion
            ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, gray.shape[::-1], None, None, flags=flags
            )
            
            if ret:
                # Calculate reprojection error
                total_error = 0
                for i in range(len(objpoints)):
                    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
                    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                    total_error += error
                mean_error = total_error / len(objpoints)
                
                # Validate distortion coefficients are reasonable
                k1, k2, p1, p2, k3 = dist_coeffs[0] if len(dist_coeffs[0]) >= 5 else (0, 0, 0, 0, 0)
                
                # Check if distortion coefficients are within reasonable bounds
                if abs(k1) > 1.0 or abs(k2) > 1.0 or abs(k3) > 1.0:
                    print(f"WARNING: Extreme distortion coefficients detected!")
                    print(f"k1={k1:.3f}, k2={k2:.3f}, k3={k3:.3f}")
                    print("This may cause visual distortion. Consider recalibrating with better conditions.")
                    
                    # Optionally, clamp extreme values
                    dist_coeffs_clamped = dist_coeffs.copy()
                    dist_coeffs_clamped[0][0] = max(-1.0, min(1.0, k1))  # k1
                    dist_coeffs_clamped[0][1] = max(-1.0, min(1.0, k2))  # k2
                    if len(dist_coeffs_clamped[0]) > 4:
                        dist_coeffs_clamped[0][4] = max(-1.0, min(1.0, k3))  # k3
                    
                    print("Using clamped distortion coefficients for better stability.")
                    dist_coeffs = dist_coeffs_clamped
                
                # Store calibration data
                self.camera_matrix = camera_matrix
                self.dist_coeffs = dist_coeffs
                self.calibration_error = mean_error
                
                print("Camera calibration successful!")
                print(f"Mean reprojection error: {mean_error:.3f} pixels")
                print(f"Distortion coefficients: k1={k1:.3f}, k2={k2:.3f}, k3={k3:.3f}")
                
                return True
            else:
                print("Camera calibration failed!")
                return False
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def select_board_corners_interactive_from_frame(
        self, frame, initial_corners: Optional[List[Tuple[float, float]]] = None
    ) -> bool:
        """
        Interactive board corner selection - no corner labels. After 4 corners,
        shows black/white orientation overlay. Press 'r' to rotate, 's' to save.

        If initial_corners (e.g. from previous calibration) is provided and valid,
        they are pre-loaded so you can press 's' immediately to go to orientation.
        """
        print("\n" + "="*60)
        print("    BOARD CORNER SELECTION")
        print("="*60)
        if initial_corners and len(initial_corners) == 4 and self._validate_corners(initial_corners):
            print("Loaded previous 4 corners. Press 's' to go to orientation, or click to replace.")
        else:
            print("Click on the four corners of the chessboard (any order)")
        print("Press 's' after 4 corners for orientation, 'r' to reset, 'q' to quit\n")

        if frame is None:
            print("Error: No frame provided")
            return False

        self._temp_corners = list(initial_corners) if initial_corners and len(initial_corners) == 4 else []

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(self._temp_corners) < 4:
                    self._temp_corners.append((x, y))
                    print(f"Corner {len(self._temp_corners)}: ({x}, {y})")
                else:
                    print("All 4 corners selected. Press 's' for orientation phase, 'r' to reset.")

        window_name = "Select Board Corners"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        work = undistort_and_orient_frame(frame, self.camera_matrix, self.dist_coeffs)
        height, width = work.shape[:2]
        cv2.resizeWindow(window_name, min(width, 1200), min(height, 800))
        cv2.setMouseCallback(window_name, mouse_callback)

        try:
            while True:
                display_frame = work.copy()
                for i, (x, y) in enumerate(self._temp_corners):
                    cv2.circle(display_frame, (x, y), 8, (0, 255, 0), -1)
                    cv2.putText(display_frame, str(i + 1), (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"Corners: {len(self._temp_corners)}/4",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display_frame, "s=orientation | r=reset | q=quit", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow(window_name, display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    print("Corner selection cancelled")
                    return False
                elif key == ord('s'):
                    if len(self._temp_corners) == 4 and self._validate_corners(self._temp_corners):
                        break
                    elif len(self._temp_corners) < 4:
                        print(f"Select all 4 corners first. Currently: {len(self._temp_corners)}")
                    else:
                        print("Invalid corners. Press 'r' to reset.")
                elif key == ord('r'):
                    self._temp_corners = []
                    print("Reset. Select corners again.")
        except KeyboardInterrupt:
            cv2.destroyWindow(window_name)
            return False

        # Orientation phase: overlay with black/white bars
        cv2.destroyWindow(window_name)  # Close corner window before orientation
        self.board_corners = self._temp_corners.copy()
        if not self._run_orientation_phase(frame, self.board_corners):
            return False

        self._calculate_homography_from_corners()
        return True

    def _run_orientation_phase(self, frame, corners) -> bool:
        """
        After 4 corners: show warped overlay with black/white bars.
        Black bars = where black pieces go (ranks 7-8). White bars = white pieces (ranks 1-2).
        Press 'r' to rotate 90°. Press 's' to save orientation.
        """
        print("\n" + "="*60)
        print("    ORIENTATION")
        print("="*60)
        print("Black bars = black pieces (ranks 7-8). White bars = white pieces (ranks 1-2).")
        print("Press 'r' to rotate until correct. Press 's' to save.\n")

        ordered = self._order_quad(corners)
        S = self.output_size if isinstance(self.output_size, int) else self.output_size[0]
        dst = np.float32([[0, 0], [S - 1, 0], [S - 1, S - 1], [0, S - 1]])
        H = cv2.getPerspectiveTransform(ordered, dst)
        if H is None:
            print("Failed to compute homography for overlay")
            return False

        img = undistort_and_orient_frame(frame, self.camera_matrix, self.dist_coeffs)
        warped = cv2.warpPerspective(img, H, (S, S))

        window_name = "Board Orientation"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, min(S, 800), min(S, 800))

        try:
            while True:
                disp = warped.copy()
                # Draw black/white overlays based on orientation
                # orientation 0: top 2 rows = black, bottom 2 = white
                # orientation 1: right 2 cols = black, left 2 = white
                # orientation 2: bottom 2 = black, top 2 = white
                # orientation 3: left 2 cols = black, right 2 = white
                k = self.board_orientation % 4
                sq = S / 8
                # Black = ranks 7-8, White = ranks 1-2. Orientation: which edge is "top" (a8-h8).
                if k == 0:  # Top=black, bottom=white
                    black_rects = [(0, 0, S, int(2 * sq))]
                    white_rects = [(0, int(6 * sq), S, S)]
                elif k == 1:  # Right=black, left=white (board rotated 90 CW)
                    black_rects = [(int(6 * sq), 0, S, S)]
                    white_rects = [(0, 0, int(2 * sq), S)]
                elif k == 2:  # Bottom=black, top=white
                    black_rects = [(0, int(6 * sq), S, S)]
                    white_rects = [(0, 0, S, int(2 * sq))]
                else:  # k==3: Left=black, right=white
                    black_rects = [(0, 0, int(2 * sq), S)]
                    white_rects = [(int(6 * sq), 0, S, S)]

                overlay = disp.copy()
                for (x1, y1, x2, y2) in black_rects:
                    cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (20, 20, 20), -1)
                for (x1, y1, x2, y2) in white_rects:
                    cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (200, 200, 200), -1)
                cv2.addWeighted(overlay, 0.5, disp, 0.5, 0, disp)
                if k == 0:
                    cv2.putText(disp, "BLACK", (int(S // 2 - 35), int(1.2 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(disp, "WHITE", (int(S // 2 - 35), int(7.2 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
                elif k == 1:
                    cv2.putText(disp, "BLACK", (int(6.5 * sq), int(S // 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(disp, "WHITE", (int(0.5 * sq), int(S // 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
                elif k == 2:
                    cv2.putText(disp, "BLACK", (int(S // 2 - 35), int(6.8 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(disp, "WHITE", (int(S // 2 - 35), int(0.8 * sq)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
                else:
                    cv2.putText(disp, "BLACK", (int(0.5 * sq), int(S // 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(disp, "WHITE", (int(6.5 * sq), int(S // 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
                cv2.putText(disp, "r=rotate | s=save", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow(window_name, disp)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    break
                elif key == ord('r'):
                    self.board_orientation = (self.board_orientation + 1) % 4
                    print(f"Orientation rotated: {self.board_orientation * 90}°")
        except KeyboardInterrupt:
            cv2.destroyWindow(window_name)
            return False

        cv2.destroyWindow(window_name)
        return True

    def _validate_corners(self, corners):
        """Validate that the selected corners form a reasonable rectangle."""
        if len(corners) != 4:
            return False
        
        # Check if corners form a reasonable quadrilateral
        # Basic checks: no duplicate points, reasonable distances
        for i in range(4):
            for j in range(i+1, 4):
                if corners[i] == corners[j]:
                    return False
        
        # Check minimum distance between corners
        min_distance = 50  # pixels
        for i in range(4):
            for j in range(i+1, 4):
                dist = np.sqrt((corners[i][0] - corners[j][0])**2 + (corners[i][1] - corners[j][1])**2)
                if dist < min_distance:
                    return False
        
        return True

    def _calculate_homography_from_corners(self):
        """Calculate homography. Always map [TL, TR, BR, BL] to square (no rotation).
        Orientation is used only for FEN square mapping, not for the warp."""
        if len(self.board_corners) != 4:
            return False
        ordered = self._order_quad(self.board_corners)  # [TL, TR, BR, BL]
        src_points = np.array(ordered, dtype=np.float32)  # Fixed homography
        target_size = self.output_size if isinstance(self.output_size, int) else self.output_size[0]
        target_corners = np.array([
            [0, 0],
            [target_size - 1, 0],
            [target_size - 1, target_size - 1],
            [0, target_size - 1]
        ], dtype=np.float32)
        self.homography_matrix = cv2.getPerspectiveTransform(
            np.array(src_points, dtype=np.float32), target_corners
        )
        self.is_calibrated = True
        print(f"Homography matrix calculated successfully")
        print(f"Determinant: {np.linalg.det(self.homography_matrix):.6f}")
        print(f"Board corners (ordered): {self._order_quad(self.board_corners)}")
        self.save_calibration_data()
        print("Calibration data saved to files")
        return True

    def _order_quad(self, pts):
        """Order quadrilateral corners as TL, TR, BR, BL (same as existing system)."""
        pts = np.asarray(pts, dtype=np.float32)
        s = pts.sum(axis=1)
        d = np.diff(pts, axis=1).ravel()
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(d)]
        bl = pts[np.argmax(d)]
        return np.array([tl, tr, br, bl], dtype=np.float32)

    def select_board_corners_interactive(self, camera_id=0, droidcam_ip=None, width=None, height=None) -> bool:
        """Interactive board corner selection - no corner labels, then orientation phase."""
        print("\n" + "="*60)
        print("    BOARD CORNER SELECTION")
        print("="*60)
        print("Click the four corners of the chessboard (any order)")
        print("Press 's' after 4 corners for orientation, 'r' to reset, 'q' to quit\n")
        
        # Initialize camera
        cap = self._initialize_camera(camera_id, width=width, height=height)
        if cap is None:
            return False
        
        self.corners = []
        try:
            last_raw = None
            while True:
                ret, raw = cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                last_raw = raw
                frame = undistort_and_orient_frame(
                    raw, self.camera_matrix, self.dist_coeffs
                )
                display_frame = frame.copy()
                for i, corner in enumerate(self.corners):
                    x, y = int(corner[0]), int(corner[1])
                    cv2.circle(display_frame, (x, y), 15, self.colors[i], -1)
                    cv2.putText(display_frame, str(i + 1), (x + 20, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.colors[i], 3)
                if len(self.corners) == 4:
                    pts = np.array(self.corners, dtype=np.int32)
                    cv2.polylines(display_frame, [pts], True, (255, 255, 255), 3)
                cv2.putText(display_frame, f"Corners: {len(self.corners)}/4", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.putText(display_frame, "s=orientation | r=reset | q=quit", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.namedWindow('Board Corner Selection', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Board Corner Selection', 1280, 720)
                cv2.imshow('Board Corner Selection', display_frame)
                cv2.setMouseCallback('Board Corner Selection', self._mouse_callback)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s') and len(self.corners) == 4 and self._validate_corners(self.corners):
                    break
                elif key == ord('r'):
                    self.corners = []
                    print("Reset.")
                elif key == ord('q'):
                    return False
            self.board_corners = self.corners.copy()
            if last_raw is None:
                return False
            if not self._run_orientation_phase(last_raw, self.board_corners):
                return False
            self._calculate_homography_from_corners()
            self.transformer.homography_matrix = self.homography_matrix
            self.transformer.inverse_homography_matrix = np.linalg.inv(self.homography_matrix)
            self.transformer.has_homography = True
            self.transformer.is_calibrated = True
            print("Board corner selection successful!")
            self._show_validation(last_raw)
            return True
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for corner selection (no corner labels)."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.corners) < 4:
                self.corners.append((x, y))
                print(f"Corner {len(self.corners)}: ({x}, {y})")
    
    def _show_validation(self, frame):
        """Show validation of the selected corners."""
        print("\n" + "="*60)
        print("    VALIDATION")
        print("="*60)
        
        # Generate bird's eye view
        birdseye = self.transformer.transform_to_birdseye(frame)
        if birdseye is not None:
            # Add grid overlay
            board_ort = getattr(self, 'board_orientation', 0)
            birdseye_with_grid = self.transformer.draw_precise_grid(birdseye, board_orientation=board_ort)
            
            # Show validation window
            cv2.namedWindow('Validation - Bird\'s Eye View', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Validation - Bird\'s Eye View', 800, 800)
            cv2.imshow('Validation - Bird\'s Eye View', birdseye_with_grid)
            
            print("Is the board mapping correct? (y/n)")
            print("Press 'y' to confirm, 'n' to reject")
            
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('y'):
                    print("Board mapping confirmed!")
                    cv2.destroyAllWindows()
                    return True
                elif key == ord('n'):
                    print("Board mapping rejected. Please try again.")
                    cv2.destroyAllWindows()
                    return False
        else:
            print("Failed to generate bird's eye view for validation")
            return False
    
    def _initialize_camera(self, camera_id=0, width=None, height=None):
        """Initialize camera capture."""
        from vision.camera_utils import initialize_camera_robust
        
        cap = initialize_camera_robust(camera_id, width=width, height=height)
        if cap is None:
            raise RuntimeError(f"Failed to open camera {camera_id}")
        
        return cap
    
    def run_full_calibration(self, camera_id=0, width=None, height=None) -> bool:
        """
        Run the complete calibration process with a single camera connection.
        
        Args:
            camera_id: Camera device ID
            droidcam_ip: DroidCam IP address
            
        Returns:
            True if calibration was successful
        """
        print("\n" + "="*80)
        print("    ENHANCED CALIBRATION SYSTEM")
        print("="*80)
        print("This will perform camera calibration and board corner selection.")
        print("The calibration data will be saved for future use.\n")
        
        # Check if calibration already exists
        if self.load_calibration_data():
            print("Existing calibration data found!")
            print(f"Camera calibration error: {self.calibration_error:.3f}px")
            print(f"Board corners: {self.board_corners}")
            print("Starting recalibration...")
        
        # Initialize camera once for the entire process
        cap = self._initialize_camera(camera_id, width=width, height=height)
        if cap is None:
            print("Failed to initialize camera!")
            return False
        
        try:
            # Step 1: Camera calibration
            print("\nStep 1: Camera Calibration")
            if not self._calibrate_camera_with_cap(cap):
                print("Camera calibration failed!")
                return False
            
            # Step 2: Board corner selection
            print("\nStep 2: Board Corner Selection")
            if not self._select_board_corners_with_cap(cap):
                print("Board corner selection failed!")
                return False
            
            # Step 3: Save calibration data
            print("\nStep 3: Saving Calibration Data")
            if self.save_calibration_data():
                print("Calibration data saved successfully!")
                print(f"Camera calibration error: {self.calibration_error:.3f}px")
                print(f"Board corners: {self.board_corners}")
                return True
            else:
                print("Failed to save calibration data!")
                return False
                
        finally:
            # Always release camera at the end
            cap.release()
            cv2.destroyAllWindows()
    
    def _calibrate_camera_with_cap(self, cap) -> bool:
        """
        Calibrate camera using an existing camera connection.
        
        Args:
            cap: OpenCV VideoCapture object
            
        Returns:
            True if calibration was successful
        """
        patterns = [(7, 7), (6, 6), (5, 5), (8, 8), (9, 9)]
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        objpoints = []
        imgpoints = []
        successful_pattern = None
        captured_count = 0
        num_images = 15
        
        print(f"Starting camera calibration with {num_images} images...")
        print("Press SPACE to capture, 'q' to quit")
        print("Move the chessboard to different positions and angles\n")
        
        try:
            while captured_count < num_images:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                best_corners = None
                best_pattern = None
                
                # Try different pattern sizes
                for pattern_size in patterns:
                    ret_corners, chess_corners = cv2.findChessboardCorners(
                        gray, pattern_size,
                        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                    )
                    if ret_corners:
                        best_corners = chess_corners
                        best_pattern = pattern_size
                        break
                
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Captured: {captured_count}/{num_images}", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
                if best_corners is not None:
                    # Refine corners
                    refined_corners = cv2.cornerSubPix(
                        gray, best_corners, (11, 11), (-1, -1), criteria
                    )
                    
                    # Draw detected pattern
                    cv2.drawChessboardCorners(display_frame, best_pattern, refined_corners, True)
                    cv2.putText(display_frame, f"Pattern: {best_pattern}", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Press SPACE to capture", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # Prepare object points
                    objp = np.zeros((best_pattern[0] * best_pattern[1], 3), np.float32)
                    objp[:, :2] = np.mgrid[0:best_pattern[0], 0:best_pattern[1]].T.reshape(-1, 2)
                else:
                    cv2.putText(display_frame, "No chessboard detected", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(display_frame, "Move chessboard and try again", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show frame
                cv2.namedWindow('Camera Calibration', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Camera Calibration', 1280, 720)
                cv2.imshow('Camera Calibration', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space
                    if best_corners is not None:
                        objpoints.append(objp)
                        imgpoints.append(refined_corners)
                        captured_count += 1
                        print(f"Captured image {captured_count}/{num_images}")
                    else:
                        print("No chessboard pattern detected in current frame!")
                elif key == ord('q'):
                    print("Calibration cancelled by user")
                    break
            
            if captured_count < 10:
                print(f"Not enough images captured ({captured_count}). Need at least 10.")
                return False
            
            print(f"Calibrating camera with {captured_count} images...")
            
            # Perform calibration with conservative distortion modeling
            flags = cv2.CALIB_FIX_K3  # Fix k3 to 0 to prevent extreme distortion
            ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, gray.shape[::-1], None, None, flags=flags
            )
            
            if ret:
                # Calculate reprojection error
                total_error = 0
                for i in range(len(objpoints)):
                    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
                    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                    total_error += error
                mean_error = total_error / len(objpoints)
                
                # Validate distortion coefficients are reasonable
                k1, k2, p1, p2, k3 = dist_coeffs[0] if len(dist_coeffs[0]) >= 5 else (0, 0, 0, 0, 0)
                
                # Check if distortion coefficients are within reasonable bounds
                if abs(k1) > 1.0 or abs(k2) > 1.0 or abs(k3) > 1.0:
                    print(f"WARNING: Extreme distortion coefficients detected!")
                    print(f"k1={k1:.3f}, k2={k2:.3f}, k3={k3:.3f}")
                    print("This may cause visual distortion. Consider recalibrating with better conditions.")
                    
                    # Optionally, clamp extreme values
                    dist_coeffs_clamped = dist_coeffs.copy()
                    dist_coeffs_clamped[0][0] = max(-1.0, min(1.0, k1))  # k1
                    dist_coeffs_clamped[0][1] = max(-1.0, min(1.0, k2))  # k2
                    if len(dist_coeffs_clamped[0]) > 4:
                        dist_coeffs_clamped[0][4] = max(-1.0, min(1.0, k3))  # k3
                    
                    print("Using clamped distortion coefficients for better stability.")
                    dist_coeffs = dist_coeffs_clamped
                
                # Store calibration data
                self.camera_matrix = camera_matrix
                self.dist_coeffs = dist_coeffs
                self.calibration_error = mean_error
                
                print("Camera calibration successful!")
                print(f"Mean reprojection error: {mean_error:.3f} pixels")
                print(f"Distortion coefficients: k1={k1:.3f}, k2={k2:.3f}, k3={k3:.3f}")
                
                return True
            else:
                print("Camera calibration failed!")
                return False
                
        except Exception as e:
            logger.error(f"Camera calibration error: {e}")
            return False
    
    def _select_board_corners_with_cap(self, cap) -> bool:
        """
        Select board corners using an existing camera connection.
        
        Args:
            cap: OpenCV VideoCapture object
            
        Returns:
            True if corners were selected successfully
        """
        print("\n" + "="*60)
        print("    BOARD CORNER SELECTION")
        print("="*60)
        print("Click the four corners of the chessboard (any order)")
        print("Press 's' after 4 corners for orientation, 'r' to reset, 'q' to quit\n")

        self.corners = []

        try:
            last_raw = None
            while True:
                ret, raw = cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                last_raw = raw
                frame = undistort_and_orient_frame(
                    raw, self.camera_matrix, self.dist_coeffs
                )
                display_frame = frame.copy()
                for i, corner in enumerate(self.corners):
                    x, y = int(corner[0]), int(corner[1])
                    cv2.circle(display_frame, (x, y), 15, self.colors[i], -1)
                    cv2.putText(display_frame, str(i + 1), (x + 20, y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.colors[i], 3)
                if len(self.corners) == 4:
                    pts = np.array(self.corners, dtype=np.int32)
                    cv2.polylines(display_frame, [pts], True, (255, 255, 255), 3)
                cv2.putText(display_frame, f"Corners: {len(self.corners)}/4", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.putText(display_frame, "s=orientation | r=reset | q=quit", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.namedWindow('Board Corner Selection', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Board Corner Selection', 1280, 720)
                cv2.imshow('Board Corner Selection', display_frame)
                cv2.setMouseCallback('Board Corner Selection', self._mouse_callback)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s') and len(self.corners) == 4 and self._validate_corners(self.corners):
                    break
                elif key == ord('r'):
                    self.corners = []
                    print("Reset.")
                elif key == ord('q'):
                    return False

            self.board_corners = self.corners.copy()
            if last_raw is None:
                return False
            if not self._run_orientation_phase(last_raw, self.board_corners):
                return False
            self._calculate_homography_from_corners()
            self.transformer.homography_matrix = self.homography_matrix
            self.transformer.inverse_homography_matrix = np.linalg.inv(self.homography_matrix)
            self.transformer.has_homography = True
            self.transformer.is_calibrated = True
            print("Board corner selection successful!")
            self._show_validation(last_raw)
            return True
                
        except Exception as e:
            logger.error(f"Board corner selection error: {e}")
            return False
    
    def get_calibration_status(self) -> Dict[str, Any]:
        """
        Get current calibration status.
        
        Returns:
            Dictionary with calibration status information
        """
        return {
            'camera_calibrated': self.camera_matrix is not None,
            'board_calibrated': self.is_calibrated,
            'calibration_error': self.calibration_error,
            'board_corners': self.board_corners,
            'homography_matrix': self.homography_matrix is not None
        }


def main():
    """Main function for calibration system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Camera and Board Calibration System')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID (default: 0)')
    parser.add_argument('--droidcam', type=str, help='DroidCam IP address')
    parser.add_argument('--output-size', type=int, default=800, help='Bird\'s eye view output size (default: 800)')
    
    args = parser.parse_args()
    
    # Create calibration system
    calibration_system = EnhancedCalibrationSystem(args.output_size)
    
    # Run full calibration
    success = calibration_system.run_full_calibration(args.camera, args.droidcam)
    
    if success:
        print("\nCalibration completed successfully!")
        status = calibration_system.get_calibration_status()
        print(f"Status: {status}")
    else:
        print("\nCalibration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
