# Build offense matrix: each row has 1 for players on scoring team
X_home <- matrix(0, nrow = nrow(volley), ncol = length(players))
X_away <- matrix(0, nrow = nrow(volley), ncol = length(players))
colnames(X_home) <- colnames(X_away) <- players

for (i in 1:nrow(volley)) {
  X_home[i, as.character(volley$player1_team1[i])] <- 1
  X_home[i, as.character(volley$player2_team1[i])] <- 1
  X_away[i, as.character(volley$player1_team2[i])] <- 1
  X_away[i, as.character(volley$player2_team2[i])] <- 1
}

# Build offense and defense matrices
X_offense <- rbind(X_home, X_away)
X_defense <- rbind(X_away, X_home)

# Response vector: all scores
Y <- c(volley$team1_score, volley$team2_score)

# Fit individual offense-defense model
X_individual <- cbind(X_offense, -X_defense)
off_def_model <- lm(Y ~ 0 + X_individual)

# Extract and center ratings
ratings <- coef(off_def_model)
ratings[is.na(ratings)] <- 0
ratings <- ratings - mean(ratings)

offense <- ratings[1:length(players)]
defense <- ratings[(length(players)+1):(2*length(players))]

# Combine results
offdef_df <- tibble(
  player = players,
  offense = offense,
  defense = defense,
  total = offense + defense
) |> arrange(desc(total))

# Output Jarad's offensive rating
jarad_off <- offdef_df |> filter(player == "Jarad") |> pull(offense)
print(paste("Jarad's offensive rating is:", round(jarad_off, 3)))

jarad_def <- offdef_df |> filter(player == "Jarad") |> pull(defense)
print(paste("Jarad's defensive rating is:", round(jarad_def, 3)))