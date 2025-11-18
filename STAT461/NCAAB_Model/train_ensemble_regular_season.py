import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from calculate_elos import calculate_elo_ratings
from team_season_stats import compute_stat_differences
import os

# === Load data ===
print("📦 Loading regular season doubled data...")
doubled_reg_season = pd.read_csv("mmdata/MNCAADoubledRegularSeasonDetailedResults.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")

# === Build training features ===
feature_rows = []
labels = []

for _, row in doubled_reg_season.iterrows():
    season = row["Season"]
    t1 = row["T1_TeamID"]
    t2 = row["T2_TeamID"]
    label = row["Label"]

    # Elo difference
    t1_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]
    t2_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]
    if t1_elo_row.empty or t2_elo_row.empty:
        continue
    elo_diff = t1_elo_row.iloc[0]["Elo"] - t2_elo_row.iloc[0]["Elo"]

    # Stat differences
    stat_diff = compute_stat_differences(t1, t2, season, teamStats)
    if stat_diff is None:
        continue

    feature_row = {
        "SeedDiff": 0,  # no seed info in regular season
        "EloDiff": elo_diff,
        **stat_diff
    }

    feature_rows.append(feature_row)
    labels.append(label)

X = pd.DataFrame(feature_rows)
y = pd.Series(labels)
print(f"✅ Finished feature extraction: {len(X)} samples")

# === Train ensemble models ===
os.makedirs("models", exist_ok=True)
n_models = 3
for i in range(n_models):
    print(f"\n🧠 Training model {i+1}/{n_models}...")

    model = xgb.XGBClassifier(
        n_estimators=np.random.randint(150, 300),
        max_depth=np.random.randint(4, 10),
        learning_rate=np.random.uniform(0.02, 0.15),
        subsample=np.random.uniform(0.7, 1.0),
        colsample_bytree=np.random.uniform(0.6, 1.0),
        min_child_weight=np.random.randint(1, 10),
        eval_metric="logloss",
        use_label_encoder=False,
        verbosity=0,
        random_state=42 + i
    )

    model.fit(X, y)
    model_path = f"models/ensemble_model_{i+1}.pkl"
    joblib.dump(model, model_path)
    print(f"✅ Saved to {model_path}")

print("\n✅ All ensemble models trained and saved.")
