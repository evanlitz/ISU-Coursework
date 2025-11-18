# Load necessary libraries
library(dplyr)

# Read the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Compute Margin of Victory
df_2024 <- df_2024 %>%
  mutate(margin_victory = score_home - score_away)

# Compute Home Field Advantage (HFA)
home_field_advantage <- mean(df_2024$margin_victory, na.rm = TRUE)

# Get estimated team strengths
vikings_strength <- team_strengths["Minnesota Vikings"]
bears_strength <- team_strengths["Chicago Bears"]

# Calculate expected point difference (Vikings @ Bears)
expected_margin_away <- vikings_strength - bears_strength - home_field_advantage

# Compute standard deviation of residuals
residual_sd <- sd(df_2024$margin_victory - (team_strengths[df_2024$team_home] - team_strengths[df_2024$team_away] + home_field_advantage), na.rm = TRUE)

# Compute probability Vikings win at Soldier Field (Point Difference > 0)
prob_vikings_win_away <- 1 - pnorm(0, mean = expected_margin_away, sd = residual_sd)

# Print result
print(paste("Probability Vikings beat Bears at Soldier Field:", round(prob_vikings_win_away, 6)))
