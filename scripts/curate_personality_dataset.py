"""Curate a conversational fine-tune dataset from SlimOrca (or other HF datasets).

Implements / extends the user-provided snippet:
  - Loads dataset (default: Open-Orca/SlimOrca train split)
  - Extracts first human turn
  - Scores via keyword heuristic (positive and exclusion lists)
  - Filters to score > 0 (and not excluded)
  - Random samples target size (default 5000)
  - Writes JSONL output

Enhancements:
  * CLI arguments for dataset name, split, target size, output path
  * Optional --stream mode to process large sets with constant memory (no full pandas)
  * Stats summary (kept vs dropped, top keywords)
  * Optional deterministic shuffling seed
  * Duplicate detection on human query (first occurrence kept) with --dedupe flag
  * Keyword sets overridable via external JSON file (--rules rules.json)

Rules JSON format example:
{
  "good_keywords": {"explain": 2, "brainstorm": 3},
  "bad_keywords": ["medical advice", "nsfw"]
}

Usage examples:
  python curate_personality_dataset.py \
      --dataset Open-Orca/SlimOrca --split train --target-size 5000 \
      --output personality_engine_dataset.jsonl

  python curate_personality_dataset.py --stream --target-size 3000 --dedupe

Environment variables:
  HF_DATASETS_CACHE (optional) to control datasets cache path.

NOTE: Streaming mode processes sequentially & retains only curated examples; if
      target-size reached early and --early-stop set, it exits sooner.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter
from typing import Dict, Iterable, List, Tuple

try:
    from datasets import load_dataset
except ImportError:
    print("datasets package not installed. Run: pip install datasets", file=sys.stderr)
    raise

try:
    import pandas as pd  # type: ignore
except ImportError:
    pd = None  # Pandas optional in streaming mode

DEFAULT_GOOD = {
    'explain': 2, 'what is': 2, 'how does': 2, 'summarize': 2,
    'brainstorm': 3, 'ideas for': 3, 'what if': 3, 'write a story': 3,
    'plan': 2, 'compare': 2, 'can you help': 1
}
DEFAULT_BAD = [
    'nsfw', 'political', 'unethical', 'financial advice',
    'medical advice', 'legal advice', 'python code for', 'generate a script'
]


def load_rules(path: str | None) -> Tuple[Dict[str, int], List[str]]:
    if not path:
        return DEFAULT_GOOD, DEFAULT_BAD
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    good = data.get('good_keywords', DEFAULT_GOOD)
    bad = data.get('bad_keywords', DEFAULT_BAD)
    return good, bad


def extract_first_human(conversation) -> str:
    if not conversation:
        return ''
    for turn in conversation:
        if turn.get('from') == 'human':
            return (turn.get('value') or '').lower()
    return ''


def score_query(q: str, good: Dict[str, int], bad: List[str]) -> int:
    if not q:
        return 0
    for b in bad:
        if b in q:
            return -1
    s = 0
    for k, pts in good.items():
        if k in q:
            s += pts
    return s


def curate_streaming(dataset_name: str, split: str, good: Dict[str, int], bad: List[str], target: int, seed: int,
                     dedupe: bool, early_stop: bool) -> List[dict]:
    ds_iter = load_dataset(dataset_name, split=split, streaming=True)
    rng = random.Random(seed)
    reservoir: List[dict] = []
    seen_queries = set() if dedupe else None
    kept = 0
    total = 0
    keyword_counter = Counter()
    for row in ds_iter:  # type: ignore
        total += 1
        q = extract_first_human(row.get('conversations'))
        if dedupe and q in seen_queries:  # type: ignore[arg-type]
            continue
        sc = score_query(q, good, bad)
        if sc > 0:
            row['_score'] = sc
            row['_human_query'] = q
            kept += 1
            if seen_queries is not None:
                seen_queries.add(q)
            # reservoir sampling to uniformly keep up to target
            if len(reservoir) < target:
                reservoir.append(row)
            else:
                # Replace with decreasing probability
                j = rng.randint(0, kept - 1)
                if j < target:
                    reservoir[j] = row
            for gk in good.keys():
                if gk in q:
                    keyword_counter[gk] += 1
        if early_stop and kept >= target:
            break
        if total % 5000 == 0:
            print(f"[stream] processed={total} kept={kept} reservoir={len(reservoir)}", file=sys.stderr)
    print(f"[stream] done total={total} kept={kept} returned={len(reservoir)}", file=sys.stderr)
    if keyword_counter:
        top_kw = keyword_counter.most_common(10)
        print(f"[stream] top keywords: {top_kw}", file=sys.stderr)
    return reservoir


def curate_full(dataset_name: str, split: str, good: Dict[str, int], bad: List[str], target: int, seed: int, dedupe: bool) -> List[dict]:
    if pd is None:
        raise SystemExit("pandas required for non-streaming mode (pip install pandas)")
    ds = load_dataset(dataset_name, split=split)
    print(f"Loaded dataset rows: {len(ds)}")
    df = ds.to_pandas()
    df['_human_query'] = df['conversations'].apply(extract_first_human)
    df['_score'] = df['_human_query'].apply(lambda q: score_query(q, good, bad))
    curated = df[df['_score'] > 0]
    if dedupe:
        curated = curated.drop_duplicates(subset=['_human_query'])
    print(f"Curated rows after score>0{' + dedupe' if dedupe else ''}: {len(curated)}")
    if len(curated) > target:
        curated = curated.sample(n=target, random_state=seed)
    # Convert back to list of dicts (drop helper fields except we may leave _score for analysis)
    return curated.to_dict(orient='records')


def write_jsonl(rows: Iterable[dict], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            r_out = dict(r)
            # Remove temporary helper fields
            for k in ['_human_query']:
                r_out.pop(k, None)
            f.write(json.dumps(r_out, ensure_ascii=False) + '\n')


def main():  # pragma: no cover
    ap = argparse.ArgumentParser(description="Curate conversational dataset for fine-tuning")
    ap.add_argument('--dataset', default='Open-Orca/SlimOrca')
    ap.add_argument('--split', default='train')
    ap.add_argument('--target-size', type=int, default=5000)
    ap.add_argument('--output', default='personality_engine_dataset.jsonl')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--stream', action='store_true', help='Use streaming (memory efficient)')
    ap.add_argument('--early-stop', action='store_true', help='Stop once target-size reached (stream only)')
    ap.add_argument('--dedupe', action='store_true', help='Dedupe by first human query')
    ap.add_argument('--rules', help='Path to JSON rules file overriding keyword lists')
    args = ap.parse_args()

    good, bad = load_rules(args.rules)
    print("Step 1: Loading dataset (streaming=" + str(args.stream) + ") ...")
    if args.stream:
        rows = curate_streaming(args.dataset, args.split, good, bad, args.target_size, args.seed, args.dedupe, args.early_stop)
    else:
        rows = curate_full(args.dataset, args.split, good, bad, args.target_size, args.seed, args.dedupe)
    print(f"Step 2: Writing {len(rows)} examples -> {args.output}")
    write_jsonl(rows, args.output)
    print("Done.")


if __name__ == '__main__':  # pragma: no cover
    main()
