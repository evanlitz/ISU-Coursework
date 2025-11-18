# Load required packages
library(tidyverse)
library(MASS)    # polr: ordinal logistic regression model
library(ordinal) # clm: ordinal logistic regression model
library(DT)

# Load the dataset
df <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter for the 2022 season and remove playoff games
df_2022 <- df %>%
  filter(schedule_season == 2022 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Create game outcome as an ordered factor (Loss < Tie < Win)
df_2022 <- df_2022 %>%
  mutate(
    home_result = case_when(
      score_home > score_away ~ "Win",
      score_home == score_away ~ "Tie",
      score_home < score_away ~ "Loss"
    ),
    home_result = factor(home_result, levels = c("Loss", "Tie", "Win"), ordered = TRUE),
    team_home = factor(team_home),
    team_away = factor(team_away)
  )

# Construct the model matrix
construct_model_matrix <- function(d, homeCol = "team_home", awayCol = "team_away") {
  n_games <- nrow(d)
  n_teams <- length(unique(unlist(d[, c(homeCol, awayCol)])))
  
  m <- matrix(0, nrow = n_games, ncol = n_teams)
  
  for (g in 1:n_games) {
    m[g, as.numeric(d[g, homeCol])] <-  1
    m[g, as.numeric(d[g, awayCol])] <- -1
  }
  
  return(m)
}

X <- construct_model_matrix(df_2022, "team_home", "team_away")

# Fit ordinal logistic regression model
m <- polr(df_2022$home_result ~ X, Hess = TRUE)

# Print model summary
summary(m)

# Extract threshold estimates
thresholds <- m$zeta

# Output the estimated value of the loss-tie threshold
cat("Estimated Loss-Tie Threshold:", thresholds[1], "\n")

# Compute team strengths
teams <- data.frame(
  names    = levels(df_2022$team_home),
  strength = c(coef(m), 0)  # The last team gets strength = 0 for identifiability
)

# Adjust strengths so that the sum of all team strengths equals zero
mean_strength <- mean(teams$strength)  # Compute the mean
teams <- teams %>%
  mutate(centered_strength = strength - mean_strength)  # Center strengths

# Find the centered strength of the Minnesota Vikings and Chicago Bears
vikings_strength <- teams$centered_strength[teams$names == "Minnesota Vikings"]
bears_strength <- teams$centered_strength[teams$names == "Chicago Bears"]

# Compute home-field advantage (this is an approximation)
home_field_advantage <- mean(teams$centered_strength)

# Compute strength difference (Vikings are away, so we subtract H)
strength_diff_soldier_field <- vikings_strength - bears_strength - home_field_advantage

# Function to compute win, tie, and loss probabilities
calculate_ordinal_probabilities <- function(mean, zeta) {
  p <- c(
    plogis(zeta[1] - mean),                  # P(Loss)
    diff(plogis(zeta - mean)),               # P(Tie)
    plogis(zeta[2] - mean, lower.tail = FALSE) # P(Win)
  )
  
  names(p) <- c("Loss", "Tie", "Win")
  
  return(p)
}

# Compute probability of Vikings winning AT Soldier Field
vikings_vs_bears_soldier_probs <- calculate_ordinal_probabilities(strength_diff_soldier_field, thresholds)

# Output probabilities
cat("Probability the Vikings win vs Bears at Soldier Field:", vikings_vs_bears_soldier_probs["Win"], "\n")
cat("Probability the game ends in a tie:", vikings_vs_bears_soldier_probs["Tie"], "\n")
cat("Probability the Bears win:", vikings_vs_bears_soldier_probs["Loss"], "\n")

# Display team strengths
datatable(teams, filter = "top")

# Visualize adjusted team strengths
ggplot(teams, aes(x = centered_strength, y = names)) +
  geom_bar(stat = "identity") +
  labs(x = 'Centered Strength', y = 'Team', title = '2022 NFL Team Strengths (Sum = 0)')
