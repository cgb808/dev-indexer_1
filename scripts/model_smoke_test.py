#!/usr/bin/env python
"""Minimal model smoke test.

Checks:
1. torch import + CUDA availability
2. transformers import (no model download unless specified)
3. Prints a short report used by CI or manual task.

Exit code 0 even if GPU not present (informational).
"""
from __future__ import annotations
import json, os, sys

report = {"torch": None, "cuda": None, "transformers": None}

try:
    import torch  # type: ignore
    report["torch"] = torch.__version__
    report["cuda"] = bool(torch.cuda.is_available())
except Exception as e:  # noqa: BLE001
    report["torch"] = f"missing ({e.__class__.__name__})"
    report["cuda"] = False

try:
    import transformers  # type: ignore
    report["transformers"] = getattr(transformers, "__version__", "?")
except Exception as e:  # noqa: BLE001
    report["transformers"] = f"missing ({e.__class__.__name__})"

print(json.dumps(report, indent=2))

# Non-fatal status helps early bring-up.
missing = [k for k,v in report.items() if isinstance(v, str) and v.startswith("missing")]  # type: ignore
if missing:
    print(f"[info] Optional components missing: {', '.join(missing)}")
sys.exit(0)
