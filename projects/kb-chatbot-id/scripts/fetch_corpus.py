#!/usr/bin/env python3
"""Fetch the P4 knowledge-base corpus from suksesdenganemas.com (Ahmad's own articles).

Read-only: this script only GETs public pages. It never writes to the WordPress site.
Stdlib only (urllib), so it runs on macOS and in the container without pip.
"""
import json, re, html, sys, time, urllib.request, urllib.parse
from pathlib import Path

BASE = "https://suksesdenganemas.com"
API = BASE + "/wp-json/wp/v2/posts"

SLUGS = [
    "cara-membaca-harga-emas",
    "spread-harga-beli-dan-jual-emas",
    "kadar-kemurnian-emas",
    "emas-24-karat",
    "cara-membedakan-emas-asli-dan-palsu",
    "zakat-emas-cara-hitung-nisab",
    "menabung-emas-modal-kecil",
    "dollar-cost-averaging-emas-cara-investasi",
    "emas-untuk-dana-darurat",
    "keamanan-menyimpan-emas",
    "spot-price-emas-vs-harga-antam",
    "emas-digital-vs-emas-fisik",
]

def strip_html(raw: str) -> str:
    # drop scripts/styles/media markup and inline style attrs
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<img[^>]*>", " ", raw, flags=re.I)
    raw = re.sub(r"<figure.*?</figure>", " ", raw, flags=re.S | re.I)
    # block-level -> newline
    raw = re.sub(r"</(p|h[1-6]|li|ul|ol|div|blockquote|tr)>", "\n", raw, flags=re.I)
    raw = re.sub(r"<(p|h[1-6]|li|ul|ol|div|blockquote|tr)[^>]*>", "\n", raw, flags=re.I)
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    # collapse whitespace, keep paragraph breaks
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in raw.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)

def fetch(slug: str) -> dict | None:
    url = API + "?slug=" + urllib.parse.quote(slug) + "&_fields=id,date,link,title,content"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (portfolio corpus builder)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data:
        return None
    post = data[0]
    title = re.sub(r"<[^>]+>", "", post["title"]["rendered"]).strip()
    body = strip_html(post["content"]["rendered"])
    return {
        "slug": slug,
        "id": post["id"],
        "date": post["date"],
        "link": post["link"],
        "title": title,
        "body": body,
    }

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    corpus = root / "corpus"
    corpus.mkdir(exist_ok=True)
    rows = []
    ok, fail = 0, 0
    for slug in SLUGS:
        try:
            doc = fetch(slug)
            if doc is None:
                print(f"  ! no post for slug {slug}", file=sys.stderr)
                fail += 1
                continue
            rows.append(doc)
            # individual markdown file
            md = f"# {doc['title']}\n\n**Sumber:** {doc['link']}\n**Tanggal:** {doc['date'][:10]}\n\n{doc['body']}\n"
            (corpus / f"{slug}.md").write_text(md, encoding="utf-8")
            ok += 1
            print(f"  ok  {slug}  ({len(doc['body'].split())} kata)")
        except Exception as e:  # noqa: BLE001
            print(f"  X   {slug}: {e}", file=sys.stderr)
            fail += 1
        time.sleep(0.4)
    # provenance JSONL
    with (corpus / "_provenance.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nFetched {ok} articles, {fail} failed -> corpus/_provenance.jsonl")

if __name__ == "__main__":
    main()
