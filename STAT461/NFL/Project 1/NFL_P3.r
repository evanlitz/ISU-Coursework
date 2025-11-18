library(dplyr)

df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

vikings_home_wins <- sum(df_2024$team_home == "Minnesota Vikings" & df_2024$score_home > df_2024$score_away, na.rm = TRUE)
vikings_away_wins <- sum(df_2024$team_away == "Minnesota Vikings" & df_2024$score_away > df_2024$score_home, na.rm = TRUE)

total_vikings_wins <- vikings_home_wins + vikings_away_wins

print(paste("Total wins by Minnesota Vikings:", total_vikings_wins))