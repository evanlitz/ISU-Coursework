# Load necessary libraries
library(dplyr)

# Read the CSV file
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

# Create margin of victory variable
df_2024 <- df_2024 %>%
  mutate(
    margin_victory = score_home - score_away,
    team_home = as.factor(team_home),
    team_away = as.factor(team_away)
  )

# Construct the model matrix
construct_model_matrix <- function(data) {
  n_games <- nrow(data)
  teams <- unique(c(levels(data$team_home), levels(data$team_away)))
  n_teams <- length(teams)
  
  model_matrix <- matrix(0, nrow = n_games, ncol = n_teams)
  colnames(model_matrix) <- teams
  
  for (i in 1:n_games) {
    model_matrix[i, as.character(data$team_home[i])] <-  1
    model_matrix[i, as.character(data$team_away[i])] <- -1
  }
  
  return(model_matrix)
}

X_2024 <- construct_model_matrix(df_2024)

# Fit the linear model
model_2024 <- lm(df_2024$margin_victory ~ X_2024 + 1)

# Extract the estimated home-field advantage
home_field_advantage_2024 <- coef(model_2024)[1]
print(paste("Estimated Home-Field Advantage for 2024:", round(home_field_advantage_2024, 4)))
