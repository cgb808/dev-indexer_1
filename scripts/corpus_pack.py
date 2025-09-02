#!/usr/bin/env python3
"""Corpus Pack / Unpack Utility

Purpose:
  Efficiently store and transport a document corpus (currently plain text files) in a single
  MessagePack (optionally compressed) artifact with lightweight metadata, enabling faster
  ingestion (less filesystem overhead) and optional future transformations.

Pack Format (MessagePack top-level map):
  {
    "version": 1,
    "created_at": ISO8601,
    "doc_count": N,
    "compression": "none" | "zstd",
    "records": [
        {"path": relative_path, "sha256": content_hash, "bytes": len, "text": maybe_compressed_or_plain }
    ]
  }

If compression == 'zstd', each record's 'text' field is raw bytes of zstd-compressed UTF-8.
Otherwise it's a UTF-8 string.

Unpack will recreate a directory tree (default: unpacked_corpus/) with original relative paths.

Usage:
  Pack:   python corpus_pack.py pack --glob 'docs/**/*.txt' --out data/corpus/my_corpus.msgpack --zstd
  Unpack: python corpus_pack.py unpack --file data/corpus/my_corpus.msgpack --out restored_docs
  List:   python corpus_pack.py list --file data/corpus/my_corpus.msgpack

Notes:
  - This is a scaffold; for very large corpora consider streaming / chunked packing.
  - Compatible with rag_ingest.py after enhancement via --msgpack-corpus flag.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, sys, time
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Dict, Any

try:
    import msgpack  # type: ignore
except Exception as e:  # noqa: BLE001
    print("[error] python-msgpack required: pip install msgpack", file=sys.stderr)
    raise

try:
    import zstd  # type: ignore  # optional lightweight alias some envs provide
    HAVE_ZSTD = True
except Exception:  # noqa: BLE001
    try:
        import zstandard as zstd  # type: ignore
        HAVE_ZSTD = True
    except Exception:  # noqa: BLE001
        HAVE_ZSTD = False

def sha256_text(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def pack_files(pattern: str, out_path: Path, use_zstd: bool):
    paths = sorted(glob.glob(pattern, recursive=True))
    records: List[Dict[str, Any]] = []
    for p in paths:
        if not os.path.isfile(p):
            continue
        try:
            with open(p,'r',encoding='utf-8',errors='ignore') as f:
                txt = f.read()
        except Exception as e:  # noqa: BLE001
            print(f"[warn] skip {p}: {e}")
            continue
        rel = p
        h = sha256_text(txt)
        rec: Dict[str, Any] = {"path": rel, "sha256": h, "bytes": len(txt.encode('utf-8'))}
        if use_zstd and HAVE_ZSTD:
            cctx = zstd.ZstdCompressor()
            rec["text"] = cctx.compress(txt.encode('utf-8'))
        else:
            rec["text"] = txt
        records.append(rec)
    payload = {
        "version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "doc_count": len(records),
        "compression": 'zstd' if (use_zstd and HAVE_ZSTD) else 'none',
        "records": records,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('wb') as f:
        f.write(msgpack.packb(payload, use_bin_type=True))
    print(f"[pack] wrote {len(records)} docs -> {out_path}")

def unpack_file(file_path: Path, out_dir: Path):
    with file_path.open('rb') as f:
        payload = msgpack.unpackb(f.read(), raw=False)
    comp = payload.get('compression','none')
    recs = payload.get('records',[])
    if comp == 'zstd' and not HAVE_ZSTD:
        raise SystemExit('zstd compressed corpus but zstd module not available')
    dctx = zstd.ZstdDecompressor() if comp=='zstd' and HAVE_ZSTD else None
    for rec in recs:
        rel = rec['path']
        data = rec['text']
        if isinstance(data, bytes):
            if dctx:
                data = dctx.decompress(data).decode('utf-8', errors='ignore')
            else:
                data = data.decode('utf-8','ignore')
        out_path = out_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(data, encoding='utf-8')
    print(f"[unpack] restored {len(recs)} docs -> {out_dir}")

def list_corpus(file_path: Path):
    with file_path.open('rb') as f:
        payload = msgpack.unpackb(f.read(), raw=False)
    print(json.dumps({k: v for k,v in payload.items() if k!='records'}, indent=2))
    print("Records:")
    for rec in payload.get('records',[])[:25]:
        print(f"  - {rec['path']} bytes={rec['bytes']}")
    if len(payload.get('records',[]))>25:
        print(f"  ... ({len(payload['records'])-25} more)")

def main():
    ap = argparse.ArgumentParser(description='Pack/unpack/list text corpus via msgpack (+optional zstd).')
    sub = ap.add_subparsers(dest='cmd', required=True)
    ap_pack = sub.add_parser('pack')
    ap_pack.add_argument('--glob', required=True)
    ap_pack.add_argument('--out', required=True)
    ap_pack.add_argument('--zstd', action='store_true')
    ap_unpack = sub.add_parser('unpack')
    ap_unpack.add_argument('--file', required=True)
    ap_unpack.add_argument('--out', default='unpacked_corpus')
    ap_list = sub.add_parser('list')
    ap_list.add_argument('--file', required=True)
    args = ap.parse_args()
    if args.cmd=='pack':
        pack_files(args.glob, Path(args.out), args.zstd)
    elif args.cmd=='unpack':
        unpack_file(Path(args.file), Path(args.out))
    elif args.cmd=='list':
        list_corpus(Path(args.file))

if __name__=='__main__':
    main()
