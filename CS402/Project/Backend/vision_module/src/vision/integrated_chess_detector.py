import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging
from pathlib import Path

from vision.piece_classifier import PieceClassifier, fen_from_classifier
from vision.enhanced_homography_transformer import EnhancedHomographyTransformer
from .enhanced_chessboard_detector import EnhancedChessBoardDetector

logger = logging.getLogger(__name__)


class IntegratedChessDetector:
    """
    Integrates chessboard detection, homography transformation,
    per-square piece classification, and FEN generation.
    """

    def __init__(self, classifier_path: Optional[str] = None, output_size: int = 800):
        """
        Initializes the integrated chess detector.

        Args:
            classifier_path: Path to the trained piece classifier (Model/piece_classifier.pt)
            output_size: Desired size for the bird's eye view of the chessboard
        """
        self.output_size = output_size
        self.board_detector = EnhancedChessBoardDetector()
        self.homography_transformer = EnhancedHomographyTransformer(output_size=output_size)
        self.piece_classifier = None

        if classifier_path:
            try:
                self.piece_classifier = PieceClassifier(classifier_path, tile_size=128)
                if self.piece_classifier.is_available:
                    logger.info(f"Piece classifier loaded from: {classifier_path}")
                else:
                    self.piece_classifier = None
            except Exception as e:
                logger.warning(f"Failed to load piece classifier: {e}")
                self.piece_classifier = None

    def process_image(self, image: np.ndarray) -> Dict:
        """
        Processes an image to detect the chessboard, classify pieces, and produce FEN.

        Args:
            image: Input image (BGR format)

        Returns:
            A dictionary containing processing results
        """
        results = {
            'success': False,
            'detected_pieces': [],
            'piece_fen': None,
            'piece_map': {},
            'warped_board': None,
            'detections': [],
            'corners_image': None,
            'error_message': ''
        }

        try:
            # Step 1: Detect board corners
            logger.info("Step 1: Detecting board corners...")
            corners = self.board_detector.detect_board_corners(image, method='auto')
            if not corners:
                results['error_message'] = "Failed to detect board corners"
                return results

            results['corners_image'] = self.board_detector.visualize_corners(image.copy(), corners)

            # Step 2: Calibrate homography and warp to bird's-eye
            if not self.homography_transformer.calibrate(image, corners):
                results['error_message'] = "Homography calibration failed"
                return results

            warped = self.homography_transformer.warp_image(image)
            if warped is None:
                results['error_message'] = "Bird's-eye transform failed"
                return results

            results['warped_board'] = warped

            # Step 3: Piece classification
            if self.piece_classifier is None or not self.piece_classifier.is_available:
                results['error_message'] = "Piece classifier not available"
                results['piece_fen'] = "8/8/8/8/8/8/8/8"
                results['success'] = True
                return results

            pipeline_results = fen_from_classifier(
                warped,
                self.piece_classifier,
                top_overlap=0.2,
                tile_size=128,
                confidence_threshold=0.5,
            )
            results.update(pipeline_results)
            results['piece_fen'] = pipeline_results['fen']
            results['detected_pieces'] = pipeline_results.get('detections', [])
            results['detections'] = results['detected_pieces']

            results['success'] = True
            logger.info(f"Integrated pipeline produced FEN: {results.get('piece_fen')}")
            return results

        except Exception as e:
            results['error_message'] = f"Processing failed: {e}"
            logger.error(results['error_message'])
            return results
