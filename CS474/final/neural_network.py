import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import shap
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, ConfusionMatrixDisplay, classification_report
)

# ── Reproducibility ───────────────────────────────────────────────────────────
torch.manual_seed(42)
np.random.seed(42)

# ── Data loading & cleaning ───────────────────────────────────────────────────
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
df["circadian_ratio"] = df["M5VALUE"] / (df["L5VALUE"] + 1e-6)
FEATURES = FEATURES + ["circadian_ratio"]

X = df[FEATURES].values
y = (df[TARGET] >= 0.85).astype(int).values

print(f"Class distribution: good sleeper={y.mean():.1%}, poor sleeper={(1-y.mean()):.1%}")

# ── Train / val / test split ──────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
)

# ── Normalize features (critical for neural networks) ─────────────────────────
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val   = scaler.transform(X_val)
X_test  = scaler.transform(X_test)

# ── PyTorch tensors & DataLoaders ─────────────────────────────────────────────
def to_tensors(X, y):
    return TensorDataset(
        torch.tensor(X, dtype=torch.float32),
        torch.tensor(y, dtype=torch.float32).unsqueeze(1)
    )

train_loader = DataLoader(to_tensors(X_train, y_train), batch_size=256, shuffle=True)
val_loader   = DataLoader(to_tensors(X_val,   y_val),   batch_size=512)
test_loader  = DataLoader(to_tensors(X_test,  y_test),  batch_size=512)

# ── Model definition ──────────────────────────────────────────────────────────
# Feedforward MLP: input → 64 → 32 → 1
# Dropout for regularization, BatchNorm for stable training
class SleepMLP(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)

n_features = X_train.shape[1]
model = SleepMLP(n_features)

# Class imbalance: weight the positive class inversely to its frequency
pos_weight = torch.tensor([(1 - y_train.mean()) / y_train.mean()])
criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

# Use raw logits for loss, so rebuild without final Sigmoid for training
class SleepMLPLogits(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x)

model     = SleepMLPLogits(n_features)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

# ── Training loop ─────────────────────────────────────────────────────────────
EPOCHS = 100
train_losses, val_losses = [], []

best_val_loss = float("inf")
best_state    = None

for epoch in range(1, EPOCHS + 1):
    # Train
    model.train()
    epoch_loss = 0.0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        loss = criterion(model(X_batch), y_batch)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item() * len(X_batch)
    train_losses.append(epoch_loss / len(X_train))

    # Validate
    model.eval()
    with torch.no_grad():
        val_loss = sum(
            criterion(model(X_b), y_b).item() * len(X_b)
            for X_b, y_b in val_loader
        ) / len(X_val)
    val_losses.append(val_loss)
    scheduler.step(val_loss)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_state    = {k: v.clone() for k, v in model.state_dict().items()}

    if epoch % 10 == 0:
        print(f"  Epoch {epoch:3d} | train loss {train_losses[-1]:.4f} | val loss {val_losses[-1]:.4f}")

# Restore best weights
model.load_state_dict(best_state)

# ── Evaluation ────────────────────────────────────────────────────────────────
model.eval()
all_logits, all_labels = [], []
with torch.no_grad():
    for X_batch, y_batch in test_loader:
        all_logits.append(model(X_batch))
        all_labels.append(y_batch)

logits = torch.cat(all_logits).squeeze().numpy()
probs  = 1 / (1 + np.exp(-logits))   # sigmoid
preds  = (probs >= 0.5).astype(int)
labels = torch.cat(all_labels).squeeze().numpy().astype(int)

accuracy  = accuracy_score(labels, preds)
precision = precision_score(labels, preds)
recall    = recall_score(labels, preds)
f1        = f1_score(labels, preds)
roc_auc   = roc_auc_score(labels, probs)

print("\n=== Neural Network — Good Sleeper Classification (>= 0.85) ===")
print(f"  Accuracy  : {accuracy:.4f}")
print(f"  Precision : {precision:.4f}")
print(f"  Recall    : {recall:.4f}")
print(f"  F1 Score  : {f1:.4f}")
print(f"  ROC-AUC   : {roc_auc:.4f}")
print()
print(classification_report(labels, preds, target_names=["Poor Sleeper", "Good Sleeper"]))

# ── Model weights ─────────────────────────────────────────────────────────────
print("\n=== Model Weights ===")
for name, param in model.named_parameters():
    print(f"\n  {name}  {tuple(param.shape)}")
    print(param.data.numpy())

# ── SHAP feature importance ───────────────────────────────────────────────────
model.eval()
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor  = torch.tensor(X_test,  dtype=torch.float32)

background  = X_train_tensor[:100]
explainer   = shap.DeepExplainer(model, background)
shap_values = explainer.shap_values(X_test_tensor[:500])

print("\n=== SHAP Feature Importances (mean |SHAP|) ===")
sv = shap_values[0] if isinstance(shap_values, list) else shap_values
mean_shap = np.abs(sv).mean(axis=0).flatten()
shap_series = pd.Series(mean_shap, index=FEATURES).sort_values(ascending=False)
for feat, val in shap_series.items():
    print(f"  {feat:<25} {val:.4f}")

fig_shap, ax_shap = plt.subplots(figsize=(8, 5))
shap_series.sort_values().plot(kind="barh", ax=ax_shap, color="steelblue")
ax_shap.set_xlabel("Mean |SHAP value|")
ax_shap.set_title("Neural Network — Feature Importance (SHAP)")
fig_shap.tight_layout()
fig_shap.savefig("nn_shap.png", dpi=150)
print("Saved nn_shap.png")

# ── Plots ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Neural Network (MLP) — Good Sleeper Classification (efficiency >= 0.85)", fontsize=13)

# 1. Training / validation loss curve
ax = axes[0]
ax.plot(train_losses, label="Train loss")
ax.plot(val_losses,   label="Val loss")
ax.set_xlabel("Epoch")
ax.set_ylabel("BCE Loss")
ax.set_title("Training & Validation Loss")
ax.legend()

# 2. Confusion matrix
cm   = confusion_matrix(labels, preds)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Poor", "Good"])
disp.plot(ax=axes[1], colorbar=False, cmap="Blues")
axes[1].set_title(f"Confusion Matrix  (Accuracy = {accuracy:.3f})")

plt.tight_layout()
plt.savefig("nn_results.png", dpi=150)
print("Saved nn_results.png")
