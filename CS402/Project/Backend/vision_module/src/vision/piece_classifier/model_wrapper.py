"""
Piece classifier model wrapper - loads trained PyTorch model and runs inference on tiles.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .class_folders import FOLDER_TO_FEN
import torch
import torch.nn as nn
from torchvision import models, transforms

logger = logging.getLogger(__name__)

# Must match train_transfer_learning.py
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
NUM_CLASSES = 13


def _build_model(arch: str) -> nn.Module:
    """Build model architecture (without loading weights)."""
    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    elif arch == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    elif arch == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=None)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, NUM_CLASSES)
    else:
        raise ValueError(f"Unknown arch: {arch}")
    return model


class PieceClassifier:
    """
    Wraps a trained piece classifier for inference on board tiles.
    """

    def __init__(
        self,
        model_path: str,
        tile_size: int = 128,
        device: Optional[str] = None,
    ):
        """
        Args:
            model_path: Path to saved model (e.g. Model/piece_classifier.pt)
            tile_size: Input tile size (must match training)
            device: 'cuda', 'cpu', or None (auto)
        """
        self.tile_size = tile_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.idx_to_class: Dict[int, str] = {}
        self.model = None

        path = Path(model_path)
        if not path.exists():
            logger.warning(f"Piece classifier model not found: {path}")
            return

        try:
            checkpoint = torch.load(path, map_location=self.device)
            arch = checkpoint.get("arch", "efficientnet_b0")
            class_to_idx = checkpoint.get("class_to_idx", {})
            self.idx_to_class = {v: k for k, v in class_to_idx.items()}

            self.model = _build_model(arch)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model = self.model.to(self.device)
            self.model.eval()

            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((tile_size, tile_size)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ])
            logger.info(f"Piece classifier loaded from {path}")
        except Exception as e:
            logger.warning(f"Failed to load piece classifier: {e}")
            self.model = None

    @property
    def is_available(self) -> bool:
        return self.model is not None

    def predict_tiles(
        self,
        tile_images: List[np.ndarray],
        confidence_threshold: float = 0.5,
    ) -> List[Tuple[str, float]]:
        """
        Run inference on a list of tile images (BGR, from OpenCV).

        Returns:
            List of (fen_symbol, confidence) for each tile, in same order.
            'empty' -> no piece. Non-empty -> FEN symbol (P, p, N, etc.)
        """
        if not self.is_available:
            return [("empty", 0.0)] * len(tile_images)

        tensors = []
        for img in tile_images:
            rgb = img[:, :, ::-1].copy() if len(img.shape) == 3 else np.stack([img] * 3, axis=-1)
            t = self.transform(rgb)
            tensors.append(t)
        batch = torch.stack(tensors).to(self.device)

        with torch.no_grad():
            logits = self.model(batch)
            probs = torch.softmax(logits, dim=1)
            confs, preds = probs.max(dim=1)

        results = []
        for i in range(len(tile_images)):
            idx = int(preds[i].item())
            conf = float(confs[i].item())
            folder_name = self.idx_to_class.get(idx, "empty")
            # Map Windows-safe folder name (p_b, n_b, etc.) back to FEN symbol
            fen = FOLDER_TO_FEN.get(folder_name, folder_name)
            if fen == "empty" or conf < confidence_threshold:
                results.append(("empty", conf))
            else:
                results.append((fen, conf))
        return results
