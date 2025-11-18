import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the rounds and feature names
rounds = ["R1", "R2", "R3", "R4", "R5", "R6"]
feature_names = [
    "SeedDiff", "EloDiff", "fgm_diff", "fg_pct_diff", "to_diff", "reb_diff",
    "3p_pct_diff", "ft_pct_diff", "ast_diff", "pf_diff", "stl_diff",
    "avg_pts_scored_diff", "avg_pts_allowed_diff", "avg_point_margin_diff"
]

# Load models and extract importances
importance_df = pd.DataFrame(index=feature_names)

for rnd in rounds:
    model_path = f"RbyRModels/{rnd}_model.pkl"
    try:
        model = joblib.load(model_path)
        importance_df[rnd] = model.feature_importances_
        print(f"Loaded model: {model_path}")
    except FileNotFoundError:
        print(f"Model file not found: {model_path}")
        importance_df[rnd] = [0] * len(feature_names)  

importance_df["Total"] = importance_df.sum(axis=1)
importance_df = importance_df.sort_values("Total", ascending=False).drop(columns="Total")


plt.figure(figsize=(12, 8))
ax = sns.heatmap(
    importance_df,
    annot=True,
    annot_kws={"fontsize": 10, "fontweight": "bold"},
    cmap="YlGnBu",
    linewidths=0.5,
    fmt=".2f"
)
plt.title("Feature Importance by Tournament Round", fontsize=18, fontweight='bold')
plt.xlabel("Round", fontsize=14, fontweight='bold')
plt.ylabel("Feature", fontsize=14, fontweight='bold')

# Bold and increase tick labels
plt.xticks(fontsize=12, fontweight='bold', rotation=0)
plt.yticks(fontsize=12, fontweight='bold', rotation=0)

colorbar = ax.collections[0].colorbar
colorbar.ax.yaxis.label.set_fontsize(12)
colorbar.ax.yaxis.label.set_fontweight('bold')
for label in colorbar.ax.get_yticklabels():
    label.set_fontsize(10)
    label.set_fontweight('bold')

plt.tight_layout()
plt.show()
