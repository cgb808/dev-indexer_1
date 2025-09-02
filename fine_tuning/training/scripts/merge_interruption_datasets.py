#!/usr/bin/env python3
"""Merge interruption handling related JSONL files into a unified dataset.

Rules:
  - Base + specialized + existing interruption_handling_training + session_management (if present)
  - Deduplicate by (instruction,input,output) triple
  - Preserve metadata fields
  - Annotate each record with `merge_source` array (which component(s) it came from)
  - Output path: fine_tuning/datasets/processed/interruption_handling/interruption_all_merged.jsonl

Usage:
  python merge_interruption_datasets.py \
    --dir fine_tuning/datasets/processed/interruption_handling \
    --out fine_tuning/datasets/processed/interruption_handling/interruption_all_merged.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

PRIMARY_FILES = [
    "interruption_handling_training.jsonl",
    "session_management_training.jsonl",
    "interruption_recovery_base_400.jsonl",
    "interruption_recovery_specialized_100.jsonl",
]

KEY_FIELDS = ("instruction", "input", "output")


def read_jsonl(p: Path):
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def key_for(obj) -> Tuple[str, str, str]:
    return tuple(obj.get(f, "") for f in KEY_FIELDS)


def merge(dir_path: Path):
    merged = []
    index: Dict[Tuple[str, str, str], Dict] = {}
    for fname in PRIMARY_FILES:
        fp = dir_path / fname
        if not fp.exists():
            continue
        for obj in read_jsonl(fp):
            k = key_for(obj)
            if k in index:
                srcs = index[k].setdefault("merge_source", [])
                # ensure uniqueness
                if fname not in srcs:
                    srcs.append(fname)
            else:
                obj["merge_source"] = [fname]
                index[k] = obj
    # finalize
    merged = list(index.values())
    return merged


def write_jsonl(objs, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dir", default="fine_tuning/datasets/processed/interruption_handling"
    )
    ap.add_argument(
        "--out",
        default="fine_tuning/datasets/processed/interruption_handling/interruption_all_merged.jsonl",
    )
    args = ap.parse_args()

    d = Path(args.dir)
    if not d.exists():
        raise SystemExit(f"Directory not found: {d}")
    merged = merge(d)
    write_jsonl(merged, Path(args.out))
    print(
        f"[merge] wrote {args.out} records={len(merged)} sources_scanned={len(PRIMARY_FILES)}"
    )


if __name__ == "__main__":
    main()
