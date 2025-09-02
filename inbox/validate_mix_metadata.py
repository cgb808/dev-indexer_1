#!/usr/bin/env python
"""Validate a built mix JSONL for required metadata fields.
Usage:
  python training/jarvis_mix/validate_mix_metadata.py --input path/to/mix.jsonl \
      --required persona readability_level affect_tone
"""
import argparse, json, sys
from collections import Counter

def main(inp: str, required: list[str]):
    missing_counts = Counter()
    total = 0
    with open(inp,'r') as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                missing_counts['__invalid_json'] += 1
                continue
            meta = obj.get('meta') or {}
            for r in required:
                if r not in meta or meta[r] in (None,''):
                    missing_counts[r]+=1
    if total == 0:
        print('[error] no records read', file=sys.stderr)
        sys.exit(1)
    print('[report] total_records', total)
    for k,v in missing_counts.items():
        print(f'[missing] {k} {v}')
    # Non-zero missing treated as failure for CI
    failures = {k:v for k,v in missing_counts.items() if v>0}
    if failures:
        print('[fail] metadata validation failures present', file=sys.stderr)
        sys.exit(2)
    print('[ok] metadata validation passed')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--required', nargs='+', required=True)
    args = ap.parse_args()
    main(args.input, args.required)
