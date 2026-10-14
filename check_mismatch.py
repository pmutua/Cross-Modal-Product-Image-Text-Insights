"""Gold check: exits 1 unless KND-01 is unflagged and NK-99 is flagged."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _rows(report_path: Path, catalog_path: Path):
    if report_path.exists():
        return json.loads(report_path.read_text())
    from mismatch import score_row
    catalog = json.loads(catalog_path.read_text())
    return [score_row(r) for r in catalog]


def _find(rows, sku):
    for r in rows:
        if r["sku"] == sku:
            return r
    return None


def main(report_path: Path = ROOT / "mismatch_report.json", catalog_path: Path = ROOT / "catalog.json") -> int:
    rows = _rows(report_path, catalog_path)
    knd = _find(rows, "KND-01")
    nk = _find(rows, "NK-99")
    if knd is None or nk is None:
        print("FAIL: KND-01 or NK-99 missing from mismatch_report.json")
        return 1
    print("KND-01 score", knd["score"], "flag", knd["flag"])
    print("NK-99 score", nk["score"], "flag", nk["flag"])
    if knd["flag"] is not False or nk["flag"] is not True:
        print("FAIL: expected KND-01 unflagged and NK-99 flagged")
        return 1
    for sku in ("SHU-07", "KTG-14"):
        extra = _find(rows, sku)
        if extra is not None:
            print(sku, "score", extra["score"], "flag", extra["flag"])
            if extra["flag"] is not False:
                print("FAIL: expected", sku, "unflagged")
                return 1
    print("check_mismatch OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
