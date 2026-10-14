"""query -> top-k SKUs, scored by the same bag-of-words cosine as
mismatch.py (over image_tags, since that's what actually stands in for an
image encoder here).

Toy recall note: for the 2 queries exercised below, recall@1 is 2/2 (the
intended SKU lands first). That is a teaching-sized n=2 sample over a
4-row catalog, not a claim about retrieval quality at scale -- see
vocab_gaps.json for why a 15-word VOCAB will miss real queries.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from mismatch import bow, cosine, tokens


def search(query, catalog, k=3):
    qv = bow(tokens(query))
    scored = []
    for row in catalog:
        iv = bow(row.get("image_tags") or [])
        scored.append((cosine(qv, iv), row["sku"]))
    scored.sort(reverse=True)
    return scored[:k]


if __name__ == "__main__":
    catalog = json.loads((ROOT / "catalog.json").read_text())
    r1 = search("navy sisal kiondo", catalog, k=2)
    r2 = search("canvas white shoe", catalog, k=2)
    assert r1[0][1] == "KND-01"
    assert r2[0][1] == "SHU-07"
    print("search('navy sisal kiondo') =", r1)
    print("search('canvas white shoe') =", r2)
    print("toy recall@1 over these 2 queries: 2/2 (n=2, teaching sample)")
