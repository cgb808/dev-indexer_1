#!/usr/bin/env python3
"""
Hybrid Methodology Epoch Visualization
Shows what an actual epoch looks like with the proven hybrid model:
500 pure methodology + 500 math+methodology examples
"""

import json
import os
import random

import torch


class HybridEpochVisualizer:
    """Visualize actual epoch structure for hybrid methodology training"""

    def __init__(self):
        self.hybrid_dataset_path = "data/hybrid/hybrid_methodology_math_dataset.jsonl"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_hybrid_dataset(self):
        """Load and analyze the hybrid dataset"""

        if not os.path.exists(self.hybrid_dataset_path):
            raise FileNotFoundError(
                f"Hybrid dataset not found: {self.hybrid_dataset_path}"
            )

        examples = []
        with open(self.hybrid_dataset_path, "r") as f:
            for line in f:
                examples.append(json.loads(line.strip()))

        # Analyze composition
        pure_methodology = [
            ex for ex in examples if ex.get("example_type") == "pure_methodology"
        ]
        math_methodology = [
            ex
            for ex in examples
            if ex.get("example_type") == "mathematics_with_methodology"
        ]

        print("📊 Hybrid Dataset Analysis:")
        print(f"  Total examples: {len(examples)}")
        print(
            f"  Pure methodology: {len(pure_methodology)} ({len(pure_methodology)/len(examples)*100:.1f}%)"
        )
        print(
            f"  Math + methodology: {len(math_methodology)} ({len(math_methodology)/len(examples)*100:.1f}%)"
        )

        return examples, pure_methodology, math_methodology

    def show_epoch_structure(self, examples, batch_size=8, learning_rate=5e-5):
        """Show what a complete epoch looks like"""

        print("\n🎯 HYBRID METHODOLOGY EPOCH STRUCTURE")
        print("=" * 70)
        print(f"Dataset: {len(examples)} examples (500 pure + 500 math+methodology)")
        print(f"Batch size: {batch_size}")
        print(f"Learning rate: {learning_rate}")
        print(f"Device: {self.device}")
        print(f"Total batches per epoch: {len(examples) // batch_size}")
        print("=" * 70)

        # Shuffle examples for training (important for hybrid training)
        shuffled_examples = examples.copy()
        random.shuffle(shuffled_examples)

        total_batches = len(examples) // batch_size

        # Show epoch progression
        print("\n📚 EPOCH PROGRESSION:")

        for batch_idx in range(
            min(10, total_batches)
        ):  # Show first 10 batches as example
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, len(examples))
            batch_examples = shuffled_examples[batch_start:batch_end]

            # Analyze batch composition
            pure_count = len(
                [
                    ex
                    for ex in batch_examples
                    if ex.get("example_type") == "pure_methodology"
                ]
            )
            math_count = len(
                [
                    ex
                    for ex in batch_examples
                    if ex.get("example_type") == "mathematics_with_methodology"
                ]
            )

            print(f"\n  Batch {batch_idx + 1}/{total_batches}:")
            print(f"    Examples: {len(batch_examples)}")
            print(f"    Pure methodology: {pure_count}")
            print(f"    Math + methodology: {math_count}")
            print(f"    Ratio: {pure_count}:{math_count}")

            # Show sample examples from this batch
            if batch_idx < 3:  # Show details for first 3 batches
                print("    Sample examples:")
                for i, example in enumerate(batch_examples[:2]):
                    example_type = example.get("example_type", "unknown")
                    instruction = example.get("instruction", "")[:80] + "..."
                    print(f"      {i+1}. [{example_type}] {instruction}")

        if total_batches > 10:
            print(f"    ... (showing first 10 of {total_batches} total batches)")

        return shuffled_examples

    def show_calculative_phases_with_epochs(self, examples):
        """Show how calculative phases integrate with epoch structure"""

        print("\n🔄 CALCULATIVE PHASES WITH EPOCH STRUCTURE")
        print("=" * 70)

        # Calculative phases for hybrid training
        phases = [
            {
                "name": "Foundation Integration",
                "epochs": 2,
                "focus": "Balance pure methodology with subject-specific application",
                "examples_per_epoch": len(examples),
                "learning_rate": 5e-5,
                "description": "Establish foundation integrating teaching techniques with mathematical content",
            },
            {
                "name": "Advanced Synthesis",
                "epochs": 2,
                "focus": "Sophisticated integration of methodology with content",
                "examples_per_epoch": len(examples),
                "learning_rate": 3e-5,
                "description": "Advanced synthesis of pedagogical approaches with mathematical reasoning",
            },
            {
                "name": "Unified Mastery",
                "epochs": 1,
                "focus": "Perfect integration of all approaches",
                "examples_per_epoch": len(examples),
                "learning_rate": 1e-5,
                "description": "Master seamless integration of methodology and content",
            },
        ]

        total_epochs = sum(phase["epochs"] for phase in phases)
        epoch_counter = 0

        for phase_idx, phase in enumerate(phases, 1):
            print(f"\n📍 PHASE {phase_idx}: {phase['name']}")
            print(f"   Focus: {phase['focus']}")
            print(f"   Epochs: {phase['epochs']}")
            print(f"   Learning Rate: {phase['learning_rate']}")
            print(f"   Examples per epoch: {phase['examples_per_epoch']}")
            print("-" * 50)

            for epoch_in_phase in range(phase["epochs"]):
                epoch_counter += 1
                print(
                    f"\n     EPOCH {epoch_counter}/{total_epochs} (Phase {phase_idx}, Epoch {epoch_in_phase + 1})"
                )
                print(f"     Learning Rate: {phase['learning_rate']}")
                print("     Methodology Examples: ~500 (randomly distributed)")
                print("     Math+Methodology Examples: ~500 (randomly distributed)")
                print(f"     Total Training Steps: {len(examples) // 8} (batch_size=8)")

                # Show sample training progression for first epoch
                if epoch_counter == 1:
                    self.show_sample_training_steps(
                        examples[:24], phase["learning_rate"]
                    )

        print(
            f"\n✅ Total Training: {total_epochs} epochs across {len(phases)} calculative phases"
        )
        print(f"   Total examples processed: {len(examples) * total_epochs:,}")
        print(f"   Estimated training time: {total_epochs * 2:.1f} hours (RTX 3060 Ti)")

    def show_sample_training_steps(self, sample_examples, learning_rate):
        """Show what individual training steps look like"""

        print(f"\n       📋 Sample Training Steps (Learning Rate: {learning_rate}):")

        for step, example in enumerate(sample_examples[:8], 1):
            example_type = example.get("example_type", "unknown")
            methodology_focus = example.get("methodology_focus", "N/A")

            # Format for display
            if example_type == "pure_methodology":
                step_type = "🔬 Pure Methodology"
                details = "Subject-agnostic teaching technique"
            else:
                step_type = "🔢 Math+Methodology"
                details = f"Method: {methodology_focus}"

            instruction_preview = example.get("instruction", "")[:60] + "..."

            print(f"         Step {step:2d}: {step_type}")
            print(f"                {details}")
            print(f"                Input: {instruction_preview}")

            if step == 4:
                print("         ... (continuing with remaining batch steps)")
                break

    def show_memory_and_performance_estimates(self, examples):
        """Show memory usage and performance estimates"""

        print("\n💾 MEMORY & PERFORMANCE ESTIMATES")
        print("=" * 50)

        # Model parameters (Phi-3 Mini)
        model_params = 3.8e9  # 3.8B parameters
        param_size = 2  # bytes per parameter (FP16)

        # Training memory calculations
        base_model_memory = model_params * param_size / (1024**3)  # GB
        optimizer_memory = base_model_memory * 2  # Adam optimizer
        gradients_memory = base_model_memory
        activations_memory = 0.5  # estimated for batch_size=8

        total_memory = (
            base_model_memory + optimizer_memory + gradients_memory + activations_memory
        )

        print("🖥️  Hardware Requirements:")
        print(f"   Base model (FP16): {base_model_memory:.1f} GB")
        print(f"   Optimizer states: {optimizer_memory:.1f} GB")
        print(f"   Gradients: {gradients_memory:.1f} GB")
        print(f"   Activations: {activations_memory:.1f} GB")
        print(f"   Total VRAM needed: {total_memory:.1f} GB")
        print("   Available VRAM: 8.0 GB (RTX 3060 Ti)")
        print(
            f"   Status: {'✅ Sufficient' if total_memory <= 8.0 else '❌ Insufficient - Need gradient checkpointing'}"
        )

        # Performance estimates
        batch_size = 8
        steps_per_epoch = len(examples) // batch_size
        total_epochs = 5  # from calculative phases
        total_steps = steps_per_epoch * total_epochs

        # RTX 3060 Ti estimates
        time_per_step = 1.2  # seconds (estimated for Phi-3 Mini)
        total_training_time = total_steps * time_per_step / 3600  # hours

        print("\n⏱️  Performance Estimates:")
        print(f"   Steps per epoch: {steps_per_epoch}")
        print(f"   Total epochs: {total_epochs}")
        print(f"   Total training steps: {total_steps:,}")
        print(f"   Time per step: {time_per_step:.1f}s")
        print(f"   Total training time: {total_training_time:.1f} hours")
        print(f"   Examples processed: {len(examples) * total_epochs:,}")

        # Dataset efficiency
        print("\n📊 Dataset Efficiency:")
        print("   Hybrid composition: 50% pure methodology + 50% math+methodology")
        print("   Methodology coverage: 8 core tutoring techniques")
        print("   Mathematical coverage: Enhanced with pedagogical approaches")
        print("   Training efficiency: Optimal balance for educational AI")


