#!/usr/bin/env python3
"""Run the P4 HELD-OUT test set: questions written after the threshold was chosen, used exactly once.

Why this exists: the published 10/10 refusal figure is in-sample — the threshold 4.5 was picked from the score gap of
the same 40 questions. This script answers the honest question: does the refusal hold on questions the threshold was
never chosen against?

Protocol (enforced by this script, not by good intentions):
  * the set lives in tests/heldout.json and is committed BEFORE the first run;
  * the threshold is NOT tuned here — it is the engine's DEFAULT_THRESHOLD, and the script refuses to pretend;
  * the script checks for leakage: an in-scope question whose wording duplicates the original test set is a warning;
  * every gold slug must exist in the corpus, or the label is wrong and the run is invalid;
  * the result is written once, whatever it says, and the file records the set's git commit.

Run:  python3 scripts/run_heldout.py
      python3 scripts/run_heldout.py --check      # validate the set without scoring it
"""
import json
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_engine as kb

ROOT = Path(__file__).resolve().parent.parent
HELDOUT = ROOT / "tests" / "heldout.json"
ORIGINAL = ROOT / "tests" / "testset.json"
OUT = ROOT / "results" / "heldout_results.json"


def load():
    if not HELDOUT.exists():
        sys.exit(f"Belum ada set held-out: {HELDOUT}\n"
                 f"Tulis 10 pertanyaan in-scope + 5 out-of-scope, commit dulu, baru jalankan.")
    data = json.loads(HELDOUT.read_text(encoding="utf-8"))
    in_scope = data.get("in_scope", [])
    oos = data.get("out_of_scope", [])
    if len(in_scope) != 10 or len(oos) != 5:
        sys.exit(f"Set harus 10 in-scope + 5 out-of-scope; sekarang {len(in_scope)} + {len(oos)}.")
    return data, in_scope, oos


def validate(in_scope, oos):
    """Label and leakage checks — run these BEFORE scoring anything."""
    slugs = {p.stem for p in (ROOT / "corpus").glob("*.md") if not p.name.startswith("_")}
    problems, warnings = [], []
    for q in in_scope:
        if q.get("gold_slug") not in slugs:
            problems.append(f"{q.get('id')}: gold_slug '{q.get('gold_slug')}' tidak ada di corpus")
    if ORIGINAL.exists():
        old = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        old_q = {" ".join(x["question"].lower().split()) for x in old["in_scope"] + old["out_of_scope"]}
        for q in in_scope + oos:
            if " ".join(q["question"].lower().split()) in old_q:
                warnings.append(f"{q.get('id')}: pertanyaan identik dengan test set lama (bocor)")
    if problems:
        sys.exit("Set tidak valid:\n  - " + "\n  - ".join(problems))
    if warnings:
        sys.exit("Kebocoran terdeteksi:\n  - " + "\n  - ".join(warnings))
    print(f"Set valid: {len(in_scope)} in-scope (semua gold slug ada) + {len(oos)} out-of-scope, tanpa duplikat.")


def commit_of(path: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h %ad", "--date=short",
                               "--", str(path)], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def main(check_only: bool) -> None:
    data, in_scope, oos = load()
    validate(in_scope, oos)
    if check_only:
        return

    threshold = kb.DEFAULT_THRESHOLD          # deliberately not a parameter
    k = 3
    idx = kb.build_index(ROOT / "corpus")

    rows_in, t1, t3, answered = [], 0, 0, 0
    for q in in_scope:
        r = kb.answer(q["question"], idx, k=k, threshold=threshold)
        cit = [c["link"].rstrip("/").split("/")[-1] for c in r["citations"]]
        hit1 = bool(cit) and cit[0] == q["gold_slug"]
        hit3 = q["gold_slug"] in cit
        t1 += hit1
        t3 += hit3
        answered += r["answered"]
        rows_in.append({"id": q["id"], "question": q["question"], "gold_slug": q["gold_slug"],
                        "top1": cit[0] if cit else None, "top1_hit": hit1, "top3_hit": hit3,
                        "answered": r["answered"], "score": r["score"]})

    rows_out, refused = [], 0
    for q in oos:
        r = kb.answer(q["question"], idx, k=k, threshold=threshold)
        refused += not r["answered"]
        rows_out.append({"id": q["id"], "question": q["question"], "kind": q.get("kind", "unlabelled"),
                         "refused": not r["answered"], "score": r["score"],
                         "wrongly_cited": (r["citations"][0]["title"] if r["citations"] else None)})

    n_in, n_out = len(in_scope), len(oos)
    summary = {
        "set_commit": commit_of(HELDOUT),
        "threshold_used": threshold,
        "threshold_tuned_on_this_set": False,
        "corpus_articles": len([p for p in (ROOT / "corpus").glob("*.md") if not p.name.startswith("_")]),
        "in_scope_questions": n_in,
        "out_of_scope_questions": n_out,
        "top1_hit_rate": round(t1 / n_in, 4),
        "top3_hit_rate": round(t3 / n_in, 4),
        "answered_rate_in_scope": round(answered / n_in, 4),
        "out_of_scope_refusal_rate": round(refused / n_out, 4),
        "out_of_scope_refusal_by_kind": {
            kind: f"{sum(1 for r in rows_out if r['kind'] == kind and r['refused'])}/"
                    f"{sum(1 for r in rows_out if r['kind'] == kind)}"
            for kind in sorted({r["kind"] for r in rows_out})
        },
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "in_scope": rows_in, "out_of_scope": rows_out},
                              ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== HELD-OUT RESULT (satu kali jalan, ambang tidak diubah) ===")
    for key, val in summary.items():
        print(f"  {key}: {val}")
    print("\n  Ditanya di luar cakupan tetapi tetap dijawab (ini kegagalan yang sebenarnya):")
    bad = [r for r in rows_out if not r["refused"]]
    for r in bad:
        print(f"    {r['id']} [{r['kind']}]: {r['question']} -> {r['wrongly_cited']} (skor {r['score']})")
    if not bad:
        print("    tidak ada")
    print(f"\n  Ditulis ke {OUT.relative_to(ROOT)}")
    print("  JANGAN ubah ambang lalu jalankan ulang — itu mengubah uji ini menjadi in-sample lagi.")
    if data.get("notes"):
        print("\n  Catatan penulis set:", data["notes"])


if __name__ == "__main__":
    main(check_only="--check" in sys.argv)
