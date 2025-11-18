# Load necessary library
library(dplyr)

# Read the CSV file
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

df_2024 <- df %>%
  filter(schedule_season == 2024 & !schedule_week %in% c("Wildcard", "Division", "Conference", "Superbowl"))

# Ensure required columns exist
if (!all(c("team_home", "team_away", "score_home", "score_away") %in% colnames(df_2024))) {
  stop("Required columns not found in the dataset.")
}

# Create margin of victory variable
df_2024 <- df_2024 %>%
  mutate(margin_victory = score_home - score_away,
         team_home = as.factor(team_home),
         team_away = as.factor(team_away),
         home_field = 1)  # Home field indicator (always 1 for home team)

# Fit the linear model (estimating team strengths & home field advantage)
model_2024 <- lm(margin_victory ~ team_home + team_away + home_field, data = df_2024)

# Print model summary
print(summary(model_2024))

# Extract the estimated standard deviation (Residual Standard Error)
estimated_sd_2024 <- summary(model_2024)$sigma
print(paste("Estimated Standard Deviation (Residual Standard Error):", round(estimated_sd_2024, 4)))

# Alternative way to calculate standard deviation of residuals
sd_residuals_2024 <- sd(residuals(model_2024))
print(paste("Standard Deviation of Residuals:", round(sd_residuals_2024, 4)))
