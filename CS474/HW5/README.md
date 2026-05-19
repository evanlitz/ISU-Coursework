# CS474 HW5: PCA, Hierarchical Clustering & CNN Calculations

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

Written/analytical assignment (submitted as LaTeX) covering three topics: Principal Component Analysis, hierarchical agglomerative clustering, and convolutional neural network parameter arithmetic.

## Parts

### Part 1 – Principal Component Analysis
Manual PCA computation on a set of 3D points: centering the data, computing the covariance matrix, finding eigenvectors/eigenvalues, and projecting onto the principal components.

### Part 2 – Hierarchical Clustering
Agglomerative clustering using two linkage criteria applied to a toy distance matrix:
- **Single linkage** (min distance between clusters)
- **Complete linkage** (max distance between clusters)

Results are visualized as dendrograms (`single_link_dendrogram.png`, `complete_link_dendrogram.png`).

### Part 3 – CNN Parameter Calculations
Given a CNN architecture with specified kernel sizes, strides, and padding:
- Computes output spatial dimensions at each layer
- Counts total trainable parameters (weights + biases)
- Estimates multiply-add operations per forward pass

## Files

| File | Description |
|------|-------------|
| `main.tex` | Full LaTeX source with derivations and solutions |
| `single_link_dendrogram.png` | Single-linkage clustering result |
| `complete_link_dendrogram.png` | Complete-linkage clustering result |
