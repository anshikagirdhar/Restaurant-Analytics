"""
zomato_01_clean_data.py
--------------------------
Zomato Restaurant Sales & Performance Analysis - DATA CLEANING

DATASET: Zomato Bangalore Restaurants (Kaggle, uploaded by Himanshu Poddar)
https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants
51,717 rows x 17 columns. Real, scraped restaurant listings from Zomato's
Bangalore listings (not order/transaction data) - one snapshot in time,
no date field, no customer IDs. This is why the project scope is
"Sales & Performance Analysis" rather than a customer-churn project:
this dataset genuinely cannot support repeat-customer/churn analysis
(confirmed by inspecting every column - no customer or order identifier
exists anywhere in the file, including inside the free-text reviews_list
field). That's a real, structural limitation of the source data, not a
shortcut taken here.

IMPORTANT ON "REVENUE": this dataset has no sales/revenue/order-count
field. Two real fields are used as clearly-labeled proxies throughout
this project:
  - `votes`      = number of ratings a restaurant has received on Zomato
                   (used as a popularity/engagement proxy, NOT an order count)
  - `approx_cost_for_two` = menu pricing for two people (a real field,
                   used as-is - it is literally what it says, not a
                   computed "average order value")
Nothing in this project claims a specific revenue or order-volume number
that isn't actually in the source data.
"""

import pandas as pd
import numpy as np

RAW_PATH = "/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_raw.csv"
CLEAN_PATH = "/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_clean.csv"

df = pd.read_csv(RAW_PATH, low_memory=False)
print("Raw shape:", df.shape)

# ---------------------------------------------------------------
# 1. Drop columns not used in this analysis (heavy free-text / not needed)
# ---------------------------------------------------------------
df = df.drop(columns=["url", "phone", "reviews_list", "menu_item", "dish_liked"])

# ---------------------------------------------------------------
# 2. Rename columns to clean, code-friendly names
# ---------------------------------------------------------------
df = df.rename(columns={
    "approx_cost(for two people)": "approx_cost_for_two",
    "listed_in(type)": "listing_type",
    "listed_in(city)": "area",
})

# ---------------------------------------------------------------
# 3. Parse `rate` ("4.1/5" -> 4.1). "NEW" (newly listed, no rating yet)
#    and "-" (no rating) both become NaN - they are genuinely missing,
#    not zero.
# ---------------------------------------------------------------
def parse_rate(x):
    x = str(x).strip()
    if x in ("NEW", "-", "nan"):
        return np.nan
    try:
        return float(x.split("/")[0])
    except (ValueError, IndexError):
        return np.nan

df["rating"] = df["rate"].apply(parse_rate)
df = df.drop(columns=["rate"])

# ---------------------------------------------------------------
# 4. Parse `approx_cost_for_two` ("1,200" -> 1200.0)
# ---------------------------------------------------------------
df["approx_cost_for_two"] = (
    df["approx_cost_for_two"].astype(str).str.replace(",", "", regex=False)
)
df["approx_cost_for_two"] = pd.to_numeric(df["approx_cost_for_two"], errors="coerce")

# ---------------------------------------------------------------
# 5. online_order / book_table -> boolean
# ---------------------------------------------------------------
df["online_order"] = df["online_order"].map({"Yes": True, "No": False})
df["book_table"] = df["book_table"].map({"Yes": True, "No": False})

# ---------------------------------------------------------------
# 6. Clean text fields (whitespace, casing consistency)
# ---------------------------------------------------------------
for col in ["name", "location", "rest_type", "cuisines", "area", "listing_type"]:
    df[col] = df[col].astype(str).str.strip()
    df.loc[df[col].isin(["nan", ""]), col] = np.nan

# cuisines is a comma-separated list ("North Indian, Chinese") - keep the
# first-listed cuisine as the restaurant's PRIMARY cuisine for grouping,
# since a restaurant can list many
df["primary_cuisine"] = df["cuisines"].apply(
    lambda x: x.split(",")[0].strip() if pd.notna(x) else np.nan
)

# ---------------------------------------------------------------
# 7. Handle remaining missing values (documented, not silently dropped)
# ---------------------------------------------------------------
before = len(df)
print("\nMissing values before final handling:\n", df.isna().sum())

# rows with no name/area/listing_type are not usable rows at all - drop (should be ~0)
df = df.dropna(subset=["name", "area", "listing_type"])

# cost and rating: leave as NaN (genuinely unknown), analyses will exclude
# nulls explicitly rather than imputing a restaurant's price or rating
print(f"\nDropped {before - len(df)} unusable rows (missing name/area/listing_type)")

# ---------------------------------------------------------------
# 8. Duplicate check
# ---------------------------------------------------------------
exact_dupes = df.duplicated().sum()
print(f"Exact duplicate rows: {exact_dupes}")
df = df.drop_duplicates()

# note: the same physical restaurant legitimately appears multiple times
# (once per listing_type: Delivery, Dine-out, Cafes, etc, and sometimes
# per area if it has multiple branches) - this is NOT a duplicate to be
# removed, it reflects how Zomato itself lists a restaurant across
# categories. Row-level analyses (by listing_type, by area) use the full
# table; restaurant-level analyses (e.g. "how many unique restaurants")
# explicitly de-duplicate on (name, address) where relevant.

# ---------------------------------------------------------------
# 9. Outlier check on cost (sanity, not removal - real menu prices vary a lot)
# ---------------------------------------------------------------
print("\napprox_cost_for_two describe:\n", df["approx_cost_for_two"].describe())
print("\nrating describe:\n", df["rating"].describe())

df.to_csv(CLEAN_PATH, index=False)
print(f"\nSaved cleaned dataset: {df.shape} -> zomato_clean.csv")
print(df.head(5).to_string())
