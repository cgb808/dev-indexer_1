#!/usr/bin/env python
"""Placeholder generator for safety_moderation_interventions dataset.
Generates synthetic moderation intervention training pairs.
TODO: Replace with real pipeline sourcing from policy templates and real logs.
"""
import json, os, random
from datetime import datetime

PROMPTS = [
    "Describe how to safely dispose of household chemicals.",
    "Give advice to a teen experiencing online bullying.",
    "What should someone do if they see hateful content in a forum?",
]

def main(out_path: str, n: int):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path,'w') as f:
        for i in range(n):
            p = random.choice(PROMPTS)
            assistant = "I can help with safety-oriented guidance. First, avoid harm. " + p.split('.')[0]
            obj = {
                "id": f"safety_mod_{i:05d}",
                "messages": [
                    {"role": "user", "content": p},
                    {"role": "assistant", "content": assistant}
                ],
                "meta": {
                    "bucket": "safety_moderation_interventions",
                    "persona": "jarvis",
                    "safety": True,
                    "readability_level": "B1",
                    "affect_tone": "calm_neutral",
                    "generated_at": datetime.utcnow().isoformat() + 'Z'
                }
            }
            f.write(json.dumps(obj) + '\n')
    print(f'[done] wrote {out_path}')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='../safety/generated/safety_moderation_interventions.jsonl')
    ap.add_argument('--n', type=int, default=200)
    args = ap.parse_args()
    main(args.output, args.n)
