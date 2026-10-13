# Indonesian Market Brief Agent

**Status: personal, running.** The agent is live (a Hermes skill plus a weekly scheduled job) and produces drafts
that a human approves before anything is published. It serves my own gold business and doubles as my market
intelligence practice — it is not a production system for any employer.

## Business problem

Monitoring the Indonesian gold market by hand means opening BPS, Bank Indonesia, Pegadaian/Logam Mulia and a few
news sites, then reconciling figures that disagree and dates that do not line up. The expensive failure is not
missing news — it is **publishing a number that is stale or wrong**. A single out-of-date interest rate in a
customer conversation does more damage than a week of missed headlines.

So the agent is built around one rule: **no claim is published that was not fetched and read at its source.**

## Role of the agent

| The agent does | The human does |
|---|---|
| Fetches BPS, BI, gold-price and media sources on a schedule | Sets the topic scope and the review standard |
| Records claim → value → source → type → data date → fetch status | Approves, edits or rejects the draft |
| Rejects any claim whose page failed to fetch, and says why | Decides what may be shared with customers |
| Drafts the brief in Indonesian and saves it to Drive | Never delegates the publish decision to the agent |

## Tools

- Hermes Agent (this runtime) with a dedicated skill, `indonesia-market-brief`, holding the source list, the
  verification rules and the output format
- Web search + page extraction tools for the fetch-and-verify loop
- A cron schedule (Monday 08:00 WIB / 01:00 UTC) so the brief appears without being remembered
- Google Drive for storage; the brief is delivered to Telegram as a draft

## Flow

```
Monday 01:00 UTC (scheduled)
      │
      ▼
confirm the date  →  fetch in fixed order: BPS inflation → BI IHK release → BI-Rate indicator page
      │                                     → JISDOR → gold retail (primary, else media citing it) → spot
      ▼
one row per claim: claim | value | source | type | data date | fetch status
      │
      ├── page fetched and figure found in the text  ──►  eligible for the brief
      └── page failed / figure absent                ──►  "sources rejected", with the reason
      ▼
derived figures computed only from fetched values, formula stated
      ▼
draft written (Indonesian, ≤1 page) → saved to Drive → delivered as DRAFT
      ▼
[APPROVAL GATE] Ahmad approves, edits or rejects — nothing is published by the agent
```

## Usage example (first real run, 13 October 2026)

The brief covers inflation, the policy rate, the exchange rate and the gold price, and it reports its own
verification record. Two things in that run are the reason the rule exists:

1. **A stale number was caught.** The first search result for "BI-Rate" was a Bank Indonesia press release dated
   **9 June 2026** saying 5.50%. The BI indicator page showed the rate had been **5.75% since 18 June 2026**, held
   at the 23 September 2026 meeting. Without the "check the source's date, not the headline" rule, the brief would
   have published a rate two months out of date.
2. **Three sources were rejected rather than used.** Two media pages returned fetch errors and one conflicting
   headline claimed a price far away from other reports; the official Logam Mulia price table is JavaScript-rendered
   and not machine-readable. The brief therefore states plainly that the latest verified Antam retail price is from
   1 October 2026 — instead of quietly quoting an unverified figure.

## Test results

| Metric | Result (first run, 13 Oct 2026) |
|---|---|
| Source pages attempted | 8 |
| Claims published | 8 |
| Published claims traced to a page that was fetched and read | 8 / 8 (100%) |
| Claims admitted from search snippets without fetching | 0 |
| Sources rejected before publication | 3 (2 fetch failures, 1 non-machine-readable table) |
| Stale-data errors caught by the date rule | 1 (BI-Rate 5.50% → 5.75%) |
| Primary vs secondary sources in the citation table | 6 primary, 2 secondary (labelled) |
| Published without human approval | 0 |

The honest benefit claim is therefore about **error catch rate and traceability**, not time saved: manual
preparation time for the same brief has not been measured, and until it is, no time-saving number is claimed.

## Limitations

- Scope is fixed to gold, CPI, the policy rate and USD/IDR. Tax, zakat and regulation are deliberately out of scope.
- Two of eight sources failed to fetch; on a different day the failure set will differ, so the brief can never
  guarantee the freshest retail price.
- The retail price comes from media citing the official page, not from the official page directly — labelled
  secondary, but still second-hand.
- Derived figures mix data dates (1 October retail vs 12 October spot) and are flagged as indicative; a strict
  comparison needs same-day inputs.
- One human reviewer only, so there is no inter-rater check on what counts as "verified".
- No cost control on the number of fetches per run, and no automatic detection of a source changing its URL scheme.
- The agent cannot detect a source that is itself wrong; it can only detect that the figure is where the source says.

## How to run

```bash
# manual run
hermes --profile career "run the indonesia-market-brief skill and save this week's brief"

# scheduled: Monday 08:00 WIB (01:00 UTC / 09:00 MYT) — cron job id e3f7fec7b256, next run 19 Oct 2026
```

Output lands in `home/tracker/proyek/P3 - Indonesian Market Brief Agent/briefs/` and is mirrored to Drive folder
`Proyek P3 - Indonesian Market Brief Agent`.
