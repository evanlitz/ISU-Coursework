import pandas as pd

# Load the ELO data
elos = pd.read_csv("mmdata/TeamElos.csv")

# Find the highest ELO per team and the corresponding season
peak_elo_per_team = elos.loc[elos.groupby("TeamID")["Elo"].idxmax()].copy()

# Merge with team names for better readability
teams = pd.read_csv("mmdata/MTeams.csv")
peak_elo_per_team = peak_elo_per_team.merge(teams, on="TeamID")

# Sort and extract top/bottom 50
top_50 = peak_elo_per_team.sort_values(by="Elo", ascending=False).head(50)
bottom_50 = peak_elo_per_team.sort_values(by="Elo", ascending=True).head(50)

# Output
print("=== Top 50 ELOs ===")
print(top_50[["TeamName", "Season", "Elo"]].to_string(index=False))

print("\n=== Bottom 50 ELOs ===")
print(bottom_50[["TeamName", "Season", "Elo"]].to_string(index=False))
