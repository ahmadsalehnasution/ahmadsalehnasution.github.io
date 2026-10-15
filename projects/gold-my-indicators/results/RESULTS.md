# P2 — Hasil Query (dihasilkan otomatis oleh `run_queries.py`)

Database: `gold_my.duckdb` · Basis data mentah: `data/raw/` · Semua angka di bawah dihasilkan langsung dari query.


## q01_inflation_trend.sql  (18 baris)

| division | yr | cpi_index_avg | cpi_yoy_pct |
|---|---|---|---|
| 01 | 2021 | 137.13 |  |
| 01 | 2022 | 145.02 | 5.75 |
| 01 | 2023 | 152.02 | 4.83 |
| 01 | 2024 | 155.03 | 1.98 |
| 01 | 2025 | 158.19 | 2.04 |
| 01 | 2026 | 160.14 | 1.23 |
| 04 | 2021 | 121.03 |  |
| 04 | 2022 | 123.22 | 1.81 |
| 04 | 2023 | 125.26 | 1.66 |
| 04 | 2024 | 129.02 | 3.01 |
| 04 | 2025 | 131.09 | 1.6 |
| 04 | 2026 | 132.88 | 1.36 |
| overall | 2021 | 123.08 |  |
| overall | 2022 | 127.23 | 3.38 |
| overall | 2023 | 130.4 | 2.49 |
| overall | 2024 | 132.79 | 1.83 |
| overall | 2025 | 134.62 | 1.38 |
| overall | 2026 | 136.73 | 1.56 |

## q02_gold_price_myr.sql  (61 baris)

| month | usd_per_oz | usd_myr | gold_myr_per_gram | data_quality |
|---|---|---|---|---|
| 2021-10 | 1788.13 | 4.1639 | 239.38 | partial month - treat with care |
| 2021-11 | 1819.93 | 4.1789 | 244.51 | ok |
| 2021-12 | 1792.53 | 4.2109 | 242.68 | ok |
| 2022-01 | 1816.79 | 4.1898 | 244.73 | ok |
| 2022-02 | 1858.99 | 4.1874 | 250.27 | ok |
| 2022-03 | 1951.87 | 4.1997 | 263.55 | ok |
| 2022-04 | 1937.55 | 4.2718 | 266.1 | ok |
| 2022-05 | 1846.7 | 4.3809 | 260.11 | ok |
| 2022-06 | 1838.78 | 4.4007 | 260.16 | ok |
| 2022-07 | 1730.82 | 4.4404 | 247.09 | ok |
| 2022-08 | 1778.65 | 4.4661 | 255.4 | ok |
| 2022-09 | 1690.06 | 4.5449 | 246.95 | ok |
| 2022-10 | 1672.74 | 4.6944 | 252.47 | ok |
| 2022-11 | 1728.63 | 4.6094 | 256.18 | ok |
| 2022-12 | 1807.73 | 4.4123 | 256.44 | ok |
| 2023-01 | 1902.83 | 4.3268 | 264.7 | ok |
| 2023-02 | 1864.42 | 4.3678 | 261.82 | ok |
| 2023-03 | 1916.84 | 4.4667 | 275.27 | ok |
| 2023-04 | 2013.76 | 4.4276 | 286.66 | ok |
| 2023-05 | 1997.94 | 4.5204 | 290.37 | ok |
| 2023-06 | 1954.63 | 4.6316 | 291.06 | ok |
| 2023-07 | 1954.53 | 4.5902 | 288.45 | ok |
| 2023-08 | 1949.95 | 4.6106 | 289.05 | ok |
| 2023-09 | 1934.71 | 4.6824 | 291.26 | ok |
| 2023-10 | 1928.62 | 4.7471 | 294.35 | ok |
| 2023-11 | 1989.51 | 4.6881 | 299.87 | ok |
| 2023-12 | 2046.04 | 4.6618 | 306.66 | ok |
| 2024-01 | 2032.05 | 4.6864 | 306.17 | ok |
| 2024-02 | 2038.77 | 4.7679 | 312.53 | ok |
| 2024-03 | 2166.43 | 4.716 | 328.48 | ok |
| 2024-04 | 2349.3 | 4.7671 | 360.07 | ok |
| 2024-05 | 2355.25 | 4.7143 | 356.98 | ok |
| 2024-06 | 2343.38 | 4.7105 | 354.9 | ok |
| 2024-07 | 2398.49 | 4.6788 | 360.8 | ok |
| 2024-08 | 2506.98 | 4.4143 | 355.8 | ok |
| 2024-09 | 2601.18 | 4.2631 | 356.52 | ok |
| 2024-10 | 2706.17 | 4.2999 | 374.12 | ok |
| 2024-11 | 2654.83 | 4.4351 | 378.55 | ok |
| 2024-12 | 2662.09 | 4.4594 | 381.68 | ok |
| 2025-01 | 2727.53 | 4.4655 | 391.59 | ok |

