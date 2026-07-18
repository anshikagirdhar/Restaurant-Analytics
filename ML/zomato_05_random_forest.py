"""
zomato_05_random_forest.py
-----------------------------
Light Random Forest classifier: predicts whether a restaurant listing
is HIGH-rated or LOW-rated, from real, pre-existing fields only
(cost, votes, online ordering, table booking, cuisine, area, restaurant
type). This replaces the originally-planned "customer churn" model,
since the source dataset has no customer/order data to support that
(see zomato_01_clean_data.py header and the project writeup for why).

Kept deliberately light, matching a Blinkit-project scope:
  - one model family (Random Forest) vs. a Logistic Regression baseline
  - a small, common-sense feature set (no exotic feature engineering)
  - no hyperparameter-tuning rabbit hole (a couple of sensible defaults)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

df = pd.read_csv("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_clean.csv")

# only rows with a real rating and cost can be used (can't predict/train on missing target)
df = df.dropna(subset=["rating", "approx_cost_for_two"]).copy()

# ---- Target: HIGH (1) vs LOW (0) rated, split at the median rating ----
# Median (not a round number like 4.0) is used so the two classes are
# genuinely balanced, rather than picking a round threshold that happens
# to produce a lopsided split.
median_rating = df["rating"].median()
df["target_high_rated"] = (df["rating"] >= median_rating).astype(int)
print(f"Median rating used as split point: {median_rating}")
print("Class balance:\n", df["target_high_rated"].value_counts(normalize=True))

# ---- Features ----
# Bucket long-tail categoricals so the model stays light/interpretable
top_cuisines = df["primary_cuisine"].value_counts().head(15).index
df["cuisine_bucketed"] = df["primary_cuisine"].where(df["primary_cuisine"].isin(top_cuisines), "Other")

top_rest_types = df["rest_type"].value_counts().head(10).index
df["rest_type_bucketed"] = df["rest_type"].where(df["rest_type"].isin(top_rest_types), "Other")

feature_df = df[["approx_cost_for_two", "votes", "online_order", "book_table",
                  "cuisine_bucketed", "area", "rest_type_bucketed", "listing_type"]].copy()
feature_df["online_order"] = feature_df["online_order"].astype(int)
feature_df["book_table"] = feature_df["book_table"].astype(int)

feature_df = pd.get_dummies(feature_df, columns=["cuisine_bucketed", "area", "rest_type_bucketed", "listing_type"],
                             drop_first=True)

X = feature_df
y = df["target_high_rated"]

# ---- Standard train/test split (cross-sectional data, not time series -
# there's no date field, so a random stratified split is the correct
# choice here, unlike the time-series projects) ----
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"\nTrain rows: {len(X_train)} | Test rows: {len(X_test)}")

# ---- Baseline: Logistic Regression (needs scaled numeric features) ----
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()
X_train_scaled[["approx_cost_for_two", "votes"]] = scaler.fit_transform(X_train[["approx_cost_for_two", "votes"]])
X_test_scaled[["approx_cost_for_two", "votes"]] = scaler.transform(X_test[["approx_cost_for_two", "votes"]])

logreg = LogisticRegression(max_iter=1000)
logreg.fit(X_train_scaled, y_train)
pred_lr = logreg.predict(X_test_scaled)

# ---- Main model: Random Forest ----
rf = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
pred_rf = rf.predict(X_test)

def evaluate(name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    print(f"\n=== {name} ===")
    print(f"Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")
    print(f"Confusion matrix [[TN, FP],[FN, TP]]:\n{cm}")
    return {"model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

results = []
results.append(evaluate("Logistic Regression (baseline)", y_test, pred_lr))
results.append(evaluate("Random Forest (main model)", y_test, pred_rf))

# ---- Feature importance ----
importances = pd.DataFrame({"feature": X.columns, "importance": rf.feature_importances_}) \
    .sort_values("importance", ascending=False)
print("\nTop 15 feature importances:")
print(importances.head(15).to_string(index=False))

importances.to_csv("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_feature_importance.csv", index=False)
pd.DataFrame(results).to_csv("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_model_metrics.csv", index=False)

test_out = df.loc[X_test.index, ["name", "area", "primary_cuisine", "rating", "votes", "approx_cost_for_two", "target_high_rated"]].copy()
test_out["pred_rf"] = pred_rf
test_out.to_csv("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_test_predictions.csv", index=False)

print("\nSaved zomato_feature_importance.csv, zomato_model_metrics.csv, zomato_test_predictions.csv")
