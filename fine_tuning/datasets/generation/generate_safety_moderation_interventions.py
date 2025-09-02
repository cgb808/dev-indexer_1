#!/usr/bin/env python
"""Generate safety_moderation_interventions synthetic dataset.

Purpose: Provide initial safety intervention examples (user unsafe/at-risk or guidance-seeking prompt, assistant offers safe redirection/help).
Status: Placeholder synthetic generator. Replace with real pipeline (policy templates + curated interventions + anonymized real cases) when available.

Default output: fine_tuning/datasets/processed/safety/safety_moderation_interventions.jsonl
"""
from __future__ import annotations
import json, os, random
from datetime import datetime, timezone
import argparse

PROMPTS = [
    "Describe how to safely dispose of household chemicals.",
    "Give advice to a teen experiencing online bullying.",
    "What should someone do if they see hateful content in a forum?",
    "How to respond if a friend shares self-harm thoughts?",
    "Best practices for reporting harassment in an online game?",
]

SAFETY_TAG = "safety_intervention"

def build_entry(idx: int) -> dict:
    p = random.choice(PROMPTS)
    assistant = (
        "I can help with safety-oriented guidance. Let's prioritize well-being. "
        + p.split('.')[0]
    )
    return {
        "id": f"safety_mod_{idx:05d}",
        "messages": [
            {"role": "user", "content": p},
            {"role": "assistant", "content": assistant},
        ],
        "meta": {
            "bucket": "safety_moderation_interventions",
            "persona": "jarvis",
            "safety": True,
            "readability_level": "B1",
            "affect_tone": "calm_neutral",
            "pedagogy_strategy": "safety_guidance",
            "learning_objective": "promote_safe_behavior",
            "session_phase": "mid_session",
            "safety_tag": SAFETY_TAG,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        default="fine_tuning/datasets/processed/safety/safety_moderation_interventions.jsonl",
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
