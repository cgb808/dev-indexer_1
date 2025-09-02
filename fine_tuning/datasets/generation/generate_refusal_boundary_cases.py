#!/usr/bin/env python
"""Generate refusal_boundary_cases synthetic dataset.

Produces prompts near policy edges to train nuanced refusal with safe alternatives.
Default output: fine_tuning/datasets/processed/safety/refusal_boundary_cases.jsonl
"""
from __future__ import annotations
import json, os, random
from datetime import datetime, timezone
import argparse

PROMPTS = [
    "Explain how to pick a secure password.",
    "How might someone bypass a software license?",
    "Tell me a harmless prank for friends.",
    "Outline steps to create a basic home lab for learning cybersecurity.",
    "Suggest ways to strengthen community moderation policies.",
]

SAFE_REFUSAL = (
    "I can't assist with that aspect, but I can offer safer, constructive guidance instead."
)

def label_and_response(p: str):
    lower = p.lower()
    if any(k in lower for k in ["bypass", "license"]):
        return "refuse", SAFE_REFUSAL
    return "allow", "Here's constructive guidance: " + p.split(".")[0]


def build_entry(idx: int) -> dict:
    p = random.choice(PROMPTS)
    label, resp = label_and_response(p)
    return {
        "id": f"refusal_case_{idx:05d}",
        "messages": [
            {"role": "user", "content": p},
            {"role": "assistant", "content": resp},
        ],
        "meta": {
            "bucket": "refusal_boundary_cases",
            "persona": "jarvis",
            "policy_label": label,
            "readability_level": "B1",
            "affect_tone": "calm_neutral",
            "pedagogy_strategy": "safety_refusal" if label == "refuse" else "benign_guidance",
            "learning_objective": "policy_boundary_modeling",
            "session_phase": "mid_session",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        default="fine_tuning/datasets/processed/safety/refusal_boundary_cases.jsonl",
    )
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for i in range(args.n):
            f.write(json.dumps(build_entry(i), ensure_ascii=False) + "\n")
    print(f"[done] wrote {args.n} rows -> {args.output}")


if __name__ == "__main__":  # pragma: no cover
    main()
