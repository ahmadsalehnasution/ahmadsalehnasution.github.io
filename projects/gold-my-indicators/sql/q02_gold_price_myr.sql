-- BUSINESS QUESTION: what did a gram of gold actually cost in ringgit each month?
-- SQL PRACTISED: joining two daily sources onto a monthly grain, unit conversion (troy ounce -> gram),
-- CASE for data-completeness flags.
SELECT strftime(month, '%Y-%m')                                   AS month,
       ROUND(usd_per_oz_avg, 2)                                   AS usd_per_oz,
       ROUND(usd_myr_avg, 4)                                      AS usd_myr,
       ROUND(gold_myr_per_gram, 2)                                AS gold_myr_per_gram,
       CASE WHEN trading_days < 15 OR quote_days < 15
            THEN 'partial month - treat with care' ELSE 'ok' END  AS data_quality
FROM mart_gold_myr_monthly
ORDER BY month;
