#!/usr/bin/env python3
"""Synthetic RAG Training Example Builder.

Generates supervised training pairs that demonstrate proper usage of retrieved
context (RAG) with citation discipline and fallback behavior.

Outputs JSONL with fields described in docs/rag_training_guidelines.md.

NOTE: This is a scaffold using simplistic heuristics. Replace or augment with
real retrieval logs + human authored examples for production.
"""
from __future__ import annotations

import argparse, os, json, random, textwrap, hashlib
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import List, Dict, Any


@dataclass
class DocStub:
    doc_id: str
    title: str
    content: str


SCENARIOS = [
    "direct", "multi_hop", "conflict", "insufficient", "distractor", "summarize"
]

DEFAULT_DISTRIBUTION = {
    "direct": 0.35,
    "multi_hop": 0.25,
    "conflict": 0.10,
    "insufficient": 0.10,
    "distractor": 0.10,
    "summarize": 0.10,
}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def make_prompt(query: str, docs: List[DocStub]) -> str:
    ctx_lines = ["[RAG_CONTEXT]"]
    for d in docs:
        ctx_lines.append(f"<{d.doc_id} title=\"{d.title}\">\n{d.content}\n</{d.doc_id}>")
    ctx_lines.append("[/RAG_CONTEXT]")
    instructions = textwrap.dedent(
        """[INSTRUCTIONS]
        You are a tutoring assistant. Use ONLY facts in documents D* above.
        Cite sources inline as [Dk]. If insufficient info, output NEED_RETRIEVAL_MORE only.
        """.strip()
    )
    return f"[USER]\n{query}\n\n" + "\n".join(ctx_lines) + "\n\n" + instructions


def build_example(rng: random.Random, scenario: str, idx: int) -> Dict[str, Any]:
    # Create synthetic docs
    docs: List[DocStub] = []
    def add_doc(title: str, content: str):
        doc_id = f"D{len(docs)+1}"
        docs.append(DocStub(doc_id, title, content))

    if scenario == "direct":
        add_doc("Place Value Basics", "Place value assigns value based on a digit's position in a number.")
        query = "Explain place value briefly."
        answer = "Place value means a digit's value depends on its position in the number [D1]."
        reasoning = "Need basic definition; single doc D1 sufficient."
        citations = ["D1"]
    elif scenario == "multi_hop":
        add_doc("Fraction Definition", "A fraction represents equal parts of a whole.")
        add_doc("Simplifying Fractions", "To simplify a fraction divide numerator and denominator by their greatest common factor.")
        query = "How do you explain a fraction and also how to simplify it?"
        answer = "A fraction shows equal parts of a whole [D1]. To simplify, divide top and bottom by their greatest common factor [D2]."
        reasoning = "Two pieces: definition from D1 + simplification process from D2."
        citations = ["D1","D2"]
    elif scenario == "conflict":
        add_doc("Study Time Advice A", "Recommended daily study time is 30 minutes for early learners.")
        add_doc("Study Time Advice B", "Some experts suggest 45 minutes daily study for early learners.")
        query = "How long should early learners study daily?"
        answer = "Sources disagree: one recommends 30 minutes [D1] while another suggests 45 minutes [D2]."
        reasoning = "Identify conflict; present both without choosing."
        citations = ["D1","D2"]
    elif scenario == "insufficient":
        add_doc("Math Motivation", "Encouraging a growth mindset improves persistence.")
        query = "What is the capital of France?"
        answer = "NEED_RETRIEVAL_MORE"
        reasoning = "Question unrelated to provided context; must signal retrieval."
        citations = []
    elif scenario == "distractor":
        add_doc("Irrelevant Volcano Fact", "Volcanoes emit lava and ash.")
        add_doc("Multiplication Tip", "Skip counting helps learners internalize multiplication patterns.")
        query = "Give a quick multiplication learning tip."
        answer = "Using skip counting builds recognition of multiplication patterns [D2]."
        reasoning = "Ignore irrelevant volcano doc D1; use D2 only."
        citations = ["D2"]
    elif scenario == "summarize":
        add_doc("Note Taking Benefit", "Summarizing in own words improves retention.")
        add_doc("Active Recall", "Quizzing oneself strengthens memory pathways.")
        add_doc("Spaced Practice", "Spacing study sessions enhances long-term retention.")
        query = "Summarize the study strategies listed."
        answer = (
            "Effective strategies include summarizing concepts in your own words [D1], quizzing yourself for active recall [D2], "
            "and spacing study sessions to boost long-term retention [D3]."
        )
        reasoning = "Enumerate each strategy with matching doc citation."
        citations = ["D1","D2","D3"]
    else:
        raise ValueError(scenario)

    prompt = make_prompt(query, docs)
    if answer != "NEED_RETRIEVAL_MORE":
        response = f"[THINK]\n{reasoning}\n[/THINK]\n[ANSWER]\n{answer}\n[/ANSWER]"
    else:
        response = f"[THINK]\n{reasoning}\n[/THINK]\n[ANSWER]\n{answer}\n[/ANSWER]"
    record = {
        "id": f"{scenario}_{idx}",
        "type": "rag_usage",
        "scenario": scenario,
        "query": query,
        "rag_context": [d.__dict__ for d in docs],
        "expected_answer": answer,
        "reasoning": reasoning,
        "citations": citations,
        "prompt": prompt,
        "response": response,
        "created_at": datetime.now(UTC).isoformat(),
        "hash": sha256(prompt + "\n" + response),
    }
    return record


def allocate_counts(total: int, dist: Dict[str, float]) -> Dict[str, int]:
    raw = {k: total * v for k, v in dist.items()}
    counts = {k: int(v) for k, v in raw.items()}
    # distribute remainder
    remainder = total - sum(counts.values())
    if remainder > 0:
        # sort by fractional part descending
        frac = sorted(((raw[k]-counts[k], k) for k in counts), reverse=True)
        for _, k in frac[:remainder]:
            counts[k] += 1
    return counts


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic RAG usage training examples")
    ap.add_argument("--out", default="data/rag/rag_usage_examples.jsonl")
    ap.add_argument("--total", type=int, default=120)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--no-msgpack", action="store_true", help="Skip msgpack artifact")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    rng = random.Random(args.seed)
    counts = allocate_counts(args.total, DEFAULT_DISTRIBUTION)
    records: List[Dict[str, Any]] = []
    for scenario in SCENARIOS:
        for i in range(counts[scenario]):
            records.append(build_example(rng, scenario, i))
    rng.shuffle(records)
    with open(args.out, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"[jsonl] wrote {len(records)} examples -> {args.out}")
    if not args.no_msgpack:
        try:
            import msgpack  # type: ignore
            mp_path = args.out.replace('.jsonl', '.msgpack')
            payload = {"version": 1, "total": len(records), "examples": records}
            with open(mp_path, 'wb') as f:
                f.write(msgpack.packb(payload, use_bin_type=True))
            print(f"[msgpack] {mp_path}")
        except Exception as e:  # noqa: BLE001
            print(f"[msgpack] skip ({e})")

if __name__ == '__main__':
    main()
