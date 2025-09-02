#!/usr/bin/env python
"""Ingest curated tutoring JSONL dataset into doc_embeddings.

Usage:
  python scripts/ingest_curated_dataset.py --file data/family_tutor/curated_principal_tutor_epoch1.jsonl \
      --source principal_tutor --batch-tag tutor_epoch1

Behavior:
  - Reads JSONL examples with schema {messages:[{role:user},{role:assistant}], meta:{...}}
  - Extracts assistant content as one chunk (or splits if > max_chars)
  - Calls local embedding endpoint /model/embed
  - Inserts into Postgres doc_embeddings with source, chunk, embedding, batch_tag
  - Optionally stores meta JSON as a separate row (if --store-meta) under source '<source>_meta'
"""
from __future__ import annotations
import os, argparse, json, math, hashlib, re, statistics, time, pathlib
from typing import List, Dict, Any
import requests

EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "http://127.0.0.1:8000/model/embed")
DSN = os.getenv("DATABASE_URL")
MAX_CHARS = 1200
OVERLAP = 120

# ---------------- Quality Helpers -----------------
RE_WORD = re.compile(r"[A-Za-z']+")

def flesch_reading_ease(text: str) -> float:
    words = RE_WORD.findall(text)
    if not words:
        return 0.0
    sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
    syllables = 0
    for w in words:
        wl = w.lower()
        wl = re.sub(r"e$", "", wl)
        vowels = re.findall(r"[aeiouy]+", wl)
        syllables += max(1, len(vowels))
    wcount = len(words)
    return 206.835 - 1.015 * (wcount / sentences) - 84.6 * (syllables / wcount)

def hash_text(t: str) -> str:
    return hashlib.sha256(t.strip().lower().encode()).hexdigest()

def chunk_answer(text: str) -> List[str]:
    txt = text.replace('\r','')
    if len(txt) <= MAX_CHARS:
        return [txt.strip()]
    chunks=[]; start=0; n=len(txt)
    while start < n:
        end = min(start+MAX_CHARS, n)
        seg = txt[start:end].strip()
        if seg:
            chunks.append(seg)
        if end >= n:
            break
        start = end - OVERLAP
        if start < 0: start = 0
    return chunks

def embed(chunks: List[str]) -> List[List[float]]:
    if not chunks:
        return []
    r = requests.post(EMBED_ENDPOINT, json={"texts": chunks}, timeout=300)
    r.raise_for_status()
    data = r.json()
    return data.get("embeddings", [])

def insert(rows):
    if not DSN:
        raise SystemExit("DATABASE_URL not set")
    from psycopg2.extras import execute_values
    import psycopg2
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            execute_values(cur,
                "INSERT INTO doc_embeddings (source, chunk, embedding, batch_tag) VALUES %s",
                rows)

def read_examples(path: str):
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                obj=json.loads(line)
                yield obj
            except json.JSONDecodeError:
                continue

