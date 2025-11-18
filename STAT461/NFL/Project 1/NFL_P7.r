# Load necessary libraries
library(dplyr)

# Read the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Ensure required columns exist
required_columns <- c("team_home", "team_away", "score_home", "score_away")
if (!all(required_columns %in% colnames(df_2024))) {
  stop("Required columns not found in the dataset.")
}

# Compute Margin of Victory
df_2024 <- df_2024 %>%
  mutate(margin_victory = score_home - score_away)

# Get unique teams
teams <- unique(c(df_2024$team_home, df_2024$team_away))
n_teams <- length(teams)
n_games <- nrow(df_2024)

# Create an empty model matrix
X <- matrix(0, nrow = n_games, ncol = n_teams)
colnames(X) <- teams

# Fill the matrix
for (i in 1:n_games) {
  X[i, df_2024$team_home[i]] <-  1  # Home team +1
  X[i, df_2024$team_away[i]] <- -1  # Away team -1
}

# Check if X is full rank
print(paste("Matrix Rank:", qr(t(X) %*% X)$rank))
print(paste("Number of Columns:", ncol(X)))

# Drop one team from the design matrix to ensure invertibility
X_reduced <- X[, -1]  # Drop the first team arbitrarily

# Solve for team strengths using Least Squares
b <- qr.solve(t(X_reduced) %*% X_reduced, t(X_reduced) %*% df_2024$margin_victory)

# Reintroduce the removed team with strength 0
team_strengths <- c(0, setNames(b, colnames(X_reduced)))
names(team_strengths)[1] <- colnames(X)[1]  # Assign name back

# Print all team strengths
print(team_strengths)

if ("Washington Commanders" %in% names(team_strengths)) {
  commanders_strength <- team_strengths["Washington Commanders"]
} else {
  stop("Washington Commanders not found in computed team strengths.")
}

# Adjust all team strengths relative to Washington Commanders
adjusted_strengths <- team_strengths - commanders_strength

# Extract Minnesota Vikings' strength
if ("Minnesota Vikings" %in% names(adjusted_strengths)) {
  vikings_strength <- adjusted_strengths["Minnesota Vikings"]
  print(paste("Estimated Strength of Minnesota Vikings (relative to Washington Commanders):", round(vikings_strength, 4)))
} else {
  stop("Minnesota Vikings not found in adjusted strengths.")
}