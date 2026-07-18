"""
zomato_03_load_sqlite.py
--------------------------
Loads the cleaned Zomato dataset into a local SQLite database
(zomato.db, table: restaurants).
"""

import sqlite3
import pandas as pd
import os
import shutil

CSV_PATH = "/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_clean.csv"
TMP_DB_PATH = "/tmp/zomato.db"
DB_PATH = "/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato.db"

df = pd.read_csv(CSV_PATH)

if os.path.exists(TMP_DB_PATH):
    os.remove(TMP_DB_PATH)
conn = sqlite3.connect(TMP_DB_PATH)
df.to_sql("restaurants", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_area ON restaurants(area);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_cuisine ON restaurants(primary_cuisine);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_listing_type ON restaurants(listing_type);")
conn.commit()

cur = conn.execute("SELECT COUNT(*) FROM restaurants;")
print("Rows loaded:", cur.fetchone()[0])
cur = conn.execute("PRAGMA table_info(restaurants);")
print("Columns:", [c[1] for c in cur.fetchall()])
conn.close()

shutil.copyfile(TMP_DB_PATH, DB_PATH)
print(f"Copied DB to {DB_PATH}")
