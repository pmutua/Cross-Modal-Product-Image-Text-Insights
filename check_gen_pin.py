"""Gate: the hash in gen_pin.json must match the current prompt file bytes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(pin_path: Path = ROOT / "gen_pin.json") -> int:
    pin = json.loads(pin_path.read_text())
    path = ROOT / pin["prompt_file"]
    got = sha(path)
    if got != pin["sha256"]:
        print("GEN PIN MISMATCH", got, pin["sha256"])
        return 1
    print("gen pin OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
