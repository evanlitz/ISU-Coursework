# CS474 HW2: Perceptron Implementation

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

From-scratch NumPy implementation of the Perceptron learning algorithm for binary classification of handwritten digits (1 vs. 5) using two hand-crafted features extracted from 16×16 grayscale images.

## Task

Binary classification of MNIST-derived digit images (class +1 = digit 1, class -1 = digit 5) using only two features:
- **Symmetry**: Measures horizontal symmetry of the pixel grid
- **Average Intensity**: Mean pixel value across the 16×16 image

## Files

| File | Description |
|------|-------------|
| `code/solution.py` | Perceptron class with `fit`, `predict`, and `score` methods |
| `code/helper.py` | Data loading from text files; symmetry and intensity feature extraction |
| `code/main.py` | Entry point: loads data, trains perceptron, evaluates and plots results |
| `code/Readme.txt` | Original assignment notes |
| `code/result.png` | Decision boundary plot in 2D feature space |
| `code/train_features.png` | Feature scatter plot of training data |
| `data/train.txt` | Training set (16×16 pixel values + label per row) |
| `data/test.txt` | Test set |

## Algorithm

The perceptron iterates over training examples and updates weights on misclassification:

```
w ← w + yₙxₙ  if  sign(wᵀxₙ) ≠ yₙ
```

Training terminates when the data is correctly separated or a maximum number of iterations is reached.

## Dependencies

- Python 3
- `numpy`
- `matplotlib`