*(menampilkan 40 dari 61 baris; CSV lengkap ada di `results/`)*

## q03_gold_vs_inflation.sql  (47 baris)

| month | gold_yoy_pct | cpi_yoy_pct | gold_real_yoy_pct | verdict |
|---|---|---|---|---|
| 2022-10 | 5.47 | 3.96 | 1.51 | gold ahead |
| 2022-11 | 4.77 | 4.03 | 0.74 | gold ahead |
| 2022-12 | 5.67 | 3.78 | 1.9 | gold ahead |
| 2023-01 | 8.16 | 3.68 | 4.48 | gold ahead |
| 2023-02 | 4.61 | 3.67 | 0.94 | gold ahead |
| 2023-03 | 4.45 | 3.42 | 1.02 | gold ahead |
| 2023-04 | 7.72 | 3.26 | 4.47 | gold ahead |
| 2023-05 | 11.63 | 2.84 | 8.79 | gold ahead |
| 2023-06 | 11.88 | 2.35 | 9.52 | gold ahead |
| 2023-07 | 16.74 | 2.03 | 14.7 | gold ahead |
| 2023-08 | 13.18 | 1.95 | 11.23 | gold ahead |
| 2023-09 | 17.94 | 1.95 | 15.99 | gold ahead |
| 2023-10 | 16.59 | 1.79 | 14.8 | gold ahead |
| 2023-11 | 17.05 | 1.47 | 15.58 | gold ahead |
| 2023-12 | 19.58 | 1.55 | 18.03 | gold ahead |
| 2024-01 | 15.67 | 1.47 | 14.2 | gold ahead |
| 2024-02 | 19.37 | 1.77 | 17.6 | gold ahead |
| 2024-03 | 19.33 | 1.77 | 17.56 | gold ahead |
| 2024-04 | 25.61 | 1.85 | 23.76 | gold ahead |
| 2024-05 | 22.94 | 2.0 | 20.94 | gold ahead |
| 2024-06 | 21.93 | 1.99 | 19.94 | gold ahead |
| 2024-07 | 25.08 | 1.99 | 23.09 | gold ahead |
| 2024-08 | 23.09 | 1.91 | 21.18 | gold ahead |
| 2024-09 | 22.41 | 1.83 | 20.57 | gold ahead |
| 2024-10 | 27.1 | 1.91 | 25.19 | gold ahead |
| 2024-11 | 26.24 | 1.83 | 24.41 | gold ahead |
| 2024-12 | 24.46 | 1.68 | 22.79 | gold ahead |
| 2025-01 | 27.9 | 1.67 | 26.22 | gold ahead |
| 2025-02 | 33.23 | 1.51 | 31.71 | gold ahead |
| 2025-03 | 29.89 | 1.44 | 28.45 | gold ahead |
| 2025-04 | 27.42 | 1.44 | 25.98 | gold ahead |
| 2025-05 | 26.23 | 1.2 | 25.03 | gold ahead |
| 2025-06 | 29.55 | 1.13 | 28.42 | gold ahead |
| 2025-07 | 26.38 | 1.2 | 25.18 | gold ahead |
| 2025-08 | 30.65 | 1.28 | 29.38 | gold ahead |
| 2025-09 | 41.27 | 1.5 | 39.77 | gold ahead |
| 2025-10 | 47.34 | 1.27 | 46.07 | gold ahead |
| 2025-11 | 44.33 | 1.35 | 42.98 | gold ahead |
| 2025-12 | 49.54 | 1.57 | 47.97 | gold ahead |
| 2026-01 | 56.71 | 1.57 | 55.14 | gold ahead |

