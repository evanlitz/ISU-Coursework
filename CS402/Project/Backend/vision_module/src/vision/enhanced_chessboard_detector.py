"""
Enhanced Chess Board Detection & Homography – Combined Version
Robust chessboard detection using multiple CV techniques, adaptive parameters,
stability tracking, camera-movement handling, and fast corner tracking.

@author Abhay Prasanna Rao
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any
from sklearn.cluster import DBSCAN
from collections import deque
import warnings
# warnings.filterwarnings('ignore', category=np.RankWarning)

logger = logging.getLogger(__name__)


class EnhancedChessBoardDetector:
    """
    Enhanced chess board detector combining robust methods with adaptive parameters,
    stability heuristics, camera movement detection, and fast corner tracking.
    """

    def __init__(self):
        # Order matters: we try more reliable/fast methods first.
        self.detection_methods = [
            'combined_robust',    # Primary method combining best techniques
            'yolo_contour',       # Second fallback: "YOLO + contour" (threshold + contours)
            'opencv_chessboard',  # OpenCV chessboard detection w/ extrapolated outer corners
            'contour_adaptive',   # Adaptive contour method
            'edge_based',         # Edge + morphology contour method
            'harris_lines',       # Harris corners + hull
            'gradient_hough',     # Gradient-informed Hough transform
            'line_intersection',  # Polar Hough + intersections
            'morphological'       # Morphology-based edges
        ]

        # ---- State & history tracking ----
        self.detection_history = deque(maxlen=20)
        self.adaptive_enabled = True
        self.last_successful_params = None
        self.consecutive_failures = 0
        self.stable_detection_count = 0

        # For stability/fast tracking across frames
        self.last_valid_corners: Optional[List[Tuple[float, float]]] = None
        self.last_detection_method: Optional[str] = None
        self.frames_since_detection = 0
        self.camera_moved = False
        self.last_frame_gray = None
        self.motion_threshold = 20.0  # Mean absolute diff on downsampled frames

        # ---- Base per-method parameters (kept from Improved Version; extended) ----
        self.base_params = {
            'yolo_contour': {
                'adaptive_thresh_block_size': 9,
                'adaptive_thresh_c': 3,
                'epsilon_factor': 0.02,
                'min_contour_area': 10000
            },
            'opencv_chessboard': {
                'patterns': [(7, 7), (6, 6), (5, 5), (8, 8), (9, 9)],
                'flags': cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_ADAPTIVE_THRESH,
                'subpixel_window': (11, 11),
                'subpixel_criteria': (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            },
            'gradient_hough': {
                'canny_low': 50,
                'canny_high': 150,
                'hough_threshold': 30,
                'min_line_length': 100,
                'max_line_gap': 10,
                'gradient_threshold': 0.9,
                'angle_threshold': 15 * np.pi / 180
            },
            'line_intersection': {
                'vertical_slope_threshold': 9.0,
                'horizontal_slope_threshold': 0.3,
                'intersection_tolerance': 5
            },
            'contour_adaptive': {
                'canny_low': 50,
                'canny_high': 150,
                'epsilon_factor': 0.02,
                'min_area_ratio': 0.05  # (global min area ratio used by several methods)
            },
            'edge_based': {
                'canny_low': 30,
                'canny_high': 100,
                'dilate_kernel': (3, 3),
                'erode_kernel': (2, 2),
                'min_contour_area': 5000
            },
            'morphological': {
                'kernel_size': (5, 5),
                'iterations': 3,
                'canny_low': 40,
                'canny_high': 120,
                'min_contour_area': 8000
            },
            # Global-ish knobs shared by multiple detectors
            'global': {
                'max_area_ratio': 0.95,    # Max board area as ratio of image
                'harris_corner_quality': 0.01,
                'harris_corner_min_dist': 30,
                'hough_threshold': 80,     # for gradient_hough variant if needed
            }
        }

        # Working parameters (mutable clones)
        self.params = {k: v.copy() for k, v in self.base_params.items()}

        # ---- Adaptive validation params ----
        self.adaptive_params = {
            'min_corner_distance_ratio': 0.05,  # relative to image diagonal
            'max_corner_distance_ratio': 0.95,
            'angle_tolerance': 30,              # degrees
            'area_tolerance': 0.3,
            # (Optional controls updated by external sources)
            'confidence_threshold': 0.25,
            'corner_distance_threshold': 50,
            'detection_method': 'auto'
        }

        # Smoothing when adapting thresholds
        self.param_smoothing = {
            'factor': 0.2,
            'stability_threshold': 3
        }

    # ---------------------- External adaptive update ----------------------

    def update_adaptive_params(self, external_params: Dict[str, Any]):
        """Update adaptive parameters from external source (e.g., FrameProcessor) with smoothing."""
        if 'corner_distance_threshold' in external_params:
            new_ratio = external_params['corner_distance_threshold'] / 1000.0
            self.adaptive_params['min_corner_distance_ratio'] = (
                self.adaptive_params['min_corner_distance_ratio'] * (1 - self.param_smoothing['factor']) +
                new_ratio * self.param_smoothing['factor']
            )

        if 'confidence_threshold' in external_params:
            self.adaptive_params['confidence_threshold'] = external_params['confidence_threshold']
            # Adjust Canny thresholds based on confidence with smoothing
            factor = 1.0 + (0.25 - self.adaptive_params['confidence_threshold']) * 2
            factor = 1.0 + (factor - 1.0) * self.param_smoothing['factor']
            for method_name, method_params in self.params.items():
                if 'canny_low' in method_params:
                    base_low = self.base_params[method_name].get('canny_low', method_params['canny_low'])
                    method_params['canny_low'] = int(base_low * factor)
                if 'canny_high' in method_params:
                    base_high = self.base_params[method_name].get('canny_high', method_params['canny_high'])
                    method_params['canny_high'] = int(base_high * factor)

        if 'detection_method' in external_params:
            self.adaptive_params['detection_method'] = external_params['detection_method']

    # ---------------------- Image-driven parameter adaptation ----------------------

    def _adapt_parameters_to_image(self, image: np.ndarray):
        """Adapt detection parameters based on image characteristics with stability checks."""
        if not self.adaptive_enabled:
            return

        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        image_diagonal = np.sqrt(h**2 + w**2)

        # If stable, reuse last success values for consistency
        if self.last_successful_params and self.stable_detection_count > self.param_smoothing['stability_threshold']:
            for method_name in self.params:
                for param_name, param_value in self.last_successful_params.get(method_name, {}).items():
                    if param_name in self.params[method_name]:
                        self.params[method_name][param_name] = param_value
            # Still update absolute distances
            self.adaptive_params['min_corner_distance'] = int(
                image_diagonal * self.adaptive_params['min_corner_distance_ratio']
            )
            self.adaptive_params['max_corner_distance'] = int(
                image_diagonal * self.adaptive_params['max_corner_distance_ratio']
            )
            return

        size_factor = image_diagonal / 1000.0

        # Adapt contour area thresholds
        for method in ['yolo_contour', 'edge_based', 'morphological']:
            if 'min_contour_area' in self.params[method]:
                base_area = self.base_params[method]['min_contour_area']
                new_area = int(base_area * (size_factor ** 2))
                if self.last_successful_params and method in self.last_successful_params:
                    if 'min_contour_area' in self.last_successful_params[method]:
                        prev_area = self.last_successful_params[method]['min_contour_area']
                        new_area = int(prev_area * 0.7 + new_area * 0.3)
                self.params[method]['min_contour_area'] = new_area

        # Adapt line detection parameters
        if 'min_line_length' in self.params['gradient_hough']:
            base_length = self.base_params['gradient_hough']['min_line_length']
            self.params['gradient_hough']['min_line_length'] = int(base_length * size_factor)

        # Brightness-based Canny tuning
        if mean_brightness < 80:  # Dark
            adjustment = 0.8 if self.consecutive_failures < 3 else 0.6
            for method in self.params.values():
                if 'canny_low' in method:
                    method['canny_low'] = int(method.get('canny_low', 50) * adjustment)
                if 'canny_high' in method:
                    method['canny_high'] = int(method.get('canny_high', 150) * adjustment)
        elif mean_brightness > 180:  # Bright
            adjustment = 1.2 if self.consecutive_failures < 3 else 1.4
            for method in self.params.values():
                if 'canny_low' in method:
                    method['canny_low'] = min(80, int(method.get('canny_low', 50) * adjustment))
                if 'canny_high' in method:
                    method['canny_high'] = min(200, int(method.get('canny_high', 150) * adjustment))

        # Contrast-based tweak
        if std_brightness < 30:
            if 'adaptive_thresh_c' in self.params['yolo_contour']:
                self.params['yolo_contour']['adaptive_thresh_c'] = max(
                    1, self.base_params['yolo_contour']['adaptive_thresh_c'] - 1
                )

        # Absolute corner distance bounds (pixels)
        self.adaptive_params['min_corner_distance'] = int(
            image_diagonal * self.adaptive_params['min_corner_distance_ratio']
        )
        self.adaptive_params['max_corner_distance'] = int(
            image_diagonal * self.adaptive_params['max_corner_distance_ratio']
        )

    # ---------------------- Public API ----------------------

    def detect_board_corners(self, image: np.ndarray, method: str = 'auto') -> List[Tuple[float, float]]:
        """
        Detect chess board corners (TL, TR, BL, BR) with adaptive validation/stability.
        """
        if image is None or image.size == 0:
            logger.error("Invalid input image")
            self.consecutive_failures += 1
            return []

        # Adapt thresholds to this frame
        self._adapt_parameters_to_image(image)

        # Motion detection to handle camera movement
        self._detect_camera_movement(image)

        # Reset tracking if camera moved
        if self.camera_moved:
            logger.info("Camera movement detected, resetting tracking")
            self.last_valid_corners = None
            self.last_detection_method = None
            self.frames_since_detection = 0

        # Fast tracking path
        if method == 'auto':
            if self.last_valid_corners is not None and not self.camera_moved and self.frames_since_detection < 10:
                tracked = self._try_fast_tracking(image)
                if len(tracked) == 4 and self._validate_corners_adaptive(tracked, image.shape):
                    self.frames_since_detection += 1
                    return self._order_corners_robust(tracked, image.shape)

            # Try recent successful methods first
            method_order = self.detection_methods.copy()
            recent_successful = []
            for h in self.detection_history:
                if h['success'] and h['method'] not in recent_successful:
                    recent_successful.append(h['method'])
            for m in recent_successful[:3]:
                if m in method_order:
                    method_order.remove(m)
                    method_order.insert(0, m)

            # Attempt detection
            for detection_method in method_order:
                try:
                    corners = self._detect_corners_by_method(image, detection_method)
                    if len(corners) == 4 and self._validate_corners_adaptive(corners, image.shape):
                        ordered = self._order_corners_robust(corners, image.shape)
                        logger.info(f"Successfully detected with method: {detection_method}")

                        # Save success state
                        self.detection_history.append({'method': detection_method, 'success': True,
                                                       'image_shape': image.shape, 'corners': ordered})
                        self.last_successful_params = {k: v.copy() for k, v in self.params.items()}
                        self.last_valid_corners = ordered
                        self.last_detection_method = detection_method
                        self.frames_since_detection = 0
                        self.consecutive_failures = 0
                        self.stable_detection_count += 1
                        return ordered
                except Exception as e:
                    logger.debug(f"Method {detection_method} failed: {str(e)[:120]}")
                    continue

            # Record failure
            self.detection_history.append({'method': 'auto', 'success': False,
                                           'image_shape': image.shape, 'corners': []})
            self.consecutive_failures += 1
            self.stable_detection_count = 0
            self.frames_since_detection += 1
            logger.error("All automatic detection methods failed")
            return []

        else:
            # Specific method requested
            try:
                corners = self._detect_corners_by_method(image, method)
                if len(corners) == 4 and self._validate_corners_adaptive(corners, image.shape):
                    ordered = self._order_corners_robust(corners, image.shape)
                    self.last_valid_corners = ordered
                    self.last_detection_method = method
                    self.frames_since_detection = 0
                    self.consecutive_failures = 0
                    self.stable_detection_count += 1
                    return ordered
                else:
                    self.consecutive_failures += 1
                    self.stable_detection_count = 0
            except Exception as e:
                logger.error(f"Method {method} failed: {str(e)[:120]}")
                self.consecutive_failures += 1
                self.stable_detection_count = 0
            return []

    # ---------------------- Method multiplexer ----------------------

    def _detect_corners_by_method(self, image: np.ndarray, method: str) -> List[Tuple[float, float]]:
        try:
            if method == 'yolo_contour':
                return self._detect_yolo_contour_corners(image)
            elif method == 'opencv_chessboard':
                return self._detect_opencv_chessboard_corners(image)
            elif method == 'gradient_hough':
                return self._detect_gradient_hough_corners(image)
            elif method == 'line_intersection':
                return self._detect_line_intersection_corners(image)
            elif method == 'contour_adaptive':
                return self._detect_contour_adaptive_corners(image)
            elif method == 'edge_based':
                return self._detect_corners_edge_based(image)
            elif method == 'morphological':
                return self._detect_corners_morphological(image)
            elif method == 'combined_robust':
                return self._detect_combined_robust(image)
            elif method == 'harris_lines':
                return self._detect_harris_lines(image)
            else:
                logger.warning(f"Unknown detection method: {method}")
                return []
        except Exception as e:
            logger.error(f"Error in detection method {method}: {str(e)[:120]}")
            return []

    # ---------------------- Validation & ordering ----------------------

    def _validate_corners_adaptive(self, corners: List[Tuple[float, float]], image_shape: Tuple[int, int]) -> bool:
        """Adaptive validation accounting for perspective, area, bounds, spacing."""
        if len(corners) != 4:
            return False

        h, w = image_shape[:2]
        image_diagonal = np.sqrt(h**2 + w**2)

        min_distance = self.adaptive_params.get('min_corner_distance', image_diagonal * 0.05)
        max_distance = self.adaptive_params.get('max_corner_distance', image_diagonal * 0.95)

        # Relax after multiple failures
        if self.consecutive_failures > 3:
            min_distance *= 0.7
            max_distance *= 1.2

        # Pairwise distances
        for i in range(4):
            for j in range(i + 1, 4):
                dist = np.hypot(corners[i][0] - corners[j][0], corners[i][1] - corners[j][1])
                if dist < min_distance or dist > max_distance:
                    return False

        # Bounds (with small margin)
        margin = int(image_diagonal * 0.02)
        for x, y in corners:
            if x < -margin or x >= w + margin or y < -margin or y >= h + margin:
                return False

        # Convexity
        ca = np.array(corners, dtype=np.float32)
        hull = cv2.convexHull(ca)
        if len(hull) != 4:
            return False

        # Area ratio
        area = cv2.contourArea(ca)
        image_area = float(w * h)
        area_ratio = area / max(1.0, image_area)

        min_area_ratio = 0.03 if self.consecutive_failures > 2 else 0.05
        max_area_ratio = self.params['global']['max_area_ratio']
        if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
            return False

        # Angles near 90 deg (tolerate perspective)
        angles = self._calculate_corner_angles(corners)
        min_angle = self.adaptive_params.get('angle_tolerance', 30)
        if self.consecutive_failures > 2:
            min_angle *= 1.5
        max_angle = 180 - min_angle

        extreme = sum(1 for a in angles if (a < min_angle or a > max_angle))
        if extreme > 2 and not self._check_perspective_distortion(corners):
            return False

        return True

    def _calculate_corner_angles(self, corners: List[Tuple[float, float]]) -> List[float]:
        pts = np.array(corners, dtype=np.float32)
        angs = []
        for i in range(4):
            p1 = pts[(i - 1) % 4]
            p2 = pts[i]
            p3 = pts[(i + 1) % 4]
            v1 = p1 - p2
            v2 = p3 - p2
            denom = (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            cos_a = np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)
            angs.append(np.degrees(np.arccos(cos_a)))
        return angs

    def _check_perspective_distortion(self, corners: List[Tuple[float, float]]) -> bool:
        c = np.array(corners, dtype=np.float32)
        tw = np.linalg.norm(c[1] - c[0])
        bw = np.linalg.norm(c[3] - c[2])
        lh = np.linalg.norm(c[2] - c[0])
        rh = np.linalg.norm(c[3] - c[1])
        max_ratio = 4.0 if self.consecutive_failures > 2 else 3.0
        wr = max(tw, bw) / (min(tw, bw) + 1e-10)
        hr = max(lh, rh) / (min(lh, rh) + 1e-10)
        return wr <= max_ratio and hr <= max_ratio

    def _order_corners_robust(self, corners: List[Tuple[float, float]], image_shape: Tuple[int, int] = None) -> List[Tuple[float, float]]:
        """Order corners as [TL, TR, BR, BL] robustly."""
        if len(corners) != 4:
            return corners
        pts = np.array(corners, dtype=np.float32)
        center = pts.mean(axis=0)
        angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
        idx = np.argsort(angles)
        sc = pts[idx]

        # TL has min (x+y)
        sums = sc[:, 0] + sc[:, 1]
        tl_i = np.argmin(sums)
        ordered = np.roll(sc, -tl_i, axis=0)  # TL, ?, ?, ?

        # Try to ensure TL, TR, BR, BL (clockwise-like)
        tr = ordered[1]
        br = ordered[2]
        bl = ordered[3]

        # If geometry seems wrong, fallback to sum/diff trick
        if not self._is_valid_quadrilateral(ordered):
            sums_all = pts.sum(axis=1)
            diffs_all = pts[:, 0] - pts[:, 1]
            top_left = pts[np.argmin(sums_all)]
            bottom_right = pts[np.argmax(sums_all)]
            top_right = pts[np.argmax(diffs_all)]
            bottom_left = pts[np.argmin(diffs_all)]
            ordered = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

        # Final order: TL, TR, BR, BL
        return [tuple(ordered[0]), tuple(ordered[1]), tuple(ordered[2]), tuple(ordered[3])]

    # ---------------------- Detection methods ----------------------

    def _detect_yolo_contour_corners(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

            variants = []
            # Mean adaptive
            th_mean = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                self.params['yolo_contour']['adaptive_thresh_block_size'],
                self.params['yolo_contour']['adaptive_thresh_c']
            )
            variants.append(('adaptive_mean', th_mean))

            # Gaussian adaptive
            th_gauss = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                self.params['yolo_contour']['adaptive_thresh_block_size'],
                self.params['yolo_contour']['adaptive_thresh_c']
            )
            variants.append(('adaptive_gaussian', th_gauss))

            # CLAHE + adaptive
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            th_clahe = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                self.params['yolo_contour']['adaptive_thresh_block_size'],
                self.params['yolo_contour']['adaptive_thresh_c']
            )
            variants.append(('clahe_adaptive', th_clahe))

            for name, img_th in variants:
                contours, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    continue
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) < self.params['yolo_contour']['min_contour_area']:
                    continue

                for eps_factor in [
                    self.params['yolo_contour']['epsilon_factor'],
                    self.params['yolo_contour']['epsilon_factor'] * 0.5,
                    self.params['yolo_contour']['epsilon_factor'] * 2.0
                ]:
                    eps = eps_factor * cv2.arcLength(largest, True)
                    approx = cv2.approxPolyDP(largest, eps, True)
                    if len(approx) == 4:
                        return [(float(p[0][0]), float(p[0][1])) for p in approx]

                # Try hull extraction if near-quad
                approx = cv2.approxPolyDP(largest, self.params['yolo_contour']['epsilon_factor'] * cv2.arcLength(largest, True), True)
                if 3 <= len(approx) <= 6:
                    hull = cv2.convexHull(approx)
                    if len(hull) >= 4:
                        corners = self._extract_four_corners_from_hull(hull)
                        if len(corners) == 4:
                            return corners

            return []
        except Exception as e:
            logger.error(f"Error in YOLO-contour: {str(e)[:120]}")
            return []

    def _detect_opencv_chessboard_corners(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            preprocess = [
                ("original", gray),
                ("gaussian_blur", cv2.GaussianBlur(gray, (5, 5), 0)),
                ("bilateral", cv2.bilateralFilter(gray, 9, 75, 75)),
                ("clahe", cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)),
                ("median_blur", cv2.medianBlur(gray, 5))
            ]
            for pattern in self.params['opencv_chessboard']['patterns']:
                rows, cols = pattern
                for name, imgp in preprocess:
                    try:
                        # Prefer SB if available
                        try:
                            ret, corners = cv2.findChessboardCornersSB(imgp, pattern, flags=self.params['opencv_chessboard']['flags'])
                        except Exception:
                            ret, corners = cv2.findChessboardCorners(imgp, pattern, flags=self.params['opencv_chessboard']['flags'])

                        if ret and corners is not None:
                            # Subpixel refine
                            corners = cv2.cornerSubPix(
                                imgp, corners,
                                self.params['opencv_chessboard']['subpixel_window'], (-1, -1),
                                self.params['opencv_chessboard']['subpixel_criteria']
                            ).reshape(-1, 2)

                            tl_i, tr_i = 0, cols - 1
                            bl_i, br_i = -cols, -1
                            tl, tr = corners[tl_i], corners[tr_i]
                            bl, br = corners[bl_i], corners[br_i]
                            u = (tr - tl) / (cols - 1)
                            v = (bl - tl) / (rows - 1)

                            TL = tl - 0.5 * u - 0.5 * v
                            TR = tr + 0.5 * u - 0.5 * v
                            BR = br + 0.5 * u + 0.5 * v
                            BL = bl - 0.5 * u + 0.5 * v
                            return [tuple(TL), tuple(TR), tuple(BL), tuple(BR)]
                    except Exception:
                        continue
            return []
        except Exception as e:
            logger.error(f"Error in OpenCV-chessboard: {str(e)[:120]}")
            return []

    def _detect_gradient_hough_corners(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0),
                              self.params['gradient_hough']['canny_low'],
                              self.params['gradient_hough']['canny_high'])
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                                    self.params['gradient_hough']['hough_threshold'],
                                    minLineLength=self.params['gradient_hough']['min_line_length'],
                                    maxLineGap=self.params['gradient_hough']['max_line_gap'])
            if lines is None:
                return []

            intersections = []
            for i in range(len(lines)):
                for j in range(i + 1, len(lines)):
                    pt = self._line_intersection(lines[i][0], lines[j][0])
                    if pt is not None:
                        intersections.append(pt)
            if len(intersections) < 4:
                return []

            labels = DBSCAN(eps=30, min_samples=1).fit(np.array(intersections)).labels_
            corners = []
            for lab in set(labels):
                if lab == -1:
                    continue
                group = np.array(intersections)[labels == lab]
                corners.append(tuple(group.mean(axis=0)))
            if len(corners) >= 4:
                corners = self._select_best_quadrilateral(corners)
            return corners[:4] if len(corners) >= 4 else []
        except Exception as e:
            logger.error(f"Error in gradient-hough: {str(e)[:120]}")
            return []

    def _detect_line_intersection_corners(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
            if lines is None:
                return []

            horizontals, verticals = [], []
            for line in lines:
                rho, theta = line[0]
                if abs(np.sin(theta)) < self.params['line_intersection']['horizontal_slope_threshold']:
                    horizontals.append((rho, theta))
                elif abs(np.cos(theta)) < 1.0 / self.params['line_intersection']['vertical_slope_threshold']:
                    verticals.append((rho, theta))

            inters = []
            for h in horizontals:
                for v in verticals:
                    pt = self._polar_line_intersection(h, v)
                    if pt is not None:
                        inters.append(pt)
            if len(inters) >= 4:
                return self._select_best_quadrilateral(inters)[:4]
            return []
        except Exception as e:
            logger.error(f"Error in line-intersection: {str(e)[:120]}")
            return []

    def _detect_contour_adaptive_corners(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
            edges = cv2.Canny(enhanced, self.params['contour_adaptive']['canny_low'],
                              self.params['contour_adaptive']['canny_high'])
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            img_area = image.shape[0] * image.shape[1]
            min_area = img_area * self.params['contour_adaptive']['min_area_ratio']
            valid = [c for c in contours if cv2.contourArea(c) > min_area]
            if not valid:
                return []

            largest = max(valid, key=cv2.contourArea)
            for eps_mult in [0.01, 0.02, 0.03, 0.04]:
                eps = eps_mult * cv2.arcLength(largest, True)
                approx = cv2.approxPolyDP(largest, eps, True)
                if len(approx) == 4:
                    return [(float(p[0][0]), float(p[0][1])) for p in approx]
            return []
        except Exception as e:
            logger.error(f"Error in contour-adaptive: {str(e)[:120]}")
            return []

    def _detect_corners_edge_based(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            params = self.params['edge_based']
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            pre = [
                ("original", gray),
                ("gaussian", cv2.GaussianBlur(gray, (5, 5), 0)),
                ("bilateral", cv2.bilateralFilter(gray, 9, 75, 75))
            ]
            for name, proc in pre:
                edges = cv2.Canny(proc, params['canny_low'], params['canny_high'])
                edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_RECT, params['dilate_kernel']), iterations=1)
                edges = cv2.erode(edges, cv2.getStructuringElement(cv2.MORPH_RECT, params['erode_kernel']), iterations=1)

                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                valid = [c for c in contours if cv2.contourArea(c) > params['min_contour_area']]
                if not valid:
                    continue

                largest = max(valid, key=cv2.contourArea)
                approx = None
                for eps_mult in [0.01, 0.02, 0.03, 0.04]:
                    eps = eps_mult * cv2.arcLength(largest, True)
                    approx = cv2.approxPolyDP(largest, eps, True)
                    if len(approx) == 4:
                        corners = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
                        if self._validate_corners_adaptive(corners, image.shape):
                            return self._order_corners_robust(corners, image.shape)

                if approx is not None and len(approx) > 4:
                    hull = cv2.convexHull(approx)
                    if len(hull) >= 4:
                        corners = self._extract_four_corners_from_hull(hull)
                        if len(corners) == 4 and self._validate_corners_adaptive(corners, image.shape):
                            return self._order_corners_robust(corners, image.shape)
            return []
        except Exception as e:
            logger.error(f"Error in edge-based: {str(e)[:120]}")
            return []

    def _detect_corners_morphological(self, image: np.ndarray) -> List[Tuple[float, float]]:
        try:
            params = self.params['morphological']
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, params['kernel_size'])
            morph = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
            _, thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=params['iterations'])

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid = [c for c in contours if cv2.contourArea(c) > params['min_contour_area']]
            if not valid:
                return []

            largest = max(valid, key=cv2.contourArea)
            for eps_mult in [0.01, 0.02, 0.03]:
                eps = eps_mult * cv2.arcLength(largest, True)
                approx = cv2.approxPolyDP(largest, eps, True)
                if len(approx) == 4:
                    return [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
            return []
        except Exception as e:
            logger.error(f"Error in morphological: {str(e)[:120]}")
            return []

    # New from "Fixed Version": a combined robust method reusing per-method params
    def _detect_combined_robust(self, image: np.ndarray) -> List[Tuple[float, float]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Use edge thresholds from edge_based
        edges = cv2.Canny(blurred, self.params['edge_based']['canny_low'], self.params['edge_based']['canny_high'])

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []

        largest = max(contours, key=cv2.contourArea)
        img_area = float(image.shape[0] * image.shape[1])
        if cv2.contourArea(largest) < img_area * self.params['contour_adaptive']['min_area_ratio']:
            return []

        # Epsilon from contour_adaptive
        eps = self.params['contour_adaptive']['epsilon_factor'] * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, eps, True)
        if len(approx) == 4:
            return [(float(p[0][0]), float(p[0][1])) for p in approx]

        # Try convex hull extreme points
        hull = cv2.convexHull(largest)
        if len(hull) >= 4:
            hp = hull.reshape(-1, 2)
            lt = hp[np.argmin(hp[:, 0] + hp[:, 1])]
            rt = hp[np.argmax(hp[:, 0] - hp[:, 1])]
            rb = hp[np.argmax(hp[:, 0] + hp[:, 1])]
            lb = hp[np.argmin(hp[:, 0] - hp[:, 1])]
            return [tuple(lt), tuple(rt), tuple(rb), tuple(lb)]  # TL, TR, BR, BL
        return []

    def _detect_harris_lines(self, image: np.ndarray) -> List[Tuple[float, float]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        dst = cv2.cornerHarris(gray, 2, 3, 0.04)
        dst = cv2.dilate(dst, None)
        thresh = 0.01 * dst.max()
        ys, xs = np.where(dst > thresh)
        if len(xs) < 4:
            return []

        pts = np.vstack([xs, ys]).T.astype(np.float32)
        hull = cv2.convexHull(pts)
        if len(hull) >= 4:
            hp = hull.reshape(-1, 2)
            idx_tl = np.argmin(hp[:, 0] + hp[:, 1])
            idx_tr = np.argmax(hp[:, 0] - hp[:, 1])
            idx_br = np.argmax(hp[:, 0] + hp[:, 1])
            idx_bl = np.argmin(hp[:, 0] - hp[:, 1])
            return [tuple(hp[idx_tl]), tuple(hp[idx_tr]), tuple(hp[idx_br]), tuple(hp[idx_bl])]  # TL, TR, BR, BL
        return []

    # ---------------------- Supporting Functions ----------------------

    def _extract_four_corners_from_hull(self, hull: np.ndarray) -> List[Tuple[float, float]]:
        try:
            hp = hull.reshape(-1, 2)
            if len(hp) < 4:
                return []
            # Pick 4 that maximize area and form valid quad
            from itertools import combinations
            best = None
            max_area = 0.0
            for combo in combinations(range(len(hp)), 4):
                quad = hp[list(combo)]
                if not self._is_valid_quadrilateral(quad):
                    continue
                area = abs(cv2.contourArea(quad.astype(np.float32)))
                if area > max_area:
                    max_area = area
                    best = quad
            if best is not None:
                return [tuple(p) for p in best]
            # Fallback: extremes
            leftmost = hp[hp[:, 0].argmin()]
            rightmost = hp[hp[:, 0].argmax()]
            topmost = hp[hp[:, 1].argmin()]
            bottommost = hp[hp[:, 1].argmax()]
            uniq = []
            for p in [leftmost, rightmost, topmost, bottommost]:
                t = tuple(p)
                if not any(np.allclose(t, q, atol=5) for q in uniq):
                    uniq.append(t)
            return uniq if len(uniq) == 4 else []
        except Exception as e:
            logger.error(f"Error extracting corners from hull: {str(e)[:120]}")
            return []

    def _is_valid_quadrilateral(self, points: np.ndarray) -> bool:
        if len(points) != 4:
            return False

        def seg_intersect(p1, p2, p3, p4):
            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
            return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

        p = points
        if seg_intersect(p[0], p[1], p[2], p[3]):
            return False
        if seg_intersect(p[1], p[2], p[3], p[0]):
            return False
        return True

    def _line_intersection(self, l1, l2):
        x1, y1, x2, y2 = l1
        x3, y3, x4, y4 = l2
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)

    def _polar_line_intersection(self, line1, line2):
        rho1, theta1 = line1
        rho2, theta2 = line2
        A = np.array([[np.cos(theta1), np.sin(theta1)],
                      [np.cos(theta2), np.sin(theta2)]])
        b = np.array([rho1, rho2])
        try:
            x, y = np.linalg.solve(A, b)
            return (x, y)
        except Exception:
            return None

    def _select_best_quadrilateral(self, points):
        if len(points) < 4:
            return points
        pts = np.array(points, dtype=np.float32)
        hull = cv2.convexHull(pts)
        hp = hull.reshape(-1, 2)
        if len(hp) == 4:
            return [tuple(p) for p in hp]
        from itertools import combinations
        best = None
        max_area = 0.0
        for combo in combinations(range(len(hp)), 4):
            quad = hp[list(combo)]
            area = abs(cv2.contourArea(quad.astype(np.float32)))
            if area > max_area:
                max_area = area
                best = quad
        if best is not None:
            return [tuple(p) for p in best]
        return points[:4]

    # ---------------------- Motion & tracking ----------------------

    def _detect_camera_movement(self, image: np.ndarray):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        if self.last_frame_gray is not None:
            try:
                gray_s = cv2.resize(gray, (320, 240))
                last_s = cv2.resize(self.last_frame_gray, (320, 240))
                diff = cv2.absdiff(gray_s, last_s)
                motion_score = float(np.mean(diff))
                self.camera_moved = motion_score > self.motion_threshold
                if self.camera_moved:
                    logger.debug(f"Camera motion score={motion_score:.1f} > {self.motion_threshold}")
            except Exception:
                self.camera_moved = False
        self.last_frame_gray = gray.copy()

    def _try_fast_tracking(self, image: np.ndarray) -> List[Tuple[float, float]]:
        if self.last_valid_corners is None or len(self.last_valid_corners) != 4:
            return []
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            sw = 40
            refined = []
            for (x0, y0) in self.last_valid_corners:
                x, y = int(x0), int(y0)
                x_min = max(0, x - sw); x_max = min(gray.shape[1], x + sw)
                y_min = max(0, y - sw); y_max = min(gray.shape[0], y + sw)
                roi = gray[y_min:y_max, x_min:x_max]
                if roi.size == 0:
                    return []
                corners_roi = cv2.goodFeaturesToTrack(roi, 1, self.params['global']['harris_corner_quality'],
                                                      self.params['global']['harris_corner_min_dist'])
                if corners_roi is not None and len(corners_roi) > 0:
                    rx = corners_roi[0][0][0] + x_min
                    ry = corners_roi[0][0][1] + y_min
                    refined.append((float(rx), float(ry)))
                else:
                    refined.append((float(x), float(y)))
            return refined if len(refined) == 4 else []
        except Exception as e:
            logger.debug(f"Fast tracking failed: {str(e)[:120]}")
            return []

    # ---------------------- Visualization ----------------------

    def visualize_corners(self, image: np.ndarray, corners: List[Tuple[float, float]]) -> np.ndarray:
        vis = image.copy()
        if len(corners) == 4:
            names = ['a8', 'h8', 'h1', 'a1']  # TL, TR, BR, BL
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
            for (corner, name, color) in zip(corners, names, colors):
                x, y = int(corner[0]), int(corner[1])
                cv2.circle(vis, (x, y), 10, color, -1)
                cv2.circle(vis, (x, y), 12, (255, 255, 255), 2)
                label_pos = (x + 15, y - 15) if y > 30 else (x + 15, y + 30)
                cv2.putText(vis, name, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                coord_text = f"({x},{y})"
                coord_pos = (x + 15, y + 5) if y > 30 else (x + 15, y + 50)
                cv2.putText(vis, coord_text, coord_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            pts = np.array(corners, dtype=np.int32)
            cv2.polylines(vis, [pts], True, (255, 255, 255), 3)
            cv2.polylines(vis, [pts], True, (0, 255, 255), 2)

            # Diagonals
            cv2.line(vis, (int(corners[0][0]), int(corners[0][1])), (int(corners[3][0]), int(corners[3][1])), (128, 128, 128), 1, cv2.LINE_AA)
            cv2.line(vis, (int(corners[1][0]), int(corners[1][1])), (int(corners[2][0]), int(corners[2][1])), (128, 128, 128), 1, cv2.LINE_AA)

            valid = self._validate_corners_adaptive(corners, vis.shape)
            status_text = "VALID" if valid else "INVALID"
            status_color = (0, 255, 0) if valid else (0, 0, 255)
            cv2.putText(vis, f"Status: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            method_text = f"Method: {self.last_detection_method or 'Auto'}"
            cv2.putText(vis, method_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            stability_text = f"Stability: {self.stable_detection_count}/{self.param_smoothing['stability_threshold']}"
            stability_color = (0, 255, 0) if self.stable_detection_count >= self.param_smoothing['stability_threshold'] else (255, 255, 0)
            cv2.putText(vis, stability_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, stability_color, 2)

        return vis


# ---------------------- Test harness ----------------------

def test_enhanced_detection():
    """Interactive test: run on image, webcam, or a directory."""
    import cv2
    from pathlib import Path

    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    detector = EnhancedChessBoardDetector()

    test_mode = input("Test mode - (i)mage, (c)amera, or (d)irectory: ").strip().lower()

    if test_mode == 'i':
        image_path = input("Enter image path: ").strip()
        p = Path(image_path)
        if not p.exists():
            print(f"Image not found: {image_path}")
            return

        image = cv2.imread(str(p))
        if image is None:
            print(f"Could not load image: {image_path}")
            return

        print("Testing enhanced board corner detection...")
        corners = detector.detect_board_corners(image, 'auto')
        if len(corners) == 4:
            print("Success: Detected 4 corners")
            print(f"Corners: {corners}")
            vis = detector.visualize_corners(image, corners)
            out = "enhanced_corners_result.jpg"
            cv2.imwrite(out, vis)
            print(f"Saved visualization: {out}")
            cv2.imshow("Corner Detection Result", vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f"Failed to detect corners: {len(corners)} found")

    elif test_mode == 'c':
        print("Starting camera test... Press 'q' to quit, 's' to save frame")
        try:
            from vision.camera_utils import initialize_camera_robust
            cap = initialize_camera_robust(0)
        except ImportError:
            cap = cv2.VideoCapture(0)
        
        if cap is None or not cap.isOpened():
            print("Failed to open camera")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break

            corners = detector.detect_board_corners(frame, 'auto')
            display = detector.visualize_corners(frame, corners) if len(corners) == 4 else frame.copy()
            if len(corners) != 4:
                cv2.putText(display, "No corners detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Camera Test", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite("camera_test_frame.jpg", display)
                print("Saved frame")

        cap.release()
        cv2.destroyAllWindows()

    elif test_mode == 'd':
        dir_path = input("Enter directory path: ").strip()
        d = Path(dir_path)
        if not d.is_dir():
            print(f"Directory not found: {dir_path}")
            return

        image_files = list(d.glob("*.jpg")) + list(d.glob("*.png")) + list(d.glob("*.jpeg"))
        if not image_files:
            print(f"No images found in {dir_path}")
            return

        print(f"Testing {len(image_files)} images...")
        success = 0
        for imgp in image_files:
            image = cv2.imread(str(imgp))
            if image is None:
                print(f"Failed to load: {imgp.name}")
                continue
            corners = detector.detect_board_corners(image, 'auto')
            if len(corners) == 4:
                success += 1
                print(f"[OK] {imgp.name}")
                vis = detector.visualize_corners(image, corners)
                out = imgp.parent / f"detected_{imgp.name}"
                cv2.imwrite(str(out), vis)
            else:
                print(f"[--] {imgp.name}: {len(corners)} corners")

        print(f"\nResults: {success}/{len(image_files)} successful")

    else:
        print("Invalid test mode")


if __name__ == "__main__":
    test_enhanced_detection()