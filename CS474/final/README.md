# CS474 Final Project: Sleep Efficiency Classification (NHANES)

**Course**: CS474 – Introduction to Machine Learning, Iowa State University  
**Team**: Evan Litzer, Eric Huang, Madison Vosburg

## Overview

Extension of the midterm project using the real-world NHANES actigraphy dataset. Switched from a synthetic lifestyle survey to wrist-accelerometer measurements, added Random Forest and a Neural Network, and performed SHAP-based feature importance analysis.

## Task

Binary classification: **good sleep** (efficiency ≥ 0.85) vs. **poor sleep**, using accelerometry-derived features from wrist-worn devices.

## Dataset

**NHANES Actigraphy Sleep Data** — ~85,000 rows, 42 columns. Features are derived from wrist accelerometer measurements and include circadian rhythm indicators, sleep-period acceleration, device-wear percentage, and sleep/wake timing.

Key features used after preprocessing:
- `L5/L10VALUE` — acceleration during least active 5/10-hour window
- `M5/M10VALUE` — acceleration during most active 5/10-hour window
- `ACC_spt_sleep_mg` — average wrist acceleration during sleep window
- `sleeponset`, `wakeup` — sleep start/end times
- `dur_spt_min` — sleep window duration in minutes
- `nonwear_perc_day` — percentage of day device was not worn

Preprocessing: drop redundant columns, convert timestamps to float, 70/15/15 split.

## Models & Results

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|----|
| Linear Perceptron | 0.516 | 0.667 | 0.499 | 0.571 |
| Logistic Regression | 0.566 | 0.723 | 0.557 | 0.629 |
| Random Forest | 0.595 | 0.742 | 0.593 | 0.659 |
| **Neural Network** | **0.622** | **0.745** | **0.652** | **0.695** |

The neural network achieves the best performance across all metrics. Linear models approach random-guessing, confirming the relationships are nonlinear.

## Model Details

**Random Forest**: 200 trees, max depth 10, min 5 samples/leaf, balanced class weights. Top feature: sleep period duration (19.7% importance).

**Neural Network** (PyTorch MLP): architecture `12 → 64 → 32 → 1`, ReLU activations, BatchNorm + Dropout(0.3), Adam optimizer with ReduceLROnPlateau, BCEWithLogitsLoss with pos_weight for class imbalance, 100 epochs, batch size 256. SHAP analysis identifies `L5VALUE` (0.771) and `ACC_spt_sleep_mg` (0.682) as the strongest predictors.

## Files

| File | Description |
|------|-------------|
| `neural_network.py` | PyTorch MLP with SHAP analysis |
| `random_forest.py` | scikit-learn Random Forest with feature importance |
| `NHANES Preliminary Day Level Output.csv` | Full dataset (~85k rows) |
| `nn_results.png` | Neural network confusion matrix and training curves |
| `nn_shap.png` | SHAP feature importance plot |
| `rf_results.png` | Random Forest confusion matrix and feature importance |
| `CS474_Final_Report.pdf` | Full written report |
| `CS 474 Final Presentation.pptx.pdf` | Presentation slides |

## Dependencies

- Python 3
- `torch`, `numpy`, `pandas`
- `scikit-learn`
- `shap`
- `matplotlib`
