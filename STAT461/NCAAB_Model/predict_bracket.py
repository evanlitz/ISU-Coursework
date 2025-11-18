import pandas as pd
from team_season_stats import compute_stat_differences

def simulate_bracket(season, model, teamStats, elos, seeds_df, slots_df):
    # Filter seed and slot data for the season
    season_seeds = seeds_df[seeds_df["Season"] == season].copy()
    season_slots = slots_df[slots_df["Season"] == season].copy()

    # Map Seed -> TeamID
    seed_to_team = dict(zip(season_seeds["Seed"], season_seeds["TeamID"]))
    slot_to_team = {}

    # Separate play-in and main slots
# Hardcoded play-in slot mapping by year
    play_in_slots_by_year = {
        2003: ["X16"],
        2004: ["Z16"],
        2005: ["Z16"],
        2006: ["Y16"],
        2007: ["Z16"],
        2008: ["W16"],
        2009: ["Y16"],
        2010: ["X16"],
        2011: ["W12", "W16", "Y16", "Z11"],
        2012: ["X12", "X16", "Y16", "Z14"],
        2013: ["W16", "Y11", "Y16", "Z13"],
        2014: ["X16", "Y11", "Y12", "Y16"],
        2015: ["W11", "X16", "Y16", "Z11"],
        2016: ["W11", "W16", "Y11", "Z16"],
        2017: ["W11", "W16", "Y16", "Z11"],
        2018: ["W11", "W16", "X11", "Z16"],
        2019: ["W11", "W16", "X11", "X16"],
        2021: ["W11", "W16", "X11", "X16"],
        2022: ["W12", "X11", "Y16", "Z16"],
        2023: ["W16", "X16", "Y11", "Z11"],
        2024: ["X16", "Y10", "Y16", "Z10"],
        2025: ["W16", "X11", "Y11", "Y16"]
}

    # Get play-in slots for the given season
    play_in_slots = play_in_slots_by_year.get(season, [])
    play_ins = season_slots[season_slots["Slot"].isin(play_in_slots)]
    main_slots = season_slots[~season_slots["Slot"].isin(play_in_slots)]

    def process_match(slot, strong, weak):
        t1 = seed_to_team.get(strong) if strong in seed_to_team else slot_to_team.get(strong)
        t2 = seed_to_team.get(weak) if weak in seed_to_team else slot_to_team.get(weak)

        if t1 is None or t2 is None:
            print(f"❌ SKIPPED {slot}: Missing team(s) — strong: {strong}, weak: {weak}")
            return

        t1_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t1)]
        t2_elo_row = elos[(elos["Season"] == season) & (elos["TeamID"] == t2)]
        if t1_elo_row.empty or t2_elo_row.empty:
            print(f"❌ SKIPPED {slot}: Missing Elo rating for team(s): {t1}, {t2}")
            return
        elo_diff = t1_elo_row.iloc[0]["Elo"] - t2_elo_row.iloc[0]["Elo"]

        seed1 = int(strong[1:3]) if strong in seed_to_team else -1
        seed2 = int(weak[1:3]) if weak in seed_to_team else -1
        seed_diff = seed2 - seed1

        stat_diff = compute_stat_differences(t1, t2, season, teamStats)
        if stat_diff is None:
            print(f"❌ SKIPPED {slot}: Missing stats for {t1} vs {t2}")
            return

        features = {
            "SeedDiff": seed_diff,
            "EloDiff": elo_diff,
            **stat_diff
        }

        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        winner = t1 if prediction == 1 else t2

        print(f"✅ {slot}: {t1} vs {t2} → Winner: {winner}")
        slot_to_team[slot] = winner

    # 1. Process play-in games
    for _, row in play_ins.iterrows():
        process_match(row["Slot"], row["StrongSeed"], row["WeakSeed"])

    # 2. Assign winners to their seed slots
    for seed in play_in_slots:
        if seed in slot_to_team:
            seed_to_team[seed] = slot_to_team[seed]
            print(f"🔁 Assigned play-in winner {slot_to_team[seed]} to seed {seed}")

    # 3. Process the rest of the bracket
    for _, row in main_slots.iterrows():
        process_match(row["Slot"], row["StrongSeed"], row["WeakSeed"])

    if "R6CH" not in slot_to_team:
        print("⚠️ Final championship slot (R6CH) was never reached!")

    return slot_to_team

def validate_bracket(predicted_bracket, actual_results_df, season, seeds_df, slots_df):
    score = 0
    round_weights = {
        "R1": 1,
        "R2": 2,
        "R3": 4,
        "R4": 8,
        "R5": 16,
        "R6": 32
    }

    # Create a lookup of actual matchups (frozenset(team1, team2)) → winner
    actual_results = actual_results_df[actual_results_df["Season"] == season]
    actual_matchups = {}
    for _, row in actual_results.iterrows():
        t1, t2 = row["WTeamID"], row["LTeamID"]
        matchup = frozenset([t1, t2])
        actual_matchups[matchup] = row["WTeamID"]

    # Validate predicted bracket
    for slot, winner in predicted_bracket.items():
        round_id = slot[:2]
        if round_id not in round_weights:
            continue

        # Get the two teams in the slot
        strong = slots_df.loc[(slots_df["Season"] == season) & (slots_df["Slot"] == slot), "StrongSeed"]
        weak = slots_df.loc[(slots_df["Season"] == season) & (slots_df["Slot"] == slot), "WeakSeed"]
        if strong.empty or weak.empty:
            continue

        seed_lookup = seeds_df[seeds_df["Season"] == season]
        seed_map = dict(zip(seed_lookup["Seed"], seed_lookup["TeamID"]))

        t1 = seed_map.get(strong.values[0], predicted_bracket.get(strong.values[0]))
        t2 = seed_map.get(weak.values[0], predicted_bracket.get(weak.values[0]))

        if not t1 or not t2:
            continue

        matchup = frozenset([t1, t2])
        actual_winner = actual_matchups.get(matchup)

        if actual_winner and actual_winner == winner:
            score += round_weights[round_id]

    return score

def find_game_slot(season, team1, team2, seeds_df, slots_df):
    # Load season data
    season_seeds = seeds_df[seeds_df["Season"] == season]
    season_slots = slots_df[slots_df["Season"] == season]

    # Create lookup: teamID → seed string (e.g., W01, X12, etc.)
    team_to_seed = dict(zip(season_seeds["TeamID"], season_seeds["Seed"]))

    seed1 = team_to_seed.get(team1)
    seed2 = team_to_seed.get(team2)

    # Since teams progress through slots, try seed or previous slot match
    possible_keys_1 = [seed1, seed2]
    possible_keys_2 = [seed2, seed1]

    for _, row in season_slots.iterrows():
        strong, weak = row["StrongSeed"], row["WeakSeed"]
        if ((strong in possible_keys_1 and weak in possible_keys_2) or
            (strong in possible_keys_2 and weak in possible_keys_1)):
            return row["Slot"]

    return None  # Not found
