import argparse
import pandas as pd
import joblib
from team_season_stats import compute_stat_differences
from visualize_bracket import visualize_bracket
from predict_bracket import validate_bracket


# Load all data
elos = pd.read_csv("mmdata/TeamElos.csv")
teamStats = pd.read_csv("mmdata/TeamSeasonStats.csv")
seeds_df = pd.read_csv("mmdata/RbyRMNCAATourneySeeds.csv")
slots_df = pd.read_csv("mmdata/MNCAATourneySlots.csv")
teams_df = pd.read_csv("mmdata/MTeams.csv")  # Optional: team names
tourney_results = pd.read_csv("mmdata/MNCAATourneyDetailedResults.csv")


# Load models per round
rounds = ["R1", "R2", "R3", "R4", "R5", "R6"]
models = {rnd: joblib.load(f"RbyRModels/{rnd}_model.pkl") for rnd in rounds}

# Play-in slots by year
play_in_slots_by_year = {
    2003: ["X16"], 2004: ["Z16"], 2005: ["Z16"], 2006: ["Y16"], 2007: ["Z16"],
    2008: ["W16"], 2009: ["Y16"], 2010: ["X16"],
    2011: ["W12", "W16", "Y16", "Z11"], 2012: ["X12", "X16", "Y16", "Z14"],
    2013: ["W16", "Y11", "Y16", "Z13"], 2014: ["X16", "Y11", "Y12", "Y16"],
    2015: ["W11", "X16", "Y16", "Z11"], 2016: ["W11", "W16", "Y11", "Z16"],
    2017: ["W11", "W16", "Y16", "Z11"], 2018: ["W11", "W16", "X11", "Z16"],
    2019: ["W11", "W16", "X11", "X16"], 2021: ["W11", "W16", "X11", "X16"],
    2022: ["W12", "X11", "Y16", "Z16"], 2023: ["W16", "X16", "Y11", "Z11"],
    2024: ["X16", "Y10", "Y16", "Z10"], 2025: ["W16", "X11", "Y11", "Y16"]
}

def simulate_bracket_round_by_round(season: int):
    season_seeds = seeds_df[seeds_df["Season"] == season]
    season_slots = slots_df[slots_df["Season"] == season]
    seed_to_team = dict(zip(season_seeds["Seed"], season_seeds["TeamID"]))
    slot_to_team = {}

    # Separate play-in handling
    play_in_slots = play_in_slots_by_year.get(season, [])
    play_ins = season_slots[season_slots["Slot"].isin(play_in_slots)]
    main_slots = season_slots[~season_slots["Slot"].isin(play_in_slots)]

    def resolve_team_id(seed_or_slot):
        return slot_to_team.get(seed_or_slot) or seed_to_team.get(seed_or_slot)

    def simulate_game(slot, strong, weak):
        t1 = resolve_team_id(strong)
        t2 = resolve_team_id(weak)
        if t1 is None or t2 is None:
            print(f"❌ SKIPPED {slot}: Missing teams {strong} vs {weak}")
            return

        e1 = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]["Elo"]
        e2 = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]["Elo"]
        if e1.empty or e2.empty:
            print(f"❌ SKIPPED {slot}: Missing Elo for {t1} or {t2}")
            return
        elo_diff = float(e1.values[0] - e2.values[0])

        try:
            s1 = int(strong[1:3])
            s2 = int(weak[1:3])
            seed_diff = s2 - s1
        except:
            seed_diff = 0

        stat_diff = compute_stat_differences(t1, t2, season, teamStats)
        if stat_diff is None:
            print(f"❌ SKIPPED {slot}: Missing stats")
            return

        rnd = slot[:2]
        model = models.get(rnd)
        if not model:
            print(f"❌ SKIPPED {slot}: No model for round {rnd}")
            return

        feature_vec = pd.DataFrame([{"SeedDiff": seed_diff, "EloDiff": elo_diff, **stat_diff}])
        pred = model.predict(feature_vec)[0]
        winner = t1 if pred == 1 else t2

        print(f"✅ {slot} ({rnd}): {t1} vs {t2} → Winner: {winner}")
        slot_to_team[slot] = winner

    # Handle play-ins
    for _, row in play_ins.iterrows():
        simulate_game(row["Slot"], row["StrongSeed"], row["WeakSeed"])
    for playin in play_in_slots:
        if playin in slot_to_team:
            seed_to_team[playin] = slot_to_team[playin]

    # Round-by-round simulation
    for rnd in rounds:
        for _, row in main_slots[main_slots["Slot"].str.startswith(rnd)].iterrows():
            simulate_game(row["Slot"], row["StrongSeed"], row["WeakSeed"])

    return slot_to_team

# Command-line interface
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2025)
    args = parser.parse_args()

    result = simulate_bracket_round_by_round(args.season)

    print(f"\n🧠 Final bracket prediction for {args.season}")
    for slot, team in result.items():
        name = teams_df.loc[teams_df["TeamID"] == team, "TeamName"].values[0]
        print(f"{slot}: {team} ({name})")

    visualize_bracket(
    predicted_bracket=result,
    actual_results_df=tourney_results,
    season=args.season,
    seeds_df=seeds_df,
    slots_df=slots_df,
    teams_df=teams_df
    )


    # score = validate_bracket(
    # predicted_bracket=result,
    # actual_results_df=tourney_results,
    # season=args.season,
    # seeds_df=seeds_df,
    # slots_df=slots_df
    # )

    # print(f"🎯 Bracket validation score for {args.season}: {score}")