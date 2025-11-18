import pandas as pd
import joblib
import json
from collections import Counter
from predict_bracket import validate_bracket
from team_season_stats import compute_stat_differences

# Load models
models = [joblib.load(f"RFtop_model_{i}.pkl") for i in range(1, 6)]

# Load data
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")
seeds_df = pd.read_csv("mmdata/RbyRMNCAATourneySeeds.csv")
slots_df = pd.read_csv("mmdata/MNCAATourneySlots.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")

# Ensemble years
YEARS = [y for y in range(2016, 2025) if y != 2020]

# Helper: simulate one full bracket for a single model
def model_bracket_predict(model, season):
    season_seeds = seeds_df[seeds_df["Season"] == season]
    season_slots = slots_df[slots_df["Season"] == season]
    seed_to_team = dict(zip(season_seeds["Seed"], season_seeds["TeamID"]))
    slot_to_team = {}

    play_in_slots_by_year = {
        2025: ["W16", "X11", "Y11", "Y16"],
        2024: ["X16", "Y10", "Y16", "Z10"],
        2023: ["W16", "X16", "Y11", "Z11"]
    }
    play_ins = season_slots[season_slots["Slot"].isin(play_in_slots_by_year.get(season, []))]
    main_slots = season_slots[~season_slots["Slot"].isin(play_in_slots_by_year.get(season, []))]

    def predict_winner(t1, t2):
        t1_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]["Elo"]
        t2_elo = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]["Elo"]
        if t1_elo.empty or t2_elo.empty:
            return t1
        elo_diff = t1_elo.values[0] - t2_elo.values[0]
        stat_diff = compute_stat_differences(t1, t2, season, teamStats)
        if stat_diff is None:
            return t1
        features = {"SeedDiff": 0, "EloDiff": elo_diff, **stat_diff}
        X = pd.DataFrame([features])
        pred = model.predict(X)[0]
        return t1 if pred == 1 else t2

    def process_match(slot, strong, weak):
        t1 = seed_to_team.get(strong) or slot_to_team.get(strong)
        t2 = seed_to_team.get(weak) or slot_to_team.get(weak)
        if not t1 or not t2:
            return
        winner = predict_winner(t1, t2)
        slot_to_team[slot] = winner

    for _, row in play_ins.iterrows():
        process_match(row["Slot"], row["StrongSeed"], row["WeakSeed"])
    for seed in play_in_slots_by_year.get(season, []):
        if seed in slot_to_team:
            seed_to_team[seed] = slot_to_team[seed]
    for _, row in main_slots.iterrows():
        process_match(row["Slot"], row["StrongSeed"], row["WeakSeed"])

    return slot_to_team

# Ensemble simulation using majority vote per slot
def simulate_ensemble_bracket(season):
    model_brackets = [model_bracket_predict(m, season) for m in models]
    all_slots = slots_df[slots_df["Season"] == season]["Slot"].tolist()
    slot_to_team = {}

    for slot in all_slots:
        votes = [bracket.get(slot) for bracket in model_brackets if slot in bracket]
        if votes:
            winner = Counter(votes).most_common(1)[0][0]
            slot_to_team[slot] = winner

    return slot_to_team

# Run ensemble evaluation
total_score = 0
for year in YEARS:
    bracket = simulate_ensemble_bracket(year)
    score = validate_bracket(bracket, tourney_results, year, seeds_df, slots_df)
    print(f"✅ {year} Score: {score}")
    total_score += score

avg_score = total_score / len(YEARS)
print(f"\n🎯 Ensemble Avg Score (2016–2024): {avg_score:.2f}")

# Predict 2025 and save bracket
bracket_2025 = simulate_ensemble_bracket(2025)
with open("ensemble_bracket_2025.json", "w") as f:
    json.dump(bracket_2025, f)
print("🧠 2025 Ensemble Bracket saved to ensemble_bracket_2025.json")
