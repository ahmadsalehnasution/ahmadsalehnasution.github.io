# Knowledge Base Chatbot (Indonesian, retrieval + citation + "I don't know")

**Status: prototype (personal project).** A retrieval-augmented question-answering system over a small corpus
of my own published articles. It answers only from the documents, cites the source of every answer, and says
"I don't know" when nothing in the corpus is relevant — it never fabricates. It is a demo of a retrieval and
guardrail design, not a production system for any employer, and it has no paying users.

## Business problem

Answers about a product or policy are inconsistent when the knowledge lives scattered across documents, and the
expensive failure is a confident answer that is wrong. A system that answers **only** from official documents,
cites its source, and is willing to say "there is nothing in my documents about that" is safer than one that
guesses. The test below measures exactly those three behaviours.

## What the system does, and what stays with the human

| The system | The human |
|---|---|
| Fetches articles, splits them into passages, indexes them | Chooses which documents are authoritative and in scope |
| Ranks passages with BM25 and returns the most relevant one verbatim | Writes the test set and the gold (correct) source per question |
| Cites title + URL for every answer | Sets the relevance threshold and judges correctness |
| Refuses (says "I don't know") when the top score is below threshold | Decides what may be shown to a customer |

The answer is **extractive**: the most relevant passage is returned word-for-word with its citation, so the system
cannot invent a number that is not in a document. Generation (rewording into a natural answer) is deliberately
left out of this prototype.

## Tools

- Python 3 standard library only — no vector database, no paid embedding or model API
- `urllib` to fetch the WordPress REST API of my own site (read-only)
- BM25 scoring implemented from scratch in `scripts/kb_engine.py` (Okapi BM25, k1=1.5, b=0.75, Indonesian stopword list)
- Corpus: 12 of my own published articles from suksesdenganemas.com on gold saving and investment

## Flow

```
corpus articles (suksesdenganemas.com, fetched via REST API)
        ↓
split each article into ~160-word passages  →  tokenize (lowercase, drop Indonesian stopwords)
        ↓
index passages with BM25 (term frequency + inverse document frequency)
        ↓
user question  →  tokenize  →  score every passage
        ↓
top score ≥ 4.5  ──►  return top passage VERBATIM + citations (title, URL, score)
top score <  4.5  ──►  "Saya tidak menemukan jawabannya di dokumen yang saya miliki."
        ↓
(unanswered questions are a signal that the knowledge base has a gap)
```

## Usage example (real runs)

**In scope — "Apa itu spread harga emas dan bagaimana cara menghitungnya?"**

> Answer (verbatim passage, score 5.254): "…FAQ — 1. Apa arti spread harga emas? Selisih antara harga saat
> membeli dan harga saat menjual kembali emas. 2. Apakah spread membuat investasi emas rugi? Tidak, bagian
> normal transaksi — jangka panjang kenaikan harga bisa melewati selisih tersebut…"
>
> Citations: **Spread Harga Beli dan Jual Emas: Panduan Lengkap** (suksesdenganemas.com/spread-harga-beli-dan-jual-emas/),
> and Zakat Emas as a lower-ranked supporting passage.

**Out of scope — "Bagaimana cara membuat paspor di kantor imigrasi?"**

> "Saya tidak menemukan jawabannya di dokumen yang saya miliki." (top score 3.39, below the 4.5 threshold)

## Test results — in-sample (40 questions) and held-out (15 questions)

| Metric | Result |
|---|---|
| Corpus | 12 articles, 47 passages |
| Test set | 30 in-scope questions + 10 out-of-scope questions |
| Top-1 retrieval hit (correct source ranked first) | 28 / 30 = **93.3%** |
| Top-3 retrieval hit (correct source in the citations) | 29 / 30 = **96.7%** |
| In-scope questions answered (not falsely refused) | 30 / 30 = 100% |
| Out-of-scope questions correctly refused | 10 / 10 = **100%** |
| Out-of-scope questions wrongly answered (fabrication) | **0** |
| In-scope top-score range | min 5.25 · median 9.39 · max 19.58 |
| Out-of-scope top-score range | min 0.00 · median 1.42 · max 4.21 |

### Threshold sensitivity (what the 4.5 choice buys and costs)

| Threshold | Top-1 | In-scope answered | Out-of-scope refused |
|---|---|---|---|
| 4.0 | 93.3% | 30 / 30 | 9 / 10 — one slips through |
| **4.5 (used)** | **93.3%** | **30 / 30** | **10 / 10** |
| 5.0 | 93.3% | 30 / 30 | 10 / 10 |
| 5.5 | 90.0% | 29 / 30 — one refused wrongly | 10 / 10 |

The threshold (4.5) sits inside the natural gap between the two groups — out-of-scope questions share at most one
or two generic words with the corpus (top score 4.21), while every in-scope question shares many content words
(top score 5.25 and up). The sweep matters as much as the single number: 4.5 and 5.0 behave identically, so the
cut is not knife-edge, and the table shows exactly what breaks on either side.

**Read the refusal figure with its caveat.** The threshold was chosen from the score gap of *this same test set*,
so 10/10 is an **in-sample** result: it demonstrates that the two classes are separable and where the cut lands,
not that unseen questions would be refused at the same rate. A held-out question set is the next honest step and
has since been written and run once; the result is below, and it is worse.

