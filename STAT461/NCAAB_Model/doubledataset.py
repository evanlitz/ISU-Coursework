import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Regular season detailed results (for stats features)
regular_season_results = pd.read_csv("mmdata/MRegularSeasonDetailedResults.csv")

# Tournament results (to build training labels)
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")

# Seeds (for seed features)
seeds = pd.read_csv("mmdata/MNCAATourneySeeds.csv")

# Massey rankings (for team strength)
massey = pd.read_csv("mmdata/MMasseyOrdinals.csv")

# Team metadata if needed
teams = pd.read_csv("mmdata/MTeams.csv")

season = 2003
regular_season_results = regular_season_results.loc[regular_season_results["Season"] >= season]
tourney_results = tourney_results.loc[tourney_results["Season"] >= season]
seeds = seeds.loc[seeds["Season"] >= season]

def double_dataset(df):
    df = df[["Season", "DayNum", "LTeamID", "LScore", "WTeamID", "WScore", "NumOT",
             "LFGM", "LFGA", "LFGM3", "LFGA3", "LFTM", "LFTA", "LOR", "LDR", "LAst", "LTO", "LStl", "LBlk", "LPF",
             "WFGM", "WFGA", "WFGM3", "WFGA3", "WFTM", "WFTA", "WOR", "WDR", "WAst", "WTO", "WStl", "WBlk", "WPF"]].copy()

    # Normalize stats by game length
    adj = (40 + 5 * df["NumOT"]) / 40
    # Only adjust actual stats — not IDs, scores, NumOT
    stat_cols = ["LFGM", "LFGA", "LFGM3", "LFGA3", "LFTM", "LFTA", "LOR", "LDR", "LAst", "LTO", "LStl", "LBlk", "LPF",
             "WFGM", "WFGA", "WFGM3", "WFGA3", "WFTM", "WFTA", "WOR", "WDR", "WAst", "WTO", "WStl", "WBlk", "WPF"]

    df[stat_cols] = df[stat_cols].div(adj, axis=0)

    # Create mirrored version
    dfswap = df.copy()

    # Rename: original winner = T1, loser = T2
    df.columns = [col.replace("W", "T1_").replace("L", "T2_") for col in df.columns]
    dfswap.columns = [col.replace("L", "T1_").replace("W", "T2_") for col in dfswap.columns]

    combined = pd.concat([df, dfswap], ignore_index=True)
    combined["PointDiff"] = combined["T1_Score"] - combined["T2_Score"]
    combined["Label"] = (combined["PointDiff"] > 0).astype(int)
    return combined

# Create new datasets
doubled_regular = double_dataset(regular_season_results)
doubled_tourney = double_dataset(tourney_results)

# Save to CSV
doubled_regular.to_csv("mmdata/MNCAADoubledRegularSeasonDetailedResults.csv", index=False)
doubled_tourney.to_csv("mmdata/MNCAADoubledTourneyResults.csv", index=False)

def validate_doubled_dataset(file_path):
    df = pd.read_csv(file_path)
    n = len(df)

    # Check even length
    if n % 2 != 0:
        print(f"[ERROR] File has odd number of rows: {n}")
        return False

    mid = n // 2
    valid = True

    for i in range(mid):
        row1 = df.iloc[i]
        row2 = df.iloc[i + mid]

        # Check if teams are mirrored
        if not (
            row1["T1_TeamID"] == row2["T2_TeamID"] and
            row1["T2_TeamID"] == row2["T1_TeamID"]
        ):
            print(f"[ERROR] Team IDs not mirrored at row {i} and {i + mid}")
            valid = False
            continue

        # Label should be flipped
        if row1["Label"] == row2["Label"]:
            print(f"[ERROR] Labels not flipped at row {i} and {i + mid}")
            valid = False

        # Check stat mirroring
        stat_cols = [col for col in df.columns if col.startswith("T1_")]
        for col in stat_cols:
            t1_col = col
            t2_col = col.replace("T1_", "T2_")
            if not np.isclose(row1[t1_col], row2[t2_col], atol=1e-3):
                print(f"[ERROR] Stat mismatch: {t1_col} <-> {t2_col} at rows {i} and {i + mid}")
                valid = False
                break

        # Optional: verify PointDiff and scores flip
        if not np.isclose(row1["PointDiff"], -row2["PointDiff"], atol=1e-3):
            print(f"[ERROR] PointDiff not flipped at rows {i} and {i + mid}")
            valid = False

    if valid:
        print(f"[SUCCESS] {file_path} passed all checks.")
    return valid

# Run checks
validate_doubled_dataset("mmdata/MNCAADoubledRegularSeasonDetailedResults.csv")
validate_doubled_dataset("mmdata/MNCAADoubledTourneyResults.csv")

sample = doubled_regular[doubled_regular["Season"] == 2025].sample(1, random_state=42)
t1 = sample["T1_TeamID"].values[0]
t2 = sample["T2_TeamID"].values[0]

match1 = (doubled_regular["T1_TeamID"] == t1) & (doubled_regular["T2_TeamID"] == t2)
match2 = (doubled_regular["T1_TeamID"] == t2) & (doubled_regular["T2_TeamID"] == t1)

subset = doubled_regular.loc[(match1 | match2) & (doubled_regular["Season"] == 2025)]

