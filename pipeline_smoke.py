#!/usr/bin/env python3
"""Optional encode pass: offline stub by default; live transformers if installed.
Run: python pipeline_smoke.py
Set LIVE_HF=1 to attempt transformers.pipeline feature-extraction.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "encode_cache.json"
CATALOG_PATH = ROOT / "catalog.json"


def stub_encode(tags):
    from mismatch import VOCAB
    return [1.0 if t in tags else 0.0 for t in VOCAB]


def live_encode(texts):
    from transformers import pipeline
    pipe = pipeline("feature-extraction", model="openai/clip-vit-base-patch32", revision="main")
    return pipe(texts[0], return_tensors=False)


def main() -> int:
    try:
        rows = json.loads(CATALOG_PATH.read_text())
    except FileNotFoundError:
        print("FAIL: catalog.json missing at", CATALOG_PATH)
        return 1

    live = os.environ.get("LIVE_HF") == "1"
    mode = "live-transformers" if live else "offline-stub"
    vectors = {}

    if live:
        try:
            for r in rows[:1]:
                vectors[r["sku"]] = {"mode": mode, "vector": live_encode([r.get("title") or ""])}
        except Exception as e:
            print("LIVE_HF failed; declare fallback in README. Error:", e)
            mode = "offline-stub-after-live-fail"
            live = False

    if not live:
        for r in rows:
            vectors[r["sku"]] = {"mode": mode, "vector": stub_encode(r.get("image_tags") or [])}

    OUT.write_text(json.dumps({"mode": mode, "vectors": vectors}, indent=2))
    print("wrote", OUT.name, "mode=", mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
