-- BUSINESS QUESTION: can I trust these numbers before I publish them?
-- SQL PRACTISED: data-quality checks — coverage, gaps, cross-source agreement.
-- (a) monthly coverage per source
SELECT 'gold trading days per month' AS check_name,
       CAST(MIN(trading_days) AS VARCHAR) || ' min / ' || CAST(MAX(trading_days) AS VARCHAR) || ' max' AS result
FROM stg_gold_monthly WHERE month >= DATE '2021-10-01'
UNION ALL
SELECT 'fx quote days per month',
       CAST(MIN(quote_days) AS VARCHAR) || ' min / ' || CAST(MAX(quote_days) AS VARCHAR) || ' max'
FROM stg_fx_monthly WHERE month >= DATE '2021-10-01'
UNION ALL
SELECT 'months in the gold mart', CAST(COUNT(*) AS VARCHAR) FROM mart_gold_myr_monthly
UNION ALL
SELECT 'CPI divisions covered', CAST(COUNT(DISTINCT division) AS VARCHAR) FROM stg_cpi_monthly
UNION ALL
-- (b) cross-source agreement: ECB reference rate vs the official BNM spot rate on the same day
SELECT 'ECB vs BNM spot (MYR per USD)',
       'ECB ' || CAST(ROUND((SELECT usd_myr FROM raw_fx ORDER BY date DESC LIMIT 1), 4) AS VARCHAR)
       || ' vs BNM ' || CAST((SELECT usd_myr_middle FROM raw_bnm_spot LIMIT 1) AS VARCHAR)
FROM (SELECT 1);
