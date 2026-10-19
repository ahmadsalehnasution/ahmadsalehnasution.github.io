#!/usr/bin/env python3
"""Run the P4 test set and measure retrieval hit rate, rejection rate and
false-acceptance. Stdlib only. Outputs results/eval_results.json and a summary.
"""
import json, statistics, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_engine as kb

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = kb  # placeholder; we read below

def main(threshold: float = 0.5, k: int = 3) -> None:
    idx = kb.build_index(ROOT / "corpus")
    ts = json.loads((ROOT / "tests" / "testset.json").read_text(encoding="utf-8"))

    in_scope = ts["in_scope"]
    out_of_scope = ts["out_of_scope"]

    # --- score distributions (calibration transparency) ---
    def top_score(q: str) -> float:
        return max(idx.score(kb.tokenize(q))) if idx.n else 0.0

    ins_scores = [top_score(q["question"]) for q in in_scope]
    out_scores = [top_score(q["question"]) for q in out_of_scope]
    print(f"In-scope  top-score: min={min(ins_scores):.3f}  median={statistics.median(ins_scores):.3f}  max={max(ins_scores):.3f}")
    print(f"Out-scope top-score: min={min(out_scores):.3f}  median={statistics.median(out_scores):.3f}  max={max(out_scores):.3f}")
    print(f"Threshold = {threshold}")

    # --- in-scope evaluation ---
    top1_hits = top3_hits = answered = false_reject = 0
    in_rows = []
    for q in in_scope:
        r = kb.answer(q["question"], idx, k=k, threshold=threshold)
        slugs = [c["title"] for c in r["citations"]]
        # citation slugs: rebuild from the answer's citations (title only) — map to slug via link
        cit_slugs = [c["link"].rstrip("/").split("/")[-1] for c in r["citations"]]
        top1 = cit_slugs[0] == q["gold_slug"] if cit_slugs else False
        top3 = q["gold_slug"] in cit_slugs
        ans = r["answered"]
        top1_hits += top1
        top3_hits += top3
        answered += ans
        false_reject += (not ans)
        in_rows.append({
            "id": q["id"], "question": q["question"], "gold_slug": q["gold_slug"],
            "top1": cit_slugs[0] if cit_slugs else None, "top1_hit": top1,
            "top3_hits": top3, "answered": ans, "score": r["score"],
        })

    # --- out-of-scope evaluation ---
    rejected = false_accept = 0
    out_rows = []
    for q in out_of_scope:
        r = kb.answer(q["question"], idx, k=k, threshold=threshold)
        rej = not r["answered"]
        rejected += rej
        false_accept += r["answered"]
        out_rows.append({
            "id": q["id"], "question": q["question"], "rejected": rej,
            "score": r["score"],
            "accepted_source": (r["citations"][0]["title"] if r["citations"] else None),
        })

    n_in, n_out = len(in_scope), len(out_of_scope)
    summary = {
        "corpus_articles": len([m for m in (ROOT / "corpus").glob("*.md") if not m.name.startswith("_")]),
        "in_scope_questions": n_in,
        "out_of_scope_questions": n_out,
        "threshold": threshold,
        "k": k,
        "top1_hit_rate": round(top1_hits / n_in, 4),
        "top3_hit_rate": round(top3_hits / n_in, 4),
        "answered_rate_in_scope": round(answered / n_in, 4),
        "false_rejection_rate": round(false_reject / n_in, 4),
        "out_of_scope_rejection_rate": round(rejected / n_out, 4),
        "false_acceptance_rate": round(false_accept / n_out, 4),
        "in_scope_scores": {"min": round(min(ins_scores), 3), "median": round(statistics.median(ins_scores), 3), "max": round(max(ins_scores), 3)},
        "out_of_scope_scores": {"min": round(min(out_scores), 3), "median": round(statistics.median(out_scores), 3), "max": round(max(out_scores), 3)},
    }

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "eval_results.json").write_text(
        json.dumps({"summary": summary, "in_scope": in_rows, "out_of_scope": out_rows},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== SUMMARY ===")
    for kk, vv in summary.items():
        print(f"{kk}: {vv}")
    print("\nFalse-rejected in-scope questions (answered=False):")
    for r in in_rows:
        if not r["answered"]:
            print(f"  {r['id']}: {r['question']} (score={r['score']})")
    print("\nFalse-accepted out-of-scope questions (answered=True):")
    for r in out_rows:
        if not r["rejected"]:
            print(f"  {r['id']}: {r['question']} -> {r['accepted_source']}")

if __name__ == "__main__":
    main(threshold=float(sys.argv[1]) if len(sys.argv) > 1 else 0.5)
