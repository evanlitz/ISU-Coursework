import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from calculate_elos import calculate_elo_ratings
from team_season_stats import compute_stat_differences
from predict_bracket import simulate_bracket, validate_bracket

# Load data
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")
training_data = pd.read_csv("mmdata/ProcessedTourneyResults_withSeedDiff.csv")
tourney_slots = pd.read_csv("mmdata/MNCAATourneySlots.csv")
seeds = pd.read_csv("mmdata/MNCAATourneySeeds.csv")
teams = pd.read_csv("mmdata/MTeams.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")

TRAIN_YEARS = list(range(2003, 2016))
TARGET_YEARS = [y for y in range(2016, 2025) if y != 2020]
N_TRIALS = 100

# Build training set (same for all years)
X_train, y_train = [], []
for _, row in training_data.iterrows():
    if row["Season"] not in TRAIN_YEARS:
        continue
    t1, t2, season = row["T1_TeamID"], row["T2_TeamID"], row["Season"]
    label = row["Label"]

    t1_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]
    t2_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]
    if t1_elo.empty or t2_elo.empty:
        continue

    elo_diff = t1_elo.iloc[0]["Elo"] - t2_elo.iloc[0]["Elo"]
    stat_diff = compute_stat_differences(t1, t2, season, teamStats)
    if stat_diff is None:
        continue

    features = {"SeedDiff": row["Seed_diff"], "EloDiff": elo_diff, **stat_diff}
    X_train.append(features)
    y_train.append(label)

X_train = pd.DataFrame(X_train)
y_train = pd.Series(y_train)

print(f"✅ Prepared training set with {len(X_train)} games")

# Optimize per year
for year in TARGET_YEARS:
    print(f"\n🎯 Optimizing model for {year} bracket only...")
    best_score = -float("inf")
    best_model = None
    best_params = None

    for trial in range(N_TRIALS):
        params = {
            "n_estimators": np.random.randint(300, 800),
            "max_depth": np.random.randint(10, 40),
            "min_samples_split": np.random.randint(5, 20),
            "min_samples_leaf": np.random.randint(2, 10),
            "max_features": np.random.choice(["sqrt", "log2"]),
            "bootstrap": np.random.choice([True, False]),
            "criterion": np.random.choice(["gini", "entropy"]),
            "random_state": trial,
            "class_weight": "balanced"
        }

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        pred = simulate_bracket(
            season=year,
            model=model,
            teamStats=teamStats,
            elos=elos,
            seeds_df=seeds,
            slots_df=tourney_slots
        )
        score = validate_bracket(
            predicted_bracket=pred,
            actual_results_df=tourney_results,
            season=year,
            seeds_df=seeds,
            slots_df=tourney_slots
        )

        if score > best_score:
            best_score = score
            best_model = model
            best_params = params

        print(f"Trial {trial+1}: {score:.2f}", end="\r")

    print(f"🏆 Best Score for {year}: {best_score} with params: {best_params}")
    joblib.dump(best_model, f"best_model_{year}.pkl")

    # Save feature importances
    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": best_model.feature_importances_
    }).sort_values("importance", ascending=False)
    importance_df.to_csv(f"feature_importances_{year}.csv", index=False)
