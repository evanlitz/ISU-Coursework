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
X <- matrix(0, nrow = nrow(df), ncol = length(players) - 1) # drop one player
colnames(X) <- players[-length(players)] # keep names, exclude last

# Map player names to columns
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

# 4. Fit model (no intercept, one player dropped)
model <- lm(df$margin ~ X + 0)

# 5. Reconstruct full vector of strengths, assume last player = 0
strengths <- coef(model)
strengths_full <- c(strengths, setNames(0, players[length(players)]))
names(strengths_full)[length(players)] <- players[length(players)]

# 6. Center to have average strength 0
strengths_full <- strengths_full - mean(strengths_full)

# 7. Output
strengths_df <- tibble(
  player = names(strengths_full),
  strength = as.numeric(strengths_full)
) |> arrange(desc(strength))

print(strengths_df)

# 8. Q1: Strength for Jarad
cat("Estimated strength for Jarad:", strengths_full["Jarad"], "\n")
