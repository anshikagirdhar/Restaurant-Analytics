"""Runs the 10 queries from zomato_04_queries.sql against zomato.db and
writes a readable report with results + a one-line explanation for each
(the sandbox doesn't have the sqlite3 CLI installed, so queries are
run here via pandas instead of piping the .sql file directly)."""

import sqlite3
import pandas as pd
import shutil

shutil.copyfile("/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato.db", "/tmp/zomato_query.db")
DB_PATH = "/tmp/zomato_query.db"
OUT_PATH = "/sessions/peaceful-youthful-maxwell/mnt/outputs/zomato_query_results.txt"

QUERIES = [
    ("Q1. Top 10 restaurants by votes (popularity proxy)",
     "Closest real substitute for 'top restaurants by revenue' - this dataset has no sales figures, "
     "so votes (number of ratings received) stands in as a labeled popularity proxy.",
     """SELECT name, area, primary_cuisine, votes, rating FROM restaurants
        GROUP BY name, address ORDER BY votes DESC LIMIT 10;"""),

    ("Q2. Average cost-for-two by area (top 15 by listing volume)",
     "Answers 'which areas skew premium vs. budget' - a real, direct use of the cost field.",
     """SELECT area, COUNT(*) AS num_listings, ROUND(AVG(approx_cost_for_two),0) AS avg_cost_for_two
        FROM restaurants WHERE approx_cost_for_two IS NOT NULL
        GROUP BY area ORDER BY num_listings DESC LIMIT 15;"""),

    ("Q3. Listing type performance (Delivery/Dine-out/Cafes/etc.)",
     "Since there's no per-customer order history, this is the closest real proxy to a "
     "'channel mix' question - how does rating/popularity differ by how a restaurant is listed.",
     """SELECT listing_type, COUNT(*) AS num_listings, ROUND(AVG(rating),2) AS avg_rating,
        ROUND(AVG(votes),0) AS avg_votes FROM restaurants
        GROUP BY listing_type ORDER BY num_listings DESC;"""),

    ("Q4. Votes-proxy contribution by cuisine (NOT real revenue)",
     "Mirrors 'revenue contribution by cuisine' but explicitly using the votes proxy, labeled as such.",
     """SELECT primary_cuisine, COUNT(*) AS num_listings, SUM(votes) AS total_votes_proxy,
        ROUND(AVG(approx_cost_for_two),0) AS avg_cost_for_two, ROUND(AVG(rating),2) AS avg_rating
        FROM restaurants WHERE primary_cuisine IS NOT NULL
        GROUP BY primary_cuisine ORDER BY total_votes_proxy DESC LIMIT 10;"""),

    ("Q5. Online order availability vs. rating/votes/cost",
     "Tests whether offering online ordering associates with higher popularity or rating.",
     """SELECT online_order, COUNT(*) AS num_listings, ROUND(AVG(rating),3) AS avg_rating,
        ROUND(AVG(votes),0) AS avg_votes, ROUND(AVG(approx_cost_for_two),0) AS avg_cost_for_two
        FROM restaurants GROUP BY online_order;"""),

    ("Q6. Table booking availability vs. cost/rating",
     "Tests whether bookable restaurants skew premium (higher cost) and/or higher rated.",
     """SELECT book_table, COUNT(*) AS num_listings, ROUND(AVG(approx_cost_for_two),0) AS avg_cost_for_two,
        ROUND(AVG(rating),3) AS avg_rating FROM restaurants GROUP BY book_table;"""),

    ("Q7. Top 5 areas by total votes (engagement concentration)",
     "Identifies where Zomato engagement/popularity is most concentrated geographically.",
     """SELECT area, SUM(votes) AS total_votes, COUNT(*) AS num_listings
        FROM restaurants GROUP BY area ORDER BY total_votes DESC LIMIT 5;"""),

    ("Q8. Restaurant type (rest_type) performance",
     "Which physical restaurant formats (Quick Bites, Casual Dining, etc.) rate best, filtered to "
     "types with at least 50 listings so small categories don't dominate the ranking by noise.",
     """SELECT rest_type, COUNT(*) AS num_listings, ROUND(AVG(rating),2) AS avg_rating,
        ROUND(AVG(votes),0) AS avg_votes, ROUND(AVG(approx_cost_for_two),0) AS avg_cost_for_two
        FROM restaurants WHERE rest_type IS NOT NULL
        GROUP BY rest_type HAVING COUNT(*) >= 50 ORDER BY avg_rating DESC LIMIT 15;"""),

    ("Q9. Cost bracket vs. average rating",
     "Tests whether spending more correlates with a better-rated experience.",
     """SELECT CASE WHEN approx_cost_for_two < 300 THEN '1. Under 300'
        WHEN approx_cost_for_two < 600 THEN '2. 300-599' WHEN approx_cost_for_two < 1000 THEN '3. 600-999'
        WHEN approx_cost_for_two < 2000 THEN '4. 1000-1999' ELSE '5. 2000+' END AS cost_bracket,
        COUNT(*) AS num_listings, ROUND(AVG(rating),3) AS avg_rating, ROUND(AVG(votes),0) AS avg_votes
        FROM restaurants WHERE approx_cost_for_two IS NOT NULL
        GROUP BY cost_bracket ORDER BY cost_bracket;"""),

    ("Q10. 'Hidden gems': high rating (>=4.3), below-average votes",
     "Business-relevant discovery query: well-reviewed restaurants that haven't built up much visibility yet.",
     """SELECT name, area, primary_cuisine, rating, votes FROM restaurants
        WHERE rating >= 4.3 AND votes < (SELECT AVG(votes) FROM restaurants)
        ORDER BY rating DESC, votes ASC LIMIT 10;"""),
]

conn = sqlite3.connect(DB_PATH)
out_lines = []
for label, why, query in QUERIES:
    out_lines.append("=" * 100)
    out_lines.append(label)
    out_lines.append(f"Why: {why}")
    out_lines.append("-" * 100)
    df = pd.read_sql_query(query, conn)
    out_lines.append(df.to_string(index=False))
    out_lines.append("")
conn.close()

report = "\n".join(out_lines)
with open(OUT_PATH, "w") as f:
    f.write(report)

print(report)
