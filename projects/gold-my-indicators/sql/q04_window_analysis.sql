-- BUSINESS QUESTION: is the recent gold move a spike or a sustained trend?
-- SQL PRACTISED: 12-month moving average, cumulative product return, ROWS BETWEEN frame, MAX/MIN OVER.
SELECT strftime(month, '%Y-%m') AS month,
       ROUND(gold_myr_per_gram, 2) AS gold_myr_per_gram,
       ROUND(AVG(gold_myr_per_gram) OVER (ORDER BY month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW), 2)
                                   AS moving_avg_12m,
       ROUND(gold_myr_per_gram - AVG(gold_myr_per_gram) OVER (ORDER BY month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW), 2)
                                   AS gap_to_moving_avg,
       ROUND(MAX(gold_myr_per_gram) OVER (ORDER BY month) , 2) AS running_max,
       CASE WHEN gold_myr_per_gram = MAX(gold_myr_per_gram) OVER (ORDER BY month)
            THEN 'new high' ELSE '' END AS note
FROM mart_gold_myr_monthly
WHERE month >= DATE '2022-10-01'
ORDER BY month;
