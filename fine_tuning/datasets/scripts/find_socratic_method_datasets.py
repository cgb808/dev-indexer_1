#!/usr/bin/env python3
"""
Socratic Method Dataset Finder and Extractor
Searches for and extracts Socratic teaching method examples
"""

import json
import re
from datetime import datetime
from pathlib import Path


class SocraticMethodExtractor:
    """Find and extract Socratic method training examples"""

    def __init__(self, workspace_root="/home/cgbowen/AIWorkspace"):
        self.workspace_root = Path(workspace_root)
        self.fine_tuning_dir = self.workspace_root / "fine_tuning"

        # Socratic method indicators
        self.socratic_indicators = [
            "socratic",
            "questioning",
            "what do you think",
            "how does this connect",
            "what would happen if",
            "can you explain why",
            "what evidence supports",
            "how did you arrive at",
            "what assumptions",
            "what questions does this raise",
        ]

        # Question patterns that indicate Socratic method
        self.question_patterns = [
            r"what makes you think",
            r"can you walk me through",
            r"how does this connect",
            r"what would happen if",
            r"what evidence",
            r"how did you",
            r"why do you think",
            r"what assumptions",
            r"can you give an example",
            r"what questions",
        ]

    def search_existing_datasets(self):
        """Search through existing datasets for Socratic method examples"""

        print("🔍 SEARCHING FOR SOCRATIC METHOD EXAMPLES")
        print("=" * 60)

        socratic_examples = []

        # Search locations
        search_paths = [
            self.fine_tuning_dir / "datasets/processed/pure_methodology_tutoring.jsonl",
            self.fine_tuning_dir
            / "datasets/processed/next_epoch/final_balanced_dataset.jsonl",
            self.fine_tuning_dir
            / "datasets/processed/hybrid/hybrid_methodology_math_dataset.jsonl",
            self.workspace_root / "data/tutoring_datasets",
            self.workspace_root / "data/tutoring_instructional",
        ]

        for search_path in search_paths:
            if search_path.exists():
                if search_path.is_file() and search_path.suffix == ".jsonl":
                    examples = self._extract_socratic_from_file(search_path)
                    socratic_examples.extend(examples)
                    print(
                        f"📂 {search_path.name}: {len(examples)} Socratic examples found"
                    )
                elif search_path.is_dir():
                    for jsonl_file in search_path.glob("*.jsonl"):
                        examples = self._extract_socratic_from_file(jsonl_file)
                        socratic_examples.extend(examples)
                        print(
                            f"📂 {jsonl_file.name}: {len(examples)} Socratic examples found"
                        )

        return socratic_examples

    def _extract_socratic_from_file(self, file_path: Path):
        """Extract Socratic method examples from a specific file"""

        socratic_examples = []

        try:
            with open(file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        example = json.loads(line.strip())

                        if self._is_socratic_example(example):
                            # Add source information
                            example["socratic_metadata"] = {
                                "source_file": str(file_path),
                                "line_number": line_num,
                                "extraction_timestamp": datetime.now().isoformat(),
                                "socratic_confidence": self._calculate_socratic_confidence(
                                    example
                                ),
                            }
                            socratic_examples.append(example)

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")

        return socratic_examples

    def _is_socratic_example(self, example):
        """Determine if an example uses Socratic method"""

        instruction = example.get("instruction", "").lower()
        output = example.get("output", "").lower()
        combined_text = instruction + " " + output

        # Check for explicit Socratic indicators
        for indicator in self.socratic_indicators:
            if indicator in combined_text:
                return True

        # Check for question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, combined_text):
                return True

        # Check for high question density (Socratic method uses lots of questions)
        question_count = combined_text.count("?")
        word_count = len(combined_text.split())

        if word_count > 0:
            question_density = question_count / word_count
            if question_density > 0.05:  # More than 5% questions
                return True

        return False

    def _calculate_socratic_confidence(self, example):
        """Calculate confidence score for Socratic classification"""

        instruction = example.get("instruction", "").lower()
        output = example.get("output", "").lower()
        combined_text = instruction + " " + output

        confidence = 0.0

        # Check for explicit Socratic references
        if "socratic" in combined_text:
            confidence += 0.4

        # Check for questioning indicators
        indicator_matches = sum(
            1 for indicator in self.socratic_indicators if indicator in combined_text
        )
        confidence += min(indicator_matches * 0.1, 0.3)

        # Check for question patterns
        pattern_matches = sum(
            1 for pattern in self.question_patterns if re.search(pattern, combined_text)
        )
        confidence += min(pattern_matches * 0.1, 0.3)

        return min(confidence, 1.0)

    def create_socratic_dataset(self, examples):
        """Create a dedicated Socratic method dataset"""

        if not examples:
            print("❌ No Socratic examples found to create dataset")
            return

        # Sort by confidence score
        examples.sort(
            key=lambda x: x["socratic_metadata"]["socratic_confidence"], reverse=True
        )

        # Create output directory
        socratic_dir = self.fine_tuning_dir / "datasets/processed/socratic_method"
        socratic_dir.mkdir(parents=True, exist_ok=True)

        # Save high-confidence Socratic examples
        high_confidence_examples = [
            ex
            for ex in examples
            if ex["socratic_metadata"]["socratic_confidence"] >= 0.5
        ]
        medium_confidence_examples = [
            ex
            for ex in examples
            if 0.3 <= ex["socratic_metadata"]["socratic_confidence"] < 0.5
        ]

        # High confidence dataset
        if high_confidence_examples:
            high_conf_file = socratic_dir / "socratic_method_high_confidence.jsonl"
            with open(high_conf_file, "w") as f:
                for example in high_confidence_examples:
                    f.write(json.dumps(example) + "\n")
            print(
                f"✅ High confidence Socratic dataset: {len(high_confidence_examples)} examples"
            )

        # Medium confidence dataset
        if medium_confidence_examples:
            med_conf_file = socratic_dir / "socratic_method_medium_confidence.jsonl"
            with open(med_conf_file, "w") as f:
                for example in medium_confidence_examples:
                    f.write(json.dumps(example) + "\n")
            print(
                f"✅ Medium confidence Socratic dataset: {len(medium_confidence_examples)} examples"
            )

        # Combined dataset
        combined_file = socratic_dir / "socratic_method_combined.jsonl"
        with open(combined_file, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")

        # Create analysis report
        self._create_socratic_analysis_report(examples, socratic_dir)

        return {
            "total_examples": len(examples),
            "high_confidence": len(high_confidence_examples),
            "medium_confidence": len(medium_confidence_examples),
            "dataset_dir": socratic_dir,
        }

    def _create_socratic_analysis_report(self, examples, output_dir):
        """Create detailed analysis report of Socratic examples"""

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_socratic_examples": len(examples),
            "confidence_distribution": {
                "high_confidence": len(
                    [
                        ex
                        for ex in examples
                        if ex["socratic_metadata"]["socratic_confidence"] >= 0.5
                    ]
                ),
                "medium_confidence": len(
                    [
                        ex
                        for ex in examples
                        if 0.3 <= ex["socratic_metadata"]["socratic_confidence"] < 0.5
                    ]
                ),
                "low_confidence": len(
                    [
                        ex
                        for ex in examples
                        if ex["socratic_metadata"]["socratic_confidence"] < 0.3
                    ]
                ),
            },
            "source_files": {},
            "sample_examples": examples[:10] if examples else [],
            "socratic_characteristics": {
                "average_questions_per_example": 0,
                "most_common_question_types": [],
                "typical_socratic_patterns": [],
            },
        }

        # Analyze source distribution
        for example in examples:
            source = example["socratic_metadata"]["source_file"]
            if source not in report["source_files"]:
                report["source_files"][source] = 0
            report["source_files"][source] += 1

        # Save report
        report_file = output_dir / "socratic_analysis_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Analysis report saved: {report_file}")

    def find_external_socratic_datasets(self):
        """Search for external Socratic method datasets"""

        print("\n🌐 EXTERNAL SOCRATIC METHOD DATASETS")
        print("=" * 50)

        external_sources = {
            "educational_datasets": [
                "Philosophy Socratic Dialogues Dataset",
                "Critical Thinking Question Banks",
                "Inquiry-Based Learning Examples",
                "Educational Questioning Frameworks",
            ],
            "huggingface_datasets": [
                "socratic-method-dialogues",
                "philosophy-questions",
                "educational-questioning",
                "critical-thinking-prompts",
            ],
            "academic_sources": [
                "Stanford Encyclopedia of Philosophy - Socratic Method",
                "Educational Research Socratic Questioning Banks",
                "Philosophy Teaching Resources",
                "Critical Pedagogy Question Collections",
            ],
            "github_repositories": [
                "socratic-method-training-data",
                "educational-questioning-datasets",
                "philosophy-dialogue-examples",
                "critical-thinking-prompts",
            ],
        }

        for category, sources in external_sources.items():
            print(f"\n📚 {category.replace('_', ' ').title()}:")
            for source in sources:
                print(f"  • {source}")

        return external_sources


