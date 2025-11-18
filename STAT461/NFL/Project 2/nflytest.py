import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

# Load the data
nfl_data = pd.read_csv("nfl.csv")

# Filter missing values
nfl_data = nfl_data.dropna(subset=["team_home", "team_away", "score_home", "score_away"])

# Create binary outcome (1 = home win, 0 = away win)
nfl_data["home_win"] = (nfl_data["score_home"] > nfl_data["score_away"]).astype(int)

# Encode teams as numerical values
teams = np.unique(nfl_data[["team_home", "team_away"]].values)
team_encoder = LabelEncoder()
team_encoder.fit(teams)

nfl_data["home_team_id"] = team_encoder.transform(nfl_data["team_home"])
nfl_data["away_team_id"] = team_encoder.transform(nfl_data["team_away"])

# Create a design matrix
X = np.zeros((len(nfl_data), len(teams)))
for i, row in nfl_data.iterrows():
    X[i, row["home_team_id"]] = 1
    X[i, row["away_team_id"]] = -1

# Add home-field advantage column
X = np.hstack([np.ones((X.shape[0], 1)), X])  # First column = home advantage

# Define the target variable
y = nfl_data["home_win"].values

# Fit logistic regression (similar to Bradley-Terry)
model = LogisticRegression(fit_intercept=False, solver='lbfgs', max_iter=1000)
model.fit(X, y)

# Extract coefficients
coef = model.coef_.flatten()
home_advantage = coef[0]  # First coefficient is home field advantage
team_strengths = dict(zip(teams, coef[1:]))  # Remaining are team strengths

# Normalize team strengths by setting Washington Commanders' strength to 0
baseline_team = "Washington Commanders"
offset = team_strengths[baseline_team]
for team in team_strengths:
    team_strengths[team] -= offset

# Compute probability of home win when teams are equal strength
home_win_prob = 1 / (1 + np.exp(-home_advantage))

# Get Minnesota Vikings' adjusted strength
vikings_strength = team_strengths["Minnesota Vikings"]

# Output results
output = {
    "home_field_advantage": home_advantage,
    "home_win_probability_equal_teams": home_win_prob,
    "minnesota_vikings_strength": vikings_strength
}

print(output)
