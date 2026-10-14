"""Hashes the generation prompt file and writes gen_pin.json so a later
re-run (or a reviewer) can prove the prompt that produced outputs/ hasn't
silently drifted.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "prompts" / "gen" / "kiondo_navy_stilllife_v1.txt"


def main() -> int:
    if not PROMPT.exists():
        print("FAIL prompt file missing:", PROMPT)
        return 1
    sha256 = hashlib.sha256(PROMPT.read_bytes()).hexdigest()
    pin = {"prompt_file": str(PROMPT.relative_to(ROOT)), "sha256": sha256}
    (ROOT / "gen_pin.json").write_text(json.dumps(pin, indent=2))
    print("wrote gen_pin.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
