import pandas as pd

df = pd.read_csv("data/sleep_study_1000.csv")

# Encode categorical columns numerically for correlation
df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})
df["SmokingStatus"] = df["SmokingStatus"].map({"Yes": 1, "No": 0})

features = [
    "Age", "Gender", "SleepDuration",
    "REMSleepPercentage", "DeepSleepPercentage", "LightSleepPercentage",
    "Awakenings", "CaffeineConsumption", "AlcoholConsumption",
    "SmokingStatus", "ExerciseFrequency"
]

corr = df[features].corrwith(df["SleepEfficiency"]).sort_values(key=abs, ascending=False)

print(f"{'Feature':<25} {'Correlation':>12}")
print("-" * 38)
for feature, val in corr.items():
    print(f"{feature:<25} {val:>12.4f}")