*(menampilkan 40 dari 47 baris; CSV lengkap ada di `results/`)*

## q04_window_analysis.sql  (49 baris)

| month | gold_myr_per_gram | moving_avg_12m | gap_to_moving_avg | running_max | note |
|---|---|---|---|---|---|
| 2022-10 | 252.47 | 252.47 | 0.0 | 252.47 | new high |
| 2022-11 | 256.18 | 254.32 | 1.86 | 256.18 | new high |
| 2022-12 | 256.44 | 255.03 | 1.41 | 256.44 | new high |
| 2023-01 | 264.7 | 257.45 | 7.25 | 264.7 | new high |
| 2023-02 | 261.82 | 258.32 | 3.5 | 264.7 |  |
| 2023-03 | 275.27 | 261.15 | 14.13 | 275.27 | new high |
| 2023-04 | 286.66 | 264.79 | 21.87 | 286.66 | new high |
| 2023-05 | 290.37 | 267.99 | 22.38 | 290.37 | new high |
| 2023-06 | 291.06 | 270.55 | 20.51 | 291.06 | new high |
| 2023-07 | 288.45 | 272.34 | 16.11 | 291.06 |  |
| 2023-08 | 289.05 | 273.86 | 15.19 | 291.06 |  |
| 2023-09 | 291.26 | 275.31 | 15.94 | 291.26 | new high |
| 2023-10 | 294.35 | 278.8 | 15.55 | 294.35 | new high |
| 2023-11 | 299.87 | 282.44 | 17.43 | 299.87 | new high |
| 2023-12 | 306.66 | 286.63 | 20.03 | 306.66 | new high |
| 2024-01 | 306.17 | 290.08 | 16.09 | 306.66 |  |
| 2024-02 | 312.53 | 294.31 | 18.22 | 312.53 | new high |
| 2024-03 | 328.48 | 298.74 | 29.74 | 328.48 | new high |
| 2024-04 | 360.07 | 304.86 | 55.21 | 360.07 | new high |
| 2024-05 | 356.98 | 310.41 | 46.57 | 360.07 |  |
| 2024-06 | 354.9 | 315.73 | 39.17 | 360.07 |  |
| 2024-07 | 360.8 | 321.76 | 39.04 | 360.8 | new high |
| 2024-08 | 355.8 | 327.32 | 28.48 | 360.8 |  |
| 2024-09 | 356.52 | 332.76 | 23.76 | 360.8 |  |
| 2024-10 | 374.12 | 339.41 | 34.71 | 374.12 | new high |
| 2024-11 | 378.55 | 345.96 | 32.59 | 378.55 | new high |
| 2024-12 | 381.68 | 352.22 | 29.46 | 381.68 | new high |
| 2025-01 | 391.59 | 359.33 | 32.25 | 391.59 | new high |
| 2025-02 | 416.37 | 367.99 | 48.38 | 416.37 | new high |
| 2025-03 | 426.65 | 376.17 | 50.48 | 426.65 | new high |
| 2025-04 | 458.78 | 384.39 | 74.38 | 458.78 | new high |
| 2025-05 | 450.63 | 392.2 | 58.43 | 458.78 |  |
| 2025-06 | 459.76 | 400.94 | 58.83 | 459.76 | new high |
| 2025-07 | 455.98 | 408.87 | 47.12 | 459.76 |  |
| 2025-08 | 464.86 | 417.96 | 46.91 | 464.86 | new high |
| 2025-09 | 503.66 | 430.22 | 73.44 | 503.66 | new high |
| 2025-10 | 551.24 | 444.98 | 106.27 | 551.24 | new high |
| 2025-11 | 546.36 | 458.96 | 87.4 | 551.24 |  |
| 2025-12 | 570.77 | 474.72 | 96.05 | 570.77 | new high |
| 2026-01 | 613.65 | 493.23 | 120.43 | 613.65 | new high |

