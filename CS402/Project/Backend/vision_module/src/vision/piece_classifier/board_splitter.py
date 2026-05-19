"""
Board Splitter - Split bird's-eye view into 64 square tiles with overlap.

Designed for per-square piece classification: pieces at the top of squares
often get cut off in the bird's-eye view. This module adds upward overlap
so each tile extends into the square above, capturing the full piece.

Board orientation (from EnhancedHomographyTransformer):
- Top-left = a8, Top-right = h8
- Bottom-left = a1, Bottom-right = h1
- row 0 = rank 8, row 7 = rank 1
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)


@dataclass
class SquareTile:
    """A single square tile extracted from the board."""
    image: np.ndarray
    row: int          # 0 = rank 8 (top), 7 = rank 1 (bottom)
    col: int          # 0 = file a, 7 = file h
    square: str       # Algebraic notation, e.g. "a1", "h8"
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2) in original board pixels

    @property
    def square_idx(self) -> int:
        """0-63 index: row*8 + col."""
        return self.row * 8 + self.col


def _bottom_crop_px_for_row(row: int) -> int:
    """
    Rank-dependent bottom crop: remove board-only pixels from the bottom.
    Rank 1 (row 7): 18 px, increasing to rank 8 (row 0): 60 px.
    These pixels are shifted to the top so tile height stays the same.
    """
    # row 0 = rank 8 -> 40 px, row 7 = rank 1 -> 12 px
    return 60 - 6 * row


def _extra_top_grab_px_for_row(row: int) -> int:
    """
    Extra pixels to grab from above for higher ranks (taller pieces like kings/queens).
    We can't crop more from the bottom, so for rank 8/7/6 we extend further up,
    then squish the taller tile down to 128x128. Rank 1 (row 7) gets 0.
    """
    # row 0 = rank 8 -> 80 px, row 1 = rank 7 -> 68 px, ... row 7 = rank 1 -> 0 px
    if row in [7, 6]:
        return 0
    elif row == 5:
        return 8
    elif row == 4:
        return 20
    elif row == 3:
        return 40
    elif row == 2:
        return 85
    elif row == 1:
        return 95
    elif row == 0:
        return 105


def _lateral_shift_px_for_col(col: int) -> Tuple[int, int]:
    """
    File-dependent lateral shift: remove pixels from one side, add to the other.
    D (col 3): small shift left (crop right, add left). E (col 4): small shift right.
    Values increase toward board edges (a/h) so edge files get more view correction.
    Returns (shift_right_px, shift_left_px):
      - shift_right_px: for cols 4-7, pixels to crop from left and add to right
      - shift_left_px: for cols 0-3, pixels to crop from right and add to left
    """
    # col 0-3 (a,b,c,d): shift left; col 3 (d) = 2 px, col 0 (a) = 14 px
    # col 4-7 (e,f,g,h): shift right; col 4 (e) = 2 px, col 7 (h) = 14 px
    if col <= 3:
        shift_left = 20 + 5 * (3 - col)
        return (0, shift_left)
    else:
        shift_right = 20 + 5 * (col - 4)
        return (shift_right, 0)


def split_board_into_tiles(
    board_image: np.ndarray,
    top_overlap: float = 0.2,
    top_overlap_px: Optional[int] = None,
    side_overlap: float = 0.0,
    tile_size: Optional[int] = None,
    board_top_margin: int = 0,
    board_side_margin: int = 0,
    tile_scale: float = 0.5,
) -> List[SquareTile]:
    """
    Split a bird's-eye view chess board into 64 square tiles.

    Args:
        board_image: Warped bird's-eye view (square or with top/side margins).
        top_overlap: Fraction of square height to extend upward (used if top_overlap_px is None).
        top_overlap_px: Fixed pixels for base top overlap. When set, overrides top_overlap.
        side_overlap: Fraction of square width to overlap horizontally (optional).
        tile_size: If set, resize each tile to (tile_size, tile_size) for the model.
        board_top_margin: Pixels above rank 8 (when homography uses output_top_margin).
        board_side_margin: Pixels left/right of board (when homography uses output_side_margin).
                          Board occupies center; enables lateral view shift for piece capture.
        tile_scale: Scale factor for tile crop/overlap pixels (1.0=default). Use >1 for taller
                    pieces (higher camera), <1 for shorter. Preserves row/rank differences.

    Returns:
        List of 64 SquareTile objects in order a8, b8, ..., h8, a7, ..., h1.
    """
    h, w = board_image.shape[:2]
    # Board dimensions: top margin adds to height, side margin adds to width
    if board_top_margin > 0 and h > w:
        board_h = h - board_top_margin
        y_offset = board_top_margin
    else:
        board_h = h
        y_offset = 0
    if board_side_margin > 0 and w > board_h:
        board_w = w - 2 * board_side_margin
        x_offset = board_side_margin
    else:
        board_w = min(w, board_h) if w != board_h else w
        x_offset = 0
        if w != board_h and board_side_margin == 0:
            logger.warning(f"Board is not square ({w}x{h}), using min dimension")
            size = min(h, w)
            board_image = board_image[:size, :size]
            h, w = size, size
            board_w = board_h = size
    square_h = board_h / 8.0
    square_w = board_w / 8.0

    tile_size_out = tile_size

    # Base top overlap: fixed px (default 20) or fraction, whichever gives more
    if top_overlap_px is not None:
        base_top_overlap_px = float(top_overlap_px)
    else:
        base_top_overlap_px = max(20.0, square_h * top_overlap)
    side_overlap_px = square_w * side_overlap

    tiles: List[SquareTile] = []

    for row in range(8):
        for col in range(8):
            # Rank-dependent bottom crop: shift window up (crop bottom, add to top)
            raw_bottom_crop = _bottom_crop_px_for_row(row)
            bottom_crop_px = raw_bottom_crop * tile_scale
            # Total top = base + bottom_crop (shift from bottom to top), scaled
            extra_top_px = (base_top_overlap_px + raw_bottom_crop) * tile_scale

            # Base y bounds (board starts at y_offset when board_top_margin is used)
            y_base_start = y_offset + row * square_h
            y_base_end = y_offset + (row + 1) * square_h

            # Add top overlap. Row 0 can use full extra_top if we have board_top_margin.
            if row > 0:
                y_start = y_base_start - extra_top_px
            elif y_offset >= extra_top_px:
                # Row 0 with margin: extend into the margin above rank 8
                y_start = y_base_start - extra_top_px
            else:
                # Row 0, no/little margin: shift up only by bottom_crop
                y_start = y_base_start - bottom_crop_px

            # For higher rows, grab more from top (taller pieces); tile gets taller, we squish to 128x128
            extra_top_grab = _extra_top_grab_px_for_row(row) * tile_scale
            y_start = y_start - extra_top_grab

            # Shift bottom up by bottom_crop_px (crop from bottom, add equivalent to top)
            y_end = y_base_end - bottom_crop_px

            # Base x bounds (board starts at x_offset when board_side_margin is used)
            x_base_start = x_offset + col * square_w
            x_base_end = x_offset + (col + 1) * square_w

            # Lateral shift: d shifts right (crop left, add right), e shifts left; increases toward a/h
            sr, sl = _lateral_shift_px_for_col(col)
            shift_right, shift_left = sr * tile_scale, sl * tile_scale
            x_start = x_base_start + shift_right - shift_left - (side_overlap_px if col > 0 else 0)
            x_end = x_base_end + shift_right - shift_left + (side_overlap_px if col < 7 else 0)

            # Clamp to image bounds
            x1 = max(0, int(np.floor(x_start)))
            y1 = max(0, int(np.floor(y_start)))
            x2 = min(w, int(np.ceil(x_end)))
            y2 = min(h, int(np.ceil(y_end)))

            # Extract tile
            tile_img = board_image[y1:y2, x1:x2].copy()

            # Resize if requested
            if tile_size_out is not None and (tile_img.shape[0] != tile_size_out or tile_img.shape[1] != tile_size_out):
                tile_img = cv2.resize(tile_img, (tile_size_out, tile_size_out), interpolation=cv2.INTER_LINEAR)

            # Algebraic notation: a8 at top-left, a1 at bottom-left
            file_char = chr(ord("a") + col)
            rank_num = 8 - row
            square_name = f"{file_char}{rank_num}"

            tile = SquareTile(
                image=tile_img,
                row=row,
                col=col,
                square=square_name,
                bbox=(x1, y1, x2, y2),
            )
            tiles.append(tile)

    return tiles


def row_col_to_square(row: int, col: int, board_orientation: int = 0) -> str:
    """
    Map warp position (row, col) to algebraic square based on board orientation.

    The bird's-eye warp is fixed (TL, TR, BR, BL -> square). Orientation indicates
    which physical edge is rank 8 (a8-h8). FEN expects left-to-right within each rank.

    Orientation: 0=TL is a8, 1=90°CW (right=rank8), 2=180°, 3=270°CW (left=rank8).
    """
    o = board_orientation % 4
    if o == 0:
        # Top=rank8, Left=file a. Row 0=a8..h8, row 7=a1..h1
        file_idx, rank_idx = col, row
    elif o == 1:
        # Right=rank8. Col 7 has a8..h8 (row 0..7). rank_idx=7-col, file_idx=row
        rank_idx = 7 - col
        file_idx = row
    elif o == 2:
        # Bottom=rank8. Row 7 has h8..a8 (col 0..7)
        rank_idx = 7 - row
        file_idx = 7 - col
    else:
        # o==3: Left=rank8. Col 0 has a8..h8 (row 0..7). When black is vertical on left,
        # corner order can place files reversed in the warp: use file_idx=7-row
        rank_idx = col
        file_idx = 7 - row
    file_char = chr(ord("a") + file_idx)
    rank_num = 8 - rank_idx
    return f"{file_char}{rank_num}"


def square_to_row_col(square: str, board_orientation: int = 0) -> Tuple[int, int]:
    """
    Inverse of row_col_to_square: algebraic square -> (row, col) in warp.
    """
    file_char, rank_char = square[0], square[1]
    file_idx = ord(file_char) - ord("a")
    rank_idx = 8 - int(rank_char)  # 0=rank8, 7=rank1
    o = board_orientation % 4
    if o == 0:
        row, col = rank_idx, file_idx
    elif o == 1:
        col = 7 - rank_idx
        row = file_idx
    elif o == 2:
        row = 7 - rank_idx
        col = 7 - file_idx
    else:
        col = rank_idx
        row = 7 - file_idx  # inverse of file_idx=7-row
    return row, col


def square_idx_to_algebraic(square_idx: int, board_orientation: int = 0) -> str:
    """
    Convert 0-63 index to algebraic notation.
    Index 0 = a8 (for orient 0), index 63 = h1.
    """
    row = square_idx // 8
    col = square_idx % 8
    return row_col_to_square(row, col, board_orientation)
