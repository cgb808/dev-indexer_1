#!/usr/bin/env python3
"""
Extract Varied Drill-Down Questioning - Real questioning sequences
Get actual varied drill-down examples, not templated responses
"""

import json
import re
from pathlib import Path


def extract_varied_drill_down_data():
    """Extract actual varied drill-down questioning sequences"""

    workspace_root = Path("/home/cgbowen/AIWorkspace")

    # Check all available dataset files
    dataset_files = [
        workspace_root
        / "fine_tuning/datasets/processed/pure_methodology/pure_methodology_tutoring.jsonl",
        workspace_root
        / "fine_tuning/datasets/processed/personality_examples/personality_tutoring_examples.jsonl",
        workspace_root / "data/eli5_sample.jsonl",
    ]

    # Drill-down questioning patterns
    drill_patterns = [
        r"what makes you think",
        r"why do you believe",
        r"can you walk me through",
        r"what evidence",
        r"how did you arrive",
        r"what assumptions",
        r"what led you to conclude",
        r"how do you know",
        r"what would convince you",
        r"can you explain your logic",
        r"what are you really trying",
        r"what's your actual goal",
        r"what's behind your thinking",
        r"what's driving this",
        r"let's dig deeper",
        r"can you be more specific",
        r"what do you mean by",
        r"how are you defining",
        r"what's your reasoning",
        r"what's the basis for",
    ]

    varied_examples = []
    unique_outputs = set()

    print("🔍 Extracting varied drill-down questioning sequences...")

    for dataset_file in dataset_files:
        if not dataset_file.exists():
            continue

        print(f"📂 Processing: {dataset_file.name}")

        with open(dataset_file, "r") as f:
            for line in f:
                try:
                    example = json.loads(line.strip())

                    instruction = example.get("instruction", "")
                    output = example.get("output", "")

                    # Skip if empty or too short
                    if len(output) < 50:
                        continue

                    # Skip templated responses
                    if (
                        "[SOCRATIC_RESPONSE]" in output
                        and "That's an interesting point" in output
                    ):
                        continue

                    # Check for drill-down patterns
                    combined = (instruction + " " + output).lower()
                    matches = sum(
                        1 for pattern in drill_patterns if re.search(pattern, combined)
                    )

                    # Must have at least 2 drill-down patterns and be unique
                    if matches >= 2 and output not in unique_outputs:
                        unique_outputs.add(output)

                        # Clean up the example
                        clean_example = {
                            "instruction": instruction.strip(),
                            "output": output.strip(),
                        }
                        varied_examples.append(clean_example)

                except json.JSONDecodeError:
                    continue

    print(f"✅ Found {len(varied_examples)} unique drill-down questioning examples")

    # Create output directory
    output_dir = (
        workspace_root / "fine_tuning/datasets/processed/drill_down_questioning"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save varied drill-down data
    output_file = output_dir / "varied_drill_down_questioning.jsonl"
    with open(output_file, "w") as f:
        for example in varied_examples:
            f.write(json.dumps(example) + "\n")

    print(f"📄 Saved to: {output_file}")

    # Show samples
    if varied_examples:
        print("\n📋 Sample varied drill-down examples:")
        for i, example in enumerate(varied_examples[:3], 1):
            print(f"\nExample {i}:")
            print(f"Instruction: {example['instruction'][:80]}...")
            print(f"Drill-down: {example['output'][:150]}...")
            print("-" * 50)

    return len(varied_examples)


if __name__ == "__main__":
    extract_varied_drill_down_data()
