"""
zomato_02_eda.py
-------------------
Light EDA (matching Blinkit-project depth: a handful of charts, not
exhaustive exploration).
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
df = pd.read_csv("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_clean.csv")
OUT = "/sessions/peaceful-youthful-maxwell/mnt/outputs/"

# 1. Cost-for-two distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["approx_cost_for_two"].dropna(), bins=40, color="#c1440e", kde=True)
plt.title("Distribution of Approx. Cost for Two")
plt.xlabel("Cost for Two (Rs.)"); plt.ylabel("Number of Listings")
plt.xlim(0, 3000)
plt.tight_layout(); plt.savefig(OUT + "zomato_chart1_cost_distribution.png", dpi=140); plt.close()

# 2. Rating distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["rating"].dropna(), bins=25, color="#2c6e91", kde=True)
plt.title("Distribution of Restaurant Ratings")
plt.xlabel("Rating (out of 5)"); plt.ylabel("Number of Listings")
plt.tight_layout(); plt.savefig(OUT + "zomato_chart2_rating_distribution.png", dpi=140); plt.close()

# 3. Top 10 cuisines by number of listings
top_cuisines = df["primary_cuisine"].value_counts().head(10)
plt.figure(figsize=(9, 5))
sns.barplot(x=top_cuisines.values, y=top_cuisines.index, hue=top_cuisines.index, palette="crest", legend=False)
plt.title("Top 10 Primary Cuisines by Number of Listings")
plt.xlabel("Number of Listings"); plt.ylabel("")
plt.tight_layout(); plt.savefig(OUT + "zomato_chart3_top_cuisines.png", dpi=140); plt.close()

# 4. Average cost-for-two by top 10 areas (by listing count)
top_areas = df["area"].value_counts().head(10).index
area_cost = df[df["area"].isin(top_areas)].groupby("area")["approx_cost_for_two"].mean().sort_values(ascending=False)
plt.figure(figsize=(9, 5))
sns.barplot(x=area_cost.values, y=area_cost.index, hue=area_cost.index, palette="mako", legend=False)
plt.title("Average Cost for Two by Area (Top 10 Areas by Listing Volume)")
plt.xlabel("Avg Cost for Two (Rs.)"); plt.ylabel("")
plt.tight_layout(); plt.savefig(OUT + "zomato_chart4_avg_cost_by_area.png", dpi=140); plt.close()

# 5. Online order availability vs average rating
plt.figure(figsize=(6, 5))
sns.boxplot(data=df.dropna(subset=["rating"]), x="online_order", y="rating", hue="online_order",
            palette={True: "#3ecf8e", False: "#e05656"}, legend=False)
plt.title("Rating Distribution: Online Order Available vs. Not")
plt.xlabel("Online Order Available"); plt.ylabel("Rating")
plt.tight_layout(); plt.savefig(OUT + "zomato_chart5_online_order_vs_rating.png", dpi=140); plt.close()

# 6. Votes vs Rating (popularity proxy vs rating relationship)
plt.figure(figsize=(8, 6))
sample = df.dropna(subset=["rating", "votes"])
plt.scatter(sample["votes"], sample["rating"], alpha=0.15, s=12, color="#4f8ff7")
plt.xscale("log")
plt.title("Votes (Popularity Proxy) vs. Rating")
plt.xlabel("Votes (log scale)"); plt.ylabel("Rating")
plt.tight_layout(); plt.savefig(OUT + "zomato_chart6_votes_vs_rating.png", dpi=140); plt.close()

print("Saved 6 EDA charts.")
print("\nTop 10 cuisines:\n", top_cuisines)
print("\nAvg cost by top 10 areas:\n", area_cost)
print("\nOnline order rating means:\n", df.groupby("online_order")["rating"].mean())
print("\nVotes-rating correlation:", round(sample["votes"].corr(sample["rating"]), 3))
