#!/usr/bin/env python3
"""Deduplicate JSONL records by a hash of selected fields or full line.

Strategy:
  - Read input JSONL
  - Compute key: if --fields provided, concatenate their JSON-serialized values; else full line trimmed
  - Keep first occurrence, skip later duplicates
  - Report counts

Usage:
  python dedupe_jsonl.py --in file.jsonl --out file.dedup.jsonl --fields prompt response
  python dedupe_jsonl.py --in file.jsonl --out file.dedup.jsonl  (whole-line)
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def make_key(obj_line: str, obj, fields):
    if fields:
        parts = []
        for f in fields:
            (
                parts.append(json.dumps(obj.get(f), sort_keys=True))
                if isinstance(obj, dict)
                else parts.append("null")
            )
        base = "\u001f".join(parts)
    else:
        base = obj_line.strip()
    return hashlib.sha256(base.encode("utf-8", "ignore")).hexdigest()


def iter_jsonl(p: Path):
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.rstrip("\n")
            if not raw:
                continue
            yield raw


def dedupe(in_path: Path, out_path: Path, fields):
    seen = set()
    kept = 0
    skipped = 0
    with out_path.open("w", encoding="utf-8") as out:
        for line in iter_jsonl(in_path):
            try:
                obj = json.loads(line)
            except Exception:
                obj = None
            key = make_key(line, obj, fields)
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            out.write(line + "\n")
            kept += 1
    return kept, skipped


def main():
    ap = argparse.ArgumentParser(description="Deduplicate JSONL file")
    ap.add_argument("--in", dest="inp", required=True, help="Input JSONL")
    ap.add_argument("--out", dest="out", required=True, help="Output JSONL")
    ap.add_argument(
        "--fields", nargs="*", help="Optional list of fields to form dedupe key"
    )
    args = ap.parse_args()

    in_path = Path(args.inp)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    kept, skipped = dedupe(in_path, out_path, args.fields)
    print(
        f"[dedupe] input={in_path} kept={kept} skipped={skipped} (fields={args.fields or 'FULL_LINE'}) -> {out_path}"
    )


if __name__ == "__main__":
    main()
