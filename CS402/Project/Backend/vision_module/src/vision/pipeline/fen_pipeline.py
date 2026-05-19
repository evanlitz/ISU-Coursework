"""
FEN Pipeline for Chess Vision
Converts YOLO detections to FEN notation and maps pieces to chess squares.

@author Abhay Prasanna Rao
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict
import chess
import logging

from vision.enhanced_homography_transformer import EnhancedHomographyTransformer

logger = logging.getLogger(__name__)


# ---------- Detection class ----------
class Detection:
    def __init__(self, label: str, board_coords: Tuple[float, float, float, float], confidence: float):
        """
        Represents a single detected piece mapped into board coordinates.
        label: FEN piece symbol (e.g., 'P', 'k')
        board_coords: bounding box in warped board coordinates (x1,y1,x2,y2)
        confidence: YOLO confidence score
        """
        self.label = label
        self.board_coords = board_coords
        self.confidence = confidence

    def center(self):
        x_min, y_min, x_max, y_max = self.board_coords
        return ((x_min + x_max) / 2, (y_min + y_max) / 2)

    def square(self, board_size: int = 800) -> str:
        """
        Convert detection center to chess square (algebraic notation).
        Default assumes a8 is top-left of warped board.
        """
        x_center, y_center = self.center()
        file_idx = int(x_center // (board_size / 8))
        rank_idx = int(y_center // (board_size / 8))
        
        # Ensure indices are within bounds
        file_idx = max(0, min(7, file_idx))
        rank_idx = max(0, min(7, rank_idx))
        
        files = "abcdefgh"
        ranks = "87654321"  # top row = rank 8
        return f"{files[file_idx]}{ranks[rank_idx]}"


# ---------- Homography ----------
def detections_with_homography(image, raw_detections, board_corners, board_size: int = 800):
    """
    Warp YOLO detections into board coordinates using homography.
    """
    transformer = EnhancedHomographyTransformer(output_size=board_size)

    if board_corners is not None:
        if not transformer.calibrate(image, board_corners):
            raise RuntimeError("Homography calibration failed in fen_pipeline")
        warped = transformer.warp_image(image)
    else:
        warped = cv2.resize(image, (board_size, board_size))

    detections = []
    for label, pixel_coords, conf in raw_detections:
        x1, y1, x2, y2 = pixel_coords

        if board_corners is not None:
            pts = np.array(
                [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                dtype=np.float32
            ).reshape(-1, 1, 2)
            warped_pts = cv2.perspectiveTransform(pts, transformer.homography_matrix).reshape(-1, 2)
            x_min, y_min = warped_pts[:, 0].min(), warped_pts[:, 1].min()
            x_max, y_max = warped_pts[:, 0].max(), warped_pts[:, 1].max()
            board_coords = (x_min, y_min, x_max, y_max)
        else:
            # Already normalized to board view
            board_coords = (x1, y1, x2, y2)

        detections.append(Detection(label, board_coords, conf))

    return detections, warped


# ---------- FEN generation ----------
def generate_fen(piece_map: Dict[str, str]) -> str:
    """
    Build piece-placement FEN string (no game state).
    """
    fen_rows = []
    ranks = "87654321"
    files = "abcdefgh"
    for rank in ranks:
        row_fen = ""
        empty_count = 0
        for file in files:
            sq = f"{file}{rank}"
            piece = piece_map.get(sq)
            if piece is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    row_fen += str(empty_count)
                    empty_count = 0
                row_fen += piece
        if empty_count > 0:
            row_fen += str(empty_count)
        fen_rows.append(row_fen)
    return "/".join(fen_rows)

# ---------- Piece label mapping ----------
PIECE_LABEL_MAP = {
    # Standard labels
    "white-pawn": "P", "white-rook": "R", "white-knight": "N",
    "white-bishop": "B", "white-queen": "Q", "white-king": "K",
    "black-pawn": "p", "black-rook": "r", "black-knight": "n",
    "black-bishop": "b", "black-queen": "q", "black-king": "k",
    
    # Alternative labels that might be detected
    "pawn": "P", "rook": "R", "knight": "N", "bishop": "B", "queen": "Q", "king": "K",
    "white_pawn": "P", "white_rook": "R", "white_knight": "N",
    "white_bishop": "B", "white_queen": "Q", "white_king": "K",
    "black_pawn": "p", "black_rook": "r", "black_knight": "n",
    "black_bishop": "b", "black_queen": "q", "black_king": "k",
    
    # Handle case variations
    "White-Pawn": "P", "White-Rook": "R", "White-Knight": "N",
    "White-Bishop": "B", "White-Queen": "Q", "White-King": "K",
    "Black-Pawn": "p", "Black-Rook": "r", "Black-Knight": "n",
    "Black-Bishop": "b", "Black-Queen": "q", "Black-King": "k",
}

# ---------- Full pipeline ----------
def fen_from_yolo(image, raw_detections, board_corners=None, board_size: int = 800):
    """
    Convert YOLO detections + board corners → raw FEN (piece placement only).

    Args:
        image: Original camera frame
        raw_detections: list of (label, (x1,y1,x2,y2), confidence)
        board_corners: list of 4 (x,y) board corner points
        board_size: size of warped output board (default=800)

    Returns:
        dict with:
          - fen: piece placement FEN only
          - piece_map: dict {square: piece}
          - warped_board: warped image
          - detections: list of Detection objects
    """
    detections, warped = detections_with_homography(image, raw_detections, board_corners, board_size)

    piece_map = {}
    for d in detections:
        try:
            square = d.square(board_size)
            if d.confidence > 0.2:
                mapped = PIECE_LABEL_MAP.get(d.label, None)
                if mapped:
                    piece_map[square] = mapped
        except Exception as e:
            logger.debug(f"Error processing detection {d.label}: {e}")
            continue

    try:
        piece_fen = generate_fen(piece_map)
    except Exception as e:
        logger.warning(f"Error generating FEN: {e}")
        piece_fen = "8/8/8/8/8/8/8/8"

    return {
        "fen": piece_fen,
        "piece_map": piece_map,
        "warped_board": warped,
        "detections": detections,
    }
