import matplotlib.pyplot as plt
import networkx as nx
from predict_bracket import find_game_slot

def visualize_bracket(predicted_bracket, actual_results_df, season, seeds_df, slots_df, teams_df):
    # Build actual bracket: teams per slot
    actual_slots = {}
    for _, row in actual_results_df[actual_results_df["Season"] == season].iterrows():
        slot = find_game_slot(season, row["WTeamID"], row["LTeamID"], seeds_df, slots_df)
        if slot:
            actual_slots[slot] = {row["WTeamID"], row["LTeamID"]}

    id_to_name = dict(zip(teams_df["TeamID"], teams_df["TeamName"]))

    G = nx.DiGraph()
    pos = {}
    labels = {}
    colors = []

    round_order = {"R1": 0, "R2": 1, "R3": 2, "R4": 3, "R5": 4, "R6": 5}
    round_labels = {
        0: "Round of 64",
        1: "Round of 32",
        2: "Sweet 16",
        3: "Elite 8",
        4: "Final Four",
        5: "Championship"
    }

    x_spacing = 4
    y_spacing = 100
    y_counter = {r: 0 for r in round_order}
    last_round_node = {}

    for slot, winner in predicted_bracket.items():
        round_code = slot[:2]
        if round_code not in round_order:
            continue
        round_num = round_order[round_code]

        match = slots_df[(slots_df["Season"] == season) & (slots_df["Slot"] == slot)]
        if match.empty:
            continue

        strong, weak = match.iloc[0]["StrongSeed"], match.iloc[0]["WeakSeed"]
        seed_map = dict(zip(seeds_df[seeds_df["Season"] == season]["Seed"],
                            seeds_df[seeds_df["Season"] == season]["TeamID"]))

        team1 = predicted_bracket.get(strong) or seed_map.get(strong)
        team2 = predicted_bracket.get(weak) or seed_map.get(weak)
        if team1 is None or team2 is None:
            continue

        actual_teams = actual_slots.get(slot)

        for team in [team1, team2]:
            team_name = id_to_name.get(team, str(team))
            node_name = f"{team_name}_{round_code}"
            x = round_num * x_spacing
            y = -y_counter[round_code] * y_spacing
            pos[node_name] = (x, y)
            labels[node_name] = team_name
            G.add_node(node_name)

            if round_code == "R1":
                colors.append("gray")
            elif actual_teams is None:
                colors.append("gray")
            elif team in actual_teams:
                colors.append("green")
            else:
                colors.append("red")

            if team in last_round_node and round_code != "R1":
                G.add_edge(last_round_node[team], node_name)

            last_round_node[team] = node_name
            y_counter[round_code] += 1

        # Draw matchup edge: losing team → winner
        winner_name = id_to_name.get(winner, str(winner))
        loser = team2 if winner == team1 else team1
        loser_name = id_to_name.get(loser, str(loser))
        G.add_edge(f"{loser_name}_{round_code}", f"{winner_name}_{round_code}")

    # Add final winner node
    final_slot = "R6CH"
    if final_slot in predicted_bracket:
        winner_id = predicted_bracket[final_slot]
        winner_name = id_to_name.get(winner_id, str(winner_id))
        winner_node = f"{winner_name}_WIN"
        x = (max(round_order.values()) + 1) * x_spacing
        champ_nodes = [n for n in pos if n.endswith("_R6")]
        avg_y = sum(pos[n][1] for n in champ_nodes) / len(champ_nodes) if champ_nodes else 0

        pos[winner_node] = (x, avg_y)
        labels[winner_node] = f"{winner_name} 🏆"
        colors.append("gold")
        G.add_node(winner_node)
        G.add_edge(f"{winner_name}_R6", winner_node)

    # Center y positions
    for round_code, r_index in round_order.items():
        nodes_in_round = [n for n in pos if n.endswith(f"_{round_code}")]
        if not nodes_in_round:
            continue
        ys = [pos[n][1] for n in nodes_in_round]
        avg_y = (max(ys) + min(ys)) / 2
        for n in nodes_in_round:
            x, y = pos[n]
            pos[n] = (x, y - avg_y)

    plt.figure(figsize=(24, 13))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color=colors,
            node_size=1300, font_size=8, edge_color='lightgray', arrows=False)

    all_y = [y for (_, y) in pos.values()]
    max_y = max(all_y) if all_y else 0
    title_y = max_y + 100

    for round_num, label in round_labels.items():
        plt.text(round_num * x_spacing, title_y, label, fontsize=12, ha='center', fontweight='bold')

    plt.text((max(round_order.values()) + 1) * x_spacing, title_y, "Winner", fontsize=12, ha='center', fontweight='bold')

    min_y = min(all_y) if all_y else -1000
    plt.xlim(-2, 5 * x_spacing + 2)
    plt.ylim(min_y - 100, title_y + 100)

    plt.title(f"NCAA Bracket Prediction ({season})\nGreen = Correct, Red = Incorrect, Gray = Unknown")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
