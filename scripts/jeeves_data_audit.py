#!/usr/bin/env python3
"""Audit & quality metrics for Jeeves training artifacts.

Computes:
  * Hybrid dataset line count
  * RAG usage examples count
  * RAG batch aggregate stats (file count, total records, per-file counts)
  * Duplicate content_hash ratio across RAG batches
  * Embedding dimension consistency + sample norm statistics (if embeddings present)
  * Suggestions / warnings

Outputs JSON summary (stdout or --out file).

Usage:
  python dev-indexer_1/scripts/jeeves_data_audit.py \
     --hybrid artifacts/hybrid/hybrid_v1_dataset.jsonl \
     --rag-usage data/rag/rag_usage_examples.jsonl \
     --rag-batch-glob 'data/msgpack/rag_batch_*.msgpack' \
     --out artifacts/jeeves_data_audit.json
"""
from __future__ import annotations

import argparse, json, os, glob, statistics, math, hashlib
from pathlib import Path
from typing import List, Dict, Any

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def count_lines(path: Path) -> int:
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f if _.strip())
    except Exception:
        return 0

def load_msgpack_batches(pattern: str) -> List[Dict[str, Any]]:
    try:
        import msgpack  # type: ignore
    except Exception:
        return []
    files = sorted(glob.glob(pattern))
    batches = []
    for f in files:
        try:
            with open(f,'rb') as fh:
                import msgpack
                obj = msgpack.unpackb(fh.read(), raw=False)
            batches.append({'file': f, 'payload': obj})
        except Exception as e:  # noqa: BLE001
            batches.append({'file': f, 'error': str(e)})
    return batches

def audit_embeddings(records: List[Dict[str, Any]]):
    norms = []
    dim = None
    for rec in records[:200]:  # sample up to 200
        emb = rec.get('embedding')
        if not emb:
            continue
        if dim is None:
            dim = len(emb)
        if len(emb) != dim:
            return {'error': f'dimension mismatch {len(emb)} vs {dim}'}
        s = sum(x*x for x in emb)
        norms.append(math.sqrt(s))
    if not norms:
        return {'present': False}
    return {
        'present': True,
        'sample_size': len(norms),
        'dim': dim,
        'norm_mean': statistics.mean(norms),
        'norm_stdev': statistics.pstdev(norms) if len(norms) > 1 else 0.0,
        'norm_min': min(norms),
        'norm_max': max(norms)
    }

def main():
    ap = argparse.ArgumentParser(description='Audit Jeeves artifacts')
    ap.add_argument('--hybrid', required=True)
    ap.add_argument('--rag-usage', required=True)
    ap.add_argument('--rag-batch-glob', required=True)
    ap.add_argument('--out')
    args = ap.parse_args()

    hybrid_path = Path(args.hybrid)
    rag_usage_path = Path(args.rag_usage)
    hybrid_lines = count_lines(hybrid_path)
    rag_usage_lines = count_lines(rag_usage_path)

    batches = load_msgpack_batches(args.rag_batch_glob)
    total_batch_records = 0
    batch_files = 0
    dup_hashes = 0
    seen = set()
    all_records_sample = []
    per_file = []
    for b in batches:
        if 'error' in b:
            per_file.append({'file': b['file'], 'error': b['error']})
            continue
        payload = b['payload']
        recs = payload.get('records') or []
        batch_files += 1
        total_batch_records += len(recs)
        file_dups = 0
        for r in recs:
            text = r.get('text') or ''
            h = r.get('metadata',{}).get('content_hash') or sha256_text(text)
            if h in seen:
                dup_hashes += 1
                file_dups += 1
            else:
                seen.add(h)
            if len(all_records_sample) < 400:
                all_records_sample.append(r)
        per_file.append({'file': b['file'], 'records': len(recs), 'duplicates_in_file': file_dups})

    embed_stats = audit_embeddings(all_records_sample)
    dup_ratio = (dup_hashes / total_batch_records) if total_batch_records else 0.0

    suggestions = []
    if dup_ratio > 0.05:
        suggestions.append(f"High duplicate ratio {dup_ratio:.2%}; consider increasing hash dedupe scope or cleaning sources.")
    if embed_stats.get('present') and 0.5 < embed_stats.get('norm_mean',1) > 20:
        suggestions.append('Embedding norm mean unusually large; verify embedding generator.')
    if hybrid_lines == 0:
        suggestions.append('Hybrid dataset empty.')
    if rag_usage_lines < 50:
        suggestions.append('RAG usage examples are few; generate more for better instruction coverage.')

    result = {
        'hybrid_lines': hybrid_lines,
        'rag_usage_lines': rag_usage_lines,
        'rag_batch_files': batch_files,
        'rag_batch_total_records': total_batch_records,
        'duplicate_hashes': dup_hashes,
        'duplicate_ratio': dup_ratio,
        'embedding_stats': embed_stats,
        'per_file': per_file,
        'suggestions': suggestions,
    }

    out_json = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out_json)
        print(f"[audit] wrote {args.out}")
    else:
        print(out_json)
    return 0

if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
