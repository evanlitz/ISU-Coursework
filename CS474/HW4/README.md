# CS474 HW4: Support Vector Machines — Implementation

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

scikit-learn SVM (`SVC`) applied to the same digits 1 vs. 5 classification task as HW2, using symmetry and average intensity features from 16×16 grayscale images. Experiments study the effect of the cost parameter C and kernel type on accuracy and support vector count.

## Experiments

### Part A – Effect of C (linear kernel)

| C | Accuracy | Support Vectors |
|---|----------|----------------|
| 0.01 | 89.39% | 1080 |
| 0.1 | 96.23% | 414 |
| 1 | 95.99% | 162 |
| 2 | 95.99% | 129 |
| 3 | 96.23% | 117 |
| 5 | 96.23% | 104 |

Very small C (soft margin) allows too many misclassifications, leading to weak boundaries and many support vectors. Accuracy stabilizes near 96% for C ≥ 0.1.

### Part B – Effect of Kernel (C=1)

| Kernel | Accuracy | Support Vectors |
|--------|----------|----------------|
| Linear | 95.99% | 162 |
| Polynomial | 95.75% | 75 |
| RBF | 96.23% | 90 |

RBF achieves the best accuracy with fewer support vectors than linear, indicating the feature space is nearly but not perfectly linearly separable.

## Files

| File | Description |
|------|-------------|
| `solution.py` | `svm_with_diff_c()` and `svm_with_diff_kernel()` functions |
| `helper.py` | Data loading and feature extraction (symmetry, intensity) |
| `main.py` | Runs both experiments and prints results |
| `data/train.txt` | Training set |
| `data/test.txt` | Test set |
| `CS_474_HW_4_Report.pdf` | Written analysis of results |

## Dependencies

- Python 3
- `scikit-learn`
- `numpy`
