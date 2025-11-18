import joblib
import pandas as pd
import matplotlib.pyplot as plt
from predict_bracket import simulate_bracket, validate_bracket
from visualize_bracket import visualize_bracket

# Load model
# model = joblib.load("best_rfbracket_model.pkl")
model = joblib.load("best_bracket_model.pkl")


# Assuming you have the same features you trained on
feature_names = [
    "SeedDiff",
    "EloDiff",
    "fgm_diff",
    "fg_pct_diff",
    "to_diff",
    "reb_diff",
    "3p_pct_diff",
    "ft_pct_diff",
    "ast_diff",
    "pf_diff",
    "stl_diff",
    "avg_pts_scored_diff",
    "avg_pts_allowed_diff",
    "avg_point_margin_diff",
]

# Get importances
importances = model.feature_importances_

# Pair feature names and importances
feature_importance_pairs = list(zip(feature_names, importances))

# Sort by most important
sorted_importances = sorted(feature_importance_pairs, key=lambda x: x[1], reverse=True)

# Display nicely
for feature, importance in sorted_importances:
    print(f"{feature}: {importance:.4f}")

tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")
seeds = pd.read_csv("mmdata/RbyRMNCAATourneySeeds.csv")
tourney_slots = pd.read_csv("mmdata/MNCAATourneySlots.csv")
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")

# Now simulate and validate each year
all_scores = {}

for year in range(2016, 2025):
    if year == 2020:
        continue  # skip canceled year

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

    all_scores[year] = score

# 📈 Plot scores by year
years = list(all_scores.keys())
scores = list(all_scores.values())

plt.figure(figsize=(12, 6))
plt.plot(years, scores, marker='o')
plt.title("Bracket Validation Scores by Year", fontweight='bold', fontsize=14)
plt.xlabel("Year", fontweight='bold', fontsize=12)
plt.ylabel("Validation Score", fontweight='bold', fontsize=12)
plt.grid(True)
plt.show()

# 🎯 Also print average
avg_score = sum(scores) / len(scores)
print(f"\n🎯 Average Validation Score: {avg_score:.2f}")


year_to_visualize = 2025
print(f"\n🧠 Visualizing bracket for {year_to_visualize}...")

predicted_bracket = simulate_bracket(
    season=year_to_visualize,
    model=model,
    teamStats=teamStats,
    elos=elos,
    seeds_df=seeds,
    slots_df=tourney_slots
)

teams = pd.read_csv("mmdata/MTeams.csv")  # Team names lookup
visualize_bracket(predicted_bracket, tourney_results, year_to_visualize, seeds, tourney_slots, teams)
