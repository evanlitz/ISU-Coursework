import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from calculate_elos import calculate_elo_ratings
from team_season_stats import compute_stat_differences
from predict_bracket import simulate_bracket, validate_bracket
import joblib

# Load data
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")
training_tourney_results = pd.read_csv("mmdata/ProcessedTourneyResults_withSeedDiff.csv")
tourney_slots = pd.read_csv("mmdata/MNCAATourneySlots.csv")
seeds = pd.read_csv("mmdata/MNCAATourneySeeds.csv")
massey = pd.read_csv("mmdata/MMasseyOrdinals.csv")
ap_df = massey[massey["SystemName"] == "AP"].drop(columns=["SystemName"])
teams = pd.read_csv("mmdata/MTeams.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")

# Year split
TRAIN_YEARS = list(range(2003, 2016))
TEST_YEARS = [y for y in range(2016, 2025) if y != 2020]

# Build training dataset
print("📦 Building training set from 2003–2015 tournament games...")
feature_rows = []
labels = []

for _, row in training_tourney_results.iterrows():
    if row["Season"] not in TRAIN_YEARS:
        continue

    season = row["Season"]
    t1 = row["T1_TeamID"]
    t2 = row["T2_TeamID"]
    label = row["Label"]

    # Elo
    t1_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]
    t2_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]
    if t1_elo_row.empty or t2_elo_row.empty:
        continue
    elo_diff = t1_elo_row.iloc[0]["Elo"] - t2_elo_row.iloc[0]["Elo"]

    # Stat differences
    stat_diff = compute_stat_differences(t1, t2, season, teamStats)
    if stat_diff is None:
        continue

    # Feature row
    feature_row = {
        "SeedDiff": row["Seed_diff"],
        "EloDiff": elo_diff,
        **stat_diff
    }

    feature_rows.append(feature_row)
    labels.append(label)

X = pd.DataFrame(feature_rows)
y = pd.Series(labels)

print(f"✅ Training rows: {len(X)}")

# Track best model
best_score = -float("inf")
best_model = None
best_trial = -1

# Try 50 models
for trial in range(50):
    print(f"\n=== Trial {trial+1} ===")

    # model = RandomForestClassifier(
    #     n_estimators=np.random.randint(200, 500),
    #     max_depth=np.random.randint(6, 20),
    #     min_samples_split=np.random.randint(5, 20),
    #     min_samples_leaf=np.random.randint(2, 10),
    #     max_features='sqrt',
    #     random_state=trial,
    #     class_weight='balanced'
    # )

    params = {
    "n_estimators": np.random.randint(300, 800),
    "max_depth": np.random.randint(12, 40),
    "min_samples_split": np.random.randint(5, 20),
    "min_samples_leaf": np.random.randint(2, 10),
    "max_features": np.random.choice(["sqrt", "log2"]),
    "bootstrap": np.random.choice([True, False]),
    "criterion": np.random.choice(["gini", "entropy"]),
    "random_state": trial,
    "class_weight": "balanced"
    }

    model = RandomForestClassifier(**params)   

    model.fit(X, y)

    trial_scores = []
    for year in TEST_YEARS:
        predicted_bracket = simulate_bracket(
            season=year,
            model=model,
            teamStats=teamStats,
            elos=elos,
            seeds_df=seeds,
            slots_df=tourney_slots
        )
        score = validate_bracket(
            predicted_bracket,
            actual_results_df=tourney_results,
            season=year,
            seeds_df=seeds,
            slots_df=tourney_slots
        )
        trial_scores.append(score)

    avg_score = np.mean(trial_scores)
    print(f"🎯 Trial Avg Bracket Score (2016–2024): {avg_score:.2f}")

    if avg_score > best_score:
        print("🔥 New Best Model Found!")
        best_score = avg_score
        best_model = model
        best_trial = trial + 1

# Final result
print(f"\n\n🏆 Best Model = Trial {best_trial} | Avg Score = {best_score:.2f}")
joblib.dump(best_model, "best_bracket_modelTAKETWO.pkl")
print("✅ Model saved to best_bracket_modelTAKETWO.pkl")
