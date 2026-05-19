import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, classification_report
)

# ── 1. Load data ───────────────────────────────────────────────────────────────
df = pd.read_csv("data/sleep_study_1000.csv")
print(f"Dataset shape: {df.shape}\n")

# ── 2. Feature engineering ─────────────────────────────────────────────────────
df["BedtimeHour"] = pd.to_datetime(df["Bedtime"]).dt.hour
df = df.drop(columns=["ID", "Bedtime", "WakeupTime"])

# Encode categorical columns
df["Gender"]        = LabelEncoder().fit_transform(df["Gender"])
df["SmokingStatus"] = LabelEncoder().fit_transform(df["SmokingStatus"])

# ── 3. Binarize target (per proposal: >= 0.85 = Good, < 0.85 = Poor) ──────────
threshold = 0.85
df["SleepEfficiencyClass"] = (df["SleepEfficiency"] >= threshold).astype(int)
print(f"Class distribution (threshold={threshold}):")
print(df["SleepEfficiencyClass"].value_counts().rename({0: "Poor (<0.85)", 1: "Good (>=0.85)"}))
print()

X = df.drop(columns=["SleepEfficiency", "SleepEfficiencyClass"])
y = df["SleepEfficiencyClass"]

# ── 4. Data split: 70% train / 15% validation / 15% test (per proposal) ───────
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)
print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}\n")

# ── 5. Preprocessing (fit on train only) ──────────────────────────────────────
imputer = SimpleImputer(strategy="median")
X_train = imputer.fit_transform(X_train)
X_val   = imputer.transform(X_val)
X_test  = imputer.transform(X_test)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val   = scaler.transform(X_val)
X_test  = scaler.transform(X_test)

# ── 6. Hyperparameter tuning on train+val ─────────────────────────────────────
# class_weight='balanced' compensates for the 787/213 class imbalance
param_grid = {
    "C":      [0.1, 1, 10, 100],
    "gamma":  ["scale", "auto", 0.01, 0.1],
    "kernel": ["rbf", "linear", "poly"]
}
grid = GridSearchCV(
    SVC(class_weight="balanced", random_state=42),
    param_grid,
    cv=5,
    scoring="f1_macro",
    n_jobs=-1
)
grid.fit(X_train, y_train)
print(f"Best hyperparameters: {grid.best_params_}\n")

# Validate on val set before final evaluation
y_val_pred = grid.best_estimator_.predict(X_val)
print(f"Validation Accuracy: {accuracy_score(y_val, y_val_pred):.4f}\n")

# ── 7. Final evaluation on held-out test set ──────────────────────────────────
y_pred = grid.best_estimator_.predict(X_test)

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall    = recall_score(y_test, y_pred)
f1        = f1_score(y_test, y_pred)

print("=" * 45)
print(f"  Accuracy  : {accuracy:.4f}")
print(f"  Precision : {precision:.4f}")
print(f"  Recall    : {recall:.4f}")
print(f"  F1-score  : {f1:.4f}")
print("=" * 45)
print("\nFull Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=["Poor (<0.85)", "Good (>=0.85)"]
))
