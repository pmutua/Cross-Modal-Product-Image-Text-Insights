"""Gate for hf_pipeline.yaml: task must be an allowed Hub pipeline task,
model a Hub org/name id, revision pinned (not left as TODO), device present.
"""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PATH = ROOT / "hf_pipeline.yaml"
ALLOWED_TASKS = {"feature-extraction", "image-classification", "automatic-speech-recognition"}


def main(path: Path = DEFAULT_PATH) -> int:
    try:
        doc = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        print("FAIL: hf_pipeline.yaml missing")
        return 1
    if not isinstance(doc, dict):
        print("FAIL: hf_pipeline.yaml must be a mapping")
        return 1
    task = str(doc.get("task") or "").strip()
    model = str(doc.get("model") or "").strip()
    revision = str(doc.get("revision") or "").strip()
    device = str(doc.get("device") or "").strip()
    if task not in ALLOWED_TASKS:
        print("FAIL task must be one of", sorted(ALLOWED_TASKS), "got", task)
        return 1
    if not model or "/" not in model:
        print("FAIL model must be a Hub org/name id")
        return 1
    if revision in ("", "TODO"):
        print("FAIL revision must be pinned, not left as TODO")
        return 1
    if not device:
        print("FAIL device is required (e.g. cpu)")
        return 1
    print("pipeline yaml OK", task, model, revision, device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
