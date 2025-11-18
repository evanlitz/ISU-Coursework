# Load necessary libraries
library(dplyr)

# Read the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 regular season games (exclude playoffs)
df_2024 <- df %>%
  filter(schedule_season == 2024 & 
         !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Compute Margin of Victory (MOV)
df_2024 <- df_2024 %>%
  mutate(margin_victory = score_home - score_away)

# Get unique teams
teams <- unique(c(df_2024$team_home, df_2024$team_away))
n_teams <- length(teams)
n_games <- nrow(df_2024)

# Create a model matrix for Least Squares Estimation
X <- matrix(0, nrow = n_games, ncol = n_teams)
colnames(X) <- teams

# Populate the matrix: Home team +1, Away team -1
for (i in 1:n_games) {
  X[i, df_2024$team_home[i]] <-  1
  X[i, df_2024$team_away[i]] <- -1
}

# Constraint: sum of all team strengths should be zero
X_constraint <- matrix(1, nrow = 1, ncol = n_teams)  # Row of ones
X_extended <- rbind(X, X_constraint)  # Add constraint row
y_extended <- c(df_2024$margin_victory, 0)  # Add a zero for constraint

# Solve for team strengths using QR decomposition (numerically stable)
team_strengths <- qr.solve(t(X_extended) %*% X_extended, t(X_extended) %*% y_extended)

# Convert to named vector
team_strengths <- setNames(team_strengths, teams)

# Estimate Home Field Advantage (HFA)
home_games <- df_2024 %>%
  filter(team_home != "" & team_away != "")

hfa <- mean(home_games$margin_victory - (team_strengths[home_games$team_home] - team_strengths[home_games$team_away]), na.rm = TRUE)

# Get strengths of Vikings and Bears
vikings_strength <- team_strengths["Minnesota Vikings"]
bears_strength <- team_strengths["Chicago Bears"]

# Compute Expected Point Difference (Vikings - Bears)
expected_margin <- (vikings_strength - bears_strength) + hfa

# Estimate Standard Deviation of MOV (σ)
sigma <- sd(df_2024$margin_victory, na.rm = TRUE)

# Compute Probability (using Normal Distribution)
probability_vikings_win <- pnorm(0, mean = expected_margin, sd = sigma, lower.tail = FALSE)

# Print results
print(paste("Expected Point Difference (Vikings - Bears at U.S. Bank Stadium):", round(expected_margin, 6)))
print(paste("Estimated Home Field Advantage:", round(hfa, 6)))
print(paste("Estimated Standard Deviation of MOV:", round(sigma, 6)))
print(paste("Probability Vikings Win:", round(probability_vikings_win, 6)))
