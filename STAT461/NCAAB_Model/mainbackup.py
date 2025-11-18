import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from calculate_elos import calculate_elo_ratings
from team_season_stats import compute_stat_differences
from team_season_stats import get_team_stats
from team_season_stats import generate_team_season_stats
from predict_bracket import simulate_bracket, validate_bracket



# Regular season detailed results (for stats features)
regular_season_results = pd.read_csv("mmdata/MRegularSeasonDetailedResults.csv")

# Tournament results (to build training labels)
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")

training_tourney_results = pd.read_csv("mmdata/ProcessedTourneyResults_withSeedDiff.csv")

# Regular season detailed results (for stats features)
doubled_reg_season = pd.read_csv("mmdata/MNCAADoubledRegularSeasonDetailedResults.csv")

# Tournament results (to build training labels)
doubled_tourney = pd.read_csv("mmdata/MNCAADoubledTourneyResults.csv")

tourney_slots = pd.read_csv("mmdata/MNCAATourneySlots.csv")

# Seeds (for seed features)
seeds = pd.read_csv("mmdata/MNCAATourneySeeds.csv")

# Massey rankings (for team strength)
massey = pd.read_csv("mmdata/MMasseyOrdinals.csv")

ap_df = massey[massey["SystemName"] == "AP"].drop(columns=["SystemName"])

# Team metadata if needed
teams = pd.read_csv("mmdata/MTeams.csv")

elos = pd.read_csv("mmdata/TeamElos.csv")

teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")


season = 2003
regular_season_results = regular_season_results.loc[regular_season_results["Season"] >= season]
tourney_results = tourney_results.loc[tourney_results["Season"] >= season]
seeds = seeds.loc[seeds["Season"] >= season]

print("Generating features dynamically...")

feature_rows = []
labels = []

for idx, row in training_tourney_results.iterrows():
    season = row["Season"]
    t1 = row["T1_TeamID"]
    t2 = row["T2_TeamID"]
    label = row["Label"]  # 1 if T1 won

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

    # Combine features
    feature_row = {
        "SeedDiff": row["Seed_diff"],
        "EloDiff": elo_diff,
        **stat_diff
    }

    feature_rows.append(feature_row)
    labels.append(label)

# Build DataFrame
X = pd.DataFrame(feature_rows)
y = pd.Series(labels)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    class_weight='balanced'  
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

all_scores = {}

# Optional: Check feature importances
importances = model.feature_importances_
for feat, imp in sorted(zip(X.columns, importances), key=lambda x: x[1], reverse=True):
    print(f"{feat}: {imp:.4f}")

for year in range(2003, 2025):
    if year == 2020:
        continue  # Skip canceled tournament

    print(f"\n==== Simulating {year} Tournament ====")
    predicted_bracket = simulate_bracket(
        season=year,
        model=model,
        teamStats=teamStats,
        elos=elos,
        seeds_df=seeds,
        slots_df=tourney_slots
    )

    final_four_slots = [s for s in predicted_bracket if s.startswith("R5")]
    championship_slot = "R6CH"

    print(f"\nPredicted Final Four for {year}:")
    for slot in final_four_slots:
        team_id = predicted_bracket.get(slot)
        team_name = teams.loc[teams["TeamID"] == team_id, "TeamName"].values[0]
        print(f"{slot}: {team_name}")

    if championship_slot in predicted_bracket:
        champ_id = predicted_bracket[championship_slot]
        champ_name = teams.loc[teams["TeamID"] == champ_id, "TeamName"].values[0]
        print(f"🏆 Predicted Champion for {year}: {champ_name}")
    else:
        print("⚠️ Could not determine champion (missing data or prediction failure).")

    score = validate_bracket(
        predicted_bracket,
        actual_results_df=tourney_results,
        season=year,
        seeds_df=seeds,
        slots_df=tourney_slots
    )

    all_scores[year] = score
    print(f"✅ Validation Score for {year}: {score}")

    # Optional: display predicted final four and champion
    final_four_slots = [s for s in predicted_bracket if s.startswith("R5")]
    championship_slot = "R6CH"

    print(f"\nPredicted Final Four for {year}:")
    for slot in final_four_slots:
        team_id = predicted_bracket.get(slot)
        team_name = teams.loc[teams["TeamID"] == team_id, "TeamName"].values[0]
        print(f"{slot}: {team_name}")

    if championship_slot in predicted_bracket:
        champ_id = predicted_bracket[championship_slot]
        champ_name = teams.loc[teams["TeamID"] == champ_id, "TeamName"].values[0]
        print(f"🏆 Predicted Champion for {year}: {champ_name}")
    else:
        print("⚠️ Could not determine champion.")


avg_score = np.mean(list(all_scores.values()))
print("\n🎯 Average Bracket Score:", avg_score)

# Optional: plot scores year-by-year
import matplotlib.pyplot as plt
plt.plot(list(all_scores.keys()), list(all_scores.values()), marker='o')
plt.title("Validation Scores by Year")
plt.xlabel("Year")
plt.ylabel("Score")
plt.grid(True)
plt.show()