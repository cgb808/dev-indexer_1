#!/usr/bin/env python3
"""
Extract Pure Methodology Examples from Hybrid Dataset
Creates a pure tutoring methodology dataset for base model training
"""

import json
from datetime import datetime
from pathlib import Path


def extract_pure_methodology():
    """Extract pure methodology examples from the hybrid dataset"""

    workspace = Path("/home/cgbowen/AIWorkspace")
    hybrid_file = (
        workspace
        / "fine_tuning/datasets/processed/hybrid/hybrid_methodology_math_dataset.jsonl"
    )

    if not hybrid_file.exists():
        print(f"❌ Hybrid dataset not found: {hybrid_file}")
        return

    print("🔍 EXTRACTING PURE METHODOLOGY EXAMPLES")
    print("=" * 60)
    print(f"Source: {hybrid_file}")

    pure_methodology_examples = []
    math_with_methodology_examples = []

    # Read and categorize examples
    with open(hybrid_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                example = json.loads(line.strip())

                # Check example type
                example_type = example.get("example_type", "")

                if example_type == "pure_methodology":
                    pure_methodology_examples.append(example)
                elif example_type == "mathematics_with_methodology":
                    math_with_methodology_examples.append(example)
                else:
                    print(f"⚠️  Unknown example type at line {line_num}: {example_type}")

            except json.JSONDecodeError as e:
                print(f"❌ JSON error at line {line_num}: {e}")

    print("\n📊 EXTRACTION RESULTS:")
    print(f"Pure Methodology Examples: {len(pure_methodology_examples)}")
    print(f"Math + Methodology Examples: {len(math_with_methodology_examples)}")
    print(
        f"Total Examples: {len(pure_methodology_examples) + len(math_with_methodology_examples)}"
    )

    # Save pure methodology examples
    pure_methodology_file = (
        workspace / "fine_tuning/datasets/processed/pure_methodology_tutoring.jsonl"
    )

    with open(pure_methodology_file, "w") as f:
        for example in pure_methodology_examples:
            f.write(json.dumps(example) + "\n")

    print(f"\n✅ Pure methodology examples saved: {pure_methodology_file}")

    # Show some examples
    print("\n📋 SAMPLE PURE METHODOLOGY EXAMPLES:")
    print("=" * 50)

    for i, example in enumerate(pure_methodology_examples[:5]):
        print(f"\nExample {i+1}:")
        instruction = (
            example.get("instruction", "")[:100] + "..."
            if len(example.get("instruction", "")) > 100
            else example.get("instruction", "")
        )
        output = (
            example.get("output", "")[:150] + "..."
            if len(example.get("output", "")) > 150
            else example.get("output", "")
        )

        print(f"  Instruction: {instruction}")
        print(f"  Output: {output}")

        if "methodology_focus" in example:
            print(f"  Methodology: {example['methodology_focus']}")

    # Create methodology breakdown
    methodology_breakdown = {}
    for example in pure_methodology_examples:
        methodology = example.get("methodology_focus", "unknown")
        if methodology not in methodology_breakdown:
            methodology_breakdown[methodology] = 0
        methodology_breakdown[methodology] += 1

    print("\n📈 METHODOLOGY BREAKDOWN:")
    print("=" * 40)
    for methodology, count in sorted(
        methodology_breakdown.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {methodology}: {count} examples")

    # Save breakdown
    breakdown_file = (
        workspace / "fine_tuning/datasets/processed/pure_methodology_breakdown.json"
    )

    breakdown_data = {
        "extraction_timestamp": datetime.now().isoformat(),
        "source_file": str(hybrid_file),
        "total_pure_methodology": len(pure_methodology_examples),
        "total_math_with_methodology": len(math_with_methodology_examples),
        "methodology_breakdown": methodology_breakdown,
        "sample_examples": pure_methodology_examples[:10],  # Save first 10 as samples
    }

    with open(breakdown_file, "w") as f:
        json.dump(breakdown_data, f, indent=2)

    print(f"\n✅ Breakdown data saved: {breakdown_file}")

    return pure_methodology_examples, breakdown_data


def main():
    """Extract and analyze pure methodology examples"""

    print("🎯 PURE METHODOLOGY EXTRACTION")
    print("=" * 50)
    print("Purpose: Extract tutoring methodology for base model training")
    print("Strategy: Pure methodology foundation + specialized subject epochs")
    print("=" * 50)

    pure_examples, breakdown = extract_pure_methodology()

    if pure_examples:
        print("\n🎉 EXTRACTION COMPLETE!")
        print("=" * 40)
        print(f"✅ {len(pure_examples)} pure methodology examples extracted")
        print("✅ Ready for base model training")
        print("✅ Can be combined with personality data")
        print("\n🚀 Next: Create base training set with methodology + personality")


if __name__ == "__main__":
    main()