def main():
    """Search for and extract Socratic method training datasets"""

    extractor = SocraticMethodExtractor()

    print("📚 SOCRATIC METHOD DATASET SEARCH")
    print("=" * 70)
    print("Purpose: Find and extract Socratic teaching method examples")
    print("Focus: Question-based learning and guided discovery")
    print("=" * 70)

    # Search existing datasets
    socratic_examples = extractor.search_existing_datasets()

    print("\n📊 SEARCH RESULTS:")
    print(f"Total Socratic examples found: {len(socratic_examples)}")

    if socratic_examples:
        # Create Socratic dataset
        dataset_stats = extractor.create_socratic_dataset(socratic_examples)

        print("\n✅ SOCRATIC DATASET CREATED:")
        print(f"  High confidence: {dataset_stats['high_confidence']} examples")
        print(f"  Medium confidence: {dataset_stats['medium_confidence']} examples")
        print(f"  Total: {dataset_stats['total_examples']} examples")

        # Show sample examples
        print("\n📋 SAMPLE SOCRATIC EXAMPLES:")
        print("=" * 50)

        high_conf_examples = [
            ex
            for ex in socratic_examples
            if ex["socratic_metadata"]["socratic_confidence"] >= 0.5
        ]

        for i, example in enumerate(high_conf_examples[:3]):
            print(
                f"\nExample {i+1} (Confidence: {example['socratic_metadata']['socratic_confidence']:.2f}):"
            )
            instruction = (
                example.get("instruction", "")[:150] + "..."
                if len(example.get("instruction", "")) > 150
                else example.get("instruction", "")
            )
            output = (
                example.get("output", "")[:200] + "..."
                if len(example.get("output", "")) > 200
                else example.get("output", "")
            )

            print(f"  Instruction: {instruction}")
            print(f"  Output: {output}")

    # Find external sources
    external_sources = extractor.find_external_socratic_datasets()

    print("\n🎯 NEXT STEPS:")
    print("=" * 40)
    print("✅ Existing Socratic examples extracted and categorized")
    print("📚 External dataset sources identified")
    print("🔍 Ready to expand Socratic method training data")
    print("🚀 Can create specialized Socratic tutoring model")


if __name__ == "__main__":
    main()
