import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
    confusion_matrix, ConfusionMatrixDisplay, classification_report
)

# ── Data loading & cleaning ────────────────────────────────────────────────────
df = pd.read_csv("NHANES Preliminary Day Level Output.csv")
df = df[df["excluded"] == 0].copy()

FEATURES = [
    "L5VALUE",
    "M5VALUE",
    "L10VALUE",
    "M10VALUE",
    "L5TIME_num",
    "M5TIME_num",
    "dayofweek",
    "dur_day_min",
    "dur_spt_min",
    "nonwear_perc_day",
    "ACC_spt_sleep_mg",
]
TARGET = "sleep_efficiency"

df = df[FEATURES + [TARGET]].dropna()

# Derived feature: circadian amplitude ratio
df["circadian_ratio"] = df["M5VALUE"] / (df["L5VALUE"] + 1e-6)
FEATURES = FEATURES + ["circadian_ratio"]

X = df[FEATURES].values

# Binary target: 1 = good sleeper (efficiency >= 0.85), 0 = poor sleeper
y = (df[TARGET] >= 0.85).astype(int).values

print(f"Class distribution: good sleeper={y.mean():.1%}, poor sleeper={(1-y.mean()):.1%}")

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Model ─────────────────────────────────────────────────────────────────────
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=5,
    class_weight="balanced",  # compensates for 66/34 class split
    random_state=42,
    n_jobs=-1,
)
rf.fit(X_train, y_train)

# ── Evaluation ────────────────────────────────────────────────────────────────
y_pred      = rf.predict(X_test)
y_pred_prob = rf.predict_proba(X_test)[:, 1]

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall    = recall_score(y_test, y_pred)
f1        = f1_score(y_test, y_pred)
roc_auc   = roc_auc_score(y_test, y_pred_prob)

cv_acc = cross_val_score(rf, X_train, y_train, cv=5, scoring="accuracy")

print("\n=== Random Forest — Good Sleeper Classification (>= 0.85) ===")
print(f"  Accuracy  : {accuracy:.4f}")
print(f"  Precision : {precision:.4f}")
print(f"  Recall    : {recall:.4f}")
print(f"  F1 Score  : {f1:.4f}")
print(f"  ROC-AUC   : {roc_auc:.4f}")
print(f"  CV Acc    : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
print()
print(classification_report(y_test, y_pred, target_names=["Poor Sleeper", "Good Sleeper"]))

# ── Feature importances ───────────────────────────────────────────────────────
print("\n=== Feature Importances ===")
importances_series = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, imp in importances_series.items():
    print(f"  {feat:<25} {imp:.4f}")

# ── Plots ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Random Forest — Good Sleeper Classification (efficiency >= 0.85)", fontsize=13)

# 1. Confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Poor", "Good"])
disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title(f"Confusion Matrix  (Accuracy = {accuracy:.3f})")

# 2. Feature importance
importances = pd.Series(rf.feature_importances_, index=FEATURES).sort_values()
importances.plot(kind="barh", ax=axes[1], color="steelblue")
axes[1].set_xlabel("Importance")
axes[1].set_title("Feature Importances")

plt.tight_layout()
plt.savefig("rf_results.png", dpi=150)
print("Saved rf_results.png")
