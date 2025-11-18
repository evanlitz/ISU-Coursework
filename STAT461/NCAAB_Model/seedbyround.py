import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load and clean data
df = pd.read_csv("seedbyround.csv")
df = df.drop(columns=["R64"])  # Remove meaningless constant column
df.set_index("Seed #", inplace=True)

# Convert to percentage of 88 possible appearances
df_percent = df / 88 * 100

# Set up the plot
plt.figure(figsize=(10, 6))
sns.set(font_scale=1.1, style="whitegrid")

# Create heatmap with percent symbols in every cell
sns.heatmap(
    df_percent,
    annot=df_percent.round(0).astype(int).astype(str) + '%',
    fmt="",  # Let annot control text
    cmap="YlOrBr",  # You can change this to "crest", "flare", etc.
    annot_kws={"fontweight": "bold", "fontsize": 10},
    cbar_kws={"label": "% of Times Advanced"}
)

# Apply bold formatting to labels
plt.title("Seed Advancement Rates by Round (2003–2024)", fontweight='bold', fontsize=14)
plt.xlabel("Round", fontweight='bold', fontsize=12)
plt.ylabel("Seed #", fontweight='bold', fontsize=12)
plt.xticks(fontweight='bold')
plt.yticks(fontweight='bold')

# Layout
plt.tight_layout()
plt.show()
