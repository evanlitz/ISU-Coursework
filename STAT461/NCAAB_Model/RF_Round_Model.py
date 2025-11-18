import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from team_season_stats import compute_stat_differences

# Load data
processed = pd.read_csv("mmdata/ProcessedTourneyResults_withSeedDiff.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")
tourney_slots = pd.read_csv("mmdata/MNCAATourneySlots.csv")
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")
seeds = pd.read_csv("mmdata/RbyRMNCAATourneySeeds.csv")

# Create output directory
os.makedirs("RbyRModels", exist_ok=True)

# Build matchup-to-round map
slot_map = {}
seed_lookup = seeds.set_index(["Season", "Seed"])["TeamID"].to_dict()
winners = {}

for _, row in tourney_results.iterrows():
    season = row["Season"]
    w, l = row["WTeamID"], row["LTeamID"]
    winners[(season, frozenset([w, l]))] = w

team_slot = {}
for _, row in tourney_slots.iterrows():
    season, slot = row["Season"], row["Slot"]
    strong, weak = row["StrongSeed"], row["WeakSeed"]

    def resolve_team(s):
        if (season, s) in seed_lookup:
            return seed_lookup[(season, s)]
        return team_slot.get((season, s))

    t1 = resolve_team(strong)
    t2 = resolve_team(weak)

    if t1 and t2:
        key = (season, frozenset([t1, t2]))
        slot_map[key] = slot[:2]
        winner = winners.get((season, frozenset([t1, t2])))
        if winner:
            team_slot[(season, slot)] = winner
            if (season, slot) not in seed_lookup:
                seed_lookup[(season, slot)] = winner
        elif (season, slot) == (2021, "R1X7"):
            winner = 1332  # Oregon's TeamID
            team_slot[(season, slot)] = winner
            seed_lookup[(season, slot)] = winner

# Group training data
rounds = ["R1", "R2", "R3", "R4", "R5", "R6"]
features_by_round = {rnd: [] for rnd in rounds}
labels_by_round = {rnd: [] for rnd in rounds}

for _, row in processed.iterrows():
    season = row["Season"]
    if season < 2003 or season > 2024 or season == 2020:
        continue

    t1, t2 = row["T1_TeamID"], row["T2_TeamID"]
    label = row["Label"]
    seed_diff = row["Seed_diff"]
    key = (season, frozenset([t1, t2]))
    rnd = slot_map.get(key)

    if rnd not in rounds:
        print(f"❌ Skipped (No round match): {season} | T1 {t1} vs T2 {t2}")
        continue

    t1_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]
    t2_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]
    if t1_elo.empty or t2_elo.empty:
        print(f"❌ Skipped (Missing Elo): {season} | T1 {t1} vs T2 {t2} | Round {rnd}")
        continue

    stat_diff = compute_stat_differences(t1, t2, season, teamStats)
    if stat_diff is None:
        print(f"❌ Skipped (Missing stats): {season} | T1 {t1} vs T2 {t2} | Round {rnd}")
        continue

    feature_row = {
        "SeedDiff": seed_diff,
        "EloDiff": t1_elo.iloc[0]["Elo"] - t2_elo.iloc[0]["Elo"],
        **stat_diff
    }

    features_by_round[rnd].append(feature_row)
    labels_by_round[rnd].append(label)

# Train and save models
for rnd in rounds:
    X = pd.DataFrame(features_by_round[rnd])
    y = pd.Series(labels_by_round[rnd])

    print(f"\n🧪 Training on {len(X)} games for {rnd}")
    if X.empty:
        print(f"⚠️ Not enough data for {rnd}")
        continue

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features='sqrt',
        random_state=42
    )
    model.fit(X, y)

    print(f"\n🎯 Feature importances for {rnd}:")
    importances = model.feature_importances_
    for name, importance in sorted(zip(X.columns, importances), key=lambda x: -x[1]):
        print(f"{name:25s}: {importance:.4f}")

    model_path = f"RbyRModels/{rnd}_model.pkl"
    joblib.dump(model, model_path)
    print(f"✅ Saved model to {model_path}")