def main():
    """Visualize hybrid methodology epoch structure"""

    visualizer = HybridEpochVisualizer()

    print("🎯 HYBRID METHODOLOGY EPOCH VISUALIZATION")
    print("=" * 80)
    print("Purpose: Show actual epoch structure for proven hybrid approach")
    print("Dataset: 500 pure methodology + 500 math+methodology examples")
    print("Training: Calculative fine-tuning with 5 total epochs")
    print("=" * 80)

    try:
        # Load and analyze dataset
        examples, pure_examples, math_examples = visualizer.load_hybrid_dataset()

        # Show epoch structure
        shuffled_examples = visualizer.show_epoch_structure(examples)

        # Show calculative phases with epochs
        visualizer.show_calculative_phases_with_epochs(examples)

        # Show memory and performance estimates
        visualizer.show_memory_and_performance_estimates(examples)

        print("\n🎉 HYBRID METHODOLOGY EPOCH STRUCTURE COMPLETE!")
        print("   Ready for actual fine-tuning implementation")
        print("   Proven optimal approach: 500 pure + 500 math+methodology")
        print("   Expected outcome: Superior educational AI with integrated pedagogy")

    except Exception as e:
        print(f"❌ Error visualizing epoch structure: {e}")


if __name__ == "__main__":
    main()
