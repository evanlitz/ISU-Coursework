library(dplyr)

df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

vikings_home_losses <- sum(df_2024$team_home == "Minnesota Vikings" & df_2024$score_home < df_2024$score_away, na.rm = TRUE)
vikings_away_losses <- sum(df_2024$team_away == "Minnesota Vikings" & df_2024$score_away < df_2024$score_home, na.rm = TRUE)

total_vikings_losses <- vikings_home_losses + vikings_away_losses

print(paste("Total losses by Minnesota Vikings:", total_vikings_losses))