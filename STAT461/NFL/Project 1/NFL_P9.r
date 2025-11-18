# Load necessary libraries
library(dplyr)
library(ggplot2)

# Read the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 regular season games (excluding playoffs)
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

# Convert to DataFrame for plotting
team_strengths_df <- data.frame(
  Team = names(team_strengths),
  Strength = as.numeric(team_strengths)
)

# Order by strength
team_strengths_df <- team_strengths_df %>% arrange(Strength)

# Plot the estimated team strengths
ggplot(team_strengths_df, aes(x = reorder(Team, Strength), y = Strength)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  coord_flip() +  # Flip to horizontal bar plot for readability
  labs(
    title = "Estimated Team Strengths (Regular Season Only, Sum = 0)",
    x = "Team",
    y = "Estimated Strength"
  ) +
  theme_minimal()

# Print success message
print("Plot generated successfully!")

if (.Platform$OS.type == "windows") {
  windows()
} else if (Sys.info()["sysname"] == "Darwin") {
  quartz()
} else {
  X11()
}

# Now generate and display the plot
print(
  ggplot(team_strengths_df, aes(x = reorder(Team, Strength), y = Strength)) +
    geom_bar(stat = "identity", fill = "steelblue") +
    coord_flip() +
    labs(
      title = "Estimated Team Strengths (Regular Season Only, Sum = 0)",
      x = "Team",
      y = "Estimated Strength"
    ) +
    theme_minimal()
)

