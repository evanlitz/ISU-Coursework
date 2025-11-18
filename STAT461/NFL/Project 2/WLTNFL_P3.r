# Load necessary libraries
library(tidyverse)
library(BradleyTerry2)

# Load the data
nfl_data <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter out rows with missing values
nfl_data <- nfl_data %>%
  filter(!is.na(team_home) & !is.na(team_away) & !is.na(score_home) & !is.na(score_away))

# Create a binary outcome for whether the home team won
nfl_data <- nfl_data %>%
  mutate(home_win = as.numeric(score_home > score_away))

# Convert team names to factors
teams <- unique(c(nfl_data$team_home, nfl_data$team_away))
nfl_data <- nfl_data %>%
  mutate(team_home = factor(team_home, levels = teams),
         team_away = factor(team_away, levels = teams))

# Fit the Bradley-Terry model
bt_model <- BTm(
  outcome = nfl_data$home_win,
  player1 = nfl_data$team_home,
  player2 = nfl_data$team_away,
  refcat = "Washington Commanders"  # Set a reference team to avoid NA issues
)

# Extract team strengths
team_strengths <- as.data.frame(BTabilities(bt_model))
team_strengths$team <- rownames(team_strengths)

# Ensure all teams have defined strengths (replace NAs with 0)
team_strengths$ability[is.na(team_strengths$ability)] <- 0

# Get Minnesota Vikings' strength when Washington Commanders' strength is 0
vikings_strength <- team_strengths %>%
  filter(team == "Minnesota Vikings") %>%
  pull(ability)

# Estimate home-field advantage
home_advantage <- coef(bt_model)["(Intercept)"]

# Compute probability of home win when teams are equal strength
home_win_prob <- 1 / (1 + exp(-home_advantage))

# Output results
results <- list(
  home_field_advantage = home_advantage,
  home_win_probability_equal_teams = home_win_prob,
  minnesota_vikings_strength = vikings_strength
)

print(results)  # This ensures the output is displayed in the console

