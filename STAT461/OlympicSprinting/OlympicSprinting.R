# Load required libraries
library(ggplot2)
library(tidyr)

# Create the dataset
data <- data.frame(
    Year = c(1900, 1904, 1908, 1912, 1920, 1924, 1928, 1932, 1936, 
             1948, 1952, 1956, 1960, 1964, 1968, 1972, 1976, 1980, 
             1984, 1988, 1992, 1996, 2000, 2004),
    
    Men = c(11.00, 11.00, 10.80, 10.80, 10.80, 10.60, 10.80, 
            10.30, 10.30, 10.30, 10.40, 10.50, 10.20, 10.00, 9.95, 10.14, 
            10.06, 10.25, 9.99, 9.92, 9.96, 9.84, 9.87, 9.85),
    
    Women = c(NA, NA, NA, NA, NA, NA, 12.20, 11.90, 11.50, 
              11.90, 11.50, 11.50, 11.00, 11.40, 11.08, 11.07, 11.08, 11.06, 
              10.97, 10.54, 10.82, 10.94, 10.75, 10.93)
)

# Reshape the dataset into long format
data_long <- pivot_longer(data, cols = c("Men", "Women"), 
                          names_to = "Gender", values_to = "Time", 
                          values_drop_na = TRUE)  # Remove NA values

# Convert Gender to a factor (categorical variable)
data_long$Gender <- factor(data_long$Gender, levels = c("Men", "Women"))

# Fit a multiple regression model: Time ~ Year + Gender
model_combined <- lm(Time ~ Year + Gender, data = data_long)

# Display summary of the model
summary(model_combined)

# Print estimated coefficients
cat("\nCombined Regression Model:\n")
cat("Estimated Intercept:", coef(model_combined)[1], "\n")
cat("Estimated Slope for Year:", coef(model_combined)[2], "\n")
cat("Estimated Coefficient for Gender (Women vs Men):", coef(model_combined)[3], "\n")

# Extract coefficients
intercept <- coef(model_combined)[1]  # β0
slope_year <- coef(model_combined)[2]  # β1 (change per year)
gender_diff <- coef(model_combined)[3]  # β2 (difference between men & women)

# Question 8: Estimated difference in mean winning times (Men vs Women)
cat("\nQuestion 8: Estimated Difference in Mean Winning Times (Men vs Women):", gender_diff, "\n")

# Question 9: Estimated change in winning time per additional year
cat("\nQuestion 9: Estimated Change in Winning Time per Year:", slope_year, "\n")

# Question 10: Predict Women's Winning Time for 1944
predicted_women_1944 <- intercept + slope_year * 1944 + gender_diff
cat("\nQuestion 10: Predicted Women's Winning Time in 1944:", predicted_women_1944, "\n")

# Plot data with regression lines for both genders
ggplot(data_long, aes(x = Year, y = Time, color = Gender)) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = FALSE) +
  labs(title = "Regression of 100m Winning Times by Gender",
       x = "Year",
       y = "Winning Time (seconds)") +
  theme_minimal()