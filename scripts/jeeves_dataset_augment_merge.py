#!/usr/bin/env python3
"""Jeeves Dataset Augment + Merge

Purpose:
  1. Load base hybrid methodology/math dataset and RAG usage examples.
  2. Generate paraphrases & stylistic variants of instructions and answers.
  3. Synthesize additional diverse examples (question reformulations, error correction, chain-of-thought expansion, short/long answer variants).
  4. Output unified supervised fine-tune JSONL + companion stats/ratios JSON.

Design Goals:
  - Deterministic-ish with a seed while still producing variability.
  - Light-weight (no model inference required) scaffold ready to later plug LLM paraphraser.
  - Track provenance per example (base_id, augmentation_technique).

Augmentation Techniques Implemented:
  paraphrase_simple: Lexical swaps + template rephrase.
  shorten_answer / expand_answer: Length variation.
  cot_expand: Add synthetic reasoning chain when absent.
  query_rewrite: Reformulate instruction with a different angle.
  distractor_injection: Add a benign irrelevant sentence (tests model focus on answer).
  error_then_fix: Present a flawed intermediate thought then correction.

Output Fields:
  id, base_id, augmentation, instruction, output, reasoning(optional), source_type (hybrid|rag|augmented), scenario(optional), metadata{...}

Ratios Report (JSON): counts & percentages per category + augmentation technique distribution.
"""
from __future__ import annotations
import argparse, json, random, re, os, hashlib
from pathlib import Path
from typing import Dict, Any, List, Iterable

RNG = random.Random()

LEX_SWAPS = {
  "explain": ["describe", "clarify", "outline"],
  "guide": ["help", "coach", "assist"],
  "student": ["learner", "pupil"],
  "improves": ["boosts", "enhances"],
  "using": ["leveraging", "applying"],
}

def sha(s: str) -> str:
  return hashlib.sha256(s.encode()).hexdigest()[:16]

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
  items=[]
  with path.open('r', encoding='utf-8') as f:
    for line in f:
      line=line.strip()
      if not line:
        continue
      try:
        items.append(json.loads(line))
      except Exception:
        continue
  return items

def simple_paraphrase(text: str, rng: random.Random) -> str:
  def repl(match: re.Match) -> str:
    word = match.group(0)
    lower = word.lower()
    if lower in LEX_SWAPS:
      return rng.choice(LEX_SWAPS[lower])
    return word
  # word boundary swap
  return re.sub(r"\b[\w']+\b", repl, text)

