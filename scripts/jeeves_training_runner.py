#!/usr/bin/env python3
"""Jeeves Training Orchestrator

High-level convenience script to assemble training artifacts for the "Jeeves"
personalized tutoring / retrieval stack.

Default Steps:
 1. Ensure hybrid dataset exists (generate if missing)
 2. Build hybrid artifacts (JSONL, MsgPack, Weaviate schema)
 3. Generate RAG usage examples (JSONL + MsgPack)
 4. (Optional) Collect RAG ingestion batch msgpack artifacts (embedding batches)
 5. Emit summary JSON (hashes, sizes, counts, rag batch metadata)
 6. (Optional) Produce consolidated tarball bundle for downstream training

Notes:
 - This does NOT perform model fine-tuning; it prepares curated data packs.
 - RAG batch msgpack files are those produced by rag_ingest.py with --msgpack-out
     or by offline replay scripts (rag_replay_msgpack). They contain chunk text,
     metadata and optionally embeddings.
"""
from __future__ import annotations

import argparse, os, subprocess, hashlib, json, sys, tarfile, io, time, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]):
    print(f"[run] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    if result.stdout.strip():
        print(result.stdout.strip())


def ensure_hybrid_dataset(dataset_path: Path, pure: int, math: int):
    if dataset_path.exists():
        print(f"[skip] Hybrid dataset exists -> {dataset_path}")
        return
    run([
        'python', 'dev-indexer_1/scripts/generate_hybrid_dataset.py',
        '--pure', str(pure), '--math', str(math), '--out', str(dataset_path)
    ])


def build_hybrid_artifacts(dataset_path: Path, out_dir: Path, prefix: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    run([
        'python', 'dev-indexer_1/scripts/hybrid_artifact_builder.py',
        '--dataset', str(dataset_path), '--out-dir', str(out_dir), '--prefix', prefix,
        '--emit-jsonl', '--emit-msgpack', '--weaviate-schema-out', 'hybrid_schema.json'
    ])


def build_rag_usage(out_path: Path, total: int):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run([
        'python', 'dev-indexer_1/scripts/rag_training_example_builder.py',
        '--out', str(out_path), '--total', str(total)
    ])


def load_rag_batches(glob_pattern: str) -> list[dict]:
    """Scan for rag batch msgpack artifacts and extract lightweight metadata.

    Expects each file has top-level keys: version, count, embedding_dim, source, batch_tag.
    Embeddings themselves are NOT loaded into memory (records omitted in summary).
    """
    try:
        import msgpack  # type: ignore
    except Exception:  # noqa: BLE001
        print("[rag-batches] msgpack not installed; skipping")
        return []
    files = sorted(glob.glob(glob_pattern))
    metas: list[dict] = []
    for f in files:
        try:
            with open(f, 'rb') as fh:
                unpacker = msgpack.Unpacker(fh, raw=False)
                obj = unpacker.unpack()
            # Avoid keeping large records list; pop it if present.
            rec_count = obj.get('count') or (len(obj.get('records', [])) if isinstance(obj.get('records'), list) else None)
            meta = {
                'file': f,
                'bytes': os.path.getsize(f),
                'sha256': sha256_file(Path(f)),
                'count': rec_count,
                'embedding_dim': obj.get('embedding_dim'),
                'source': obj.get('source'),
                'batch_tag': obj.get('batch_tag'),
                'created_at': obj.get('created_at'),
                'version': obj.get('version'),
            }
            metas.append(meta)
        except Exception as e:  # noqa: BLE001
            print(f"[rag-batches] warn: failed to parse {f}: {e}")
    if metas:
        print(f"[rag-batches] collected {len(metas)} batch files")
    return metas


def bundle_files(tar_path: Path, file_paths: list[Path], manifest: dict):
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, 'w:gz') as tf:
        # Add each file
        for p in file_paths:
            if p.exists():
                arcname = p.relative_to(ROOT)
                tf.add(p, arcname=str(arcname))
        # Add manifest as in-tar JSON
        manifest_bytes = json.dumps(manifest, indent=2).encode('utf-8')
        info = tarfile.TarInfo(name='jeeves_bundle_manifest.json')
        info.size = len(manifest_bytes)
        info.mtime = int(time.time())
        tf.addfile(info, io.BytesIO(manifest_bytes))
    print(f"[bundle] wrote {tar_path}")


def main():
    ap = argparse.ArgumentParser(description="Assemble Jeeves training artifacts")
    ap.add_argument('--hybrid-pure', type=int, default=500)
    ap.add_argument('--hybrid-math', type=int, default=500)
    ap.add_argument('--hybrid-dataset', default='data/hybrid/hybrid_methodology_math_dataset.jsonl')
    ap.add_argument('--hybrid-artifacts-dir', default='artifacts/hybrid')
    ap.add_argument('--hybrid-prefix', default='hybrid_v1')
    ap.add_argument('--rag-total', type=int, default=120)
    ap.add_argument('--rag-out', default='data/rag/rag_usage_examples.jsonl')
    ap.add_argument('--summary-out', default='artifacts/jeeves_training_summary.json')
    ap.add_argument('--include-rag-batches', action='store_true', help='Scan and include rag ingestion batch msgpack metadata')
    ap.add_argument('--rag-batch-glob', default='data/msgpack/rag_batch_*.msgpack', help='Glob for rag batch msgpack files')
    ap.add_argument('--bundle-tar', help='Optional output tar.gz consolidating artifacts + manifest')
    ap.add_argument('--audit', action='store_true', help='Run data audit and embed results into summary')
    ap.add_argument('--audit-out', default='artifacts/jeeves_data_audit.json', help='Audit output JSON path')
    args = ap.parse_args()

    dataset_path = ROOT / args.hybrid_dataset
    artifacts_dir = ROOT / args.hybrid_artifacts_dir
    rag_out = ROOT / args.rag_out
    summary_out = ROOT / args.summary_out

    ensure_hybrid_dataset(dataset_path, args.hybrid_pure, args.hybrid_math)
    build_hybrid_artifacts(dataset_path, artifacts_dir, args.hybrid_prefix)
    build_rag_usage(rag_out, args.rag_total)

    rag_batch_meta = []
    if args.include_rag_batches:
        rag_batch_meta = load_rag_batches(args.rag_batch_glob)

    audit_payload = None
    if args.audit:
        # Run audit script as a subprocess for isolation (avoids heavy imports here)
        audit_cmd = [
            'python','dev-indexer_1/scripts/jeeves_data_audit.py',
            '--hybrid', str(artifacts_dir / f"{args.hybrid_prefix}_dataset.jsonl"),
            '--rag-usage', str(rag_out),
            '--rag-batch-glob', args.rag_batch_glob,
            '--out', str(args.audit_out)
        ]
        run(audit_cmd)
        try:
            audit_payload = json.loads(Path(args.audit_out).read_text())
        except Exception as e:  # noqa: BLE001
            print(f"[audit] failed to load audit output: {e}")

    # Collect artifact hashes
    summary = {
        'generated_at': os.environ.get('SOURCE_DATE_EPOCH') or '',
        'hybrid_prefix': args.hybrid_prefix,
        'rag_usage_examples': str(rag_out.relative_to(ROOT)) if rag_out.exists() else None,
        'rag_batches': rag_batch_meta,
    'audit': audit_payload,
    }
    files_of_interest = [
        artifacts_dir / f"{args.hybrid_prefix}_metadata.json",
        artifacts_dir / f"{args.hybrid_prefix}_dataset.jsonl",
        artifacts_dir / f"{args.hybrid_prefix}_dataset.msgpack",
        artifacts_dir / 'hybrid_schema.json',
        rag_out,
        Path(str(rag_out).replace('.jsonl', '.msgpack')),
    ]
    for fp in files_of_interest:
        if fp.exists():
            summary[str(fp.relative_to(ROOT))] = {
                'bytes': fp.stat().st_size,
                'sha256': sha256_file(fp)
            }

    summary_out.parent.mkdir(parents=True, exist_ok=True)
    with summary_out.open('w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"[summary] {summary_out}")

    if args.bundle_tar:
        bundle_list = [p for p in files_of_interest if p.exists()]
        bundle_list.append(summary_out)
        bundle_files(ROOT / args.bundle_tar, bundle_list, summary)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
