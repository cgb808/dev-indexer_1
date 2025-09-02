#!/usr/bin/env python3
"""
Hybrid Methodology + Mathematics Dataset Creator
Creates a hybrid dataset with:
- 500 pure methodology examples (subject-agnostic)
- 500 mathematics + methodology examples (subject-specific with teaching techniques)
"""

import json
import os
import random
from datetime import datetime


class HybridMethodologyMathDatasetCreator:
    """Create hybrid methodology + mathematics training data"""

    def __init__(self):
        self.pure_methodology_path = (
            "data/tutoring_methodology/comprehensive_methodology_dataset.jsonl"
        )
        self.math_tutoring_path = (
            "data/tutoring_instructional/combined_tutoring_dataset.jsonl"
        )

    def load_pure_methodology_examples(self, count=500):
        """Load pure methodology examples"""

        if not os.path.exists(self.pure_methodology_path):
            raise FileNotFoundError(
                f"Pure methodology dataset not found: {self.pure_methodology_path}"
            )

        examples = []
        with open(self.pure_methodology_path, "r") as f:
            for line in f:
                examples.append(json.loads(line.strip()))

        # Randomly sample the requested count
        if len(examples) > count:
            examples = random.sample(examples, count)

        print(f"📚 Loaded {len(examples)} pure methodology examples")
        return examples

    def load_math_tutoring_examples(self, count=500):
        """Load mathematics tutoring examples"""

        if not os.path.exists(self.math_tutoring_path):
            raise FileNotFoundError(
                f"Math tutoring dataset not found: {self.math_tutoring_path}"
            )

        examples = []
        with open(self.math_tutoring_path, "r") as f:
            for line in f:
                examples.append(json.loads(line.strip()))

        # Randomly sample the requested count
        if len(examples) > count:
            examples = random.sample(examples, count)

        print(f"🔢 Loaded {len(examples)} mathematics tutoring examples")
        return examples

    def enhance_math_examples_with_methodology(self, math_examples):
        """Enhance mathematics examples with explicit methodology components"""

        enhanced_examples = []

        methodology_enhancements = [
            {
                "methodology": "Socratic Questioning",
                "prefix": "[METHODOLOGY: Socratic Questioning] Guide through strategic questions: ",
                "suffix": "\n\n[TEACHING_APPROACH] Use questioning to help student discover the solution rather than providing direct answers.",
            },
            {
                "methodology": "Scaffolding",
                "prefix": "[METHODOLOGY: Scaffolding] Break down into manageable steps: ",
                "suffix": "\n\n[TEACHING_APPROACH] Provide supportive structure while building student independence.",
            },
            {
                "methodology": "Error Analysis",
                "prefix": "[METHODOLOGY: Error Analysis] Help identify and learn from mistakes: ",
                "suffix": "\n\n[TEACHING_APPROACH] Guide student to find their own errors and understand why they occurred.",
            },
            {
                "methodology": "Step-by-Step Teaching",
                "prefix": "[METHODOLOGY: Step-by-Step] Provide clear, systematic progression: ",
                "suffix": "\n\n[TEACHING_APPROACH] Ensure each step is understood before moving to the next.",
            },
            {
                "methodology": "Conceptual Explanation",
                "prefix": "[METHODOLOGY: Conceptual Explanation] Connect to underlying concepts: ",
                "suffix": "\n\n[TEACHING_APPROACH] Help student understand the 'why' behind the procedures.",
            },
        ]

        for example in math_examples:
            # Randomly select a methodology enhancement
            enhancement = random.choice(methodology_enhancements)

            # Create enhanced instruction
            original_instruction = example.get("instruction", "")
            enhanced_instruction = f"{enhancement['prefix']}{original_instruction}"

            # Create enhanced output
            original_output = example.get("output", "")
            enhanced_output = f"{original_output}{enhancement['suffix']}"

            enhanced_example = {
                "instruction": enhanced_instruction,
                "input": example.get("input", ""),
                "output": enhanced_output,
                "methodology_focus": enhancement["methodology"],
                "original_type": "mathematics_tutoring",
                "enhancement": "methodology_integrated",
            }

            enhanced_examples.append(enhanced_example)

        print(
            f"🔧 Enhanced {len(enhanced_examples)} mathematics examples with methodology"
        )
        return enhanced_examples

    def create_hybrid_dataset(self):
        """Create hybrid dataset with 500 pure methodology + 500 enhanced math"""

        print("🎯 Creating Hybrid Methodology + Mathematics Dataset")
        print("=" * 70)
        print("Target: 500 pure methodology + 500 mathematics + methodology")
        print("=" * 70)

        # Load pure methodology examples
        pure_methodology = self.load_pure_methodology_examples(500)

        # Load and enhance mathematics examples
        math_examples = self.load_math_tutoring_examples(500)
        enhanced_math = self.enhance_math_examples_with_methodology(math_examples)

        # Combine all examples
        all_examples = []

        # Add pure methodology examples with clear tagging
        for example in pure_methodology:
            tagged_example = {
                "instruction": example["instruction"],
                "input": example.get("input", ""),
                "output": example.get(
                    "output", example.get("response", "")
                ),  # Handle both 'output' and 'response' fields
                "example_type": "pure_methodology",
                "subject_focus": "subject_agnostic",
            }
            all_examples.append(tagged_example)

        # Add enhanced mathematics examples
        for example in enhanced_math:
            tagged_example = {
                "instruction": example["instruction"],
                "input": example.get("input", ""),
                "output": example["output"],
                "example_type": "mathematics_with_methodology",
                "subject_focus": "mathematics",
                "methodology_focus": example["methodology_focus"],
            }
            all_examples.append(tagged_example)

        # Shuffle for better training distribution
        random.shuffle(all_examples)

        print("\n📊 Hybrid Dataset Statistics:")
        print(f"  Pure methodology examples: {len(pure_methodology)}")
        print(f"  Mathematics + methodology examples: {len(enhanced_math)}")
        print(f"  Total examples: {len(all_examples)}")
        print("  Ratio: 50% pure methodology, 50% subject-specific + methodology")

        return all_examples

    def save_hybrid_dataset(
        self, examples, filename="hybrid_methodology_math_dataset.jsonl"
    ):
        """Save hybrid dataset in JSONL format"""

        os.makedirs("data/hybrid", exist_ok=True)
        filepath = f"data/hybrid/{filename}"

        with open(filepath, "w") as f:
            for example in examples:
                json.dump(example, f)
                f.write("\n")

        print(f"\n💾 Hybrid dataset saved to: {filepath}")

        # Create detailed metadata
        methodology_counts = {}
        subject_counts = {}

        for example in examples:
            # Count by example type
            example_type = example.get("example_type", "unknown")
            subject_counts[example_type] = subject_counts.get(example_type, 0) + 1

            # Count methodology types for math examples
            if "methodology_focus" in example:
                methodology = example["methodology_focus"]
                methodology_counts[methodology] = (
                    methodology_counts.get(methodology, 0) + 1
                )

        metadata = {
            "dataset_name": "Hybrid Methodology + Mathematics Dataset",
            "total_examples": len(examples),
            "creation_date": datetime.now().isoformat(),
            "composition": {
                "pure_methodology": 500,
                "mathematics_with_methodology": 500,
            },
            "example_type_counts": subject_counts,
            "methodology_distribution": methodology_counts,
            "training_approach": "Combination of subject-agnostic teaching techniques with mathematics-specific content enhanced with methodology",
            "hypothesis": "Combining pure methodology with subject-specific methodology-enhanced content will produce optimal teaching AI",
            "format": "instruction-input-output with type and methodology tagging",
            "use_case": "Testing hybrid approach for calculative fine-tuning",
        }

        metadata_file = f"data/hybrid/{filename.replace('.jsonl', '_metadata.json')}"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"📋 Metadata saved to: {metadata_file}")

        return filepath

    def show_sample_examples(self, examples, count=4):
        """Show sample examples from the hybrid dataset"""

        print("\n📝 Sample Examples from Hybrid Dataset:")
        print("=" * 60)

        # Show examples of each type
        pure_methodology_samples = [
            ex for ex in examples if ex.get("example_type") == "pure_methodology"
        ]
        math_methodology_samples = [
            ex
            for ex in examples
            if ex.get("example_type") == "mathematics_with_methodology"
        ]

        print("\n🔬 PURE METHODOLOGY EXAMPLES:")
        print("-" * 40)
        for i, example in enumerate(
            random.sample(
                pure_methodology_samples, min(2, len(pure_methodology_samples))
            ),
            1,
        ):
            print(f"\nExample {i}:")
            print(f"Instruction: {example['instruction'][:150]}...")
            print(f"Output: {example['output'][:100]}...")

        print("\n🔢 MATHEMATICS + METHODOLOGY EXAMPLES:")
        print("-" * 40)
        for i, example in enumerate(
            random.sample(
                math_methodology_samples, min(2, len(math_methodology_samples))
            ),
            1,
        ):
            print(f"\nExample {i}:")
            print(f"Methodology: {example.get('methodology_focus', 'N/A')}")
            print(f"Instruction: {example['instruction'][:150]}...")
            print(f"Output: {example['output'][:100]}...")


def main():
    """Create hybrid methodology + mathematics dataset"""

    creator = HybridMethodologyMathDatasetCreator()

    print("🏗️  HYBRID METHODOLOGY + MATHEMATICS DATASET CREATION")
    print("=" * 80)
    print(
        "Purpose: Test combination of pure methodology + subject-specific methodology"
    )
    print("Composition: 500 pure methodology + 500 mathematics with methodology")
    print(
        "Hypothesis: Hybrid approach will outperform pure methodology or pure subject focus"
    )
    print("=" * 80)

    try:
        # Create hybrid dataset
        examples = creator.create_hybrid_dataset()

        # Save dataset
        filepath = creator.save_hybrid_dataset(examples)

        # Show sample examples
        creator.show_sample_examples(examples)

        print("\n🎯 Hybrid Dataset Ready for Training!")
        print(f"   Dataset: {filepath}")
        print(f"   Total Examples: {len(examples)}")
        print("   Composition: 50% pure methodology + 50% math + methodology")
        print("   Ready for calculative fine-tuning comparison!")

    except Exception as e:
        print(f"❌ Error creating hybrid dataset: {e}")


if __name__ == "__main__":
    main()
