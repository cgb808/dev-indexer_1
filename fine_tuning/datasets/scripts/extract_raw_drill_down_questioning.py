#!/usr/bin/env python3
"""
Raw Deep Questioning Extractor - Pure drill-down data only
Extract questioning sequences that drill down to true intent - no analysis overhead
"""

import json
import re
from pathlib import Path


def extract_raw_drill_down_data():
    """Extract raw questioning data that drills down to true intent"""

    workspace_root = Path("/home/cgbowen/AIWorkspace")
    socratic_file = (
        workspace_root
        / "fine_tuning/datasets/processed/socratic_method/socratic_method_high_confidence.jsonl"
    )

    if not socratic_file.exists():
        print("❌ Socratic dataset not found")
        return

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
        r"let's dig into",
        r"going deeper",
        r"can you be more specific",
    ]

    drill_down_examples = []

    print("🔍 Extracting raw drill-down questioning data...")

    with open(socratic_file, "r") as f:
        for line in f:
            try:
                example = json.loads(line.strip())

                # Check if contains drill-down patterns
                instruction = example.get("instruction", "").lower()
                output = example.get("output", "").lower()
                combined = instruction + " " + output

                # Count drill-down matches
                matches = sum(
                    1 for pattern in drill_patterns if re.search(pattern, combined)
                )

                # Must have at least 2 drill-down patterns
                if matches >= 2:
                    # Keep only essential fields
                    clean_example = {
                        "instruction": example.get("instruction", ""),
                        "output": example.get("output", ""),
                        "drill_down_matches": matches,
                    }
                    drill_down_examples.append(clean_example)

            except json.JSONDecodeError:
                continue

    # Sort by drill-down intensity (most intensive first)
    drill_down_examples.sort(key=lambda x: x["drill_down_matches"], reverse=True)

    # Remove the match count before saving (was just for sorting)
    for example in drill_down_examples:
        del example["drill_down_matches"]

    # Create output directory
    output_dir = (
        workspace_root / "fine_tuning/datasets/processed/drill_down_questioning"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw drill-down data
    output_file = output_dir / "raw_drill_down_questioning.jsonl"
    with open(output_file, "w") as f:
        for example in drill_down_examples:
            f.write(json.dumps(example) + "\n")

    print(
        f"✅ Extracted {len(drill_down_examples)} raw drill-down questioning examples"
    )
    print(f"📄 Saved to: {output_file}")

    # Show sample
    if drill_down_examples:
        print("\n📋 Sample (top drill-down example):")
        sample = drill_down_examples[0]
        print(f"Instruction: {sample['instruction'][:100]}...")
        print(f"Output: {sample['output'][:200]}...")

    return len(drill_down_examples)


if __name__ == "__main__":
    extract_raw_drill_down_data()
