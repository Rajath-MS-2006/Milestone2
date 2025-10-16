import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load analyzed CSV
df = pd.read_csv("../data/analyzed_ai_market_data.csv")

# Set Seaborn style
sns.set(style="whitegrid")

# Plot sentiment distribution by platform
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="label", hue="platform", palette="Set2")
plt.title("Sentiment Distribution by Platform")
plt.xlabel("Sentiment Label")
plt.ylabel("Number of Posts/Articles")
plt.legend(title="Platform")
plt.tight_layout()
plt.show()
