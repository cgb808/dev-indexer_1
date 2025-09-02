#!/usr/bin/env python3
"""
Mistral7b Dataset Validator - Evaluate your 1,842-example balanced dataset
Uses your LLM-as-Judge approach to assess personality integration quality
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from pathlib import Path

from tooling.coordination.mistral7b_integration_framework import \
    Mistral7bJudgeFramework


def evaluate_balanced_dataset():
    """Evaluate the 1,842-example balanced dataset with personality integration"""

    workspace = Path("/home/cgbowen/AIWorkspace")
    dataset_path = (
        workspace
        / "fine_tuning/datasets/processed/next_epoch/final_balanced_dataset.jsonl"
    )

    print("🎯 EVALUATING BALANCED DATASET WITH MISTRAL7B")
    print("=" * 70)
    print(f"Dataset: {dataset_path}")
    print("Focus: Personality integration quality assessment")
    print("=" * 70)

    # Initialize framework
    framework = Mistral7bJudgeFramework()

    # Run evaluation on sample (adjust sample_size as needed)
    print("⚖️  Starting Mistral7b evaluation...")
    summary = framework.batch_evaluate_dataset(str(dataset_path), sample_size=100)

    print("\n📊 EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Overall Average Score: {summary['overall_average']:.2f}/5.0")
    print(f"Quality Assessment: {summary['quality_assessment']}")
    print(f"Total Evaluated: {summary['total_evaluated']} examples")

    print("\n📋 ROLE BREAKDOWN:")
    for category, stats in summary["category_breakdown"].items():
        if stats["count"] > 0:
            avg = stats.get("average_score", 0)
            print(f"  {category}: {avg:.2f}/5.0 ({stats['count']} examples)")

    # Identify strengths and areas for improvement
    print("\n🎯 INSIGHTS FOR FINE-TUNING:")

    # Find best performing categories
    best_categories = sorted(
        [
            (cat, stats["average_score"])
            for cat, stats in summary["category_breakdown"].items()
            if stats.get("average_score", 0) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    if best_categories:
        print("✅ Strongest Areas:")
        for cat, score in best_categories[:3]:
            print(f"   • {cat}: {score:.2f}/5.0")

    # Find areas needing improvement
    if len(best_categories) > 3:
        print("\n🔧 Areas for Enhancement:")
        for cat, score in best_categories[-3:]:
            print(f"   • {cat}: {score:.2f}/5.0")

    print("\n✅ Evaluation complete! Check validation/results/ for detailed report.")
    return summary


def test_individual_examples():
    """Test Mistral7b evaluation on specific examples"""

    framework = Mistral7bJudgeFramework()

    print("\n🧪 TESTING INDIVIDUAL EXAMPLES")
    print("=" * 50)

    # Test family_tutor example
    family_prompt = """You are a warm, patient family tutor who helps children and parents learn together. Use age-appropriate language, encourage curiosity, and always maintain a supportive tone.

[LEARNING_OBJECTIVE]
As a family tutor, help explain fractions using a pizza analogy for a 4th grader.

[RESPONSE]"""

    family_response = """Great question! Let's use pizza to understand fractions - it's delicious and fun! 🍕

Imagine you have a whole pizza. If you cut it into 2 big slices, each slice is 1/2 of the pizza. But what if you cut it into 4 smaller slices instead? Now each slice is 1/4, but if you take 2 slices (2/4), you have the same amount as one big slice (1/2)! 

So 1/2 = 2/4 - they're equivalent fractions, just cut differently. It's like having the same amount of pizza, but in different sized pieces. The key is: as long as you multiply or divide both the top AND bottom numbers by the same amount, the fraction stays equal!

Want to try cutting our imaginary pizza into 8 slices and see what happens?"""

    evaluation = framework.llm_as_judge(family_prompt, family_response, "family_tutor")

    print("Family Tutor Example:")
    print(f"  Score: {evaluation['score']}/5")
    print(f"  Rationale: {evaluation['rationale']}")
    if "strengths" in evaluation:
        print(f"  Strengths: {evaluation['strengths']}")
    if "improvements" in evaluation:
        print(f"  Improvements: {evaluation['improvements']}")

    return evaluation


def main():
    """Run comprehensive evaluation of the balanced dataset"""

    print("🚀 MISTRAL7B DATASET VALIDATION")
    print("=" * 70)
    print("Purpose: Evaluate personality integration in 1,842-example dataset")
    print("Method: LLM-as-Judge using Mistral7b for quality assessment")
    print("=" * 70)

    # Test individual examples first
    test_evaluation = test_individual_examples()

    # Run full dataset evaluation
    print("\n" + "=" * 70)
    dataset_summary = evaluate_balanced_dataset()

    print("\n🎉 VALIDATION COMPLETE!")
    print("=" * 40)
    print("✅ Individual example testing completed")
    print("✅ Dataset batch evaluation completed")
    print("✅ Quality metrics generated")
    print("✅ Role-based performance analysis ready")
    print("\n🎯 Your balanced dataset is ready for personality-integrated fine-tuning!")


if __name__ == "__main__":
    main()
