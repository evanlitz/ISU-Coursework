#!/usr/bin/env python3
"""
Train piece classifier using Transfer Learning (PyTorch).

Expects dataset in ImageFolder format with Windows-safe class folder names:
  data/chess_dataset/square_dataset/
    train/empty/, train/P/, train/p_b/, train/N/, ... (13 classes)
    val/empty/, val/P/, ... (optional - uses train split if missing)

Class folder names must match class_folders.FOLDER_NAMES (empty, P, p_b, N, n_b, etc.)
for inference compatibility. Use organize_captured_tiles.py or batch_organize_from_fen.py
to build the dataset from captured tiles.

Usage:
  cd Backend/vision_module
  python data/chess_dataset/tools/train_transfer_learning.py [--model efficientnet_b0] [--epochs 10]

Small run (few images):
  python data/chess_dataset/tools/train_transfer_learning.py --epochs 5 --batch-size 8

Output: Model/piece_classifier_<arch>.pt (e.g. piece_classifier_efficientnet_b0.pt)
  Each base model saves to its own file so training one does not overwrite another.
"""

import argparse
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import ConcatDataset, DataLoader, Subset, random_split
from torchvision import models, transforms
from torchvision.datasets import ImageFolder

HERE = Path(__file__).resolve().parent
DS_DIR = HERE.parent
# vision_module root (tools -> chess_dataset -> data -> vision_module)
ROOT = HERE.parents[2]
MODEL_DIR = ROOT / "Model"


def get_output_path(arch: str) -> Path:
    """Model path per architecture so different base models do not overwrite each other."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"40_inch_heightpiece_classifier_{arch}.pt"

# 13 classes: empty, P, p, N, n, B, b, R, r, Q, q, K, k
NUM_CLASSES = 13

# ImageNet normalization (pretrained models expect this)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_augment_pil_transforms(tile_size: int = 128, strong_lighting: bool = True):
    """Geometric/color augmentations only (PIL in → PIL out). Used for training and viz previews."""
    augs = [
        transforms.RandomResizedCrop(tile_size, scale=(0.9, 1.0)),
        # Mirror left/right (vertical axis) — no rotation/tilt; lighting augments follow.
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(
            brightness=0.4 if strong_lighting else 0.2,
            contrast=0.4 if strong_lighting else 0.2,
            saturation=0.3 if strong_lighting else 0.2,
            hue=0.1,
        ),
    ]
    if strong_lighting:
        # Simulate low-light: random grayscale, slight blur, sharpness
        augs.extend([
            transforms.RandomGrayscale(p=0.1),  # occasional grayscale for color invariance
            transforms.RandomApply([transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 0.5))], p=0.2),
            transforms.RandomAdjustSharpness(sharpness_factor=0.5, p=0.2),  # slightly dull (low light)
        ])
    return transforms.Compose(augs)


def get_train_transforms(tile_size: int = 128, strong_lighting: bool = True):
    """Augmentations are applied on-the-fly; no disk copies are saved."""
    return transforms.Compose([
        *get_train_augment_pil_transforms(tile_size, strong_lighting).transforms,
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def get_val_transforms(tile_size: int = 128):
    return transforms.Compose([
        transforms.Resize((tile_size, tile_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def build_model(arch: str = "efficientnet_b0") -> nn.Module:
    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    elif arch == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    elif arch == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, NUM_CLASSES)
    else:
        raise ValueError(f"Unknown arch: {arch}")
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=str(DS_DIR / "square_dataset"))
    parser.add_argument("--model", type=str, default="mobilenet_v3_small",
                    choices=["efficientnet_b0", "resnet18", "mobilenet_v3_small"])
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--tile-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-strong-lighting", action="store_true",
                        help="Disable strong lighting augments (brightness/contrast 0.2 instead of 0.4)")
    parser.add_argument("--repeats", type=int, default=5,
                        help="Train on each image N times per epoch with different random augments (default: 5)")
    args = parser.parse_args()

    data_path = Path(args.data)
    train_dir = data_path / "train"
    val_dir = data_path / "val"
    if not train_dir.exists():
        print(f"Error: Dataset not found at {train_dir}")
        print("Create square_dataset/train/ with class subfolders (empty, P, p_b, N, n_b, etc.)")
        print("Use organize_captured_tiles.py or batch_organize_from_fen.py to build from captures.")
        sys.exit(1)

    train_full = ImageFolder(
        str(train_dir),
        transform=get_train_transforms(args.tile_size, strong_lighting=not args.no_strong_lighting),
    )
    if val_dir.exists():
        val_ds = ImageFolder(str(val_dir), transform=get_val_transforms(args.tile_size))
        train_ds = train_full
        print(f"Train: {len(train_ds)} samples, Val: {len(val_ds)} samples (from val/)")
    else:
        # No val folder: use 80/20 split from train for small runs
        n = len(train_full)
        n_val = max(1, n // 5)
        n_train = n - n_val
        train_subset, val_subset = random_split(train_full, [n_train, n_val])
        train_ds = train_subset
        # Use separate ImageFolder with val transforms for validation
        val_imf = ImageFolder(str(train_dir), transform=get_val_transforms(args.tile_size))
        val_ds = Subset(val_imf, val_subset.indices)
        print(f"Train: {len(train_ds)} samples, Val: {len(val_ds)} samples (80/20 split from train/)")

    # Each image appears N times per epoch, each with different random augmentations
    if args.repeats > 1:
        train_ds = ConcatDataset([train_ds] * args.repeats)
        print(f"Repeats: {args.repeats}x — training on {len(train_ds)} samples/epoch (each image {args.repeats} times with different lighting/crop)")

    print(f"Classes: {train_full.classes}")

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = build_model(args.model)
    device = torch.device(args.device)
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3)

    best_acc = 0.0
    best_loss = float("inf")
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        correct, total, val_loss_sum = 0, 0, 0.0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                out = model(imgs)
                val_loss_sum += criterion(out, labels).item()
                _, pred = out.max(1)
                correct += (pred == labels).sum().item()
                total += labels.size(0)
        val_acc = correct / total
        val_loss = val_loss_sum / len(val_loader)
        scheduler.step(1 - val_acc)

        print(f"Epoch {epoch+1}/{args.epochs}  loss={train_loss/len(train_loader):.4f}  val_acc={val_acc:.4f}  val_loss={val_loss:.4f}")
        # Save when accuracy improves, or when accuracy ties but loss is lower (more confident)
        save_this = val_acc > best_acc or (val_acc == best_acc and val_loss < best_loss)
        if save_this:
            best_acc = val_acc
            best_loss = val_loss
            output_path = get_output_path(args.model)
            torch.save({
                "model_state_dict": model.state_dict(),
                "class_to_idx": train_full.class_to_idx,
                "arch": args.model,
                "num_classes": NUM_CLASSES,
            }, output_path)
            print(f"  -> Saved best model to {output_path}")

    # Always save final model (in addition to best) so we have something usable
    output_path = get_output_path(args.model)
    torch.save({
        "model_state_dict": model.state_dict(),
        "class_to_idx": train_full.class_to_idx,
        "arch": args.model,
        "num_classes": NUM_CLASSES,
    }, output_path)

    print(f"\nTraining complete. Best val accuracy: {best_acc:.4f}")
    print(f"Model saved to: {output_path}")


if __name__ == "__main__":
    main()
