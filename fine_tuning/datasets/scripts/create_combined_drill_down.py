#!/usr/bin/env python3
"""
Create Combined Drill-Down Questioning Dataset
Combine all drill-down questioning data into one comprehensive dataset
"""

import json
from pathlib import Path


def create_combined_drill_down_dataset():
    """Create final combined drill-down questioning dataset"""

    workspace_root = Path("/home/cgbowen/AIWorkspace")
    drill_down_dir = (
        workspace_root / "fine_tuning/datasets/processed/drill_down_questioning"
    )

    # Source files
    real_drill_file = drill_down_dir / "real_drill_down_questioning.jsonl"
    socratic_file = (
        workspace_root
        / "fine_tuning/datasets/processed/socratic_method/socratic_method_high_confidence.jsonl"
    )

    combined_examples = []
    unique_outputs = set()

    print("🔄 Combining all drill-down questioning data...")

    # Add real drill-down examples first (highest quality)
    if real_drill_file.exists():
        with open(real_drill_file, "r") as f:
            for line in f:
                try:
                    example = json.loads(line.strip())
                    output = example.get("output", "")

                    if output and output not in unique_outputs:
                        unique_outputs.add(output)
                        combined_examples.append(example)

                except json.JSONDecodeError:
                    continue

        print(f"✅ Added {len(combined_examples)} real drill-down examples")

    # Add unique high-confidence Socratic examples
    if socratic_file.exists():
        socratic_count = 0
        with open(socratic_file, "r") as f:
            for line in f:
                try:
                    example = json.loads(line.strip())
                    output = example.get("output", "")

                    # Skip templated responses
                    if (
                        "[SOCRATIC_RESPONSE]" in output
                        and "That's an interesting point" in output
                    ):
                        continue

                    if output and output not in unique_outputs and len(output) > 50:
                        unique_outputs.add(output)
                        combined_examples.append(example)
                        socratic_count += 1

                except json.JSONDecodeError:
                    continue

        print(f"✅ Added {socratic_count} unique Socratic examples")

    # Save combined dataset
    combined_file = drill_down_dir / "combined_drill_down_questioning.jsonl"
    with open(combined_file, "w") as f:
        for example in combined_examples:
            f.write(json.dumps(example) + "\n")

    print(f"📄 Combined dataset saved: {combined_file}")
    print(f"📊 Total examples: {len(combined_examples)}")

    # Show stats
    print("\n📈 DRILL-DOWN QUESTIONING DATASET READY:")
    print(f"Total Examples: {len(combined_examples)}")
    print(f"File: {combined_file}")
    print(f"Size: {combined_file.stat().st_size / 1024:.1f} KB")

    # Show sample
    if combined_examples:
        print("\n📋 Sample drill-down questioning:")
        sample = combined_examples[0]
        print(f"Input: {sample['instruction'][:80]}...")
        print(f"Drill-down: {sample['output'][:120]}...")

    return len(combined_examples)


if __name__ == "__main__":
    create_combined_drill_down_dataset()
