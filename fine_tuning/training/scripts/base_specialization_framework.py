#!/usr/bin/env python3
"""
Base Model + Specialization Training Framework
Creates foundation model with tutoring methodology + personality, then specializes by subject
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class BaseSpecializationFramework:
    """Framework for base model + subject specialization training"""

    def __init__(self, workspace_root="/home/cgbowen/AIWorkspace"):
        self.workspace_root = Path(workspace_root)
        self.fine_tuning_dir = self.workspace_root / "fine_tuning"

        # Training strategy
        self.training_strategy = {
            "base_model": {
                "description": "Foundation model with tutoring methodology + personality",
                "components": [
                    "500 pure methodology examples (universal tutoring techniques)",
                    "1,842 personality examples (4 roles: family_tutor, educational_expert, philosophical_guide, general_assistant)",
                    "Total: ~2,342 examples for solid foundation",
                ],
                "focus": "Universal tutoring skills + empathetic personality integration",
            },
            "specialization_epochs": {
                "mathematics_expert": {
                    "base_examples": "500 math + methodology examples from hybrid dataset",
                    "additional_data": "Advanced mathematics problems with step-by-step solutions",
                    "methodology_focus": [
                        "step-by-step",
                        "error_analysis",
                        "conceptual_explanation",
                    ],
                },
                "science_expert": {
                    "base_examples": "Science-specific tutoring examples",
                    "additional_data": "Scientific concepts with inquiry-based learning",
                    "methodology_focus": [
                        "experimental_thinking",
                        "hypothesis_formation",
                        "observation_skills",
                    ],
                },
                "language_arts_expert": {
                    "base_examples": "Reading comprehension and writing tutoring",
                    "additional_data": "Literary analysis and composition guidance",
                    "methodology_focus": [
                        "socratic_questioning",
                        "critical_thinking",
                        "creative_expression",
                    ],
                },
                "family_tutor_specialist": {
                    "base_examples": "Enhanced family tutoring with age-appropriate communication",
                    "additional_data": "Parent-child learning dynamics and motivation techniques",
                    "methodology_focus": [
                        "patience",
                        "encouragement",
                        "age_adaptation",
                    ],
                },
            },
        }

    def create_base_training_dataset(self) -> Dict[str, Any]:
        """Combine pure methodology + personality data for base model"""

        print("🏗️  CREATING BASE MODEL TRAINING DATASET")
        print("=" * 60)

        # Load pure methodology examples
        methodology_file = (
            self.fine_tuning_dir / "datasets/processed/pure_methodology_tutoring.jsonl"
        )
        balanced_file = (
            self.fine_tuning_dir
            / "datasets/processed/next_epoch/final_balanced_dataset.jsonl"
        )

        methodology_examples = []
        personality_examples = []

        # Load methodology examples
        if methodology_file.exists():
            with open(methodology_file, "r") as f:
                for line in f:
                    methodology_examples.append(json.loads(line.strip()))
            print(f"✅ Loaded {len(methodology_examples)} methodology examples")

        # Load personality/role examples
        if balanced_file.exists():
            with open(balanced_file, "r") as f:
                for line in f:
                    personality_examples.append(json.loads(line.strip()))
            print(f"✅ Loaded {len(personality_examples)} personality examples")

        # Combine for base model
        base_dataset = []

        # Add all methodology examples (these are universal)
        for example in methodology_examples:
            base_example = {
                "instruction": example["instruction"],
                "input": example.get("input", ""),
                "output": example["output"],
                "training_phase": "base_methodology",
                "category": "universal_tutoring",
                "metadata": {
                    "source": "pure_methodology",
                    "subject_focus": example.get("subject_focus", "subject_agnostic"),
                    "example_type": "methodology_foundation",
                },
            }
            base_dataset.append(base_example)

        # Add personality examples (these provide role-based communication)
        for example in personality_examples:
            meta = example.get("meta", {})
            role = meta.get("role", "general_assistant")

            base_example = {
                "instruction": example["instruction"],
                "input": example.get("input", ""),
                "output": example["output"],
                "training_phase": "base_personality",
                "category": f"personality_{role}",
                "metadata": {
                    "source": "balanced_personality_dataset",
                    "role": role,
                    "example_type": "personality_foundation",
                    "separators": meta.get("separators_used", []),
                },
            }
            base_dataset.append(base_example)

        # Save base training dataset
        base_dataset_file = (
            self.fine_tuning_dir
            / "datasets/processed/base_model_training_dataset.jsonl"
        )

        with open(base_dataset_file, "w") as f:
            for example in base_dataset:
                f.write(json.dumps(example) + "\n")

        base_stats = {
            "total_examples": len(base_dataset),
            "methodology_examples": len(methodology_examples),
            "personality_examples": len(personality_examples),
            "creation_timestamp": datetime.now().isoformat(),
            "purpose": "Foundation model with universal tutoring + personality integration",
        }

        print("\n📊 BASE DATASET CREATED:")
        print(f"  Total Examples: {base_stats['total_examples']}")
        print(f"  Methodology: {base_stats['methodology_examples']}")
        print(f"  Personality: {base_stats['personality_examples']}")
        print(f"  Saved to: {base_dataset_file}")

        return base_stats

    def create_specialization_datasets(self) -> Dict[str, Any]:
        """Create specialized training datasets for each expert domain"""

        print("\n🎯 CREATING SPECIALIZATION DATASETS")
        print("=" * 60)

        specializations = {}

        # Mathematics Specialization
        math_spec = self._create_mathematics_specialization()
        specializations["mathematics"] = math_spec

        # Create placeholders for other specializations
        specializations["science"] = self._create_science_specialization_placeholder()
        specializations["language_arts"] = (
            self._create_language_arts_specialization_placeholder()
        )
        specializations["family_tutor"] = self._create_family_tutor_specialization()

        return specializations

    def _create_mathematics_specialization(self) -> Dict[str, Any]:
        """Create mathematics specialization dataset"""

        # Load math + methodology examples from hybrid dataset
        hybrid_file = (
            self.fine_tuning_dir
            / "datasets/processed/hybrid/hybrid_methodology_math_dataset.jsonl"
        )

        math_examples = []

        if hybrid_file.exists():
            with open(hybrid_file, "r") as f:
                for line in f:
                    example = json.loads(line.strip())
                    if example.get("example_type") == "mathematics_with_methodology":

                        # Format for specialization training
                        spec_example = {
                            "instruction": example["instruction"],
                            "input": example.get("input", ""),
                            "output": example["output"],
                            "training_phase": "mathematics_specialization",
                            "category": "mathematics_expert",
                            "metadata": {
                                "source": "hybrid_math_methodology",
                                "subject_focus": example.get(
                                    "subject_focus", "mathematics"
                                ),
                                "methodology_focus": example.get(
                                    "methodology_focus", "step_by_step"
                                ),
                                "example_type": "specialized_mathematics",
                            },
                        }
                        math_examples.append(spec_example)

        # Save mathematics specialization dataset
        math_spec_file = (
            self.fine_tuning_dir
            / "datasets/processed/specializations/mathematics_specialization.jsonl"
        )
        math_spec_file.parent.mkdir(parents=True, exist_ok=True)

        with open(math_spec_file, "w") as f:
            for example in math_examples:
                f.write(json.dumps(example) + "\n")

        math_stats = {
            "specialization": "mathematics",
            "examples_count": len(math_examples),
            "dataset_file": str(math_spec_file),
            "methodology_types": list(
                set(ex["metadata"]["methodology_focus"] for ex in math_examples)
            ),
            "training_focus": "Advanced mathematics tutoring with proven methodology integration",
        }

        print(f"📐 Mathematics Specialization: {len(math_examples)} examples")

        return math_stats

    def _create_science_specialization_placeholder(self) -> Dict[str, Any]:
        """Placeholder for science specialization"""
        return {
            "specialization": "science",
            "status": "placeholder",
            "planned_examples": 300,
            "methodology_focus": [
                "experimental_thinking",
                "hypothesis_formation",
                "observation_skills",
            ],
            "subjects": ["physics", "chemistry", "biology", "earth_science"],
        }

    def _create_language_arts_specialization_placeholder(self) -> Dict[str, Any]:
        """Placeholder for language arts specialization"""
        return {
            "specialization": "language_arts",
            "status": "placeholder",
            "planned_examples": 300,
            "methodology_focus": [
                "socratic_questioning",
                "critical_thinking",
                "creative_expression",
            ],
            "subjects": ["reading_comprehension", "writing", "literature", "grammar"],
        }

    def _create_family_tutor_specialization(self) -> Dict[str, Any]:
        """Create enhanced family tutor specialization"""

        # Extract family_tutor examples from balanced dataset
        balanced_file = (
            self.fine_tuning_dir
            / "datasets/processed/next_epoch/final_balanced_dataset.jsonl"
        )

        family_examples = []

        if balanced_file.exists():
            with open(balanced_file, "r") as f:
                for line in f:
                    example = json.loads(line.strip())
                    meta = example.get("meta", {})

                    if meta.get("role") == "family_tutor":
                        spec_example = {
                            "instruction": example["instruction"],
                            "input": example.get("input", ""),
                            "output": example["output"],
                            "training_phase": "family_tutor_specialization",
                            "category": "family_tutor_expert",
                            "metadata": {
                                "source": "balanced_family_tutor",
                                "role": "family_tutor",
                                "specialization_focus": "enhanced_family_dynamics",
                                "example_type": "specialized_family_tutoring",
                            },
                        }
                        family_examples.append(spec_example)

        # Save family tutor specialization
        family_spec_file = (
            self.fine_tuning_dir
            / "datasets/processed/specializations/family_tutor_specialization.jsonl"
        )
        family_spec_file.parent.mkdir(parents=True, exist_ok=True)

        with open(family_spec_file, "w") as f:
            for example in family_examples:
                f.write(json.dumps(example) + "\n")

        family_stats = {
            "specialization": "family_tutor",
            "examples_count": len(family_examples),
            "dataset_file": str(family_spec_file),
            "training_focus": "Enhanced family dynamics and age-appropriate communication",
        }

        print(f"👨‍👩‍👧‍👦 Family Tutor Specialization: {len(family_examples)} examples")

        return family_stats

    def generate_training_plan(
        self, base_stats: Dict[str, Any], specializations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete training plan for base + specialization approach"""

        training_plan = {
            "strategy": "base_model_plus_specializations",
            "description": "Train foundation model with methodology + personality, then specialize by domain",
            "phase_1_base_training": {
                "dataset": "base_model_training_dataset.jsonl",
                "examples": base_stats["total_examples"],
                "epochs": 8,  # Your proven calculative approach
                "focus": "Universal tutoring methodology + personality integration",
                "expected_outcome": "Competent general tutor with empathetic personality",
            },
            "phase_2_specializations": {
                "mathematics_expert": {
                    "dataset": "mathematics_specialization.jsonl",
                    "examples": specializations["mathematics"]["examples_count"],
                    "epochs": 4,  # Fewer epochs since base is already trained
                    "focus": "Advanced math tutoring with step-by-step methodology",
                },
                "family_tutor_expert": {
                    "dataset": "family_tutor_specialization.jsonl",
                    "examples": specializations["family_tutor"]["examples_count"],
                    "epochs": 4,
                    "focus": "Enhanced family dynamics and age adaptation",
                },
                "science_expert": {
                    "status": "planned",
                    "examples": 300,
                    "epochs": 4,
                    "focus": "Scientific inquiry and experimental thinking",
                },
                "language_arts_expert": {
                    "status": "planned",
                    "examples": 300,
                    "epochs": 4,
                    "focus": "Critical thinking and creative expression",
                },
            },
            "advantages": [
                "Efficient training - base model provides foundation",
                "Specialized expertise without losing general capabilities",
                "Easier to maintain and update individual specializations",
                "Can create new specializations without retraining everything",
                "Proven methodology foundation across all specializations",
            ],
            "timeline": {
                "base_model_training": "1-2 weeks",
                "mathematics_specialization": "3-5 days",
                "family_tutor_specialization": "3-5 days",
                "total_active_specializations": "2-3 weeks",
                "future_specializations": "3-5 days each",
            },
        }

        return training_plan


