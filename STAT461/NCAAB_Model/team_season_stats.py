import pandas as pd

def generate_team_season_stats(doubled_reg_season):
    stats = doubled_reg_season.groupby(["Season", "T1_TeamID"]).agg({
        "T1_FGM": "mean",
        "T1_FGA": "mean",
        "T1_FGM3": "mean",
        "T1_FGA3": "mean",
        "T1_FTM": "mean",
        "T1_FTA": "mean",
        "T1_OR": "mean",
        "T1_DR": "mean",
        "T1_Ast": "mean",
        "T1_TO": "mean",
        "T1_Stl": "mean",
        "T1_PF": "mean",
        "T1_Score": "mean",  # Points scored
        "T2_Score": "mean"   # Points allowed
    }).reset_index()

    stats["FG%"] = stats["T1_FGM"] / stats["T1_FGA"]
    stats["3P%"] = stats["T1_FGM3"] / stats["T1_FGA3"]
    stats["FT%"] = stats["T1_FTM"] / stats["T1_FTA"]

    stats = stats.rename(columns={"T1_TeamID": "TeamID"})
    stats = stats.rename(columns={
        "T1_Score": "AvgPointsScored",
        "T2_Score": "AvgPointsAllowed"
    })

    return stats

def get_team_stats(team_id, season, stats_df):
    row = stats_df[(stats_df["TeamID"] == team_id) & (stats_df["Season"] == season)]
    if row.empty:
        return None
    # Strip T1_ prefix
    stats = row.iloc[0].copy()
    stats.index = stats.index.str.replace("T1_", "")
    return stats

def compute_stat_differences(team1_id, team2_id, season, stats_df):
    stats1 = get_team_stats(team1_id, season, stats_df)
    stats2 = get_team_stats(team2_id, season, stats_df)
    
    if stats1 is None or stats2 is None:
        return None

    stat_diff = {
        "fgm_diff": stats1["FGM"] - stats2["FGM"],
        "fg_pct_diff": stats1["FG%"] - stats2["FG%"],
        "to_diff": stats1["TO"] - stats2["TO"],
        "reb_diff": (stats1["OR"] + stats1["DR"]) - (stats2["OR"] + stats2["DR"]),
        "3p_pct_diff": stats1["3P%"] - stats2["3P%"],
        "ft_pct_diff": stats1["FT%"] - stats2["FT%"],
        "ast_diff": stats1["Ast"] - stats2["Ast"],
        "pf_diff": stats1["PF"] - stats2["PF"],
        "stl_diff": stats1["Stl"] - stats2["Stl"],
        "avg_pts_scored_diff": stats1["AvgPointsScored"] - stats2["AvgPointsScored"],
        "avg_pts_allowed_diff": stats1["AvgPointsAllowed"] - stats2["AvgPointsAllowed"],
        "avg_point_margin_diff": (stats1["AvgPointsScored"] - stats1["AvgPointsAllowed"]) - (stats2["AvgPointsScored"] - stats2["AvgPointsAllowed"]),
    }

    return stat_diff






# team_stats = generate_team_season_stats(doubled_reg_season)
# team_stats.to_csv("mmdata/TeamSeasonStats.csv", index=False)