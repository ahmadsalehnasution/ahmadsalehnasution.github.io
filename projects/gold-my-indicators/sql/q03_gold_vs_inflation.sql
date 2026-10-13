-- BUSINESS QUESTION: did gold in ringgit beat Malaysian inflation, month by month?
-- SQL PRACTISED: LEFT JOIN across three grains, computed columns, filtering out the first 12 months
-- (needed for the year-on-year calculation).
SELECT strftime(month, '%Y-%m') AS month,
       gold_yoy_pct,
       cpi_yoy_pct,
       gold_real_yoy_pct,
       CASE WHEN gold_real_yoy_pct > 0 THEN 'gold ahead' ELSE 'gold behind' END AS verdict
FROM mart_monthly
WHERE gold_real_yoy_pct IS NOT NULL AND cpi_yoy_pct IS NOT NULL
ORDER BY month;
