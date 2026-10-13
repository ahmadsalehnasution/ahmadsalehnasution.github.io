-- BUSINESS QUESTION: how affordable is a gram of gold for a median household in each state?
-- SQL PRACTISED: joining an annual (2-yearly survey) grain to a monthly price grain, ranking across states,
-- percentage calculation.
SELECT year, state,
       income_median_rm_month,
       gold_myr_per_gram_year,
       grams_per_rm1000,
       pct_of_median_income_per_gram,
       RANK() OVER (PARTITION BY year ORDER BY pct_of_median_income_per_gram) AS rank_most_affordable
FROM mart_affordability
WHERE year = (SELECT MAX(year) FROM mart_affordability)
ORDER BY rank_most_affordable;
