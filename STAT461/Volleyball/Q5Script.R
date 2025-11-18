library(tidyverse)

# 1. Load and clean data
df <- read_csv("data/king_of_the_beach_volleyball.csv", 
               col_names = c("Match", "P1_A", "P1_B", "P2_A", "P2_B", "Score1", "Score2"),
               skip = 1) |>
  mutate(across(c(P1_A, P1_B, P2_A, P2_B), str_trim)) |>
  mutate(margin = Score1 - Score2)

# 2. Get unique player names
players <- sort(unique(c(df$P1_A, df$P1_B, df$P2_A, df$P2_B)))

# 3. Create design matrix (drop one player to avoid multicollinearity)
X <- matrix(0, nrow = nrow(df), ncol = length(players) - 1)
colnames(X) <- players[-length(players)]  # Drop last player

for (i in 1:nrow(df)) {
  for (p in c(df$P1_A[i], df$P1_B[i])) {
    if (p != players[length(players)]) {
      X[i, p] <- X[i, p] + 1
    }
  }
  for (p in c(df$P2_A[i], df$P2_B[i])) {
    if (p != players[length(players)]) {
      X[i, p] <- X[i, p] - 1
    }
  }
}

# 4. Fit model
model <- lm(df$margin ~ X + 0)

# 5. Reconstruct full strength vector
strengths <- coef(model)
strengths_full <- c(strengths, setNames(0, players[length(players)]))
names(strengths_full) <- players
strengths_full <- strengths_full - mean(strengths_full)

# 6. Compute expected margin & residual SD
expected_margin <- strengths_full["Dan"] + strengths_full["Jarad"]
sigma <- summary(model)$sigma

# 7. Win probability for a single set
p_set <- pnorm(expected_margin / sigma)

# 8. Match win probability (best-of-3): WW, WLW, LWW
p_match <- p_set^2 + 2 * p_set^2 * (1 - p_set)

cat("Probability Dan & Jarad win a best-of-3 match vs. average opponents:", round(p_match, 4), "\n")
