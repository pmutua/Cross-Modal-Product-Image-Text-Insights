"""No OpenAI image key / no Diffusers in this environment: write the same
meta JSON a live DALL-E or Stable Diffusion call would have produced,
plus a tiny real (but trivial) PNG so outputs/ never holds a fake claim
of a real render. not_a_photo_of_the_sku stays true either way.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "prompts" / "gen" / "kiondo_navy_stilllife_v1.txt"
OUT = ROOT / "outputs"


def write_stub_png(path: Path):
    """Write a tiny valid PNG without requiring Pillow."""
    import struct
    import zlib

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = zlib.compress(b"\x00" + bytes([0, 0, 128]))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", raw)
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def main() -> int:
    if not PROMPT.exists():
        print("FAIL prompt file missing:", PROMPT, "-- a generator must never invent its own input")
        return 1
    text = PROMPT.read_text()
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "knd-01_stub.png"
    write_stub_png(stub)
    meta = {
        "sku": "KND-01",
        "generator": "stub",
        "format": "png",
        "prompt_file": str(PROMPT.relative_to(ROOT)),
        "prompt_chars": len(text),
        "not_a_photo_of_the_sku": True,
    }
    meta_path = OUT / "knd-01_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print("wrote", stub.name, "(PNG stub image)")
    print(meta_path.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
