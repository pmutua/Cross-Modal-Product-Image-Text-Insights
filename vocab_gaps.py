"""Coverage note: which title tokens the 15-word VOCAB silently drops.
Run after mismatch.py; feeds the ethics note's 'Whose language' section.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from mismatch import VOCAB, tokens

CATALOG_PATH = ROOT / "catalog.json"


def gaps(catalog):
    known = set(VOCAB)
    rows = []
    for r in catalog:
        for t in tokens(r.get("title") or ""):
            if t not in known:
                rows.append({"sku": r["sku"], "token": t})
    return rows


if __name__ == "__main__":
    cat = json.loads(CATALOG_PATH.read_text())
    g = gaps(cat)
    (ROOT / "vocab_gaps.json").write_text(json.dumps(g, indent=2))
    print("gaps", len(g))
