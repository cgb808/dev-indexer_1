#!/usr/bin/env python3
"""Hybrid Training Artifact Builder

Generates portable training / evaluation artifacts (JSON + MessagePack) from a
hybrid methodology + mathematics dataset (JSONL). Optionally emits a Weaviate
schema template to facilitate importing the same examples into a Weaviate
vector DB cluster.

Artifacts:
  1. <prefix>_metadata.json        – summary metadata (counts, hashes, splits)
  2. <prefix>_dataset.jsonl        – (optional) normalized JSONL re-emission
  3. <prefix>_dataset.msgpack      – (optional) packed list for fast load
  4. <prefix>_weaviate_schema.json – (optional) schema class definition

MessagePack Layout (version=1):
  {
    "version": 1,
    "created_at": ISO8601 UTC,
    "dataset_name": str,
    "total": int,
    "splits": {"train": N, "val": M},
    "records": [
        {"id": str, "example_type": str, "instruction": str,
         "output": str, "methodology_focus": str|None,
         "subject_focus": str|None, "content_hash": str,
         "split": "train"|"val"}
    ]
  }

Weaviate Schema Hints:
  - Use a single class (HybridExample) with vectorizer text2vec-openai or a
    local transformer: text2vec-transformers
  - Set vectorIndexType: HNSW (default); tune efConstruction & maxConnections
  - Distance metric: cosine (recommended for embeddings)
  - Add properties with dataType ["text"] / ["date"] etc.
  - If using generative module, attach moduleConfig appropriately.

CLI Example:
  python dev-indexer_1/scripts/hybrid_artifact_builder.py \
     --dataset data/hybrid/hybrid_methodology_math_dataset.jsonl \
     --out-dir artifacts/hybrid --prefix hybrid_v1 \
     --emit-jsonl --emit-msgpack --weaviate-schema-out hybrid_schema.json

"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional


# ----------------------------- Data Model -----------------------------

@dataclass
class HybridRecord:
    id: str
    example_type: str
    instruction: str
    output: str
    methodology_focus: Optional[str]
    subject_focus: Optional[str]
    content_hash: str
    split: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "example_type": self.example_type,
            "instruction": self.instruction,
            "output": self.output,
            "methodology_focus": self.methodology_focus,
            "subject_focus": self.subject_focus,
            "content_hash": self.content_hash,
            "split": self.split,
        }


# ----------------------------- Helpers -----------------------------

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_dataset(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def split_dataset(rows: List[Dict[str, Any]], val_ratio: float, seed: int) -> List[HybridRecord]:
    rng = random.Random(seed)
    shuffled = rows.copy()
    rng.shuffle(shuffled)
    val_count = int(len(shuffled) * val_ratio)
    val_ids = {id(x) for x in shuffled[:val_count]}
    result: List[HybridRecord] = []
    for r in shuffled:
        ex_type = r.get("example_type", "unknown")
        instr = r.get("instruction", "")
        out = r.get("output", "")
        meth = r.get("methodology_focus")
        subj = r.get("subject_focus")
        c_hash = sha256_str(instr + "\n" + out)
        rid = r.get("id") or c_hash[:16]
        split = "val" if id(r) in val_ids else "train"
        result.append(HybridRecord(
            id=rid,
            example_type=ex_type,
            instruction=instr,
            output=out,
            methodology_focus=meth,
            subject_focus=subj,
            content_hash=c_hash,
            split=split,
        ))
    return result


def write_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def write_jsonl(path: str, records: List[HybridRecord]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")


def write_msgpack(path: str, dataset_name: str, records: List[HybridRecord]) -> None:
    try:
        import msgpack  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"msgpack not installed: {e}")
    train = sum(1 for r in records if r.split == "train")
    val = sum(1 for r in records if r.split == "val")
    payload = {
        "version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "dataset_name": dataset_name,
        "total": len(records),
        "splits": {"train": train, "val": val},
        "records": [r.to_dict() for r in records],
    }
    with open(path, "wb") as f:
        f.write(msgpack.packb(payload, use_bin_type=True))


def build_weaviate_schema(class_name: str = "HybridExample") -> Dict[str, Any]:
    """Return a Weaviate class schema suitable for these records.

    User can POST this (wrapped in {"classes": [ ... ]}) to /v1/schema.
    """
    return {
        "class": class_name,
        "description": "Hybrid pedagogy + math training example",
        "vectorizer": "text2vec-transformers",  # or text2vec-openai
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "distance": "cosine",
            "efConstruction": 128,
            "maxConnections": 64,
            "vectorCacheMaxObjects": 200000,
        },
        "moduleConfig": {},  # add generative config if using (e.g., generative-openai)
        "properties": [
            {"name": "example_type", "dataType": ["text"], "description": "Type of example"},
            {"name": "instruction", "dataType": ["text"], "description": "Prompt / instruction"},
            {"name": "output", "dataType": ["text"], "description": "Expected tutor response"},
            {"name": "methodology_focus", "dataType": ["text"], "description": "Pedagogical focus", "indexInverted": True},
            {"name": "subject_focus", "dataType": ["text"], "description": "Subject topic", "indexInverted": True},
            {"name": "content_hash", "dataType": ["text"], "description": "Deterministic content hash", "indexInverted": True},
            {"name": "split", "dataType": ["text"], "description": "Dataset split"},
            {"name": "created_at", "dataType": ["date"], "description": "Ingestion timestamp"},
        ],
        "replicationConfig": {"factor": 1},
    }


# ----------------------------- CLI -----------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build hybrid training artifacts (JSON/MsgPack/Weaviate schema)")
    p.add_argument("--dataset", required=True, help="Input hybrid JSONL dataset")
    p.add_argument("--out-dir", default="artifacts/hybrid", help="Output directory")
    p.add_argument("--prefix", default="hybrid", help="Artifact filename prefix")
    p.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio (0-0.5)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--emit-jsonl", action="store_true", help="Emit normalized JSONL copy")
    p.add_argument("--emit-msgpack", action="store_true", help="Emit MessagePack artifact")
    p.add_argument("--weaviate-schema-out", help="Write Weaviate class schema JSON to this filename (inside out dir if relative)")
    p.add_argument("--dataset-name", default="hybrid_methodology_math", help="Dataset name for artifacts")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if not (0.0 <= args.val_ratio < 0.5):
        print("[ERROR] val-ratio must be between 0 and 0.5", file=sys.stderr)
        return 2
    os.makedirs(args.out_dir, exist_ok=True)
    rows = load_dataset(args.dataset)
    records = split_dataset(rows, args.val_ratio, args.seed)
    train = sum(1 for r in records if r.split == "train")
    val = sum(1 for r in records if r.split == "val")
    meta = {
        "dataset_name": args.dataset_name,
        "source_path": args.dataset,
        "created_at": datetime.now(UTC).isoformat(),
        "total": len(records),
        "splits": {"train": train, "val": val},
    }
    meta_path = os.path.join(args.out_dir, f"{args.prefix}_metadata.json")
    write_json(meta_path, meta)
    print(f"[meta] {meta_path}")
    if args.emit_jsonl:
        jsonl_path = os.path.join(args.out_dir, f"{args.prefix}_dataset.jsonl")
        write_jsonl(jsonl_path, records)
        print(f"[jsonl] {jsonl_path}")
    if args.emit_msgpack:
        mp_path = os.path.join(args.out_dir, f"{args.prefix}_dataset.msgpack")
        write_msgpack(mp_path, args.dataset_name, records)
        print(f"[msgpack] {mp_path}")
    if args.weaviate_schema_out:
        schema = build_weaviate_schema()
        # Add created_at property value example? not necessary.
        schema_path = args.weaviate_schema_out
        if not os.path.isabs(schema_path):
            schema_path = os.path.join(args.out_dir, schema_path)
        write_json(schema_path, schema)
        print(f"[weaviate] schema -> {schema_path}")
    print(f"[done] total={len(records)} train={train} val={val}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
