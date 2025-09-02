#!/usr/bin/env python3
"""
Generate Interruption Handling & Recovery Dataset

Purpose:
  - 400 baseline (controller) high-quality interruption recovery examples (domain-agnostic or light-domain but reusable)
  - 100 specialized examples (distributed across expert domains) sharing same structural schema

Design Goals:
  - Provide neutral (agnostic) session closers & topic-shift handlers
  - Include Socratic probing variants to elicit missing info when context unclear
  - Distinguish interruption categories for controller routing & downstream specialized models
  - Uniform JSONL schema to append into larger ~7k medium finetune corpus

Schema Fields (per example):
  instruction: High-level narrative of tutoring/explainer state when interruption occurs
  input: Ongoing explanation text with [USER_INTERRUPTION] marker preceding user interjection
  output: Model response demonstrating recovery / clarification / closure / probe
  interruption_type: (clarification|lost_context|topic_shift|session_end|multi_turn_probe|emotion_signal)
  recovery_strategy: (agnostic_closer|socratic_probe|context_reaffirm|emotional_ack|guided_choice|topic_gateway)
  affect_focus: Emotional / motivational focus (curiosity|confusion_resolution|calm_reassurance|transition_management|positive_closure|engagement_renewal)
  controller_label: High-level action suggestion for control manager (continue|clarify|gather_info|close_session|switch_domain|pause_resume)
  tier: base|specialized
  domain: generic|mathematics|science|literature|programming|history|chemistry|physics (specialized only if tier != base)
  meta: {template_id, variant_id, source: "synthetic_v1", quality: heuristic 1-5}

Usage:
  python generate_interruption_recovery_dataset.py --out-dir fine_tuning/datasets/processed/interruption_handling --seed 13

Outputs:
  interruption_recovery_base_400.jsonl
  interruption_recovery_specialized_100.jsonl
  interruption_recovery_manifest.json (counts & distribution)
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

BASE_INTERRUPTION_TYPES = [
    "clarification",
    "lost_context",
    "topic_shift",
    "session_end",
    "multi_turn_probe",
    "emotion_signal",
]
RECOVERY_STRATEGIES = [
    "socratic_probe",
    "context_reaffirm",
    "agnostic_closer",
    "emotional_ack",
    "guided_choice",
    "topic_gateway",
]
AFFECT_FOCI = [
    "curiosity",
    "confusion_resolution",
    "calm_reassurance",
    "transition_management",
    "positive_closure",
    "engagement_renewal",
]
CONTROLLER_LABELS = [
    "continue",
    "clarify",
    "gather_info",
    "close_session",
    "switch_domain",
    "pause_resume",
]
SPECIALIZED_DOMAINS = ["mathematics", "science", "programming", "literature", "history"]

# Scenario templates (instruction + base narration + user interruption variants)
SCENARIOS = [
    {
        "id": "concept_explanation",
        "instruction": "Tutor explaining a multi-step concept when learner interrupts",
        "narration": "We break this into three logical stages. First, we establish the base principle. Second, we apply it to a concrete example.",
        "user_prompts": [
            "Sorry, can you slow down there? I'm not sure I grasp the first stage.",
            "Hold on—why do we start with that instead of an example first?",
            "Wait, before you continue, what exactly does 'base principle' mean here?",
        ],
        "default_output": "Great catch—let's anchor the very first piece before stacking more. The 'base principle' here means the fundamental rule everything else depends on. Once that feels solid, the rest becomes much easier. Could you tell me which part of it feels vague?",
    },
    {
        "id": "procedure_walkthrough",
        "instruction": "Tutor walking through a procedural sequence when learner interrupts",
        "narration": "The workflow usually flows in this order: gather inputs, normalize them, then evaluate edge conditions before final computation.",
        "user_prompts": [
            "Pause—what do you mean by normalize?",
            "Wait, is edge condition checking always before computation?",
            "Can we jump to the final step?",
        ],
        "default_output": "Normalization just means bringing inputs into a consistent, expected form (units, scale, or format). Would it help if we co-created a tiny example before proceeding?",
    },
    {
        "id": "session_wrap",
        "instruction": "Session nearing natural end; learner shifts abruptly",
        "narration": "We've covered the key objectives you set: baseline skill, error recognition, and confidence boosters.",
        "user_prompts": [
            "Uh can you just tell me a random fact instead?",
            "Actually I might be done— not sure.",
            "Can we switch to something totally different?",
        ],
        "default_output": "We can absolutely pivot or pause. I can either: (1) recap succinctly, (2) explore a quick related curiosity, or (3) close the session cleanly. Which serves you best right now?",
    },
    {
        "id": "lost_context",
        "instruction": "Learner re-enters after distraction and context must be rebuilt",
        "narration": "Earlier we mapped the core idea to a familiar analogy to lock it in.",
        "user_prompts": [
            "Sorry I zoned out—where were we?",
            "I lost the thread—can we rewind a bit?",
        ],
        "default_output": "No problem—I'll rebuild the scaffold. We had just linked the concept to an everyday pattern. Want a 1‑sentence recap or a step‑by‑step rewind?",
    },
]

SOCRATIC_FOLLOWUPS = [
    "What part feels least stable right now?",
    "If you had to explain the first step back to me, what's shaky?",
    "What do you think the goal of that stage was?",
    "Is the confusion about terminology, purpose, or sequence?",
]

EMOTIONAL_ACK_PREFIX = [
    "That's a totally valid pause.",
    "Appreciate you flagging that.",
    "Good moment to slow down.",
]

CLOSERS = [
    "You made solid progress—shall we bookmark here and pick up with a tiny refresher next time?",
    "Happy to wrap here. Want a 2‑line recap before we close?",
    "We can stop now and resume with a memory jog later—sound good?",
]

TOPIC_GATEWAYS = [
    "If we switch domains, would you prefer something conceptual, applied, or reflective?",
    "We can pivot: stick with depth, explore breadth, or practice retrieval—what's your instinct?",
]


def synthesize_output(
    base: Dict[str, Any], interruption_type: str, recovery_strategy: str
) -> str:
    """Blend elements into a response variant."""
    narration = base["narration"]
    core = base["default_output"]
    pieces = []
    if recovery_strategy == "emotional_ack":
        pieces.append(random.choice(EMOTIONAL_ACK_PREFIX))
    if recovery_strategy == "agnostic_closer":
        pieces.append(random.choice(CLOSERS))
    elif recovery_strategy == "topic_gateway":
        pieces.append(random.choice(TOPIC_GATEWAYS))
    elif recovery_strategy == "socratic_probe":
        pieces.append(core + " " + random.choice(SOCRATIC_FOLLOWUPS))
    elif recovery_strategy == "context_reaffirm":
        pieces.append(core)
    elif recovery_strategy == "guided_choice":
        pieces.append(
            "We have a few paths: a quick recap, a deeper drill, or pivot to a new angle. Which helps you more?"
        )
    # Emotional ack may accompany others
    return " ".join(pieces).strip()


@dataclass
class Example:
    instruction: str
    input: str
    output: str
    interruption_type: str
    recovery_strategy: str
    affect_focus: str
    controller_label: str
    tier: str
    domain: str
    meta: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def generate_examples(count: int, tier: str, domains: List[str]) -> List[Example]:
    examples: List[Example] = []
    template_cycle = 0
    for i in range(count):
        base = SCENARIOS[template_cycle % len(SCENARIOS)]
        template_cycle += 1
        interruption_type = random.choice(BASE_INTERRUPTION_TYPES)
        recovery_strategy = random.choice(RECOVERY_STRATEGIES)
        affect_focus = random.choice(AFFECT_FOCI)
        controller_label = random.choice(CONTROLLER_LABELS)
        domain = "generic" if tier == "base" else random.choice(domains)
        user_prompt = random.choice(base["user_prompts"])
        input_text = f"{base['narration']} [USER_INTERRUPTION] {user_prompt}"
        output_text = synthesize_output(base, interruption_type, recovery_strategy)
        quality = (
            5
            if recovery_strategy in ("socratic_probe", "guided_choice", "topic_gateway")
            else 4
        )
        examples.append(
            Example(
                instruction=base["instruction"],
                input=input_text,
                output=output_text,
                interruption_type=interruption_type,
                recovery_strategy=recovery_strategy,
                affect_focus=affect_focus,
                controller_label=controller_label,
                tier=tier,
                domain=domain,
                meta={
                    "template_id": base["id"],
                    "variant_id": i,
                    "source": "synthetic_v1",
                    "quality": quality,
                },
            )
        )
    return examples


def stratified_generate(total: int, tier: str, domains: List[str]) -> List[Example]:
    """Ensure balanced distribution across interruption types & strategies."""
    target_per_type = math.ceil(total / len(BASE_INTERRUPTION_TYPES))
    bucket: Dict[str, List[Example]] = {t: [] for t in BASE_INTERRUPTION_TYPES}
    attempts = 0
    while sum(len(v) for v in bucket.values()) < total and attempts < total * 10:
        attempts += 1
        ex = generate_examples(1, tier, domains)[0]
        if len(bucket[ex.interruption_type]) < target_per_type:
            bucket[ex.interruption_type].append(ex)
    # Flatten and trim to total
    flat = [e for group in bucket.values() for e in group]
    return flat[:total]


def build_manifest(
    base_examples: List[Example], spec_examples: List[Example]
) -> Dict[str, Any]:
    def dist(exs: List[Example], attr: str) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for e in exs:
            key = getattr(e, attr)
            out[key] = out.get(key, 0) + 1
        return dict(sorted(out.items()))

    return {
        "total_base": len(base_examples),
        "total_specialized": len(spec_examples),
        "interruption_type_distribution_base": dist(base_examples, "interruption_type"),
        "recovery_strategy_distribution_base": dist(base_examples, "recovery_strategy"),
        "controller_label_distribution_base": dist(base_examples, "controller_label"),
        "domains_specialized": dist(spec_examples, "domain"),
        "recovery_strategy_distribution_specialized": dist(
            spec_examples, "recovery_strategy"
        ),
        "notes": "Synthetic generation v1. Consider human refinement pass for top quality subset.",
        "schema_version": "1.0.0",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir", default="fine_tuning/datasets/processed/interruption_handling"
    )
    ap.add_argument("--base-count", type=int, default=400)
    ap.add_argument("--specialized-count", type=int, default=100)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    random.seed(args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_examples = stratified_generate(args.base_count, "base", [])
    spec_examples = stratified_generate(
        args.specialized_count, "specialized", SPECIALIZED_DOMAINS
    )

    base_path = out_dir / "interruption_recovery_base_400.jsonl"
    spec_path = out_dir / "interruption_recovery_specialized_100.jsonl"
    manifest_path = out_dir / "interruption_recovery_manifest.json"

    with base_path.open("w", encoding="utf-8") as bf:
        for e in base_examples:
            bf.write(e.to_json() + "\n")
    with spec_path.open("w", encoding="utf-8") as sf:
        for e in spec_examples:
            sf.write(e.to_json() + "\n")

    manifest = build_manifest(base_examples, spec_examples)
    with manifest_path.open("w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(base_examples)} base examples -> {base_path}")
    print(f"✅ Generated {len(spec_examples)} specialized examples -> {spec_path}")
    print(f"📄 Manifest -> {manifest_path}")
    print(
        "Distribution (base interruption types):",
        manifest["interruption_type_distribution_base"],
    )


if __name__ == "__main__":
    main()
