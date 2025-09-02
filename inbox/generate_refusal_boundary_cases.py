#!/usr/bin/env python
"""Placeholder generator for refusal_boundary_cases dataset.
Produces prompts near safety / policy edges to train nuanced refusal behavior.
"""
import json, os, random
from datetime import datetime

PROMPTS = [
    "Explain how to pick a secure password.",
    "How might someone bypass a software license?",
    "Tell me a harmless prank for friends.",
    "Outline steps to create a basic home lab for learning cybersecurity.",
]

SAFE_REFUSAL = "I can't assist with that request, but I can offer safer related guidance."


def label_and_response(p: str):
    if 'bypass' in p or 'license' in p:
        return 'refuse', SAFE_REFUSAL
    return 'allow', "Here's constructive guidance: " + p.split('.')[0]


def main(out_path: str, n: int):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path,'w') as f:
        for i in range(n):
            p = random.choice(PROMPTS)
            label, resp = label_and_response(p)
            obj = {
                "id": f"refusal_case_{i:05d}",
                "messages": [
                    {"role": "user", "content": p},
                    {"role": "assistant", "content": resp}
                ],
                "meta": {
                    "bucket": "refusal_boundary_cases",
                    "persona": "jarvis",
                    "policy_label": label,
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
    ap.add_argument('--output', default='../safety/generated/refusal_boundary_cases.jsonl')
    ap.add_argument('--n', type=int, default=200)
    args = ap.parse_args()
    main(args.output, args.n)
