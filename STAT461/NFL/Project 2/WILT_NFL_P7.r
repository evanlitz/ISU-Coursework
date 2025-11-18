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
) %>%
  mutate(
    names = factor(names, levels = names[order(strength)])
  ) %>%
  arrange(desc(strength))

# Adjust strength so that Washington Commanders' strength is set to 0
washington_strength <- teams$strength[teams$names == "Washington Commanders"]
teams <- teams %>%
  mutate(adjusted_strength = strength - washington_strength)

# Find the adjusted strength of the Minnesota Vikings
vikings_strength <- teams$adjusted_strength[teams$names == "Minnesota Vikings"]

# Display team strengths
datatable(teams, filter = "top")

# Visualize team strengths
ggplot(teams, aes(x = adjusted_strength, y = names)) +
  geom_bar(stat = "identity") +
  labs(x = 'Adjusted Strength', y = 'Team', title = '2022 NFL Adjusted Team Strengths')

# Output the estimated strength of the Minnesota Vikings
cat("Estimated strength of the Minnesota Vikings (if Washington Commanders' strength is 0):", vikings_strength, "\n")
