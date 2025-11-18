library(dplyr)

df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Count total games in 2024 season
total_games_2024 <- nrow(df_2024)

# Print result
print(paste("Total number of games in 2024 season:", total_games_2024))