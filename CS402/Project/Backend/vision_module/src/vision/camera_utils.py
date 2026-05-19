"""
Camera Utilities for Chess Vision
Cross-platform camera initialization and management.

Supports high-resolution (e.g. 4K UVC) webcams on Windows (DirectShow / MSMF),
optional MJPEG, and trying resolution presets until frames decode cleanly.

@author Abhay Prasanna Rao
"""

import cv2
import platform
import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try from largest — many 4K USB cameras only expose full modes or MJPEG at high res.
_RESOLUTION_PRESETS = (
    (3840, 2160),
    (2560, 1440),
    (1920, 1080),
    (1280, 720),
    (640, 480),
)


def _frame_ok(frame) -> bool:
    if frame is None:
        return False
    try:
        if frame.size == 0:
            return False
        h, w = frame.shape[:2]
        return w > 0 and h > 0
    except (AttributeError, IndexError, ValueError):
        return False


def _warmup_read(
    cap,
    max_attempts: int = 6,
    *,
    early_exit: bool = True,
) -> Tuple[bool, Optional[object]]:
    """
    Grab frames until one is valid. Uses early exit by default: at 4K MJPEG, each
    full read() can take ~1s over USB — doing 15 reads per preset was ~15–20s per try.
    """
    last = None
    for _ in range(max_attempts):
        ret, fr = cap.read()
        if ret and _frame_ok(fr):
            last = fr
            if early_exit:
                return True, last
    if last is not None:
        return True, last
    return False, None


def _try_mjpeg(cap) -> None:
    try:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    except Exception:
        pass


def _windows_backend_order():
    """
    DirectShow before MSMF: many USB 4K webcams fail MSMF ('Failed to select stream 0')
    but work on DSHOW; trying MSMF first added wasted time and noisy warnings.
    MSMF remains as fallback for devices that need it.
    """
    order = [
        (cv2.CAP_DSHOW, "DirectShow"),
    ]
    msmf = getattr(cv2, "CAP_MSMF", None)
    if msmf is not None:
        order.append((msmf, "MSMF"))
    order.append((cv2.CAP_ANY, "ANY"))
    return order


def _build_preset_list(
    width: Optional[int], height: Optional[int]
) -> Tuple[Tuple[int, int], ...]:
    if width is not None and height is not None and width > 0 and height > 0:
        user = (width, height)
        out = [user]
        for w, h in _RESOLUTION_PRESETS:
            if (w, h) != user:
                out.append((w, h))
        return tuple(out)
    return _RESOLUTION_PRESETS


def _configure_resolution(
    cap, presets: Tuple[Tuple[int, int], ...], fps: float = 30.0
) -> bool:
    """
    Apply resolution/FPS and confirm we get valid frames.
    Tries MJPEG first (USB bandwidth), then the same presets without forcing MJPEG.
    """
    def try_presets(use_mjpeg: bool) -> bool:
        for w, h in presets:
            try:
                if use_mjpeg:
                    _try_mjpeg(cap)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(w))
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(h))
                cap.set(cv2.CAP_PROP_FPS, fps)
            except Exception as e:
                logger.debug(f"Could not set {w}x{h}: {e}")
                continue

            ret, frame = _warmup_read(cap, max_attempts=6)
            if ret and _frame_ok(frame):
                aw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                ah = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                tag = "MJPEG" if use_mjpeg else "default codec"
                logger.info(f"Camera mode OK ({tag}): requested {w}x{h}, actual {aw}x{ah}")
                return True
        return False

    if try_presets(use_mjpeg=True):
        return True
    logger.info("MJPEG modes failed; retrying resolution presets without forcing MJPEG")
    if try_presets(use_mjpeg=False):
        return True

    # Last resort: driver default (no resize)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    ret, frame = _warmup_read(cap, max_attempts=8)
    if ret and _frame_ok(frame):
        aw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        ah = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera mode OK (default resolution): {aw}x{ah}")
        return True

    logger.error("Could not obtain valid frames at any resolution preset")
    return False


def initialize_camera_robust(
    camera_id=0, width: Optional[int] = None, height: Optional[int] = None
):
    """
    Open the camera and lock a working resolution.

    For 4K USB cameras on Windows, MJPEG + explicit 3840x2160 (or presets) avoids
    empty/invalid Mat frames that occur when forcing 1080p on some devices.

    Args:
        camera_id: Device index.
        width, height: If both set, try this size first, then fall back through presets.
    """
    cap = None

    try:
        system = platform.system()

        if system == "Linux":
            backend_priority = [
                (cv2.CAP_V4L2, "V4L2"),
                (cv2.CAP_ANY, "ANY"),
            ]
            os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
        else:
            backend_priority = _windows_backend_order()

        presets = _build_preset_list(width, height)

        for backend_id, backend_name in backend_priority:
            try:
                if backend_id == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(camera_id)
                else:
                    cap = cv2.VideoCapture(camera_id, backend_id)

                logger.info(f"Attempting to connect to camera {camera_id} ({backend_name} backend)")

                if not cap.isOpened():
                    if cap:
                        cap.release()
                        cap = None
                    logger.warning(f"Failed to open camera {camera_id} with {backend_name} backend")
                    continue

                ret, test_frame = cap.read()
                if not ret or not _frame_ok(test_frame):
                    cap.release()
                    cap = None
                    logger.warning(
                        f"Camera {camera_id} opened but failed initial read with {backend_name}"
                    )
                    continue

                logger.info(f"Successfully opened camera {camera_id} with {backend_name} backend")

                if not _configure_resolution(cap, presets):
                    cap.release()
                    cap = None
                    logger.warning(f"{backend_name}: could not configure usable video mode")
                    continue

                logger.info(f"Camera {camera_id} initialized successfully")
                return cap

            except Exception as e:
                if cap:
                    cap.release()
                    cap = None
                logger.warning(f"Exception with {backend_name} backend: {e}")
                continue

        logger.error(f"Failed to open camera {camera_id} with all backends")
        return None

    except Exception as e:
        logger.error(f"Camera initialization error: {e}")
        if cap:
            cap.release()
        return None
