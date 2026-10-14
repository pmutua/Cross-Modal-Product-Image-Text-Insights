"""Audio-text integration stand-in: a `.ogg.txt` sidecar beside an audio
filename is the Whisper stub this capstone grades. Returns '' for missing
audio rather than failing the whole listing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def transcribe_seller_note(audio_path: str) -> str:
    sidecar = Path(str(audio_path) + ".txt")
    if sidecar.exists():
        return sidecar.read_text().strip()
    return ""  # live Whisper would go here


if __name__ == "__main__":
    demo = ROOT / "audio" / "knd-01.ogg"
    assert transcribe_seller_note(str(demo)) == "Navy sisal kiondo, hand-woven, leather handles."
    assert transcribe_seller_note(str(ROOT / "audio" / "missing.ogg")) == ""
    print("transcribe_seller_note(audio/knd-01.ogg) =", transcribe_seller_note(str(demo)))
