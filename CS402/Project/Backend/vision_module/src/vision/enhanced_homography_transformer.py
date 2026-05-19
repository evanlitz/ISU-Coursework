"""
Enhanced Homography Transformation - Combined Best Version
Robust perspective correction with improved stability, error handling, and adaptive parameters.

@author Abhay Prasanna Rao
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger(__name__)

try:
    from vision.piece_classifier.board_splitter import row_col_to_square
except ImportError:
    row_col_to_square = None

from vision.vision_config import undistort_and_orient_frame


class EnhancedHomographyTransformer:
    """
    Enhanced homography transformer with improved stability and error recovery.
    Combines robust corner detection, validation, and adaptive parameter tuning.
    """
    
    def __init__(self, output_size=800, output_top_margin=0, output_side_margin=0):
        """Initialize the homography transformer."""
        self.output_size = output_size if isinstance(output_size, tuple) else (output_size, output_size)
        self.output_top_margin = output_top_margin  # Extra pixels above rank 8 for piece-top capture
        self.output_side_margin = output_side_margin  # Extra pixels left/right for lateral piece capture
        self.homography_matrix = None
        self.inverse_homography_matrix = None
        self.is_calibrated = False
        self.has_intrinsics = False
        self.has_homography = False
        self.last_corners = None
        self.camera_matrix = None
        self.dist_coeffs = None
        
        # Pattern for 8x8 board (7x7 inner corners)
        self.pattern_size = (7, 7)
        
        # Stability tracking
        self.last_successful_homography = None
        self.calibration_quality = 0.0
        self.consecutive_failures = 0
        self.stable_calibration_count = 0
        
        # Validation parameters - adaptive based on recent success
        self.validation_params = {
            'min_determinant': 1e-20,
            'max_determinant': 1e20,
            'max_condition_number': 1e20,
            'max_reprojection_error': 100.0,
            'min_intensity': 0,
            'max_intensity': 255,
            'min_std_intensity': 0
        }
        
        # Smoothing parameters
        self.smoothing = {
            'homography_factor': 0.3,
            'corner_factor': 0.5,
            'stability_threshold': 3
        }
        
    def set_camera_params(self, camera_matrix, dist_coeffs):
        """Set camera intrinsic parameters for undistortion."""
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.has_intrinsics = True
    
    def _order_quad(self, pts):
        """Order quadrilateral corners as TL, TR, BR, BL."""
        pts = np.asarray(pts, dtype=np.float32)
        s = pts.sum(axis=1)
        d = np.diff(pts, axis=1).ravel()
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(d)]
        bl = pts[np.argmax(d)]
        return np.array([tl, tr, br, bl], dtype=np.float32)
        
    def calibrate(self, image: np.ndarray, corners: List[Tuple[float, float]] = None) -> bool:
        """
        Calibrate homography with proper corner ordering and validation.
        """
        try:
            # Validate input
            if corners is None or len(corners) != 4:
                logger.error(f"Invalid corners: {len(corners) if corners else 0} corners provided")
                return False
            
            # Undistort + optional 180° (must match vision_config / calibration)
            image = undistort_and_orient_frame(
                image, self.camera_matrix, self.dist_coeffs
            )
            
            # Order corners properly as TL, TR, BR, BL
            src_points = self._order_quad(corners)
            
            # Calculate destination points
            S = self.output_size if isinstance(self.output_size, int) else self.output_size[0]
            dst_points = np.float32([[0, 0], [S-1, 0], [S-1, S-1], [0, S-1]])
            
            # Calculate homography
            H = cv2.getPerspectiveTransform(src_points, dst_points)
            
            if H is None:
                logger.error("Failed to calculate homography")
                return False
            
            # Store homography matrices
            self.homography_matrix = H
            self.inverse_homography_matrix = np.linalg.inv(H)
            self.has_homography = True
            self.is_calibrated = True
            self.last_corners = corners
            
            # Test the transformation
            test_warped = cv2.warpPerspective(image, H, (S, S))
            
            # Log warped corners for debugging
            warped_corners = cv2.perspectiveTransform(src_points[None, ...], H)[0]
            logger.info(f"Warped corners -> {warped_corners}")
            logger.info(f"Expected ~[[0,0],[{S-1},0],[{S-1},{S-1}],[0,{S-1}]]")
            
            logger.info(f"Homography calibration successful")
            logger.info(f"Determinant: {np.linalg.det(H):.6f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Calibration error: {e}")
            return False
    
    def _smooth_corners(self, new_corners: List[Tuple[float, float]], 
                       old_corners: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Smooth corner positions with previous corners for stability."""
        smoothed_corners = []
        factor = self.smoothing['corner_factor']
        
        for new_corner, old_corner in zip(new_corners, old_corners):
            smoothed_x = new_corner[0] * factor + old_corner[0] * (1 - factor)
            smoothed_y = new_corner[1] * factor + old_corner[1] * (1 - factor)
            smoothed_corners.append((smoothed_x, smoothed_y))
        
        return smoothed_corners
    
    def _smooth_homography(self, new_H: np.ndarray, old_H: np.ndarray) -> np.ndarray:
        """Smooth homography matrix with previous one for stability."""
        factor = self.smoothing['homography_factor']
        
        # Blend the homography matrices
        smoothed_H = new_H * factor + old_H * (1 - factor)
        
        # Normalize to ensure proper scaling
        smoothed_H = smoothed_H / smoothed_H[2, 2]
        
        return smoothed_H
    
    def _refine_homography_with_subpixel_accuracy(self, image: np.ndarray, 
                                                   corners: List[Tuple[float, float]],
                                                   src_points: np.ndarray,
                                                   dst_points: np.ndarray) -> Optional[np.ndarray]:
        """
        Refine homography using sub-pixel corner detection for better accuracy.
        """
        try:
            # Convert to grayscale for corner refinement
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Refine corners using sub-pixel accuracy
            corners_array = np.array(corners, dtype=np.float32)
            
            # Define criteria for corner refinement
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            
            # Try to refine corners
            try:
                refined_corners = cv2.cornerSubPix(
                    gray, 
                    corners_array, 
                    (11, 11),  # Search window
                    (-1, -1),  # Dead zone
                    criteria
                )
            except:
                # If refinement fails, use original corners
                refined_corners = corners_array
            
            # Use RANSAC for robust homography estimation
            H, mask = cv2.findHomography(
                refined_corners, 
                dst_points, 
                method=cv2.RANSAC,
                ransacReprojThreshold=5.0
            )
            
            if H is None:
                logger.warning("RANSAC homography failed, using basic method")
                H = cv2.getPerspectiveTransform(refined_corners, dst_points)
            
            return H
            
        except Exception as e:
            logger.warning(f"Sub-pixel refinement failed: {e}")
            # Fallback to basic homography
            try:
                H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)
                if H is None:
                    H = cv2.getPerspectiveTransform(src_points, dst_points)
                return H
            except:
                return None
    def _create_fallback_homography(self, corners: List[Tuple[float, float]], warp_size: int) -> np.ndarray:
        """
        Create a fallback homography using basic perspective transform.
        This method is more lenient and handles edge cases better.
        """
        try:
            # Ensure we have exactly 4 corners
            if len(corners) != 4:
                logger.error(f"Fallback homography requires exactly 4 corners, got {len(corners)}")
                return np.eye(3, dtype=np.float32)
            
            # Create destination points
            dst_points = np.array([
                [0, 0],
                [warp_size-1, 0],
                [0, warp_size-1],
                [warp_size-1, warp_size-1]
            ], dtype=np.float32)
            
            # Use basic perspective transform
            H = cv2.getPerspectiveTransform(np.array(corners, dtype=np.float32), dst_points)
            
            # If the determinant is still too small, create an identity-like matrix
            det = np.linalg.det(H)
            if abs(det) < 1e-20:
                logger.warning("Creating identity-like homography due to extremely small determinant")
                H = np.array([
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0]
                ], dtype=np.float32)
            
            return H
            
        except Exception as e:
            logger.error(f"Fallback homography creation failed: {e}")
            return np.eye(3, dtype=np.float32)
    
    def _ensure_corner_order(self, corners: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Ensure corners are in correct order: TL, TR, BL, BR."""
        if len(corners) != 4:
            return corners
        
        corners_array = np.array(corners, dtype=np.float32)
        
        # Calculate center
        center = np.mean(corners_array, axis=0)
        
        # Sort by angle from center
        angles = []
        for corner in corners_array:
            angle = np.arctan2(corner[1] - center[1], corner[0] - center[0])
            angles.append(angle)
        
        # Get sorted indices
        sorted_indices = np.argsort(angles)
        sorted_corners = corners_array[sorted_indices]
        
        # Find top-left (minimum sum)
        sums = sorted_corners[:, 0] + sorted_corners[:, 1]
        tl_idx = np.argmin(sums)
        
        # Reorder starting from top-left
        ordered = np.roll(sorted_corners, -tl_idx, axis=0)
        
        # Ensure correct order (TL, TR, BR, BL) -> (TL, TR, BL, BR)
        if ordered[1][0] < ordered[3][0]:  # Second point is left of fourth
            ordered = ordered[[0, 3, 1, 2]]
        
        final_order = [ordered[0], ordered[1], ordered[3], ordered[2]]
        
        return [tuple(corner) for corner in final_order]
    
    def _validate_homography_matrix(self, H: np.ndarray) -> bool:
        """Validate homography matrix with reasonable checks."""
        try:
            if H is None:
                return False
            
            # Check determinant
            det = np.linalg.det(H)
            if abs(det) < self.validation_params['min_determinant'] or abs(det) > self.validation_params['max_determinant']:
                logger.debug(f"Invalid determinant: {det}")
                return False
            
            # Check condition number
            cond = np.linalg.cond(H)
            if cond > self.validation_params['max_condition_number']:
                logger.debug(f"Poor condition number: {cond}")
                return False
            
            # Check that H[2,2] is not too small
            if abs(H[2, 2]) < 1e-10:
                logger.debug(f"H[2,2] too small: {H[2, 2]}")
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Homography validation error: {e}")
            return False
    
    def _is_warped_valid(self, warped: np.ndarray) -> bool:
        """Check if warped image is valid."""
        if warped is None or warped.size == 0:
            return False
        
        # Check if image has reasonable content
        mean_val = np.mean(warped)
        if mean_val < self.validation_params['min_intensity'] or mean_val > self.validation_params['max_intensity']:
            # Be more permissive after failures
            if self.consecutive_failures > 2:
                return True  # Accept it anyway
            return False
        
        # Check for variation
        std_val = np.std(warped)
        if std_val < self.validation_params['min_std_intensity']:
            # Be more permissive after failures
            if self.consecutive_failures > 2:
                return True  # Accept it anyway
            return False
        
        return True
    
    def _validate_and_correct_orientation(self, warped_image: np.ndarray, H: np.ndarray, warp_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Validate chess board orientation and correct if needed.
        Ensures a1 (bottom-left) is a dark square.
        """
        try:
            h, w = warped_image.shape[:2]
            
            # Extract bottom-left tile (a1 square)
            tile_height = h // 8
            tile_width = w // 8
            
            # Bottom-left tile coordinates
            y_start = h - tile_height
            y_end = h
            x_start = 0
            x_end = tile_width
            
            # Extract the tile
            a1_tile = warped_image[y_start:y_end, x_start:x_end]
            
            # Calculate mean intensity (0 = black, 255 = white)
            if len(a1_tile.shape) == 3:
                a1_tile_gray = cv2.cvtColor(a1_tile, cv2.COLOR_BGR2GRAY)
            else:
                a1_tile_gray = a1_tile
                
            tile_mean = np.mean(a1_tile_gray)
            
            logger.info(f"A1 tile mean intensity: {tile_mean:.1f}")
            
            # If a1 tile is not dark (mean > 128), rotate the image 180 degrees
            if tile_mean > 128:
                logger.info("A1 tile is not dark, rotating image 180 degrees")
                warped_image = cv2.rotate(warped_image, cv2.ROTATE_180)
                
                # Update homography matrix to account for rotation
                # Create rotation matrix for 180 degrees
                center = (warp_size // 2, warp_size // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, 180, 1.0)
                
                # Convert to 3x3 matrix
                rotation_matrix_3x3 = np.vstack([rotation_matrix, [0, 0, 1]])
                
                # Update homography matrix: H_new = R * H
                H = rotation_matrix_3x3 @ H
                
                logger.info("Applied 180-degree rotation to correct orientation")
            else:
                logger.info("A1 tile is dark, orientation is correct")
                
            return warped_image, H
            
        except Exception as e:
            logger.warning(f"Orientation validation failed: {e}")
            # Return unchanged if validation fails
            return warped_image, H
    
    def _calculate_calibration_quality(self, src_points: np.ndarray, dst_points: np.ndarray, H: np.ndarray):
        """Calculate quality metric for calibration."""
        try:
            # Project source points using homography
            src_homo = np.column_stack([src_points, np.ones(4)])
            projected = (H @ src_homo.T).T
            projected = projected[:, :2] / projected[:, 2:3]
            
            # Calculate reprojection error
            errors = np.linalg.norm(projected - dst_points, axis=1)
            mean_error = np.mean(errors)
            
            # Quality score (lower error is better)
            self.calibration_quality = max(0, min(100, 100 - mean_error))
            
        except Exception as e:
            logger.debug(f"Quality calculation error: {e}")
            self.calibration_quality = 50.0
    
    def transform_to_birdseye(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Transform image to bird's eye view."""
        if not getattr(self, "has_homography", False):
            logger.warning("No homography available")
            return None

        try:
            # Undistort + optional 180° — REQUIRED for correct alignment with saved corners.
            if getattr(self, "has_intrinsics", False):
                image = undistort_and_orient_frame(
                    image, self.camera_matrix, self.dist_coeffs
                )
            else:
                image = undistort_and_orient_frame(image, None, None)

            S = self.output_size if isinstance(self.output_size, int) else self.output_size[0]
            top_margin = getattr(self, "output_top_margin", 0)
            side_margin = getattr(self, "output_side_margin", 0)

            if top_margin > 0 or side_margin > 0:
                # Shift homography: top margin = area above rank 8; side margin = area left/right of board
                tx = side_margin
                ty = top_margin
                T = np.float32([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
                H_shifted = T @ self.homography_matrix
                out_w = S + 2 * side_margin
                out_h = S + top_margin
                warped = cv2.warpPerspective(image, H_shifted, (out_w, out_h))
            else:
                warped = cv2.warpPerspective(image, self.homography_matrix, (S, S))

            return warped

        except Exception as e:
            logger.error(f"Transform error: {e}")
            return None
    
    def pixel_to_board_coordinates(self, pixel_coords: Tuple[float, float]) -> Tuple[int, int]:
        """Convert pixel coordinates to board coordinates (row, col)."""
        if not self.is_calibrated:
            raise ValueError("Not calibrated")
        
        try:
            # Transform pixel to warped coordinates
            point = np.array([[pixel_coords]], dtype=np.float32)
            transformed = cv2.perspectiveTransform(point, self.homography_matrix)[0][0]
            
            # Convert to board coordinates
            if isinstance(self.output_size, tuple):
                h, w = self.output_size
            else:
                h = w = self.output_size
                
            col = int(transformed[0] * 8 / w)
            row = int(transformed[1] * 8 / h)
            
            # Clamp to valid range
            col = max(0, min(7, col))
            row = max(0, min(7, row))
            
            return (row, col)
            
        except Exception as e:
            logger.error(f"Coordinate conversion error: {e}")
            return (0, 0)
    
    def board_to_pixel_coordinates(self, board_coords: Tuple[int, int]) -> Tuple[float, float]:
        """Convert board coordinates to pixel coordinates."""
        if not self.is_calibrated:
            raise ValueError("Not calibrated")
        
        try:
            row, col = board_coords
            
            if isinstance(self.output_size, tuple):
                h, w = self.output_size
            else:
                h = w = self.output_size
            
            # Center of the square in warped image
            x = (col + 0.5) * w / 8
            y = (row + 0.5) * h / 8
            
            # Transform back to original image
            point = np.array([[[x, y]]], dtype=np.float32)
            transformed = cv2.perspectiveTransform(point, self.inverse_homography_matrix)[0][0]
            
            return tuple(transformed)
            
        except Exception as e:
            logger.error(f"Coordinate conversion error: {e}")
            return (0.0, 0.0)
    
    def get_square_center(self, row: int, col: int) -> Tuple[float, float]:
        """Get center of a square in original image coordinates."""
        return self.board_to_pixel_coordinates((row, col))
    
    def get_square_coordinates(self, row: int, col: int) -> Tuple[Tuple[float, float], ...]:
        """Get four corners of a square in original image."""
        if not self.is_calibrated:
            raise ValueError("Not calibrated")
        
        try:
            if isinstance(self.output_size, tuple):
                h, w = self.output_size
            else:
                h = w = self.output_size
            
            # Square corners in warped image
            x_start = col * w / 8
            x_end = (col + 1) * w / 8
            y_start = row * h / 8
            y_end = (row + 1) * h / 8
            
            warped_corners = np.array([
                [x_start, y_start],  # Top-left
                [x_end, y_start],    # Top-right
                [x_start, y_end],    # Bottom-left
                [x_end, y_end]       # Bottom-right
            ], dtype=np.float32)
            
            # Transform to original image
            original_corners = cv2.perspectiveTransform(
                warped_corners.reshape(-1, 1, 2),
                self.inverse_homography_matrix
            ).reshape(-1, 2)
            
            return tuple(tuple(corner) for corner in original_corners)
            
        except Exception as e:
            logger.error(f"Square coordinate error: {e}")
            return ((0, 0), (0, 0), (0, 0), (0, 0))
    
    def draw_precise_grid(self, image: np.ndarray, board_orientation: int = 0) -> np.ndarray:
        """
        Draw 8x8 grid on image with rank/file labels.

        Labels rotate based on board_orientation (0-3) so they match the physical
        board when corner calibration is rotated. Orientation: 0=TL is a8,
        1=90° CW (right=rank8), 2=180°, 3=270° CW (left=rank8).
        """
        if not self.is_calibrated:
            return image

        try:
            grid_image = image.copy()
            h, w = image.shape[:2]
            # Top margin: board below; side margin: board centered horizontally
            # Derive from transformer config; board is always square (S x S)
            top_margin = getattr(self, "output_top_margin", 0)
            side_margin = getattr(self, "output_side_margin", 0)
            if top_margin == 0 and h > w:
                top_margin = h - w  # Infer from dimensions when no side margin
            board_h = h - top_margin
            y_offset = top_margin
            # Board region: use explicit side_margin when set, else infer from image dimensions
            if side_margin > 0 and w > 2 * side_margin:
                x_offset = side_margin
                board_w = w - 2 * side_margin
            elif w > board_h:
                # Image wider than board height -> side margins, board centered
                x_offset = (w - board_h) // 2
                board_w = board_h
            else:
                x_offset = 0
                board_w = w
            square_width = board_w / 8.0
            square_height = board_h / 8.0

            # Scale line thickness and corner size so grid stays visible at high resolutions
            # (at 1800px, 1-pixel lines are invisible when displayed in 800px window)
            min_dim = min(board_w, board_h)
            line_thickness = max(1, min(4, min_dim // 400))
            corner_size = max(3, min(12, min_dim // 150))

            # Draw vertical lines (only in board area, not in margins)
            y_top = y_offset
            y_bottom = h - 1
            x_left = x_offset
            x_right = x_offset + board_w - 1
            for i in range(9):
                x = x_offset + int(round(i * square_width))
                x = max(0, min(x, w-1))
                cv2.line(grid_image, (x, y_top), (x, y_bottom), (0, 255, 0), line_thickness)

            # Draw horizontal lines (only in board area, offset by margins)
            for i in range(9):
                y = y_offset + int(round(i * square_height))
                y = max(0, min(y, h-1))
                cv2.line(grid_image, (x_left, y), (x_right, y), (0, 255, 0), line_thickness)

            # Add corner markers (corner_size scaled above for visibility)
            for i in range(9):
                for j in range(9):
                    x = x_offset + int(round(i * square_width))
                    y = y_offset + int(round(j * square_height))
                    if 0 <= x < w and 0 <= y < h:
                        cv2.circle(grid_image, (x, y), corner_size, (255, 0, 0), -1)

            # Add labels (file along top, rank along left) - rotate based on board_orientation
            font_scale = 2
            font_thickness = 2
            # label_orientation_offset: add to orientation when corners/warp convention differs
            # (e.g. 2 fixes a8<->h8, a1<->a8 swap; set in board_corners.json if labels are wrong)
            label_offset = int(getattr(self, "label_orientation_offset", 0))
            o = (int(board_orientation) + label_offset) % 4
            if row_col_to_square is not None:
                for col in range(8):
                    sq = row_col_to_square(0, col, o)
                    file_char = sq[0]
                    x = x_offset + int((col + 0.5) * square_width)
                    label_y = y_offset + 40
                    cv2.putText(grid_image, file_char, (x-10, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
                for row in range(8):
                    sq = row_col_to_square(row, 0, o)
                    rank_char = sq[1]
                    y = y_offset + int((row + 0.5) * square_height)
                    cv2.putText(grid_image, rank_char, (x_offset + 10, y+10),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
            else:
                # Fallback when board_splitter not available (orientation 0)
                for col in range(8):
                    x = x_offset + int((col + 0.5) * square_width)
                    label_y = y_offset + 40
                    cv2.putText(grid_image, chr(ord('a') + col), (x-10, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
                for row in range(8):
                    y = y_offset + int((row + 0.5) * square_height)
                    cv2.putText(grid_image, str(8 - row), (x_offset + 10, y+10),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)

            return grid_image

        except Exception as e:
            logger.error(f"Grid drawing error: {e}")
            return image
    
    def visualize_board_grid(self, image: np.ndarray) -> np.ndarray:
        """Visualize board grid with corners."""
        if not self.is_calibrated:
            return image
        
        try:
            grid_image = image.copy()
            h, w = image.shape[:2]
            
            # Draw 9 vertical lines
            for i in range(9):
                x = int(i * w / 8)
                cv2.line(grid_image, (x, 0), (x, h), (0, 255, 0), 2)
            
            # Draw 9 horizontal lines
            for i in range(9):
                y = int(i * h / 8)
                cv2.line(grid_image, (0, y), (w, y), (0, 255, 0), 2)
            
            # Draw corner markers - TL, TR, BR, BL order
            corner_size = min(w, h) // 20
            corners = [
                (0, 0),           # a8 (top-left)
                (w-1, 0),         # h8 (top-right)
                (w-1, h-1),       # h1 (bottom-right)
                (0, h-1)          # a1 (bottom-left)
            ]
            
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
            labels = ['a8', 'h8', 'h1', 'a1']
            
            for i, (corner, color, label) in enumerate(zip(corners, colors, labels)):
                x, y = corner
                cv2.circle(grid_image, (x, y), corner_size, color, -1)
                cv2.putText(grid_image, label, (x + corner_size, y - corner_size),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
            
            return grid_image
            
        except Exception as e:
            logger.error(f"Grid visualization error: {e}")
            return image
    
    def draw_precise_corners(self, image: np.ndarray, corners: List[Tuple[float, float]] = None) -> np.ndarray:
        """Draw corner markers."""
        if corners is None:
            corners = self.last_corners
        
        if corners is None or len(corners) != 4:
            return image
        
        try:
            vis_image = image.copy()
            
            # Draw corner markers with different colors
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
            labels = ['a8', 'h8', 'a1', 'h1']
            
            for i, (corner, color, label) in enumerate(zip(corners, colors, labels)):
                x, y = int(corner[0]), int(corner[1])
                cv2.circle(vis_image, (x, y), 10, color, -1)
                cv2.putText(vis_image, label, (x + 15, y - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            return vis_image
            
        except Exception as e:
            logger.error(f"Corner drawing error: {e}")
            return image
    
    def warp_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Warp image using calibrated homography."""
        return self.transform_to_birdseye(image)


def test_enhanced_homography():
    """Test function for enhanced homography transformation."""
    import cv2
    
    # Initialize transformer
    transformer = EnhancedHomographyTransformer()
    
    # Test with sample image
    image_path = "test_chess_board.jpg"
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            return
        
        print("Testing enhanced homography transformation...")
        
        # Auto-detect corners
        from enhanced_chessboard_detector import EnhancedChessBoardDetector
        detector = EnhancedChessBoardDetector()
        corners = detector.detect_board_corners(image)
        
        if len(corners) != 4:
            print("Failed to detect corners")
            return
        
        # Calibrate
        success = transformer.calibrate(image, corners)
        
        if success:
            print("Success: Homography calibration successful")
            
            # Transform to bird's eye view
            warped = transformer.transform_to_birdseye(image)
            
            # Draw grid
            grid_image = transformer.visualize_board_grid(warped)
            
            # Save results
            cv2.imwrite("enhanced_warped.jpg", warped)
            cv2.imwrite("enhanced_grid.jpg", grid_image)
            print("Saved warped and grid images")
            
            # Test coordinate conversion
            print("\nTesting coordinate conversion:")
            for row in range(8):
                for col in range(8):
                    center = transformer.get_square_center(row, col)
                    print(f"Square ({row},{col}): center={center}")
                    
        else:
            print("Error: Homography calibration failed")
            
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_enhanced_homography()