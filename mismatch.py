"""Catalog join: bag-of-words cosine between a listing's image_tags and its
title, flagged when the score drops below THRESHOLD.

image_tags stands in for a real image encoder (see encoder_pin.json for the
honest pin: lab-bow-v1, not a Hugging Face download). Swapping in live CLIP
later changes the pin's revision, not this contract.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

VOCAB = [
    "kiondo", "bag", "sisal", "navy", "nike", "tote", "white", "woven",
    "shoe", "canvas", "leso", "cloth", "maize", "red", "kitenge",
]
THRESHOLD = 0.25


def tokens(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


def bow(toks):
    idx = {t: i for i, t in enumerate(VOCAB)}
    v = [0.0] * len(VOCAB)
    for t in toks:
        if t in idx:
            v[idx[t]] += 1.0
    return v


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / ((na * nb) or 1.0)


def score_row(row):
    iv = bow(row.get("image_tags") or [])
    tv = bow(tokens(row.get("title") or ""))
    s = cosine(iv, tv)
    return {
        "sku": row["sku"],
        "score": round(s, 4),
        "flag": s < THRESHOLD,
    }


if __name__ == "__main__":
    path = ROOT / "catalog.json"
    try:
        rows = json.loads(path.read_text())
    except FileNotFoundError:
        print("FAIL: catalog.json not found next to mismatch.py", path)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        print("FAIL: catalog.json is not valid JSON:", e)
        raise SystemExit(1)
    out = [score_row(r) for r in rows]
    (ROOT / "mismatch_report.json").write_text(json.dumps(out, indent=2))
    print(out)
