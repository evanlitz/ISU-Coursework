# Load necessary libraries
library(tidyverse)

# ---- Part 1: Load Margin of Victory Model Strengths ----
source("Q1-2Script.R")  # defines strengths_df

# ---- Clean player names in strengths_df ----
strengths_df <- strengths_df %>%
  mutate(player = str_replace(player, "^X+", "") %>% str_trim())

# ---- Part 2: Load Offense-Defense Model Ratings ----
source("Q7-8Script.R")  # defines offdef_df

# ---- Part 3: Merge and Compute Correlation ----
merged_df <- strengths_df %>%
  inner_join(offdef_df, by = "player")

# Check merged result
print("Merged DataFrame:")
print(merged_df)

# Clean NA values
clean_df <- merged_df %>%
  filter(!is.na(strength) & !is.na(total))

# Compute correlation
if (nrow(clean_df) > 1) {
  cor_strengths <- cor(clean_df$strength, clean_df$total)
  cat("✅ Correlation between margin of victory strength and offense-defense total rating:", round(cor_strengths, 3), "\n")
} else {
  cat("❌ Not enough data to compute correlation.\n")
}