def main():
    """Create base model + specialization training framework"""

    framework = BaseSpecializationFramework()

    print("🚀 BASE MODEL + SPECIALIZATION FRAMEWORK")
    print("=" * 70)
    print("Strategy: Universal foundation → Specialized expertise")
    print("Advantage: Efficient training with maintained general capabilities")
    print("=" * 70)

    # Create base training dataset
    base_stats = framework.create_base_training_dataset()

    # Create specialization datasets
    specializations = framework.create_specialization_datasets()

    # Generate training plan
    training_plan = framework.generate_training_plan(base_stats, specializations)

    # Save training plan
    plan_file = (
        framework.fine_tuning_dir
        / "training/configs/base_specialization_training_plan.json"
    )
    plan_file.parent.mkdir(parents=True, exist_ok=True)

    with open(plan_file, "w") as f:
        json.dump(training_plan, f, indent=2)

    print("\n🎯 TRAINING PLAN SUMMARY:")
    print("=" * 50)
    print(f"Base Model: {base_stats['total_examples']} examples (8 epochs)")
    print(
        f"Mathematics: {specializations['mathematics']['examples_count']} examples (4 epochs)"
    )
    print(
        f"Family Tutor: {specializations['family_tutor']['examples_count']} examples (4 epochs)"
    )
    print("Science: Planned - 300 examples (4 epochs)")
    print("Language Arts: Planned - 300 examples (4 epochs)")

    print("\n🎉 FRAMEWORK COMPLETE!")
    print("=" * 40)
    print("✅ Base training dataset created")
    print("✅ Active specializations ready")
    print("✅ Training plan generated")
    print("✅ Efficient specialization path established")
    print("\n🚀 Ready to train your foundation model + specialized experts!")


if __name__ == "__main__":
    main()
