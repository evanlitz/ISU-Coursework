# Load necessary libraries
library(tidyverse)
library(DT)
library(BradleyTerry2)

# Load the dataset
df <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter for the 2024 season and exclude playoff games
df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Prepare the data for the Bradley-Terry model
# Create a data frame with the home team, away team, and the outcome (1 if home team wins, 0 if away team wins)
bt_data <- df_2024 %>%
  mutate(outcome = ifelse(score_home > score_away, 1, 0)) %>%
  select(team_home, team_away, outcome)

# Fit the Bradley-Terry model
bt_model <- BTm(outcome, team_home, team_away, data = bt_data)

# Extract the home advantage parameter
home_advantage <- bt_model$coefficients["home"]

# Answer to Question 1: What is the estimated value of the home advantage parameter?
cat("1. Estimated value of the home advantage parameter:", home_advantage, "\n")

# Answer to Question 2: If two equal strength teams are playing, what is the estimated probability the home team will win?
# The probability that the home team wins when two teams are equal in strength is given by the logistic function:
# P(home wins) = exp(home_advantage) / (1 + exp(home_advantage))
home_win_prob <- exp(home_advantage) / (1 + exp(home_advantage))
cat("2. Estimated probability the home team will win when two equal strength teams play:", home_win_prob, "\n")

# Answer to Question 3: What is the estimated strength of the Minnesota Vikings if Washington Commanders strength is 0?
# Extract the team strengths from the model
team_strengths <- bt_model$coefficients

# Set Washington Commanders strength to 0
team_strengths["Washington Commanders"] <- 0

# Extract the strength of the Minnesota Vikings
vikings_strength <- team_strengths["Minnesota Vikings"]
cat("3. Estimated strength of the Minnesota Vikings if Washington Commanders strength is 0:", vikings_strength, "\n")