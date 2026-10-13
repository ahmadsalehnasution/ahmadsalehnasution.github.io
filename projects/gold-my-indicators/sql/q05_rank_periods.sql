-- BUSINESS QUESTION: which years and months were genuinely the best for a ringgit gold buyer?
-- SQL PRACTISED: CTE, GROUP BY + ranking with RANK() OVER, combining two answer shapes in one file.
WITH monthly AS (
    SELECT month, gold_myr_per_gram, gold_real_yoy_pct,
           strftime(month, '%Y') AS yr, strftime(month, '%m') AS mo
    FROM mart_monthly WHERE gold_real_yoy_pct IS NOT NULL)
SELECT yr,
       ROUND(AVG(gold_myr_per_gram), 2) AS gold_myr_per_gram_avg,
       ROUND(AVG(gold_real_yoy_pct), 2) AS gold_real_yoy_pct_avg,
       RANK() OVER (ORDER BY AVG(gold_real_yoy_pct) DESC) AS rank_best_first
FROM monthly GROUP BY yr ORDER BY rank_best_first;