def compute_confidence(reading: float, word_count: int, is_fallback: bool, synthetic: bool) -> float:
    # Normalize reading (assume desirable 30..80)
    n_r = (reading - 30) / 50
    n_r = 0 if n_r < 0 else (1 if n_r > 1 else n_r)
    # Word band target 25..60 -> center 40
    band = 1 - (abs(word_count - 40) / 40)
    band = 0 if band < 0 else (1 if band > 1 else band)
    base = 0.4 * n_r + 0.4 * band + 0.2 * (0 if is_fallback else 1)
    if synthetic:
        base -= 0.1
    return round(max(0.0, min(1.0, base)), 4)

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def safe_write_json(obj: dict, path: str):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def process(file: str, source: str, batch_tag: str, limit: int | None, store_meta: bool,
            min_words: int, max_words: int, min_reading: float, exclude_synthetic: bool,
            max_fallback_fraction: float, dry_run: bool, min_accepted: int | None, relax_step: float,
            sidecar_dir: str | None, sidecar_mode: str, manifest_out: str | None):
    examples = list(read_examples(file)) if min_accepted else None
    def run_once(examples_iter, cfg):
        rows=[]; count=0; accepted=0
        by_source={}; rejections={}; hashes=set(); fallback_kept=0
        lengths=[]; reading_vals=[]
        sidecar_agg = [] if sidecar_mode=='aggregate' else None
        for ex in examples_iter:
            if limit and count >= limit:
                break
            count += 1
            meta = ex.get('meta', {})
            ex_source = meta.get('source','unknown')
            flags = meta.get('flags', []) or []
            # Gather assistant messages
            msgs=ex.get('messages') or []
            assistant_texts = [m['content'].strip() for m in msgs if m.get('role')=='assistant' and m.get('content')]
            if not assistant_texts:
                rejections['no_assistant'] = rejections.get('no_assistant',0)+1
                continue
            # Evaluate first assistant message for quality heuristics
            first = assistant_texts[0]
            word_count = len(first.split())
            if word_count < cfg['min_words']:
                rejections['too_short'] = rejections.get('too_short',0)+1; continue
            if word_count > cfg['max_words']:
                rejections['too_long'] = rejections.get('too_long',0)+1; continue
            reading = meta.get('reading_ease')
            if reading is None:
                reading = flesch_reading_ease(first)
            if reading < cfg['min_reading']:
                rejections['low_readability'] = rejections.get('low_readability',0)+1; continue
            synthetic = bool(meta.get('synthetic'))
            if synthetic and cfg['exclude_synthetic']:
                rejections['synthetic'] = rejections.get('synthetic',0)+1; continue
            is_fallback = (ex_source=='fallback_multistage') or ('fallback' in flags)
            if is_fallback:
                # check prospective fallback cap
                projected_total = accepted + 1
                if projected_total>0 and (fallback_kept+1)/projected_total > cfg['max_fallback_fraction']:
                    rejections['fallback_cap'] = rejections.get('fallback_cap',0)+1; continue
            # Dedup on first message content hash
            h = hash_text(first)
            if h in hashes:
                rejections['duplicate'] = rejections.get('duplicate',0)+1; continue
            hashes.add(h)
            # Accept: embed each assistant stage separately
            confidence = compute_confidence(reading, word_count, is_fallback, synthetic)
            by_source[ex_source]=by_source.get(ex_source,0)+1
            if is_fallback:
                fallback_kept += 1
            accepted += 1
            lengths.append(word_count)
            reading_vals.append(reading)
            # Enrich meta for sidecar
            enriched_meta = meta.copy()
            enriched_meta.update({
                'confidence': confidence,
                'is_fallback': is_fallback,
                'synthetic': synthetic,
                'word_count': word_count,
                'hash': h,
            })
            if sidecar_dir:
                if sidecar_mode == 'files':
                    safe_write_json(enriched_meta, os.path.join(sidecar_dir, f"{h}.meta.json"))
                else:
                    sidecar_agg.append(enriched_meta)
            for idx, atext in enumerate(assistant_texts):
                chunks = chunk_answer(atext)
                embeddings = [] if dry_run else embed(chunks)
                for c,e in zip(chunks, embeddings if embeddings else [[0.0]]*len(chunks)):
                    rows.append((source, f"[stage {idx+1}] {c}", e, batch_tag))
            if store_meta:
                meta_with_conf = enriched_meta.copy()
                meta_json = json.dumps(meta_with_conf, ensure_ascii=False)
                if not dry_run:
                    rows.append((f"{source}_meta", meta_json[:800], embed([meta_json])[0], batch_tag))
            if not dry_run and len(rows) >= 256:
                insert(rows); rows.clear()
        if not dry_run and rows:
            insert(rows)
        summary = {
            'scanned': count,
            'accepted': accepted,
            'accept_rate': round(accepted/max(count,1),4),
            'by_source': by_source,
            'rejections': rejections,
            'fallback_fraction': round(fallback_kept/max(accepted,1),4) if accepted else 0.0,
            'length_avg': round(sum(lengths)/len(lengths),2) if lengths else 0,
            'length_median': statistics.median(lengths) if lengths else 0,
            'reading_mean': round(sum(reading_vals)/len(reading_vals),2) if reading_vals else 0,
            'reading_min': round(min(reading_vals),2) if reading_vals else 0,
            'reading_max': round(max(reading_vals),2) if reading_vals else 0,
            'config': cfg.copy()
        }
        if sidecar_dir and sidecar_mode=='aggregate':
            safe_write_json({'batch_tag': batch_tag, 'source': source, 'items': sidecar_agg}, os.path.join(sidecar_dir, f"{batch_tag}_sidecars.json"))
        return summary
    # Initial config
    cfg = dict(min_words=min_words, max_words=max_words, min_reading=min_reading,
               exclude_synthetic=exclude_synthetic, max_fallback_fraction=max_fallback_fraction)
    summaries=[]
    def example_iter():
        return examples if examples is not None else read_examples(file)
    attempt=0
    while True:
        attempt+=1
        summary = run_once(example_iter(), cfg)
        summaries.append(summary)
        print(f"[quality] Attempt {attempt} -> accepted {summary['accepted']} / {summary['scanned']} (rate {summary['accept_rate']})")
        if min_accepted and summary['accepted'] < min_accepted:
            # Relax thresholds
            cfg['min_reading'] = max(0, cfg['min_reading'] - relax_step)
            cfg['max_fallback_fraction'] = min(1.0, cfg['max_fallback_fraction'] + relax_step/100)
            cfg['min_words'] = max(3, math.floor(cfg['min_words']*0.9))
            print(f"[quality] Relaxing constraints -> min_reading={cfg['min_reading']} min_words={cfg['min_words']} max_fallback_fraction={cfg['max_fallback_fraction']}")
            if attempt < 4:  # limit relaxation cycles
                continue
        break
    # Print detailed rejection summary last attempt
    last = summaries[-1]
    print(json.dumps(last, indent=2))
    # Manifest out
    if manifest_out:
        manifest_data = {
            'batch_tag': batch_tag,
            'source_label': source,
            'dataset_file': file,
            'dataset_sha256': file_sha256(file),
            'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'quality_summary': last,
            'embedding_endpoint': EMBED_ENDPOINT,
            'sidecar_dir': sidecar_dir,
        }
        safe_write_json(manifest_data, manifest_out)
        print(f"[manifest] Wrote batch manifest -> {manifest_out}")
    return last

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True)
    ap.add_argument('--source', default='principal_tutor')
    ap.add_argument('--batch-tag', default='curated_ingest')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--store-meta', action='store_true')
    # Quality gating args
    ap.add_argument('--min-words', type=int, default=6)
    ap.add_argument('--max-words', type=int, default=180)
    ap.add_argument('--min-reading-ease', type=float, default=30.0)
    ap.add_argument('--exclude-synthetic', action='store_true')
    ap.add_argument('--max-fallback-fraction', type=float, default=0.35, help='Maximum fraction of accepted examples allowed to be fallback/multistage before capping.')
    ap.add_argument('--dry-run', action='store_true', help='Run filtering and stats without DB inserts / embedding calls (embeddings mocked).')
    ap.add_argument('--min-accepted', type=int, help='Target minimum accepted examples; relax constraints iteratively if not reached.')
    ap.add_argument('--relax-step', type=float, default=8.0, help='Relaxation delta for readability (and scaled adjustments) per attempt when below min-accepted.')
    ap.add_argument('--sidecar-dir', type=str, help='Directory to write per-example enriched meta sidecar files or aggregate JSON.')
    ap.add_argument('--sidecar-mode', type=str, choices=['files','aggregate'], default='files', help='Sidecar write strategy.')
    ap.add_argument('--manifest-out', type=str, help='Path to write batch ingestion manifest JSON summarizing quality + config.')
    args=ap.parse_args()
    summary = process(
        file=args.file,
        source=args.source,
        batch_tag=args.batch_tag,
        limit=args.limit,
        store_meta=args.store_meta,
        min_words=args.min_words,
        max_words=args.max_words,
        min_reading=args.min_reading_ease,
        exclude_synthetic=args.exclude_synthetic,
        max_fallback_fraction=args.max_fallback_fraction,
        dry_run=args.dry_run,
        min_accepted=args.min_accepted,
        relax_step=args.relax_step,
        sidecar_dir=args.sidecar_dir,
        sidecar_mode=args.sidecar_mode,
        manifest_out=args.manifest_out
    )
    print(f"Processed examples: {summary['accepted']}")

if __name__=='__main__':
    main()
