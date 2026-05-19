"""
FEN from classifier - split board into tiles, classify, assemble FEN.
"""

import logging
from typing import Dict, Optional

from vision.pipeline.fen_pipeline import generate_fen
from vision.piece_classifier.board_splitter import split_board_into_tiles, row_col_to_square
from vision.piece_classifier.model_wrapper import PieceClassifier

logger = logging.getLogger(__name__)


def fen_from_classifier(
    warped_board,
    classifier: PieceClassifier,
    top_overlap: float = 0.2,
    top_overlap_px: Optional[int] = None,
    tile_size: int = 128,
    confidence_threshold: float = 0.5,
    board_top_margin: int = 0,
    board_side_margin: int = 0,
    board_orientation: int = 0,
    tile_scale: float = 0.5,
) -> Dict[str, object]:
    """
    Classify 64 board tiles and produce FEN.

    Args:
        warped_board: Bird's-eye view image (square or with top margin)
        classifier: Loaded PieceClassifier instance
        top_overlap: Overlap fraction for board splitter (used if top_overlap_px is None)
        top_overlap_px: Fixed pixels for top overlap
        tile_size: Tile size for model input
        confidence_threshold: Min confidence to accept non-empty prediction
        board_top_margin: Pixels above rank 8 (when homography uses output_top_margin)
        board_side_margin: Pixels left/right of board (when homography uses output_side_margin)
        board_orientation: 0-3, which physical edge is rank 8 (used for FEN mapping only)
        tile_scale: Scale factor for tile crops (1.0=default, >1 for taller pieces)

    Returns:
        dict with fen, piece_map, warped_board, detections (pseudo-detections for compatibility)
    """
    piece_map: Dict[str, str] = {}
    detections = []

    if classifier is None or not classifier.is_available:
        logger.warning("Piece classifier not available, returning empty board")
        return {
            "fen": "8/8/8/8/8/8/8/8",
            "piece_map": {},
            "warped_board": warped_board,
            "detections": [],
        }

    tiles = split_board_into_tiles(
        warped_board,
        top_overlap=top_overlap,
        top_overlap_px=top_overlap_px,
        tile_size=tile_size,
        board_top_margin=board_top_margin,
        board_side_margin=board_side_margin,
        tile_scale=tile_scale,
    )
    tile_images = [t.image for t in tiles]
    predictions = classifier.predict_tiles(tile_images, confidence_threshold=confidence_threshold)

    for tile, (fen, conf) in zip(tiles, predictions):
        if fen != "empty":
            square = row_col_to_square(tile.row, tile.col, board_orientation)
            piece_map[square] = fen
            x1, y1, x2, y2 = tile.bbox
            detections.append((fen, (float(x1), float(y1), float(x2), float(y2)), conf))

    try:
        piece_fen = generate_fen(piece_map)
    except Exception as e:
        logger.warning(f"Error generating FEN: {e}")
        piece_fen = "8/8/8/8/8/8/8/8"

    return {
        "fen": piece_fen,
        "piece_map": piece_map,
        "warped_board": warped_board,
        "detections": detections,
    }
