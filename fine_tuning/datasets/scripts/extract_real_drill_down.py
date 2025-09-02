#!/usr/bin/env python3
"""
Extract Real Drill-Down Questioning - From Socratic Teaching Dataset
Get actual drill-down questioning sequences from real tutoring conversations
"""

import json
import re
from pathlib import Path


def extract_real_drill_down_data():
    """Extract real drill-down questioning from Socratic teaching conversations"""

    workspace_root = Path("/home/cgbowen/AIWorkspace")
    socratic_file = (
        workspace_root
        / "fine_tuning/datasets/processed/tutoring/tutoring_datasets/KarthikaRajagopal_socratic_teaching_dataset_sample.jsonl"
    )

    if not socratic_file.exists():
        print("❌ Socratic teaching dataset not found")
        return

    drill_down_examples = []

    # Drill-down questioning patterns
    drill_patterns = [
        r"what do you think",
        r"can you.*try",
        r"what.*you get",
        r"how.*you",
        r"what should",
        r"where should",
        r"remember.*you can",
        r"let's.*consider",
        r"what.*rule",
        r"how many",
        r"what.*result",
        r"try again",
        r"not quite",
        r"almost.*but",
        r"let's reconsider",
        r"excellent question",
        r"here's a tip",
        r"what.*equals",
    ]

    print("🔍 Extracting real drill-down questioning from Socratic conversations...")

    with open(socratic_file, "r") as f:
        for line in f:
            try:
                conversation = json.loads(line.strip())
                messages = conversation.get("messages", [])

                # Extract assistant responses that contain questioning
                for message in messages:
                    if message.get("role") == "assistant":
                        content = message.get("content", "")

                        # Skip if too short
                        if len(content) < 20:
                            continue

                        # Check for drill-down patterns
                        content_lower = content.lower()
                        matches = sum(
                            1
                            for pattern in drill_patterns
                            if re.search(pattern, content_lower)
                        )

                        # Must have drill-down questioning and a question mark
                        if matches >= 1 and "?" in content:
                            # Extract context from previous messages
                            context = ""
                            for prev_msg in messages:
                                if prev_msg == message:
                                    break
                                if prev_msg.get("role") == "user":
                                    context = prev_msg.get("content", "")

                            drill_example = {
                                "instruction": (
                                    context.strip()
                                    if context
                                    else "Student needs guidance"
                                ),
                                "output": content.strip(),
                            }
                            drill_down_examples.append(drill_example)

            except json.JSONDecodeError:
                continue

    # Remove duplicates
    unique_examples = []
    seen_outputs = set()

    for example in drill_down_examples:
        if example["output"] not in seen_outputs:
            seen_outputs.add(example["output"])
            unique_examples.append(example)

    print(
        f"✅ Found {len(unique_examples)} unique real drill-down questioning examples"
    )

    # Create output directory
    output_dir = (
        workspace_root / "fine_tuning/datasets/processed/drill_down_questioning"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save real drill-down questioning data
    output_file = output_dir / "real_drill_down_questioning.jsonl"
    with open(output_file, "w") as f:
        for example in unique_examples:
            f.write(json.dumps(example) + "\n")

    print(f"📄 Saved to: {output_file}")

    # Show samples
    if unique_examples:
        print("\n📋 Sample real drill-down questioning:")
        for i, example in enumerate(unique_examples[:5], 1):
            print(f"\nExample {i}:")
            print(f"Context: {example['instruction'][:60]}...")
            print(f"Drill-down: {example['output'][:100]}...")
            print("-" * 50)

    return len(unique_examples)


if __name__ == "__main__":
    extract_real_drill_down_data()
