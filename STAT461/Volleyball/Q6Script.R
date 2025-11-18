library(tidyverse)

# 1. Load and clean data
df <- read_csv("data/king_of_the_beach_volleyball.csv", 
               col_names = c("Match", "P1_A", "P1_B", "P2_A", "P2_B", "Score1", "Score2"),
               skip = 1) |>
  mutate(across(c(P1_A, P1_B, P2_A, P2_B), str_trim)) |>
  mutate(margin = Score1 - Score2)

# 2. Get unique player names
players <- sort(unique(c(df$P1_A, df$P1_B, df$P2_A, df$P2_B)))

# 3. Create design matrix
X <- matrix(0, nrow = nrow(df), ncol = length(players) - 1)
colnames(X) <- players[-length(players)]

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

# 4. Fit the model
model <- lm(df$margin ~ X + 0)

# 5. Reconstruct full strength vector
strengths <- coef(model)
strengths_full <- c(strengths, setNames(0, players[length(players)]))
names(strengths_full) <- players
strengths_full <- strengths_full - mean(strengths_full)

# 6. Compute margin and win prob: Jarad vs Dan, teammates cancel
margin_diff <- strengths_full["Jarad"] - strengths_full["Dan"]
sigma <- summary(model)$sigma

# Use raw sigma (model built on full 2v2 results)
p_jarad_wins <- pnorm(margin_diff / sigma)

cat("Probability Jarad wins against Dan with equal teammates:", round(p_jarad_wins, 4), "\n")
