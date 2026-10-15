-- q10 — Did the currency effect persist, or was it a phase?
-- Business question: if the ringgit carried part of gold's return, did it carry it the whole time? A currency tailwind
-- that only blows during one phase is not protection — it is timing.
-- Method: named sub-periods taken from the actual path of USD/MYR (weakening to the 2024-02 peak, strengthening to the
-- 2026-02 trough, then the recent partial recovery), each measured start-to-end on monthly averages.
-- The counterfactual column answers "what would the ringgit price have done if the exchange rate had stood still?"

WITH periods(scope, period, from_month, to_month) AS (
    VALUES
        ('full window',        '2021-11 to 2026-09', DATE '2021-11-01', DATE '2026-09-01'),
        ('ringgit weakening',  '2021-11 to 2024-02', DATE '2021-11-01', DATE '2024-02-01'),
        ('ringgit strengthening','2024-02 to 2026-02', DATE '2024-02-01', DATE '2026-02-01'),
        ('recent rebound',     '2026-02 to 2026-09', DATE '2026-02-01', DATE '2026-09-01')
),
points AS (
    SELECT
        p.scope,
        p.period,
        m.month,
        m.usd_per_oz_avg / 31.1034768 AS gold_usd_per_gram,
        m.gold_myr_per_gram,
        m.usd_myr_avg,
        CASE WHEN m.month = p.from_month THEN 1 ELSE 0 END AS is_start,
        CASE WHEN m.month = p.to_month   THEN 1 ELSE 0 END AS is_end
    FROM mart_gold_myr_monthly m
    JOIN periods p ON m.month BETWEEN p.from_month AND p.to_month
    WHERE m.quote_days >= 15          -- exclude partial months
),
paired AS (
    SELECT
        scope,
        period,
        MAX(CASE WHEN is_start = 1 THEN gold_usd_per_gram END) AS usd_start,
        MAX(CASE WHEN is_end   = 1 THEN gold_usd_per_gram END) AS usd_end,
        MAX(CASE WHEN is_start = 1 THEN gold_myr_per_gram END) AS myr_start,
        MAX(CASE WHEN is_end   = 1 THEN gold_myr_per_gram END) AS myr_end,
        MAX(CASE WHEN is_start = 1 THEN usd_myr_avg END)       AS fx_start,
        MAX(CASE WHEN is_end   = 1 THEN usd_myr_avg END)       AS fx_end
    FROM points
    GROUP BY 1, 2
)
SELECT
    scope,
    period,
    ROUND(usd_start, 2)                                          AS gold_usd_g_start,
    ROUND(usd_end, 2)                                            AS gold_usd_g_end,
    ROUND(fx_start, 4)                                           AS usd_myr_start,
    ROUND(fx_end, 4)                                             AS usd_myr_end,
    ROUND(100 * (usd_end / usd_start - 1), 1)                    AS gold_usd_return_pct,
    ROUND(100 * (fx_end / fx_start - 1), 1)                      AS fx_effect_pct,
    ROUND(100 * (myr_end / myr_start - 1), 1)                    AS gold_myr_return_pct,
    ROUND(100 * ((myr_end / myr_start) - (usd_end / usd_start)), 1)
                                                                 AS fx_share_of_return_pp,
    ROUND(myr_start * (usd_end / usd_start), 2)                  AS myr_price_if_fx_flat
FROM paired
ORDER BY CASE scope WHEN 'full window' THEN 1 WHEN 'ringgit weakening' THEN 2
                    WHEN 'ringgit strengthening' THEN 3 ELSE 4 END;
