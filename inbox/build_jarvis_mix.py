#!/usr/bin/env python
"""Build a unified Jarvis training mix from bucket definitions.

Implements:
- Manifest load & schema validate
- Bucket sampling with target fractions
- Optional per-bucket filters (future extension)
- Hash-based dedup across all messages (SHA256 of normalized conversation)
- Metadata enforcement (global + per-bucket) with stats
- Drift warnings if realized fraction deviates > tolerance (default 5%)
- Deterministic sampling via --seed

Planned extensions (TODO):
- hash_sample_merge_dedup (currently implemented as hash_dedup) with collision stats
- Gap reporting for missing required metadata fields
- Group proportion balancing improvements (currently only warns)

Output: JSONL file of conversations with merged `meta` plus builder provenance fields

Each source JSONL line must contain: {"messages": [...], "meta": {...}} at minimum.
"""
from __future__ import annotations
import argparse, json, os, glob, math, hashlib, random, sys
from dataclasses import dataclass, field
from typing import List, Dict, Any

try:
    import jsonschema
except ImportError:
    jsonschema = None

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'mix_manifest.schema.json')

@dataclass
class BucketSpec:
    name: str
    source_glob: str
    target_fraction: float
    filters: Dict[str, Any] = field(default_factory=dict)
    min_samples: int | None = None
    max_samples: int | None = None
    metadata_required: List[str] = field(default_factory=list)

@dataclass
class Manifest:
    version: str
    description: str | None
    total_target: int
    hash_dedup: bool
    metadata_required_global: List[str]
    buckets: List[BucketSpec]


def load_manifest(path: str) -> Manifest:
    with open(path,'r') as f:
        data = json.load(f)
    if jsonschema:
        with open(SCHEMA_PATH,'r') as sf:
            schema = json.load(sf)
        jsonschema.validate(data, schema)
    buckets = [BucketSpec(**b) for b in data['buckets']]
    return Manifest(
        version=data.get('version','0.0.0'),
        description=data.get('description'),
        total_target=data['total_target'],
        hash_dedup=data.get('hash_dedup', True),
        metadata_required_global=data.get('metadata_required_global', []),
        buckets=buckets
    )


def iter_source_lines(pattern: str):
    for path in glob.glob(pattern, recursive=True):
        try:
            with open(path,'r') as f:
                for line in f:
                    if line.strip():
                        yield path, line
        except FileNotFoundError:
            continue


def normalize_conversation(obj: Dict[str,Any]) -> str:
    msgs = obj.get('messages') or []
    parts = []
    for m in msgs:
        role = m.get('role','')
        content = (m.get('content') or '').strip()
        parts.append(f'{role}:{content}')
    return '\n'.join(parts)


def hash_conv(obj: Dict[str,Any]) -> str:
    norm = normalize_conversation(obj).encode('utf-8')
    return hashlib.sha256(norm).hexdigest()


def sample_bucket(spec: BucketSpec, total_target: int, rng: random.Random) -> List[Dict[str,Any]]:
    desired = spec.target_fraction * total_target
    desired_int = math.ceil(desired)
    rows: List[Dict[str,Any]] = []
    for path, line in iter_source_lines(spec.source_glob):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        # TODO: filters support
        obj['__source_file'] = os.path.relpath(path)
        rows.append(obj)
    if spec.min_samples and len(rows) < spec.min_samples:
        print(f'[warn] bucket {spec.name} available {len(rows)} < min {spec.min_samples}', file=sys.stderr)
    rng.shuffle(rows)
    if spec.max_samples:
        rows = rows[:spec.max_samples]
    if len(rows) > desired_int:
        rows = rows[:desired_int]
    return rows


def enforce_metadata(objs: List[Dict[str,Any]], required: List[str]) -> Dict[str,int]:
    missing_counts = {k:0 for k in required}
    for o in objs:
        meta = o.get('meta') or {}
        for k in required:
            if k not in meta or meta[k] in (None,''):
                missing_counts[k]+=1
    return missing_counts


def build(cfg):
    rng = random.Random(cfg.seed)
    manifest = load_manifest(cfg.manifest)
    print(f'[info] manifest loaded version={manifest.version} total_target={manifest.total_target}')

    all_samples: List[Dict[str,Any]] = []
    per_bucket_realized: Dict[str,int] = {}
    hash_seen: set[str] = set()

    for spec in manifest.buckets:
        samples = sample_bucket(spec, manifest.total_target, rng)
        before = len(samples)
        if manifest.hash_dedup and samples:
            deduped = []
            for s in samples:
                h = hash_conv(s)
                if h in hash_seen:
                    continue
                hash_seen.add(h)
                s['__hash'] = h
                deduped.append(s)
            samples = deduped
        per_bucket_realized[spec.name] = len(samples)
        all_samples.extend(samples)
        print(f'[bucket] {spec.name} picked={len(samples)} before={before} target≈{math.ceil(spec.target_fraction*manifest.total_target)}')

    # Metadata enforcement
    global_missing = enforce_metadata(all_samples, manifest.metadata_required_global)
    print('[meta] global missing counts:', global_missing)

    # Per bucket metadata missing stats
    for spec in manifest.buckets:
        bucket_objs = [o for o in all_samples if o.get('__source_file','').endswith(spec.source_glob.split('/')[-1].replace('*','')) or spec.name in o.get('__source_file','')]
        if spec.metadata_required:
            miss = enforce_metadata(bucket_objs, spec.metadata_required)
            print(f'[meta] bucket {spec.name} missing:', miss)

    total_realized = len(all_samples)
    print(f'[info] realized total {total_realized}')

    # Drift warnings
    tol = cfg.drift_tolerance
    for spec in manifest.buckets:
        realized = per_bucket_realized.get(spec.name,0)
        expected = spec.target_fraction * manifest.total_target
        if expected > 0:
            frac_realized = realized / total_realized if total_realized else 0
            drift = abs(frac_realized - spec.target_fraction)
            if drift > tol:
                print(f'[drift] {spec.name} realized_fraction={frac_realized:.3f} target={spec.target_fraction:.3f} drift={drift:.3f} > tol={tol}', file=sys.stderr)

    # Write output
    os.makedirs(os.path.dirname(cfg.output), exist_ok=True)
    with open(cfg.output,'w') as out:
        for obj in all_samples:
            obj['__builder'] = {
                'manifest_version': manifest.version,
                'builder_version': '0.1.0',
                'seed': cfg.seed
            }
            out.write(json.dumps(obj, ensure_ascii=False) + '\n')
    print(f'[done] wrote {cfg.output}')


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--drift-tolerance', type=float, default=0.05)
    return ap.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    build(cfg)
