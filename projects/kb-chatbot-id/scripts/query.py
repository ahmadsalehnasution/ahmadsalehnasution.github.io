#!/usr/bin/env python3
"""CLI: ask the knowledge base one question. Prints the verbatim passage plus
citations, or an explicit "I don't know" when nothing scores above threshold."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_engine as kb

def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python3 scripts/query.py \"pertanyaan Anda\"")
        return
    idx = kb.build_index(Path(__file__).resolve().parent.parent / "corpus")
    q = " ".join(sys.argv[1:])
    r = kb.answer(q, idx)
    print(f"Q: {q}\n")
    if not r["answered"]:
        print(f"[TIDAK TAHU] {r['answer']}  (skor {r['score']}, ambang {kb.DEFAULT_THRESHOLD})")
        return
    print(f"JAWABAN (kutipan langsung, skor {r['score']}):\n{r['answer']}\n")
    print("SUMBER:")
    for c in r["citations"]:
        print(f"  - {c['title']}  [{c['link']}]  (skor {c['score']})")

if __name__ == "__main__":
    main()
