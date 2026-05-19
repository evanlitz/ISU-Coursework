"""
Shared vision configuration - board output size and margins.
Edit these values in one place; run.py, capture_training_data, and calibration use them.
"""

import cv2

# Output size for bird's-eye view - must match between calibration and live detection
BOARD_OUTPUT_SIZE = 1800
# Extra pixels above rank 8 (homography) for piece-top capture
BOARD_TOP_MARGIN = 225
# Extra pixels left/right of board for piece-side capture (lateral view shift)
BOARD_SIDE_MARGIN = 35

# Camera mounted upside-down: undistort first (uses K on raw sensor), then rotate 180°.
# Set True for upside-down USB mount; then re-run board corner calibration.
# After toggling, corners/homography must match this pipeline.
CAMERA_ROTATE_180 = False


def undistort_and_orient_frame(image, camera_matrix, dist_coeffs):
    """
    Lens undistortion on raw frames, then optional 180° rotation.
    Same order as EnhancedHomographyTransformer.transform_to_birdseye.
    Corners / homography are expressed in this coordinate space.
    """
    if image is None:
        return None
    if camera_matrix is not None and dist_coeffs is not None:
        out = cv2.undistort(image, camera_matrix, dist_coeffs)
    else:
        out = image.copy()
    if CAMERA_ROTATE_180:
        out = cv2.rotate(out, cv2.ROTATE_180)
    return out