*(menampilkan 40 dari 49 baris; CSV lengkap ada di `results/`)*

## q05_rank_periods.sql  (5 baris)

| yr | gold_myr_per_gram_avg | gold_real_yoy_pct_avg | rank_best_first |
|---|---|---|---|
| 2026 | 591.45 | 33.16 | 1 |
| 2025 | 474.72 | 33.1 | 2 |
| 2024 | 352.22 | 20.94 | 3 |
| 2023 | 286.63 | 9.96 | 4 |
| 2022 | 255.03 | 1.38 | 5 |

## q06_affordability_state.sql  (16 baris)

| year | state | income_median_rm_month | gold_myr_per_gram_year | grams_per_rm1000 | pct_of_median_income_per_gram | rank_most_affordable |
|---|---|---|---|---|---|---|
| 2024 | W.P. Kuala Lumpur | 10802.0 | 352.22 | 2.839 | 3.26 | 1 |
| 2024 | W.P. Putrajaya | 10769.0 | 352.22 | 2.839 | 3.27 | 2 |
| 2024 | Selangor | 10726.0 | 352.22 | 2.839 | 3.28 | 3 |
| 2024 | Johor | 7712.0 | 352.22 | 2.839 | 4.57 | 4 |
| 2024 | Pulau Pinang | 7386.0 | 352.22 | 2.839 | 4.77 | 5 |
| 2024 | W.P. Labuan | 7383.0 | 352.22 | 2.839 | 4.77 | 5 |
| 2024 | Melaka | 6891.0 | 352.22 | 2.839 | 5.11 | 7 |
| 2024 | Terengganu | 6627.0 | 352.22 | 2.839 | 5.31 | 8 |
| 2024 | Negeri Sembilan | 5591.0 | 352.22 | 2.839 | 6.3 | 9 |
| 2024 | Sarawak | 5504.0 | 352.22 | 2.839 | 6.4 | 10 |
| 2024 | Pahang | 4975.0 | 352.22 | 2.839 | 7.08 | 11 |
| 2024 | Perlis | 4950.0 | 352.22 | 2.839 | 7.12 | 12 |
| 2024 | Kedah | 4895.0 | 352.22 | 2.839 | 7.2 | 13 |
| 2024 | Sabah | 4890.0 | 352.22 | 2.839 | 7.2 | 13 |
| 2024 | Perak | 4687.0 | 352.22 | 2.839 | 7.51 | 15 |
| 2024 | Kelantan | 4083.0 | 352.22 | 2.839 | 8.63 | 16 |

## q07_retail_and_labour.sql  (6 baris)

| yr | gold_yoy_pct | cpi_yoy_pct | retail_sales_rm_million_avg | unemployment_pct | verdict |
|---|---|---|---|---|---|
| 2021 |  |  | 118142.9 | 4.27 | gold behind inflation |
| 2022 | 5.3 | 3.92 | 129543.2 | 3.82 | gold ahead of inflation |
| 2023 | 12.46 | 2.5 | 139467.2 | 3.43 | gold ahead of inflation |
| 2024 | 22.77 | 1.83 | 147169.6 | 3.25 | gold ahead of inflation |
| 2025 | 34.48 | 1.38 | 155417.6 | 3.03 | gold ahead of inflation |
| 2026 | 34.95 | 1.79 | 167897.3 | 2.95 | gold ahead of inflation |