The two top-1 misses are honest, not bugs: the corpus contains near-duplicate pairs of articles that make the same
point in different words ("emas is a long-term asset, not a quick-profit trade" appears in both the spread article
and the price-reading article; "pure gold is soft, so jewellery is alloyed" appears in both the 24-karat article and
the purity article). Both misses were recovered by the top-3 citations.

### Held-out test — 15 questions, written after the threshold was frozen

The protocol in `tests/HELDOUT-PROTOCOL.md` was followed exactly: 10 in-scope questions across 10 different
articles (one per article, none a reworded copy of the original 30), plus 5 out-of-scope questions in two labelled
kinds — 3 `unrelated` and 2 `gold-adjacent` (about gold or personal finance but unanswerable from these 12
articles). The set was committed (`543b440`) before it was scored, and the threshold was not moved.

| Metric | Held-out | In-sample |
|---|---|---|
| Top-1 retrieval hit | 8 / 10 = **80.0%** | 93.3% |
| Top-3 retrieval hit | 10 / 10 = **100%** | 96.7% |
| In-scope answered | 10 / 10 = 100% | 30 / 30 |
| Out-of-scope refused | 2 / 5 = **40.0%** | 10 / 10 = 100% |
| — `unrelated` | 2 / 3 | not separated |
| — `gold-adjacent` | **0 / 2** | not separated |
| In-scope top-score range | min 8.17 · median 16.11 · max 40.89 | min 5.25 · max 19.58 |
| Out-of-scope top-score range | min 3.23 · median 4.54 · max 6.41 | min 0.00 · max 4.21 |

**The refusal rate did not generalise: 10 of 10 in-sample became 2 of 5 held-out.** Retrieval held up; the
abstention did not. The classes overlap across the two sets — the highest held-out out-of-scope score (6.41) is
above the lowest in-sample in-scope score (5.25) — so a single top-score cut fitted to one gap cannot separate
them in general.

Answered when it should have refused (detail in `results/heldout_results.json`):

| Question | Kind | Score | Source it wrongly cited |
|---|---|---|---|
| Mana yang lebih baik untuk dana pensiun, emas atau reksa dana saham? | gold-adjacent | 6.405 | Dollar Cost Averaging Emas — Cara Investasi Cerdas |
| Berapa harga emas Antam hari ini di Jakarta? | gold-adjacent | 4.544 | Spot Price Emas Dunia vs Harga Antam |
| Bagaimana cara memilih jurusan kuliah yang sesuai minat? | unrelated | 5.218 | Emas Digital vs Emas Fisik |

The pattern the protocol predicted is the one that occurred: foreign-topic questions are mostly caught, while
gold-adjacent questions that reuse the corpus vocabulary are answered with confidence. That is the dangerous
failure — a stale price sounds like an answer.

Nothing was retuned after the result: no threshold change in either direction, and no edit to the set, because
either would turn the run back into an in-sample test. The fix belongs in the retriever and must be judged on a
new held-out set.

## Limitations

- **Extractive only.** It returns the passage verbatim; it does not write a natural-language answer, so a
  paraphrased question may surface the right passage in a raw, unpolished form.
- **Lexical retrieval.** BM25 matches words, not meaning. A synonym or paraphrase ("buyback" vs "jual kembali")
  can miss until both terms appear in the corpus.
- **Small, single-topic corpus.** 12 articles on gold, one language (Indonesian). Results do not generalise.
- **Threshold is corpus-specific and in-sample.** 4.5 was calibrated on this corpus's score gap — and on the same
  test set used to report the results. A different document set needs its own calibration, and a held-out question
  set now exists and it broke the refusal rate (2 of 5), so 4.5 is a fitted value, not a validated one.
- **No multi-turn memory, no access control, no rate limiting** — it is a single-user local demo.
- **One evaluator (me).** The gold source for each question was assigned by one person, with no inter-rater check.

## Benefit that can be demonstrated

Not time saved (never measured). The demonstrable benefit is **no fabricated answers**: 10 of 10 out-of-scope
questions were refused instead of answered (10 of 10 in-sample, but only 2 of 5 held-out — see above), and every returned answer is a
verbatim passage with a clickable source, so a reader can check it. Unanswered questions double as a gap list for the knowledge base itself.

## How to run

```bash
# one question
python3 scripts/query.py "Apa itu spread harga emas?"

# the full test set and metrics (threshold defaults to the engine's 4.5)
python3 scripts/run_eval.py

# any other threshold, to see the trade-off for yourself
python3 scripts/run_eval.py 5.0

# the held-out set: validate labels and leakage, then score once (no threshold argument by design)
python3 scripts/run_heldout.py --check
python3 scripts/run_heldout.py

# rebuild the corpus from the live site (read-only)
python3 scripts/fetch_corpus.py
```

Artefacts: `corpus/` (fetched articles + provenance), `tests/testset.json`, `results/eval_results.json`
(per-question detail), `tests/heldout.json` (the held-out set, committed before scoring),
`results/heldout_results.json` (held-out detail, including the sources wrongly cited),
`tests/HELDOUT-PROTOCOL.md` (the rules), `scripts/` (engine, CLI, eval, held-out runner, fetch).
