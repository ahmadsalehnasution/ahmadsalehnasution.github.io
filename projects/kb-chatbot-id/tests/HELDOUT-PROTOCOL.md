# Held-out test protocol (P4)

The published figures (top-1 93.3%, refusal 10/10) were measured on a 40-question set that the 4.5 threshold was
chosen from. That makes them **in-sample**: they show the two score classes can be separated and where the cut
lands — not that the refusal survives questions nobody tuned against.

This protocol answers that properly. It is written **before** the held-out set is scored, so the result cannot be
quietly reshaped afterwards.

## Rules

1. **Written before running.** The 15 questions live in `tests/heldout.json` and are committed first. The commit
   hash is recorded inside the result file, so the order of events is checkable.
2. **The threshold does not move.** `scripts/run_heldout.py` uses the engine's `DEFAULT_THRESHOLD` (4.5) and takes no
   threshold argument. If the held-out set does badly, the honest response is to fix the retriever, not the cut.
3. **One run.** The set is scored once. Re-running after changing the threshold or the corpus turns it back into an
   in-sample test and destroys its only advantage.
4. **Whatever comes out gets published**, including a worse number than the in-sample one. A portfolio that only
   publishes flattering measurements is not evidence.
5. **No leakage.** `run_heldout.py` refuses to run if any question duplicates the original test set, and refuses any
   in-scope label whose `gold_slug` is not in the corpus. A wrong label is not a model failure; it is a broken test.

## Composition (10 in-scope + 5 out-of-scope)

**In-scope (10).** Questions a real reader would ask, spread across all 12 articles, phrased differently from the
original set — different angle, synonyms, or a concrete scenario instead of a definition. Not deliberately harder and
not deliberately easier; a fair sample of ordinary use.

**Out-of-scope (5), labelled by kind — because the two kinds fail differently:**

- `unrelated` (3): plainly outside the corpus, e.g. a passport procedure or a recipe. Easy; this is the case the
  in-sample set already tested.
- `gold-adjacent` (2): about gold or personal finance but **not answerable from these 12 articles** — for example a
  live today's-price question, or a product comparison the articles never make. These are the realistic failures a
  deployment would actually face, and the ones a keyword-driven retriever most often gets wrong. A system that refuses
  these is genuinely trustworthy; a system that answers them is guessing while sounding confident.

## What gets reported

- Top-1 and top-3 retrieval hit rate on the 10 in-scope questions
- How many in-scope questions were answered rather than wrongly refused
- Out-of-scope refusal rate, **split by kind** (`unrelated` vs `gold-adjacent`)
- Every wrong answer, quoted with the source it wrongly cited

The number that matters most is the `gold-adjacent` refusal rate. If it is lower than the `unrelated` rate, that is the
finding to publish: the system knows when a topic is foreign, but is less reliable at noticing when the topic is
familiar and the specific answer is absent.

## How to run (Wednesday session)

```bash
python3 scripts/run_heldout.py --check   # validate labels and leakage first
python3 scripts/run_heldout.py           # score once
```

Then: update the case-study page with the held-out result next to the in-sample one, commit, and verify the live page
shows both.
