import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from calculate_elos import calculate_elo_ratings

# Regular season detailed results (for stats features)
regular_season_results = pd.read_csv("mmdata/MRegularSeasonDetailedResults.csv")

# Tournament results (to build training labels)
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")

# Regular season detailed results (for stats features)
doubled_reg_season = pd.read_csv("mmdata/MNCAADoubledRegularSeasonDetailedResults.csv")

# Tournament results (to build training labels)
doubled_tourney = pd.read_csv("mmdata/MNCAADoubledTourneyResults.csv")

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

# Extract numeric seed value
seeds["seed"] = seeds["Seed"].apply(lambda x: int(''.join(filter(str.isdigit, x[1:]))))

# Prepare seeds for both teams
seeds_T1 = seeds[["Season", "TeamID", "seed"]].copy()
seeds_T2 = seeds[["Season", "TeamID", "seed"]].copy()
seeds_T1.columns = ["Season", "T1_TeamID", "T1_seed"]
seeds_T2.columns = ["Season", "T2_TeamID", "T2_seed"]

doubled_tourney["T1_TeamID"] = doubled_tourney["T1_TeamID"].astype(int)
doubled_tourney["T2_TeamID"] = doubled_tourney["T2_TeamID"].astype(int)
seeds_T1["T1_TeamID"] = seeds_T1["T1_TeamID"].astype(int)
seeds_T2["T2_TeamID"] = seeds_T2["T2_TeamID"].astype(int)

# Merge seed data into doubled_tourney
doubled_tourney = pd.merge(doubled_tourney, seeds_T1, on=["Season", "T1_TeamID"], how="left")
doubled_tourney = pd.merge(doubled_tourney, seeds_T2, on=["Season", "T2_TeamID"], how="left")

# Create seed difference feature
doubled_tourney["Seed_diff"] = doubled_tourney["T2_seed"] - doubled_tourney["T1_seed"]

doubled_tourney.to_csv("mmdata/ProcessedTourneyResults_withSeedDiff.csv", index=False)