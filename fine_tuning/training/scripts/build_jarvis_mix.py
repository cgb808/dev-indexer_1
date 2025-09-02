#!/usr/bin/env python3
"""Build Jarvis mix dataset from manifest (mix_config_jarvis_v1.yaml).

Minimal first implementation: loads manifest, iterates non-gap buckets, performs simple deterministic sampling,
normalizes basic fields, writes combined JSONL + stats.

Sampling policies implemented subset:
  - full
  - full_if_<=target_else_hash_sample
  - hash_sample (uniform by sha256 hash)

Future: implement hash_sample_merge_dedup, richer normalization, artifact validation.
"""
from __future__ import annotations
import json, hashlib, os, sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import yaml

ROOT = Path(__file__).resolve().parents[3]  # repo root
MANIFEST_PATH = ROOT / 'fine_tuning/datasets/manifests/mix_config_jarvis_v1.yaml'
OUTPUT_DIR = ROOT / 'fine_tuning/datasets/processed/jarvis_mix_v1'

@dataclass
class BucketSpec:
    name: str
    target: int
    sampling: str
    sources: List[Path]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def deterministic_pick(items: List[Dict[str, Any]], target: int) -> List[Dict[str, Any]]:
    if len(items) <= target:
        return items
    # stable order by sha256(content_hash or instruction+response)
    decorated = []
    for r in items:
        base = r.get('content_hash') or sha256_text((r.get('instruction','') + '||' + r.get('response',''))[:10000])
        decorated.append((base, r))
    decorated.sort(key=lambda t: t[0])
    return [r for _h, r in decorated[:target]]


def load_source(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        print(f"[warn] source missing {path}")
        return rows
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                obj=json.loads(line)
                rows.append(obj)
            except Exception:
                continue
    return rows


def apply_sampling(rows: List[Dict[str, Any]], spec: BucketSpec) -> List[Dict[str, Any]]:
    if spec.sampling == 'full':
        return rows[:spec.target] if len(rows) > spec.target else rows
    if spec.sampling == 'full_if_<=target_else_hash_sample':
        return rows if len(rows) <= spec.target else deterministic_pick(rows, spec.target)
    if spec.sampling == 'hash_sample':
        return deterministic_pick(rows, spec.target)
    # fallback
    return deterministic_pick(rows, spec.target)


def normalize_row(r: Dict[str, Any]) -> Dict[str, Any]:
    # Basic trimming
    for k in ('instruction','response'):
        if isinstance(r.get(k), str):
            r[k]=r[k].strip()
    if 'content_hash' not in r:
        r['content_hash']=sha256_text((r.get('instruction','') + '||' + r.get('response',''))[:10000])
    return r


def main():
    if not MANIFEST_PATH.exists():
        print('[error] manifest missing', MANIFEST_PATH)
        return 2
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    buckets = manifest.get('buckets', {})
    included: List[Dict[str, Any]] = []
    stats = {}
    for name, cfg in buckets.items():
        if isinstance(cfg, dict) and cfg.get('gap'):
            continue
        target = cfg.get('target_count')
        sources = [ROOT / 'fine_tuning/datasets' / s for s in cfg.get('source_files', [])]
        sampling = cfg.get('sampling','hash_sample')
        spec = BucketSpec(name=name, target=target, sampling=sampling, sources=sources)
        all_rows: List[Dict[str, Any]] = []
        for src in spec.sources:
            all_rows.extend(load_source(src))
        sampled = apply_sampling(all_rows, spec)
        sampled = [normalize_row(r) for r in sampled]
        for r in sampled:
            r['bucket'] = name
        included.extend(sampled)
        stats[name] = {'available': len(all_rows), 'selected': len(sampled), 'target': target}
        print(f"[bucket] {name} selected={len(sampled)} target={target} avail={len(all_rows)}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_jsonl = OUTPUT_DIR / manifest['output']['final_jsonl'] if manifest.get('output') else OUTPUT_DIR / 'jarvis_mix_v1_dataset.jsonl'
    with out_jsonl.open('w', encoding='utf-8') as f:
        for r in included:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    stats_path = OUTPUT_DIR / (manifest['output']['stats_json'] if manifest.get('output') else 'jarvis_mix_v1_stats.json')
    (stats_path).write_text(json.dumps({'buckets': stats, 'total': len(included)}, indent=2))
    print(f"[done] wrote {len(included)} rows -> {out_jsonl}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
