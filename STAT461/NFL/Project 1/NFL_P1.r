# Load the dataset
df <- read.csv("nfl.csv", stringsAsFactors = FALSE)

# Filter for 2024 season
df_2024 <- df %>% filter(schedule_season == 2024)

# Get unique teams from home and away columns
unique_teams <- unique(c(df_2024$team_home, df_2024$team_away))

# Count unique teams
num_unique_teams <- length(unique_teams)

# Print the result
print(paste("Number of unique teams in 2024 season:", num_unique_teams))