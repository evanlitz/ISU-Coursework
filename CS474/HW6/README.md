# CS474 HW6: Fully-Connected Network on CIFAR-10

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

PyTorch implementation of a fully-connected (MLP) network for 10-class image classification on CIFAR-10. Experiments analyze the effect of batch size and learning rate on training/test accuracy and overfitting.

## Architecture

A LeNet-inspired fully-connected network:
```
Input (3×32×32 = 3072) → FC(512) → ReLU → FC(512) → ReLU → FC(10)
```
Trained with SGD for 20 epochs.

## Experiments

### Part A – Default Settings
Batch size 16, learning rate 0.01 → **48.27% test / 71.74% train**. Gap indicates overfitting.

### Part B – Batch Size Ablation (lr=0.01)

| Batch | Test Acc | Train Acc |
|-------|----------|-----------|
| 8 | 34.43% | 41.4% | 
| 16 | 48.27% | 71.7% |
| 32 | 52.59% | 85.59% |
| 64 | 54.07% | 90.14% |

Larger batches provide more stable gradient estimates and higher accuracy, but overfitting persists throughout.

### Part C – Learning Rate Ablation (batch=16)

| LR | Test Acc | Train Acc |
|----|----------|-----------|
| 0.01 | 48.27% | 71.74% |
| 0.001 | **55.13%** | 85.1% |
| 0.0001 | 52.13% | 54.79% |
| 0.00001 | 34.07% | 33.61% |

Best test accuracy: **55.13%** at lr=0.001. Very small learning rates fail to learn; very large rates cause instability.

## Files

| File | Description |
|------|-------------|
| `code/solution.py` | `LeNet` model definition and argument parsing |
| `code/helper.py` | CIFAR-10 data loading, training loop, test evaluation |
| `code/main.py` | Entry point |
| `code/data/cifar-10-batches-py/` | CIFAR-10 dataset (pickled batches) |
| `CS_474_HW6.pdf` | Written analysis of batch/lr ablation results |

## Dependencies

- Python 3
- `torch`, `torchvision`
- `tqdm`
