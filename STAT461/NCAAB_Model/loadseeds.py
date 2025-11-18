import pandas as pd

base_path = "mmdata"

seeds_df = pd.read_csv(f"{base_path}/MNCAATourneySeeds.csv")

slots_df = pd.read_csv(f"{base_path}/MNCAATourneySlots.csv")

teams_df = pd.read_csv(f"{base_path}/MTeams.csv")

print("Seeds:")
print(seeds_df.head(), end="\n\n")

print("Slots:")
print(slots_df.head(), end="\n\n")

print("Teams:")
print(teams_df.head())

# STEP 2: Build initial matchups for a specific year
SEASON = 2023  # You can change this to another year if needed

# 1. Filter by season
seeds = seeds_df[seeds_df['Season'] == SEASON]
slots = slots_df[slots_df['Season'] == SEASON]

# 2. Create seed → team_id map
seed_to_team = dict(zip(seeds['Seed'], seeds['TeamID']))

# 3. Build Round 1 matchups from slots
initial_matchups = []

for _, row in slots.iterrows():
    seed1 = row['StrongSeed']
    seed2 = row['WeakSeed']
    team1 = seed_to_team.get(seed1)
    team2 = seed_to_team.get(seed2)
    
    # Skip if a seed wasn't found (can happen for play-ins or incomplete data)
    if team1 is None or team2 is None:
        continue

    matchup = {
        "Slot": row['Slot'],
        "Team1ID": team1,
        "Team2ID": team2,
        "Seed1": seed1,
        "Seed2": seed2,
        "NextSlot": row.get("WinnerNextSlot", None)  # Might not exist in all files
    }
    initial_matchups.append(matchup)

# Convert to DataFrame for inspection
initial_matchups_df = pd.DataFrame(initial_matchups)
print(initial_matchups_df.head())

