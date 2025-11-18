# Load necessary libraries
library(tidyverse)
library(DT)
library(BradleyTerry2)

# Load the dataset
df <- read.csv("C:/Users/evan/OneDrive/CODE/STAT 461/NFL/nfl.csv", stringsAsFactors = FALSE)

# Filter for the 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

print(dim(df_2024))  # Ensure it's not empty
print(head(df_2024))  # View the first few rows

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

print(dim(X))  # Should be (num_games, num_teams)
print(table(X))  # Should contain only -1, 0, and 1

m <- glm(df_2024$home_win ~ X, family = binomial(link = "logit"))

summary(m)

home_advantage <- summary(m)$coefficients[1, ]  # Intercept represents home advantage

print(home_advantage)


