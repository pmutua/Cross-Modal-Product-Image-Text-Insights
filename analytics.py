"""Per-category and overall flag_rate, with the sample size (n) that makes
the rate honest rather than a bare percentage.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "catalog.json"
REPORT_PATH = ROOT / "mismatch_report.json"


def rates(catalog, reports):
    flags = {r["sku"]: r["flag"] for r in reports}
    buckets = {}
    for row in catalog:
        cat = row.get("category") or "unknown"
        b = buckets.setdefault(cat, {"n": 0, "n_flagged": 0})
        b["n"] += 1
        if flags.get(row["sku"]):
            b["n_flagged"] += 1
    out = {}
    tot_n = tot_f = 0
    for cat, b in buckets.items():
        out[cat] = {
            "n": b["n"],
            "n_flagged": b["n_flagged"],
            "flag_rate": round(b["n_flagged"] / b["n"], 4) if b["n"] else 0.0,
        }
        tot_n += b["n"]
        tot_f += b["n_flagged"]
    out["overall"] = {
        "n": tot_n,
        "n_flagged": tot_f,
        "flag_rate": round(tot_f / tot_n, 4) if tot_n else 0.0,
    }
    return out


if __name__ == "__main__":
    try:
        cat = json.loads(CATALOG_PATH.read_text())
        rep = json.loads(REPORT_PATH.read_text())
    except FileNotFoundError as e:
        print("FAIL missing input:", e)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        print("FAIL bad JSON:", e)
        raise SystemExit(1)
    out = rates(cat, rep)
    (ROOT / "rates.json").write_text(json.dumps(out, indent=2))
    print(out)