## q08_validation.sql  (5 baris)

| check_name | result |
|---|---|
| gold trading days per month | 9 min / 23 max |
| fx quote days per month | 9 min / 23 max |
| months in the gold mart | 61 |
| CPI divisions covered | 14 |
| ECB vs BNM spot (MYR per USD) | ECB 4.086 vs BNM 4.0875 |

## q09_usd_decomposition.sql  (6 baris)

**Is the ringgit doing the work?** Gold is priced in dollars and bought in ringgit, so deflating to a third currency
separates the metal from the currency. `metal_only_contribution_pct` is the ringgit return with the currency effect
subtracted — the part the metal alone would have delivered.

| yr | months_counted | gold_usd_g | gold_myr_g | usd_myr | gold_usd_yoy_pct | fx_effect_pct | gold_myr_yoy_pct | metal_only_contribution_pct |
|---|---|---|---|---|---|---|---|---|
| 2021 | 3 | 57.88 | 242.19 | 4.1846 |  |  |  |  |
| 2022 | 12 | 58.03 | 254.95 | 4.3998 | 0.3 | 5.1 | 5.3 | 0.1 |
| 2023 | 12 | 62.84 | 286.63 | 4.5601 | 8.3 | 3.6 | 12.4 | 8.8 |
| 2024 | 12 | 77.2 | 352.22 | 4.5761 | 22.9 | 0.4 | 22.9 | 22.5 |
| 2025 | 12 | 111.21 | 474.72 | 4.2835 | 44.1 | -6.4 | 34.8 | 41.2 |
| 2026 | 9 | 147.01 | 589.2 | 4.0113 | 32.2 | -6.4 | 24.1 | 30.5 |

Reading it: in **2022 the metal contributed 0.1 points of a 5.3% ringgit return** — the entire gain was the ringgit.
By 2025–2026 the relationship reverses: the metal adds 30–41 points while the currency costs 6 points each year.

## q10_fx_subperiods.sql  (4 baris)

**Did the currency effect persist, or was it a phase?** Sub-periods taken from the actual path of USD/MYR.
`fx_share_of_return_pp` is how many percentage points of the ringgit return came from the currency;
`myr_price_if_fx_flat` is the counterfactual price had the exchange rate never moved.

| scope | period | gold_usd_g_start | gold_usd_g_end | usd_myr_start | usd_myr_end | gold_usd_return_pct | fx_effect_pct | gold_myr_return_pct | fx_share_of_return_pp | myr_price_if_fx_flat |
|---|---|---|---|---|---|---|---|---|---|---|
| full window | 2021-11 to 2026-09 | 58.51 | 140.35 | 4.1789 | 4.0704 | 139.9 | -2.6 | 133.6 | -6.2 | 586.5 |
| ringgit weakening | 2021-11 to 2024-02 | 58.51 | 65.55 | 4.1789 | 4.7679 | 12.0 | 14.1 | 27.8 | 15.8 | 273.92 |
| ringgit strengthening | 2024-02 to 2026-02 | 65.55 | 161.9 | 4.7679 | 3.9124 | 147.0 | -17.9 | 102.7 | -44.3 | 771.9 |
| recent rebound | 2026-02 to 2026-09 | 161.9 | 140.35 | 3.9124 | 4.0704 | -13.3 | 4.0 | -9.8 | 3.5 | 549.11 |

Reading it: over the **full window the ringgit contributed −2.6%** — it slightly *reduced* the return, and gold would
have cost RM586.50/g against the RM571.28/g actually recorded in September 2026. The currency only carried the
return during the weakening phase (2021-11 to 2024-02, +14.1% of the +27.8% total), and cost 17.9% during the
strengthening phase that followed. **"Gold protects you from a weak ringgit" is therefore period-dependent, not a
structural property** — which is the opposite of what the retail sales pitch assumes.
