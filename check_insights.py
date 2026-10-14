"""Gate: required keys present, a flagged row's seller_message at least 20
characters, and 'verified'/'authentic' banned as overclaims a review queue
hasn't earned yet.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["sku", "score", "flag", "seller_message"]


def main(path: Path = ROOT / "insights.json") -> int:
    try:
        rows = json.loads(path.read_text())
    except FileNotFoundError:
        print("FAIL: insights.json not found")
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: bad JSON", e)
        return 1
    for r in rows:
        for k in REQUIRED:
            if k not in r:
                print("FAIL missing", k, r)
                return 1
        if r["flag"] and len(r["seller_message"]) < 20:
            print("FAIL short message on", r["sku"])
            return 1
        msg = r["seller_message"].lower()
        if "verified" in msg or "authentic" in msg:
            print("FAIL overclaim", r["sku"])
            return 1
    print("insights OK", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
