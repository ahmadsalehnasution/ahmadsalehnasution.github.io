-- BUSINESS QUESTION: how fast have Malaysian consumer prices risen since 2021?
-- SQL PRACTISED: date_trunc, aggregation, LAG window function (year-on-year), ordering.
SELECT division,
       strftime(month, '%Y')                      AS yr,
       ROUND(AVG(cpi_index), 2)                   AS cpi_index_avg,
       ROUND((AVG(cpi_index) / LAG(AVG(cpi_index)) OVER (PARTITION BY division ORDER BY strftime(month, '%Y')) - 1) * 100, 2) AS cpi_yoy_pct
FROM stg_cpi_monthly
WHERE division IN ('overall', '01', '04')
  AND month >= DATE '2021-01-01'
GROUP BY 1, 2
ORDER BY division, yr;
