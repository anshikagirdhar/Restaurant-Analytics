-- ============================================================
-- Zomato Restaurant Sales & Performance Analysis - SQL LAYER
-- Database: zomato.db   Table: restaurants (51,632 rows)
-- Run with: sqlite3 zomato.db < zomato_04_queries.sql
--
-- NOTE ON METRICS: this dataset has no revenue/order/transaction
-- field. `votes` (number of ratings a restaurant received on Zomato)
-- is used as a popularity/engagement proxy, clearly labeled as such
-- in every query below - none of these queries claim a real
-- "revenue" number that doesn't exist in the source data.
-- ============================================================

-- Q1. Top 10 restaurants by votes (popularity proxy - closest real
-- substitute for "top restaurants by revenue" since no sales data exists)
SELECT name, area, primary_cuisine, votes, rating
FROM restaurants
GROUP BY name, address
ORDER BY votes DESC
LIMIT 10;

-- Q2. Average cost-for-two by area (top 15 areas by listing volume)
SELECT area, COUNT(*) AS num_listings,
       ROUND(AVG(approx_cost_for_two), 0) AS avg_cost_for_two
FROM restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY area
ORDER BY num_listings DESC
LIMIT 15;

-- Q3. Restaurants with only "Delivery" listing vs. multi-category listings
-- (closest real proxy to "single-channel vs. multi-channel" restaurants,
-- since there's no per-customer order history to define single-order vs
-- repeat customers)
SELECT listing_type, COUNT(*) AS num_listings,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(votes), 0) AS avg_votes
FROM restaurants
GROUP BY listing_type
ORDER BY num_listings DESC;

-- Q4. Revenue-proxy contribution by cuisine (using votes as the proxy,
-- explicitly labeled - NOT a real revenue figure)
SELECT primary_cuisine, COUNT(*) AS num_listings,
       SUM(votes) AS total_votes_proxy,
       ROUND(AVG(approx_cost_for_two), 0) AS avg_cost_for_two,
       ROUND(AVG(rating), 2) AS avg_rating
FROM restaurants
WHERE primary_cuisine IS NOT NULL
GROUP BY primary_cuisine
ORDER BY total_votes_proxy DESC
LIMIT 10;

-- Q5. Online order availability vs. rating and votes (does online
-- ordering correlate with popularity/rating?)
SELECT online_order, COUNT(*) AS num_listings,
       ROUND(AVG(rating), 3) AS avg_rating,
       ROUND(AVG(votes), 0) AS avg_votes,
       ROUND(AVG(approx_cost_for_two), 0) AS avg_cost_for_two
FROM restaurants
GROUP BY online_order;

-- Q6. Table booking availability vs. cost (do bookable restaurants skew premium?)
SELECT book_table, COUNT(*) AS num_listings,
       ROUND(AVG(approx_cost_for_two), 0) AS avg_cost_for_two,
       ROUND(AVG(rating), 3) AS avg_rating
FROM restaurants
GROUP BY book_table;

-- Q7. Top 5 areas by total votes (concentration of popularity/engagement)
SELECT area, SUM(votes) AS total_votes, COUNT(*) AS num_listings
FROM restaurants
GROUP BY area
ORDER BY total_votes DESC
LIMIT 5;

-- Q8. Restaurant type (rest_type) performance: average rating and votes
SELECT rest_type, COUNT(*) AS num_listings,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(votes), 0) AS avg_votes,
       ROUND(AVG(approx_cost_for_two), 0) AS avg_cost_for_two
FROM restaurants
WHERE rest_type IS NOT NULL
GROUP BY rest_type
HAVING COUNT(*) >= 50
ORDER BY avg_rating DESC
LIMIT 15;

-- Q9. Cost bracket vs. average rating (does higher cost correlate with
-- higher rating?)
SELECT
  CASE
    WHEN approx_cost_for_two < 300 THEN '1. Under 300'
    WHEN approx_cost_for_two < 600 THEN '2. 300-599'
    WHEN approx_cost_for_two < 1000 THEN '3. 600-999'
    WHEN approx_cost_for_two < 2000 THEN '4. 1000-1999'
    ELSE '5. 2000+'
  END AS cost_bracket,
  COUNT(*) AS num_listings,
  ROUND(AVG(rating), 3) AS avg_rating,
  ROUND(AVG(votes), 0) AS avg_votes
FROM restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY cost_bracket
ORDER BY cost_bracket;

-- Q10. "Hidden gems" vs. "overhyped": high votes but modest rating, or
-- high rating but low votes (top 10 each, area+cuisine shown for context)
-- Hidden gems: rating >= 4.3 but votes below the median
SELECT name, area, primary_cuisine, rating, votes
FROM restaurants
WHERE rating >= 4.3 AND votes < (SELECT AVG(votes) FROM restaurants)
ORDER BY rating DESC, votes ASC
LIMIT 10;
