-- BUSINESS QUESTION: does gold strength line up with retail spending and the labour market?
-- SQL PRACTISED: multi-table join, conditional aggregation, deriving a yearly series from monthly data,
-- NULL-safe comparison.
WITH yearly AS (
    SELECT strftime(month, '%Y') AS yr,
           AVG(gold_yoy_pct)                                     AS gold_yoy_avg,
           AVG(cpi_yoy_pct)                                      AS cpi_yoy_avg,
           AVG(sales_rm_million)                                 AS retail_sales_avg,
           AVG(unemployment_pct)                                 AS unemp_avg
    FROM mart_monthly WHERE sales_rm_million IS NOT NULL GROUP BY 1)
SELECT yr,
       ROUND(gold_yoy_avg, 2)   AS gold_yoy_pct,
       ROUND(cpi_yoy_avg, 2)    AS cpi_yoy_pct,
       ROUND(retail_sales_avg, 1) AS retail_sales_rm_million_avg,
       ROUND(unemp_avg, 2)      AS unemployment_pct,
       CASE WHEN gold_yoy_avg > cpi_yoy_avg THEN 'gold ahead of inflation' ELSE 'gold behind inflation' END AS verdict
FROM yearly ORDER BY yr;
