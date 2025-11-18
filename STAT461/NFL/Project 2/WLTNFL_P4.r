
# Load necessary libraries
library(tidyverse)
library(DT)
library(BradleyTerry2)
library(ggplot2)


# Load the dataset
df <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter for the 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

df_2024 <- df_2024 %>%
  mutate(home_win = ifelse(score_home > score_away, 1, 0))

print(table(df_2024$home_win))  # Check distribution of home wins

construct_model_matrix <- function(d, homeCol = "team_home", awayCol = "team_away") {
  teams <- unique(c(d[[homeCol]], d[[awayCol]]))  # List of all teams
  n_games <- nrow(d)
  n_teams <- length(teams)
  
  # Initialize matrix with zeros
  m <- matrix(0, nrow = n_games, ncol = n_teams)
  
  for (g in 1:n_games) {
    home_team_index <- which(teams == d[g, homeCol])
    away_team_index <- which(teams == d[g, awayCol])
    m[g, home_team_index] <-  1  # Home team = +1
    m[g, away_team_index] <- -1  # Away team = -1
  }
  return(m)
}

X <- construct_model_matrix(df_2024, homeCol = "team_home", awayCol = "team_away")

m <- glm(df_2024$home_win ~ X, family = binomial(link = "logit"))

summary(m)

home_advantage <- summary(m)$coefficients[1, ]  # Intercept represents home advantage

print(home_advantage)

# Extract team strengths from the model (excluding intercept)
team_strengths <- coef(m)[-1]  # Remove the intercept (home field advantage)

# Get team names from the model matrix
teams <- unique(c(df_2024$team_home, df_2024$team_away))

# Create a named vector for easier lookup
team_strengths_named <- setNames(team_strengths, teams)

# Ensure all teams have defined strengths (replace NAs with 0)
team_strengths_named[is.na(team_strengths_named)] <- 0

# Check if Washington Commanders exist in the dataset
if (!"Washington Commanders" %in% names(team_strengths_named)) {
  print("Error: Washington Commanders not found in the dataset. Choosing a different reference team.")
  ref_team <- names(team_strengths_named)[1]  # Default to first team in list
} else {
  ref_team <- "Washington Commanders"
}

# Normalize strengths by setting Washington Commanders' strength to 0
washington_strength <- team_strengths_named[ref_team]
normalized_team_strengths <- team_strengths_named - washington_strength

# Get Minnesota Vikings' adjusted strength
vikings_strength <- normalized_team_strengths["Minnesota Vikings"]

# Normalize strengths so that the sum of all team strengths is zero
mean_strength <- mean(team_strengths_named)  # Compute mean strength
normalized_team_strengths_zero_sum <- team_strengths_named - mean_strength  # Adjust each strength

# Get Minnesota Vikings' adjusted strength under this constraint
vikings_strength_zero_sum <- normalized_team_strengths_zero_sum["Minnesota Vikings"]

# Print results
cat("Minnesota Vikings' strength when Washington Commanders' strength is 0:", vikings_strength, "\n")
cat("Minnesota Vikings' strength when the sum of all strengths is 0:", vikings_strength_zero_sum, "\n")
cat("Sum of all adjusted team strengths (should be ~0):", sum(normalized_team_strengths_zero_sum), "\n")

# Compute probability of each team winning against an average team (strength = 0)
win_probabilities <- 1 / (1 + exp(-normalized_team_strengths_zero_sum))

# Create a data frame for visualization
prob_df <- data.frame(
  Team = names(win_probabilities),
  Win_Probability = win_probabilities
)

# Sort teams by win probability
prob_df <- prob_df %>% arrange(desc(Win_Probability))

dev.new()  # Opens a new graphics window
print(
  ggplot(prob_df, aes(x = reorder(Team, Win_Probability), y = Win_Probability)) +
    geom_bar(stat = "identity", fill = "steelblue") +
    coord_flip() +
    labs(
      title = "Probability of Each Team Beating an Average Team on a Neutral Field",
      x = "Team",
      y = "Win Probability"
    ) +
    theme_minimal()
)