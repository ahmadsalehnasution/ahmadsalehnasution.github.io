-- q09 — Is the ringgit doing the work?
-- Business question: gold is priced in US dollars and he buys it in ringgit. When the ringgit price rises, how much
-- of that is the metal getting more valuable and how much is the ringgit getting weaker?
-- Deflating to a third currency separates the two, and the answer decides whether "gold protects me from a weak
-- ringgit" is a real property or just a story that happened to be true in one period.
-- Method: average gold (USD/gram) and the USD/MYR rate per calendar year; year-over-year change of both; then the
-- identity (1 + ringgit return) = (1 + dollar return) x (1 + currency effect).
-- Partial months are excluded so a half-finished month cannot distort a yearly average.

WITH clean AS (
    SELECT
        month,
        usd_per_oz_avg / 31.1034768 AS gold_usd_per_gram,
        gold_myr_per_gram,
        usd_myr_avg
    FROM mart_gold_myr_monthly
    WHERE quote_days >= 15
),
yearly AS (
    SELECT
        YEAR(month)                 AS yr,
        AVG(gold_usd_per_gram)      AS gold_usd_per_gram_avg,
        AVG(gold_myr_per_gram)      AS gold_myr_per_gram_avg,
        AVG(usd_myr_avg)            AS fx_usd_myr_avg,
        COUNT(*)                    AS months_counted
    FROM clean
    GROUP BY 1
)
SELECT
    yr,
    months_counted,
    ROUND(gold_usd_per_gram_avg, 2)                                     AS gold_usd_g,
    ROUND(gold_myr_per_gram_avg, 2)                                     AS gold_myr_g,
    ROUND(fx_usd_myr_avg, 4)                                            AS usd_myr,
    ROUND(100 * (gold_usd_per_gram_avg / LAG(gold_usd_per_gram_avg) OVER (ORDER BY yr) - 1), 1)
                                                                        AS gold_usd_yoy_pct,
    ROUND(100 * (fx_usd_myr_avg / LAG(fx_usd_myr_avg) OVER (ORDER BY yr) - 1), 1)
                                                                        AS fx_effect_pct,
    ROUND(100 * (gold_myr_per_gram_avg / LAG(gold_myr_per_gram_avg) OVER (ORDER BY yr) - 1), 1)
                                                                        AS gold_myr_yoy_pct,
    ROUND(100 * (
        (gold_myr_per_gram_avg / LAG(gold_myr_per_gram_avg) OVER (ORDER BY yr) - 1)
        - (fx_usd_myr_avg / LAG(fx_usd_myr_avg) OVER (ORDER BY yr) - 1)
    ), 1)                                                               AS metal_only_contribution_pct
FROM yearly
ORDER BY yr;
