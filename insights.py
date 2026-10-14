"""Turns a mismatch score into a seller-readable sentence. No silent title
rewrite happens anywhere in this file: a flagged row gets a review-queue
message, not a changed title.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from mismatch import score_row


def insight(row, scored):
    if scored["flag"]:
        sent = (
            "This listing is queued for review: the photo evidence and the title "
            "do not agree yet. Please check the photo and confirm or edit the title."
        )
    else:
        sent = "Photo tags and title look aligned."
    return {
        "sku": row["sku"],
        "score": scored["score"],
        "flag": scored["flag"],
        "seller_message": sent,
        "transcript": row.get("transcript") or "",
    }


if __name__ == "__main__":
    with_audio = ROOT / "catalog_with_audio.json"
    path = with_audio if with_audio.exists() else ROOT / "catalog.json"
    try:
        rows = json.loads(path.read_text())
    except FileNotFoundError:
        print("FAIL: catalog.json missing. Keep insights.py beside catalog.json.")
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        print("FAIL: catalog.json JSON error:", e)
        raise SystemExit(1)
    pack = [insight(r, score_row(r)) for r in rows]
    (ROOT / "insights.json").write_text(json.dumps(pack, indent=2))
    print("wrote insights.json", len(pack))