def shorten(s: str) -> str:
  if len(s) < 40:
    return s
  parts = s.split()
  return ' '.join(parts[:max(6, len(parts)//2)]) + '…'

def expand(s: str) -> str:
  if s.endswith('.'):
    base = s[:-1]
  else:
    base = s
  return base + ". This approach supports clarity and deeper reflective understanding."  # generic tail

def add_cot(reasoning: str|None, answer: str) -> (str, str):
  if reasoning:
    return reasoning, answer
  new_reason = "First clarify the core concept, then connect it to an actionable strategy, ensuring the student reflects at each step."
  return new_reason, answer

def query_rewrite(instr: str, rng: random.Random) -> str:
  return "Rephrase: " + simple_paraphrase(instr, rng)

def inject_distractor(answer: str) -> str:
  return answer + " (Note: An unrelated motivational reminder reinforces consistency.)"

def error_then_fix(answer: str) -> str:
  return "Incorrect thought: (confuses terms). Correction: " + answer

def variant_records(base: Dict[str, Any], rng: random.Random) -> Iterable[Dict[str, Any]]:
  instr = base.get('instruction') or base.get('query') or ''
  answer = base.get('output') or base.get('expected_answer') or ''
  reasoning = base.get('reasoning')
  base_id = base.get('id')
  source_type = 'rag' if base.get('type')=='rag_usage' else 'hybrid'

  # Techniques sequence decisions
  techniques = [
    ('paraphrase_simple', lambda: (simple_paraphrase(instr, rng), answer, reasoning)),
    ('shorten_answer', lambda: (instr, shorten(answer), reasoning)),
    ('expand_answer', lambda: (instr, expand(answer), reasoning)),
    ('cot_expand', lambda: (instr, answer, add_cot(reasoning, answer)[0])),
    ('query_rewrite', lambda: (query_rewrite(instr, rng), answer, reasoning)),
    ('distractor_injection', lambda: (instr, inject_distractor(answer), reasoning)),
    ('error_then_fix', lambda: (instr, error_then_fix(answer), reasoning)),
  ]
  # Sample subset for diversity
  chosen = rng.sample(techniques, k=min(3, len(techniques)))
  for tech, fn in chosen:
    try:
      new_instr, new_answer, new_reasoning = fn()
    except Exception:
      continue
    yield {
      'id': f"aug_{tech}_{sha(base_id + tech + new_instr) if base_id else sha(new_instr)}",
      'base_id': base_id,
      'augmentation': tech,
      'instruction': new_instr,
      'output': new_answer,
      'reasoning': new_reasoning,
      'source_type': source_type,
      'scenario': base.get('scenario'),
      'metadata': {
        'origin_type': base.get('example_type') or base.get('type'),
      }
    }

def build(args):
  RNG.seed(args.seed)
  hybrid = load_jsonl(Path(args.hybrid)) if args.hybrid and Path(args.hybrid).exists() else []
  rag = load_jsonl(Path(args.rag)) if args.rag and Path(args.rag).exists() else []
  base_records: List[Dict[str, Any]] = []
  # Normalize base into unified format
  for h in hybrid:
    base_records.append({
      'id': h['id'],
      'instruction': h['instruction'],
      'output': h['output'],
      'source_type': 'hybrid',
      'example_type': h.get('example_type'),
    })
  for r in rag:
    base_records.append({
      'id': r['id'],
      'instruction': r.get('prompt') or r.get('query'),
      'output': r.get('response') or r.get('expected_answer'),
      'source_type': 'rag',
      'type': r.get('type'),
      'scenario': r.get('scenario'),
      'reasoning': r.get('reasoning'),
    })
  variants: List[Dict[str, Any]] = []
  for b in base_records:
    for v in variant_records(b, RNG):
      variants.append(v)
  # Assemble final list
  all_records = []
  # Repackage base minimal structure into unified supervised form
  for b in base_records:
    all_records.append({
      'id': b['id'],
      'instruction': b['instruction'],
      'output': b['output'],
      'reasoning': b.get('reasoning'),
      'source_type': b['source_type'],
      'scenario': b.get('scenario'),
      'metadata': { 'origin_type': b.get('example_type') or b.get('type') }
    })
  all_records.extend(variants)
  RNG.shuffle(all_records)

  os.makedirs(os.path.dirname(args.out), exist_ok=True)
  with open(args.out, 'w', encoding='utf-8') as f:
    for rec in all_records:
      f.write(json.dumps(rec, ensure_ascii=False) + '\n')

  # Ratios / stats
  total = len(all_records)
  base_total = len(base_records)
  variant_total = len(variants)
  augment_counts = {}
  for v in variants:
    augment_counts[v['augmentation']] = augment_counts.get(v['augmentation'], 0) + 1
  ratios = {
    'total_examples': total,
    'base_examples': base_total,
    'variant_examples': variant_total,
    'variant_fraction': round(variant_total/total, 4) if total else 0,
    'source_breakdown': {
      'hybrid_base': sum(1 for b in base_records if b['source_type']=='hybrid'),
      'rag_base': sum(1 for b in base_records if b['source_type']=='rag'),
    },
    'augmentation_distribution': augment_counts,
  }
  with open(args.stats_out, 'w', encoding='utf-8') as f:
    json.dump(ratios, f, indent=2)
  print(f"[out] wrote unified dataset {args.out} ({total} records)")
  print(f"[stats] {args.stats_out}\n" + json.dumps(ratios, indent=2))

def parse_args():
  ap = argparse.ArgumentParser(description="Merge & augment Jeeves datasets into unified supervised JSONL")
  ap.add_argument('--hybrid', default='artifacts/hybrid/hybrid_v1_dataset.jsonl')
  ap.add_argument('--rag', default='data/rag/rag_usage_examples.jsonl')
  ap.add_argument('--out', default='data/fine_tune/jeeves_unified_supervised.jsonl')
  ap.add_argument('--stats-out', default='data/fine_tune/jeeves_unified_stats.json')
  ap.add_argument('--seed', type=int, default=42)
  return ap.parse_args()

def main():
  args = parse_args()
  build(args)

if __name__ == '__main__':
  main()
