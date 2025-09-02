#!/usr/bin/env python3
"""Generate a synthetic hybrid methodology + mathematics dataset.

Creates N_pure pure methodology examples and N_math integrated math+methodology
examples into JSONL at data/hybrid/hybrid_methodology_math_dataset.jsonl

This is a lightweight synthetic generator intended for scaffolding + pipeline
validation, NOT high-quality pedagogical content. Replace with curated data
for production fine-tuning.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from datetime import datetime
from typing import Dict, Any

PURE_METHODS = [
    "scaffold_thinking",
    "diagnose_misconception",
    "encourage_metacognition",
    "spaced_recall_prompt",
    "socratic_question_chain",
]

MATH_FOCI = [
    "place_value",
    "fractions",
    "multiplication_strategies",
    "number_sense",
    "basic_geometry",
]


def build_pure(idx: int, rng: random.Random) -> Dict[str, Any]:
    method = rng.choice(PURE_METHODS)
    return {
        "id": f"pure_{idx}",
        "example_type": "pure_methodology",
        "instruction": f"Explain the purpose of the {method.replace('_', ' ')} technique to a new tutor.",
        "output": f"The {method.replace('_', ' ')} technique helps learners by providing structured guidance and encourages reflective thinking.",
        "methodology_focus": method,
    }


def build_math(idx: int, rng: random.Random) -> Dict[str, Any]:
    focus = rng.choice(MATH_FOCI)
    method = rng.choice(PURE_METHODS)
    return {
        "id": f"math_{idx}",
        "example_type": "mathematics_with_methodology",
        "instruction": f"Guide a student through a {focus.replace('_', ' ')} problem using {method.replace('_', ' ')}.",
        "output": f"Let's break the {focus.replace('_', ' ')} concept into clear steps while applying {method.replace('_', ' ')} questions to deepen understanding.",
        "methodology_focus": method,
        "subject_focus": focus,
    }


def generate(n_pure: int, n_math: int, seed: int, out_path: str) -> None:
    rng = random.Random(seed)
    examples = []
    for i in range(n_pure):
        examples.append(build_pure(i, rng))
    for i in range(n_math):
        examples.append(build_math(i, rng))
    rng.shuffle(examples)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(examples)} examples -> {out_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--pure", type=int, default=500)
    p.add_argument("--math", type=int, default=500)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--out", default="data/hybrid/hybrid_methodology_math_dataset.jsonl")
    return p.parse_args()


def main():
    args = parse_args()
    generate(args.pure, args.math, args.seed, args.out)


if __name__ == "__main__":
    main()
