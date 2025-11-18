import pandas as pd
from math import log

# --- Elo core functions ---
def expected_result(elo_a, elo_b, width=400, home_court_advantage=0):
    return 1 / (1 + 10 ** ((elo_b - elo_a + home_court_advantage) / width))

def update_elo(winner_elo, loser_elo, margin=1, k=50, width=400, home_court_advantage=0):
    expected = expected_result(winner_elo, loser_elo, width, home_court_advantage)
    elo_diff = abs(winner_elo - loser_elo)
    mov_scale = log(margin + 1) * (2.2 / ((elo_diff * 0.001) + 2.2))  # MOV multiplier
    change = k * (1 - expected) * mov_scale
    return winner_elo + change, loser_elo - change

# --- Elo calculator ---
def calculate_elo_ratings(games_df, base_elo=1000, k=50, width=400, ap_df=None):
    all_elos = []

    for season in sorted(games_df["Season"].unique()):
        season_games = games_df[games_df["Season"] == season].sort_values("DayNum")
        team_elos = {}

        # Use AP rankings to modify initial Elo
        if ap_df is not None:
            ap_season = ap_df[(ap_df["Season"] == season) & (ap_df["RankingDayNum"] == 133)]
            for _, row in ap_season.iterrows():
                # Boost: higher rank = lower number (1 is best), so subtract from 26 to scale properly
                team_elos[row["TeamID"]] = base_elo + (26 - row["OrdinalRank"]) * 5

        for _, game in season_games.iterrows():
            t1 = game["WTeamID"]
            t2 = game["LTeamID"]
            t1_elo = team_elos.get(t1, base_elo)
            t2_elo = team_elos.get(t2, base_elo)
            margin = game["WScore"] - game["LScore"]
            loc = game.get("WLoc", "N")

                # Interpret home court advantage
            if loc == "H":
                 hca = 100  # winner played at home
            elif loc == "A":
                hca = -100  # winner was away (loser at home)
            else:
                hca = 0

            t1_new, t2_new = update_elo(t1_elo, t2_elo, margin=margin, k=k, width=width, home_court_advantage=hca)
            team_elos[t1] = t1_new
            team_elos[t2] = t2_new

        for team_id, elo in team_elos.items():
            all_elos.append({"Season": season, "TeamID": team_id, "Elo": elo})

    return pd.DataFrame(all_elos)

# Example usage:
# ap_df = massey[massey["SystemName"] == "AP"].drop(columns=["SystemName"])
# elos_df = calculate_elo_ratings(regular_season_results, ap_df=ap_df)
# elos_df.to_csv("mmdata/TeamElos.csv", index=False)
