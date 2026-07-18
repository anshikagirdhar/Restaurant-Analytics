# Zomato Restaurant Analytics 

## Overview
This project analyzes 51,632 real Zomato restaurant listings from Bangalore (8,792 unique restaurants across 30+ city areas) to uncover business insights around pricing, ratings, cuisine, and restaurant format — and builds a Random Forest classifier to predict whether a restaurant is likely to be highly rated.

**Dataset:** [Zomato Bangalore Restaurants](https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants) (Kaggle) — 51,717 raw rows × 17 columns, a scraped snapshot of Zomato listings (no date field, no customer/order IDs).


## 📂 Project Structure
```
├── zomato_01_clean_data.py             # Data cleaning & feature parsing
├── zomato_02_eda.py                    # Exploratory data analysis + 6 charts
├── zomato_03_load_sqlite.py            # Loads cleaned data into SQLite
├── zomato_04_queries.sql               # 10 business-insight SQL queries
├── zomato_run_queries.py               # Runs the SQL queries, saves results
├── zomato_05_random_forest.py          # Random Forest + Logistic Regression baseline
├── zomato_clean.csv                    # Cleaned dataset
├── zomato.db                           # SQLite database (table: restaurants)
├── zomato_query_results.txt            # Output of all 10 SQL queries
├── zomato_feature_importance.csv       # Random Forest feature importances
├── zomato_model_metrics.csv            # Model comparison metrics
├── zomato_test_predictions.csv         # Test-set predictions
├── zomato_dashboard.html               # Power BI–style interactive dashboard
├── zomato_chart1_cost_distribution.png
├── zomato_chart2_rating_distribution.png
├── zomato_chart3_top_cuisines.png
├── zomato_chart4_avg_cost_by_area.png
├── zomato_chart5_online_order_vs_rating.png
├── zomato_chart6_votes_vs_rating.png
└── README.md
```

## 🔑 Key Steps

**1. Data Cleaning (`zomato_01_clean_data.py`)**
- Parsed `rate` field ("4.1/5" → 4.1), treating "NEW" and "-" as genuinely missing (not zero)
- Cleaned cost field (removed commas, cast to numeric)
- Converted `online_order`/`book_table` to booleans
- Extracted `primary_cuisine` from the comma-separated cuisines list
- Documented (not silently dropped) missing values; de-duplicated only exact duplicate rows — legitimate repeat listings (same restaurant across multiple listing types/branches) were preserved

**2. Exploratory Data Analysis (`zomato_02_eda.py`)**
- Cost-for-two and rating distributions
- Top 10 cuisines by listing volume
- Average cost by area
- Online order availability vs. rating
- Votes (popularity proxy) vs. rating correlation

**3. SQL Analysis (`zomato_04_queries.sql`, 10 queries)**
- Top restaurants by votes, cost-by-area breakdown, listing-type performance, cuisine popularity, online-order and table-booking impact on rating/cost, area-level engagement concentration, restaurant-type performance, cost-bracket vs. rating, and "hidden gem" discovery (high rating, low visibility)
- Full results saved in `zomato_query_results.txt`, each with a one-line rationale

**4. Interactive Dashboard **
- Visual summary of the SQL/EDA findings for non-technical stakeholders

**5. Predictive Modeling (`zomato_05_random_forest.py`)**
- **Target:** High- vs. low-rated restaurant, split at the median rating (chosen over a round threshold like 4.0 to keep classes balanced)
- **Features:** cost-for-two, votes, online ordering, table booking, cuisine (top 15, bucketed), area, restaurant type (top 10, bucketed), listing type
- **Models:** Logistic Regression (baseline, scaled features) vs. Random Forest (main model)
- Deliberately kept light — one model family vs. one baseline, common-sense features, no extensive hyperparameter tuning

## 📊 Results

### Model Performance
| Model | Accuracy | Precision | Recall | F1-score |
|---|---|---|---|---|
| Logistic Regression (baseline) | 76.2% | 83.1% | 73.8% | 78.2% |
| **Random Forest (main model)** | **79.8%** | 78.1% | **90.3%** | **83.7%** |

### Top Predictive Features (Random Forest)
1. **Votes** (55.3% importance) — by far the strongest predictor of rating tier
2. **Approx. cost for two** (12.8%)
3. **Table booking availability** (10.9%)
4. Restaurant type / online ordering / cuisine (smaller, long-tail contributions)

### Key Business Insights (from SQL analysis)
- **Table-booking-enabled restaurants** average a **4.14 rating** and **₹1,271 cost-for-two**, vs. **3.62 rating** and **₹453** for non-bookable restaurants — booking availability strongly tracks with premium positioning.
- **Online ordering** availability is associated with a slightly higher average rating (3.72 vs. 3.66) and lower average cost (₹525 vs. ₹599).
- **Higher cost brackets correlate with higher ratings**: restaurants priced ₹2000+ average a 4.11 rating vs. 3.56 for those under ₹300.
- **Koramangala** (all blocks combined) and **BTM** are the areas with the highest total engagement (votes) and listing volume.
- Pub/microbrewery and premium casual-dining formats have the highest average ratings among restaurant types.

## Tech Stack
- **Python** — Pandas, NumPy, Matplotlib, Seaborn, scikit-learn
- **SQL** — SQLite
- **Power BI** — dashboard (exported as `zomato_dashboard.html` here)

## 🚀 How to Run
```bash
pip install pandas numpy matplotlib seaborn scikit-learn

python zomato_01_clean_data.py      # cleans raw data
python zomato_02_eda.py             # generates EDA charts
python zomato_03_load_sqlite.py     # loads into SQLite
python zomato_run_queries.py        # runs the 10 SQL queries
python zomato_05_random_forest.py   # trains & evaluates models
```

