# Gold vs Malaysian Household Indicators

**Status: prototype.** A reproducible SQL + BI analysis, not a production system. Every number below is produced by
the queries in `sql/` from the raw files in `data/raw/`; nothing is typed in by hand.

## Business problem

Gold is sold in Malaysia as an inflation hedge, and the sales pitch is usually just "the price keeps going up".
That claim is only testable against the household's own numbers: how fast are consumer prices actually rising, what
does a gram cost relative to a median monthly income, and how much of the rise is the gold price versus the ringgit.
A retailer who can answer those three questions sells differently — and prices differently.

## Role of the agent (and what stayed with me)

- **The agent did:** fetching the raw series, writing the SQL model and the query framework, running every query,
  producing the result tables, and flagging data-quality problems (partial months, mismatched grains).
- **I did:** choosing the business question, choosing the sources and rejecting ones that blocked automated access,
  writing the validation check, and reading the results critically — the 0.944 correlation in `q07` is an artefact
  of two rising trends, not evidence that retail spending drives the gold price. That correction is mine, not the
  agent's.

## Data sources (all free, no API key)

| File | Source | Grain | Rows |
|---|---|---|---|
| `gold_daily_yahoo.csv` | Yahoo Finance chart API, symbol `GC=F` (COMEX gold futures) | daily close, USD/oz | 1258 |
| `fx_usd_myr_ecb.csv` | frankfurter.dev (ECB reference rates) | daily USD→MYR | 1739 |
| `cpi_headline.csv` | OpenDOSM / data.gov.my `cpi_headline` | monthly CPI index, 14 divisions | 7840 |
| `retail_trade.csv` | OpenDOSM `iowrt` (wholesale & retail trade) | monthly, RM million | 299 |
| `labour_force.csv` | OpenDOSM `lfs_month` | monthly | 200 |
| `hh_income_state.csv` | OpenDOSM `hh_income_state` | 2-yearly, by state | 319 |
| `fuel_price.csv` | OpenDOSM `fuelprice` | weekly pump price | 963 |
| `bnm_usd_spot.csv` | Bank Negara Malaysia OpenAPI | single day, **validation only** | 1 |

`data/raw/_provenance.csv` records the exact URL, fetch date and row count for every file.

## Flow

```
 fetch raw (01_fetch.py, ~2.5s)
      gold (Yahoo)      fx (ECB)      CPI / retail / labour / income / fuel (OpenDOSM)      BNM spot
            │              │                            │                                      │
            └──────┬───────┘                            │                                      │
                   ▼                                    ▼                                      │
        stg_* monthly staging tables  ← clean grain, one row per month ─────────────────────────┤
                   │                                                                           │
                   ▼                                                                           │
   mart_gold_myr_monthly : USD/oz × USD/MYR ÷ 31.1034768 = RM per gram                         │
                   │                                                                           │
                   ▼                                                                           │
   mart_monthly : gold, CPI, retail, unemployment, fuel on one monthly row                     │
                   │                                                                           │
                   ▼                                                                           │
   mart_affordability : annual gold price ÷ median household income by state                   │
                   │                                                                           ▼
                   ▼                                                            q08_validation.sql cross-checks
   sql/q01…q07 → results/*.csv → results/RESULTS.md                             ECB vs BNM before publication
```

## How to run

```bash
python 01_fetch.py            # pull the raw CSVs (network)
python 02_build_and_query.py  # build gold_my.duckdb, write sql/*.sql, run everything into results/
```

Measured end-to-end refresh: **2.5 s fetch + 0.6 s build and query = 3.1 s** (13 Oct 2026). By hand, assembling the
same comparison from the source websites takes an afternoon, and it cannot be reproduced identically the next month.

## Findings

1. **A gram of gold went from RM239.38 (Oct 2021) to RM548.80 (Oct 2026) — +129.3% in ringgit over five years.**
   Malaysian consumer prices rose 12.6% over the same period (CPI overall, 122.1 in Jan 2021 → 137.5 in Aug 2026).
2. **Gold beat inflation in 47 of 47 months** measured since Oct 2022. The margin peaked at +55.1 points (Jan 2026)
   and the weakest month was still +0.7 points. Real return by year, ranked: 2026 (+33.2 pts), 2025 (+33.1),
   2024 (+20.9), 2023 (+10.0), 2022 (+1.4).
3. **The trend is not monotonic.** Gold peaked at RM633.41/g in Feb 2026 and stands 13.4% below that peak in the
   latest month — the same series that "always goes up" gave back an eighth of its value inside eight months.
4. **Affordability is uneven across states.** At the 2024 average price of RM352.22/g, one gram cost 3.26% of a
   median monthly household income in Kuala Lumpur but 8.63% in Kelantan (RM4,083) — a 2.6× difference for the
   same product. RM1,000 of median income bought 2.84 grams.
5. **Context, not explanation:** unemployment fell to 2.9% by Aug 2026 and monthly retail sales grew from
   RM118.1bn (2021) to RM167.9bn (2026). The annual correlation between gold and retail sales is 0.944 — see the
   limitations, it demonstrates nothing causal.

## Validation

`q08_validation.sql` runs five checks before anything is published. The load-bearing one is the cross-source check
on the exchange rate: the ECB reference rate on the fetch date was **4.086 MYR/USD** against Bank Negara Malaysia's
official spot rate of **4.0875** — a 0.04% gap, so the FX series is fit to convert prices with. The same query also
reports month coverage (9–23 trading days) and flags that the current month is partial.

## Limitations

- **Gold data is COMEX futures (`GC=F`), not the Malaysian retail price.** Retail gold carries a dealer premium and
  a buy/sell spread; those are not in this dataset, so the analysis covers the international price converted to
  ringgit, not what a walk-in customer pays.
- **Ringgit weakness is inside the result.** Part of the ringgit gain is a weaker ringgit, not a stronger gold
  market. A USD-denominated version of the same query would separate the two, and is a fair next step.
- **Income data is a moving 2-yearly survey (latest 2024)** joined onto a monthly price series — the affordability
  figures are indicative, and 2025–2026 affordability is estimated with the 2024 income baseline.
- **The 0.944 gold/retail correlation is not evidence.** Both series trend upward over the window; correlation on
  two trending series is spurious by construction. A real test needs differenced or seasonally adjusted series.
- **No transaction costs, taxes or zakat** are modelled; the real return is a price return only.
- **The current month is partial** (9 trading days at fetch time) and should not be compared against full months.

## Measured benefit

- Refresh time: an afternoon of manual cross-checking → **3.1 seconds**, repeatable and identical each run.
- Every published figure traces to a query file, so a challenged number can be re-derived on demand rather than
  argued over.
- Not measured: revenue or conversion effect. This is an analysis artefact; no commercial outcome has been
  attributed to it.

## Repository layout

```
01_fetch.py            fetch raw data + write provenance
02_build_and_query.py  build gold_my.duckdb, write sql/*.sql, run queries, render results/RESULTS.md
sql/q01…q08.sql        the query framework: one business question per file, SQL concept in the header comment
results/*.csv          one CSV per query + RESULTS.md (all tables rendered)
data/raw/*.csv         raw inputs + _provenance.csv
```
