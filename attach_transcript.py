"""Copies each catalog row and adds a `transcript` field from the matching
audio sidecar (or ''), writing catalog_with_audio.json. Never mutates the
input rows.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def attach(rows):
    out = []
    for r in rows:
        p = ROOT / "audio" / (r["sku"].lower() + ".ogg.txt")
        row = dict(r)
        row["transcript"] = p.read_text().strip() if p.exists() else ""
        out.append(row)
    return out


if __name__ == "__main__":
    rows = json.loads((ROOT / "catalog.json").read_text())
    (ROOT / "catalog_with_audio.json").write_text(json.dumps(attach(rows), indent=2))
    print("attached")
