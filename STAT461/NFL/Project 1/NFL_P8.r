# Load necessary libraries
library(dplyr)

# Read the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 regular season games (excluding playoffs)
df_2024 <- df %>%
  filter(schedule_season == 2024 & 
         !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Compute Margin of Victory (MOV)
df_2024 <- df_2024 %>%
  mutate(margin_victory = score_home - score_away)

# Get list of unique teams
teams <- unique(c(df_2024$team_home, df_2024$team_away))
n_teams <- length(teams)
n_games <- nrow(df_2024)

# Create team index mapping
team_index <- setNames(1:n_teams, teams)

# Construct model matrix (X)
X <- matrix(0, nrow = n_games, ncol = n_teams)

# Populate matrix: +1 for home team, -1 for away team
for (i in 1:n_games) {
  X[i, team_index[df_2024$team_home[i]]] <-  1
  X[i, team_index[df_2024$team_away[i]]] <- -1
}

# Constraint row: ensures sum(team_strengths) = 0
X_constraint <- matrix(1, nrow = 1, ncol = n_teams)  # Row of ones
X_extended <- rbind(X, X_constraint)  # Add constraint
y_extended <- c(df_2024$margin_victory, 0)  # Add zero for constraint

# Solve using QR decomposition (numerically stable)
team_strengths <- qr.solve(t(X_extended) %*% X_extended, t(X_extended) %*% y_extended)

# Convert to named vector
team_strengths <- setNames(team_strengths, teams)

# Verify sum constraint (should be very close to 0)
print(paste("Sum of all team strengths:", round(sum(team_strengths), 6)))

# Extract Minnesota Vikings' strength
vikings_strength <- team_strengths["Minnesota Vikings"]
print(paste("Estimated Strength of Minnesota Vikings:", round(vikings_strength, 6)))
