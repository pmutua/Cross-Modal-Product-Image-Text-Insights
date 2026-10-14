"""Gate: the four required headings exist, each has a concrete (not
slogan-only) body, and no 'unhackable'-style overclaim appears anywhere.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEADS = ["Who is in the photos", "Whose language", "Generated pixels", "Review path"]
MIN_BODY = 40  # characters of argument under each heading


def sections(text: str):
    lines = text.splitlines()
    cur = None
    bodies = {h: [] for h in HEADS}
    for line in lines:
        raw = line.strip()
        if raw.startswith("#"):
            title = raw.lstrip("#").strip()
            cur = None
            for h in HEADS:
                if title.lower() == h.lower():
                    cur = h
                    break
            continue
        if cur:
            bodies[cur].append(line)
    return bodies


def main(path: Path = ROOT / "ethics_note.md") -> int:
    try:
        text = path.read_text()
    except FileNotFoundError:
        print("FAIL: ethics_note.md missing")
        return 1
    low = text.lower()
    if "unhackable" in low:
        print("FAIL overclaim")
        return 1
    bodies = sections(text)
    for h in HEADS:
        body = "\n".join(bodies[h]).strip()
        if not body:
            print("FAIL empty section:", h)
            return 1
        if len(body) < MIN_BODY:
            print("FAIL section too thin (< %d chars):" % MIN_BODY, h)
            return 1
        if not any(len(s.strip()) >= 20 for s in body.split(".")):
            print("FAIL need a concrete sentence under", h)
            return 1
    print("ethics headings OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
