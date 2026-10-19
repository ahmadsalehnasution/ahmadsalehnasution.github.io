#!/usr/bin/env python3
"""P4 Knowledge Base Chatbot — retrieval engine (stdlib only).

Retrieval-augmented answering over a small Indonesian corpus of Ahmad's own
articles. The "answer" is extractive: the most relevant passage is returned
verbatim together with its source citation, so the system cannot fabricate a
claim. When nothing in the corpus scores above the threshold it says it does
not know, instead of guessing. BM25 is implemented here (no external deps) so
the whole thing runs on any machine with Python 3.
"""
import json, re, math
from collections import Counter
from pathlib import Path

STOPWORDS = set("""
yang dan di ke dari untuk dengan adalah ini itu pada sebagai atau juga tidak akan sudah bisa dalam karena
oleh bahwa jika maka saat secara lebih sangat para antara hingga namun sedang agar sementara setelah sebelum
selama ketika bagi tanpa terhadap seperti salah maka kalau pun sudah belum sedang telah ada apa siapa mana
bagaimana kenapa mengapa kapan anda saya kita mereka kamu dia ia itu tersebut sebuah suatu beberapa setiap
para maupun serta ialah ialah merupakan ialah baik jadi hanya saja lagi pun bisa dapat harus perlu boleh
agar supaya demi guna buat mengenai tentang terhadap daripada daripada ialah ialah makin semakin ialah
kembali tetap langsung cukup perlu mungkin justru sedang sedangkan padahal sebab karena ialah ialah baru lama
""".split())

K1 = 1.5
B = 0.75

DEFAULT_THRESHOLD = 4.5  # inside the observed score gap (out-of-scope max 4.21, in-scope min 5.25)

def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS and len(t) > 1]

class BM25:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.n = len(docs)
        self.doc_tf = [Counter(tokenize(d["text"])) for d in docs]
        self.doc_len = [sum(c.values()) for c in self.doc_tf]
        self.avgdl = sum(self.doc_len) / self.n if self.n else 0.0
        self.df = Counter()
        for tf in self.doc_tf:
            self.df.update(tf.keys())

    def score(self, query_tokens: list[str]) -> list[float]:
        q = Counter(query_tokens)
        scores = []
        for i in range(self.n):
            s = 0.0
            for term, qf in q.items():
                f = self.doc_tf[i].get(term, 0)
                if f == 0:
                    continue
                idf = math.log(1 + (self.n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                denom = f + K1 * (1 - B + B * self.doc_len[i] / self.avgdl)
                s += idf * (f * (K1 + 1)) / denom * qf
            scores.append(s)
        return scores

def chunk_article(slug: str, title: str, link: str, body: str, max_words: int = 160) -> list[dict]:
    paragraphs = [p.strip() for p in body.split("\n") if p.strip()]
    chunks, current = [], []
    for p in paragraphs:
        current.append(p)
        if sum(len(x.split()) for x in current) >= max_words:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return [
        {"slug": slug, "title": title, "link": link, "chunk_idx": i, "text": c}
        for i, c in enumerate(chunks) if c.strip()
    ]

def build_index(corpus_dir: Path) -> BM25:
    docs = []
    for md in sorted(corpus_dir.glob("*.md")):
        if md.name.startswith("_"):
            continue
        raw = md.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ").strip() if raw.startswith("#") else md.stem
        link = ""
        m = re.search(r"\*\*Sumber:\*\*\s*(\S+)", raw)
        if m:
            link = m.group(1)
        # body = everything after the metadata block (first blank line after the metadata)
        lines = raw.splitlines()
        body_start = 0
        for idx, ln in enumerate(lines):
            if ln.strip() == "":
                body_start = idx + 1
                break
        body = "\n".join(lines[body_start:])
        docs.extend(chunk_article(md.stem, title, link, body))
    return BM25(docs)

def answer(question: str, index: BM25, k: int = 3, threshold: float = DEFAULT_THRESHOLD) -> dict:
    qt = tokenize(question)
    scores = index.score(qt)
    top = max(scores) if scores else 0.0
    if top < threshold:
        return {
            "answered": False,
            "score": round(top, 3),
            "answer": "Saya tidak menemukan jawabannya di dokumen yang saya miliki.",
            "citations": [],
        }
    ranked = sorted(
        [(s, index.docs[i]) for i, s in enumerate(scores) if s > 0],
        key=lambda x: -x[0],
    )[:k]
    # collapse duplicate source articles, keep the best chunk per article
    seen, best = set(), []
    for s, d in ranked:
        if d["slug"] in seen:
            continue
        seen.add(d["slug"])
        best.append((s, d))
    top_chunk = best[0][1]
    citations = [
        {"title": d["title"], "link": d["link"], "score": round(s, 3), "chunk_idx": d["chunk_idx"]}
        for s, d in best
    ]
    return {
        "answered": True,
        "score": round(top, 3),
        "answer": top_chunk["text"],
        "citations": citations,
    }

if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parent.parent
    idx = build_index(root / "corpus")
    q = " ".join(sys.argv[1:]) or "Bagaimana cara membaca harga emas?"
    r = answer(q, idx)
    print(json.dumps(r, ensure_ascii=False, indent=2))
