library(tidyverse)

# Load and clean data
volley <- read_csv("data/king_of_the_beach_volleyball.csv", show_col_types = FALSE) |> 
  rename(
    player1_team1 = `Team1...2`,
    player2_team1 = `Team1...3`,
    player1_team2 = `Team2...4`,
    player2_team2 = `Team2...5`,
    team1_score   = Score1,
    team2_score   = Score2
  ) |> 
  mutate(
    margin = team1_score - team2_score
  )

# Get unique players
players <- unique(c(
  volley$player1_team1,
  volley$player2_team1,
  volley$player1_team2,
  volley$player2_team2
)) |> sort()

# Make player columns factors with fixed levels
volley <- volley |> 
  mutate(across(starts_with("player"), ~factor(., levels = players)))

# Build model matrix for margin: +1 for team1, -1 for team2
X_margin <- matrix(0, nrow = nrow(volley), ncol = length(players))
colnames(X_margin) <- players

for (i in 1:nrow(volley)) {
  X_margin[i, as.character(volley$player1_team1[i])] <-  1
  X_margin[i, as.character(volley$player2_team1[i])] <-  1
  X_margin[i, as.character(volley$player1_team2[i])] <- -1
  X_margin[i, as.character(volley$player2_team2[i])] <- -1
}

# Fit margin-of-victory model
mov_model <- lm(volley$margin ~ 0 + X_margin)
mov_coef <- coef(mov_model)
mov_coef[is.na(mov_coef)] <- 0
mov_coef <- mov_coef - mean(mov_coef)  # center player ratings

# Use index to pull player ratings safely
dan_idx   <- which(colnames(X_margin) == "Dan")
jarad_idx <- which(colnames(X_margin) == "Jarad")

rating_dan   <- mov_coef[dan_idx]
rating_jarad <- mov_coef[jarad_idx]

# Compute expected margin: Dan & Jarad vs average players (rating 0)
expected_margin <- rating_dan + rating_jarad

# Use residual SD from MOV model
resid_sd <- sd(resid(mov_model))

# Final probability of winning one set (margin > 0)
p_set <- 1 - pnorm(0, mean = expected_margin, sd = resid_sd)

# Match win probability: win 2 out of 3 sets
p_match <- p_set^2 * (3 - 2 * p_set)

# Output match win probability
cat("Expected Margin of Victory:", round(expected_margin, 3), "\n")
cat("Probability of Winning One Set:", round(p_set, 6), "\n")
cat("Probability of Winning the Match:", round(p_match, 6), "\n")
