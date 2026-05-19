# CS474 Midterm Project: Sleep Efficiency Classification

**Course**: CS474 – Introduction to Machine Learning, Iowa State University  
**Team**: Evan Litzer, Eric Huang, Madison Vosburg

## Overview

Binary classification of sleep efficiency using three linear models trained on a synthetic sleep-and-lifestyle dataset. The midterm report serves as a baseline and analysis checkpoint before the final project.

## Task

Classify whether a person has **good sleep** (efficiency ≥ 0.85) or **poor sleep** (< 0.85) using lifestyle and behavioral features.

## Dataset

**Sleep and Lifestyle Health** (Kaggle) — 1,000 synthetic samples, 15 columns. Features include bedtime, wake time, sleep duration, exercise frequency, caffeine/alcohol consumption, smoking status, awakenings, and sleep stage percentages.

Preprocessing:
- Binary target created from `SleepEfficiency` threshold 0.85
- Categorical encoding (Gender, SmokingStatus)
- Bedtime converted to seconds since midnight
- 70/15/15 train/val/test split; StandardScaler normalization

## Models & Results

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|----|
| Linear Perceptron | 0.496 | 0.230 | 0.560 | 0.326 |
| Logistic Regression | 0.518 | 0.184 | 0.391 | 0.250 |
| SVM (linear kernel) | 0.553 | 0.193 | 0.345 | 0.247 |

All models perform near random-guessing level (~50%). Feature correlation analysis revealed that no single feature has a Pearson correlation above 0.053 with the target, indicating the synthetic dataset lacks meaningful signal for linear classifiers.

## Files

| File | Description |
|------|-------------|
| `svm_sleep.py` | SVM with GridSearchCV hyperparameter tuning (C, gamma, kernel) |
| `feature_correlation.py` | Pearson correlation analysis of all features vs. SleepEfficiency |
| `data/sleep_study_1000.csv` | Dataset (1,000 samples) |
| `Midterm_Report.pdf` | Full written report with results and analysis |
| `CS 474 Project Proposal.pdf` | Original project proposal |

## Dependencies

- Python 3
- `pandas`, `scikit-learn`, `numpy`
