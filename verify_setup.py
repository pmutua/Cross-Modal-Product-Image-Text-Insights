#!/usr/bin/env python3
"""Environment check. Run: python verify_setup.py"""
import sys
from pathlib import Path

assert sys.version_info >= (3, 10), f"Need Python 3.10+, got {sys.version}"
import hashlib, math, os  # noqa: F401

ROOT = Path(__file__).resolve().parent
catalog = ROOT / "catalog.json"
if not catalog.exists():
    catalog.write_text("[]\n")
    print("STUB: wrote empty catalog.json")
else:
    print("OK catalog artifact:", catalog)

try:
    import yaml  # noqa: F401
    print("OK pyyaml available (hf_pipeline.yaml can be checked)")
except ImportError:
    print("WARN: pyyaml not installed; pip install -r requirements.txt before running check_pipeline_yaml.py")

print("Base imports OK")
print("Python", sys.version.split()[0])
