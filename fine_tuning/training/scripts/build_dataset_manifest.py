#!/usr/bin/env python3
"""Build a consolidated manifest for fine-tuning datasets.

Scans a root directory (default: fine_tuning/datasets/processed) for *.jsonl files.
Collects:
  - relative_path
  - size_bytes
  - line_count (examples)
  - sha256 (file content)
  - first_timestamp (if an 'timestamp' field present in first JSON object)
  - sample_fields (union of keys in first 3 objects)
  - avg_chars_per_line (rough heuristic length)
Optionally estimates tokens (~ chars/4) for quick budgeting.

Usage:
  python build_dataset_manifest.py \
    --root fine_tuning/datasets/processed \
    --out  fine_tuning/datasets/manifests/processed_manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

CHAR_PER_TOKEN = 4.0  # coarse heuristic

EXCLUDE_DIR_NAMES = {"__pycache__", "archive", "vendor"}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_jsonl(p: Path) -> dict:
    line_count = 0
    total_chars = 0
    sample_objs = []
    first_timestamp = None
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            line_count += 1
            total_chars += len(line)
            if len(sample_objs) < 3:
                try:
                    obj = json.loads(line)
                    sample_objs.append(obj)
                    if first_timestamp is None and isinstance(obj, dict):
                        if "timestamp" in obj:
                            first_timestamp = obj["timestamp"]
                except Exception:
                    pass
    sample_fields = sorted(
        {k for o in sample_objs if isinstance(o, dict) for k in o.keys()}
    )
    avg_chars = (total_chars / line_count) if line_count else 0.0
    est_tokens = int(avg_chars * line_count / CHAR_PER_TOKEN) if line_count else 0
    return {
        "relative_path": str(p.as_posix()),
        "size_bytes": p.stat().st_size,
        "line_count": line_count,
        "sha256": sha256_file(p),
        "first_timestamp": first_timestamp,
        "sample_fields": sample_fields,
        "avg_chars_per_line": round(avg_chars, 2),
        "est_tokens": est_tokens,
    }


def build_manifest(root: Path) -> Dict[str, Any]:
    entries: List[dict] = []
    for path in root.rglob("*.jsonl"):
        if any(part in EXCLUDE_DIR_NAMES for part in path.parts):
            continue
        entries.append(scan_jsonl(path))
    total_lines = sum(e["line_count"] for e in entries)
    total_tokens = sum(e["est_tokens"] for e in entries)
    return {
        "root": str(root),
        "total_files": len(entries),
        "total_examples": total_lines,
        "total_est_tokens": total_tokens,
        "generated_by": "build_dataset_manifest.py",
        "entries": entries,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default="fine_tuning/datasets/processed",
        help="Root directory to scan",
    )
    ap.add_argument(
        "--out",
        default="fine_tuning/datasets/manifests/processed_manifest.json",
        help="Output manifest path",
    )
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")
    manifest = build_manifest(root)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(manifest, indent=2 if args.pretty else None)
    out_path.write_text(
        data + ("\n" if not data.endswith("\n") else ""), encoding="utf-8"
    )
    print(
        f"[manifest] Wrote {out_path} (files={manifest['total_files']} examples={manifest['total_examples']} est_tokens={manifest['total_est_tokens']})"
    )


if __name__ == "__main__":
    main()
