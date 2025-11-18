# Load necessary libraries
library(tidyverse)
library(DT)
library(BradleyTerry2)
library(ggplot2)

# Load the dataset
df <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter for the 2024 season
df_2024 <- df %>% 
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

df_2024 <- df_2024 %>%
  mutate(
    home_win = ifelse(score_home > score_away, 1, 0),
    mov = score_home - score_away  # Compute Margin of Victory
  )

print(table(df_2024$home_win))  # Check distribution of home wins

# Function to construct model matrix
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

# Win-Loss Model
X_winloss <- construct_model_matrix(df_2024, homeCol = "team_home", awayCol = "team_away")
m_winloss <- glm(df_2024$home_win ~ X_winloss, family = binomial(link = "logit"))

# Extract team strengths from the win-loss model (excluding intercept)
team_strengths_winloss <- coef(m_winloss)[-1]  # Remove home advantage intercept

# Get team names
teams <- unique(c(df_2024$team_home, df_2024$team_away))

# Create named vector
team_strengths_winloss_named <- setNames(team_strengths_winloss, teams)

# Replace NAs with 0
team_strengths_winloss_named[is.na(team_strengths_winloss_named)] <- 0

# Normalize so Washington Commanders' strength = 0
washington_strength <- team_strengths_winloss_named["Washington Commanders"]
normalized_winloss_strengths <- team_strengths_winloss_named - washington_strength

# Normalize strengths so that the sum is 0
mean_strength <- mean(team_strengths_winloss_named)
normalized_winloss_strengths_zero_sum <- team_strengths_winloss_named - mean_strength

# Compute probabilities for win-loss model
win_probabilities_winloss <- 1 / (1 + exp(-normalized_winloss_strengths_zero_sum))

# --- Margin-of-Victory (MOV) Model ---
X_mov <- construct_model_matrix(df_2024, homeCol = "team_home", awayCol = "team_away")
m_mov <- lm(df_2024$mov ~ X_mov)  # Linear model for MOV

# Extract team strengths from MOV model
team_strengths_mov <- coef(m_mov)[-1]  # Remove intercept (home advantage)

# Create named vector
team_strengths_mov_named <- setNames(team_strengths_mov, teams)

# Replace NAs with 0
team_strengths_mov_named[is.na(team_strengths_mov_named)] <- 0

# Normalize so sum of strengths is zero
mean_mov_strength <- mean(team_strengths_mov_named)
normalized_mov_strengths <- team_strengths_mov_named - mean_mov_strength

# Compute probabilities for MOV model
win_probabilities_mov <- 1 / (1 + exp(-normalized_mov_strengths))

# --- Create Data Frame for Plot ---
comparison_df <- data.frame(
  Team = names(win_probabilities_mov),
  MOV_Prob = win_probabilities_mov,
  WinLoss_Prob = win_probabilities_winloss[names(win_probabilities_mov)]
)

dev.new()
print(
  ggplot(comparison_df, aes(x = MOV_Prob, y = WinLoss_Prob)) +
    geom_point(color = "blue", size = 3, alpha = 0.7) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "red") +  # Reference line
    labs(
      title = "Comparison of Win Probabilities: MOV vs. Win-Loss Model",
      x = "Margin of Victory Model Probability",
      y = "Win-Loss Model Probability"
    ) +
    theme_minimal()
)
