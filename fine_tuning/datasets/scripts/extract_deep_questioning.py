#!/usr/bin/env python3
"""
Deep Socratic Questioning Extractor
Focus on drill-down questioning sequences that probe true intent and understanding
"""

import json
import re
from datetime import datetime
from pathlib import Path


class DeepSocraticExtractor:
    """Extract deep questioning sequences that drill down to true intent"""

    def __init__(self, workspace_root="/home/cgbowen/AIWorkspace"):
        self.workspace_root = Path(workspace_root)
        self.fine_tuning_dir = self.workspace_root / "fine_tuning"

        # Deep questioning patterns - sequences that drill down
        self.drill_down_patterns = [
            r"what makes you think",
            r"can you walk me through your reasoning",
            r"what evidence supports",
            r"how did you arrive at",
            r"what assumptions",
            r"why do you believe",
            r"what led you to conclude",
            r"how do you know",
            r"what would convince you otherwise",
            r"can you explain your logic",
            r"what if we considered",
            r"how might someone disagree",
            r"what are you assuming",
            r"where does that idea come from",
            r"can you be more specific about",
        ]

        # Intent probing patterns
        self.intent_probing_patterns = [
            r"what are you really trying to",
            r"what's your actual goal",
            r"what do you hope to achieve",
            r"what problem are you solving",
            r"what's driving this question",
            r"what's behind your thinking",
            r"what's the deeper issue",
            r"what's really at stake",
            r"what matters most to you about",
            r"what outcome do you want",
        ]

        # Progressive questioning indicators
        self.progressive_indicators = [
            "first",
            "then",
            "next",
            "building on that",
            "going deeper",
            "let's dig into",
            "taking it further",
            "now consider",
            "following that logic",
            "expanding on",
        ]

    def extract_deep_questioning_sequences(self):
        """Extract examples with deep questioning drill-down sequences"""

        print("🔍 EXTRACTING DEEP SOCRATIC QUESTIONING SEQUENCES")
        print("=" * 70)
        print("Focus: Drill-down questioning that probes true intent and understanding")
        print("=" * 70)

        # Load existing Socratic examples
        socratic_file = (
            self.fine_tuning_dir
            / "datasets/processed/socratic_method/socratic_method_high_confidence.jsonl"
        )

        if not socratic_file.exists():
            print(
                "❌ Socratic dataset not found. Run find_socratic_method_datasets.py first."
            )
            return []

        deep_questioning_examples = []

        with open(socratic_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line.strip())

                    if self._has_deep_questioning(example):
                        # Analyze the questioning depth
                        questioning_analysis = self._analyze_questioning_depth(example)

                        # Add deep questioning metadata
                        example["deep_questioning_metadata"] = {
                            "drill_down_score": questioning_analysis[
                                "drill_down_score"
                            ],
                            "intent_probing_score": questioning_analysis[
                                "intent_probing_score"
                            ],
                            "question_sequence_length": questioning_analysis[
                                "question_sequence_length"
                            ],
                            "questioning_techniques": questioning_analysis[
                                "techniques"
                            ],
                            "depth_level": questioning_analysis["depth_level"],
                            "extraction_timestamp": datetime.now().isoformat(),
                        }

                        deep_questioning_examples.append(example)

                except json.JSONDecodeError:
                    continue

        # Sort by questioning depth (highest drill-down scores first)
        deep_questioning_examples.sort(
            key=lambda x: (
                x["deep_questioning_metadata"]["drill_down_score"]
                + x["deep_questioning_metadata"]["intent_probing_score"]
            ),
            reverse=True,
        )

        print(f"📊 Found {len(deep_questioning_examples)} deep questioning examples")

        return deep_questioning_examples

    def _has_deep_questioning(self, example):
        """Check if example contains deep questioning drill-down"""

        instruction = example.get("instruction", "").lower()
        output = example.get("output", "").lower()
        combined_text = instruction + " " + output

        # Check for drill-down patterns
        drill_down_matches = sum(
            1
            for pattern in self.drill_down_patterns
            if re.search(pattern, combined_text)
        )

        # Check for intent probing
        intent_matches = sum(
            1
            for pattern in self.intent_probing_patterns
            if re.search(pattern, combined_text)
        )

        # Check for progressive questioning
        progressive_matches = sum(
            1 for indicator in self.progressive_indicators if indicator in combined_text
        )

        # Must have at least 2 drill-down patterns or 1 intent probing pattern
        return (
            drill_down_matches >= 2 or intent_matches >= 1 or progressive_matches >= 1
        )

    def _analyze_questioning_depth(self, example):
        """Analyze the depth and quality of questioning in the example"""

        instruction = example.get("instruction", "").lower()
        output = example.get("output", "").lower()
        combined_text = instruction + " " + output

        # Count drill-down patterns
        drill_down_score = sum(
            1
            for pattern in self.drill_down_patterns
            if re.search(pattern, combined_text)
        )

        # Count intent probing patterns
        intent_probing_score = sum(
            1
            for pattern in self.intent_probing_patterns
            if re.search(pattern, combined_text)
        )

        # Count questions
        question_count = combined_text.count("?")

        # Identify techniques used
        techniques = []

        if re.search(r"what makes you think|why do you believe", combined_text):
            techniques.append("reasoning_probe")

        if re.search(r"what evidence|how do you know", combined_text):
            techniques.append("evidence_inquiry")

        if re.search(r"what assumptions|what are you assuming", combined_text):
            techniques.append("assumption_challenge")

        if re.search(r"what if|how might someone disagree", combined_text):
            techniques.append("perspective_shift")

        if re.search(r"can you walk me through|explain your logic", combined_text):
            techniques.append("process_exploration")

        if re.search(r"what's really|what's behind|what's driving", combined_text):
            techniques.append("intent_probing")

        # Determine depth level
        total_score = drill_down_score + intent_probing_score

        if total_score >= 4 and len(techniques) >= 3:
            depth_level = "expert_level"
        elif total_score >= 3 and len(techniques) >= 2:
            depth_level = "advanced"
        elif total_score >= 2:
            depth_level = "intermediate"
        else:
            depth_level = "basic"

        return {
            "drill_down_score": drill_down_score,
            "intent_probing_score": intent_probing_score,
            "question_sequence_length": question_count,
            "techniques": techniques,
            "depth_level": depth_level,
        }

    def create_questioning_mastery_dataset(self, examples):
        """Create specialized dataset for questioning mastery"""

        if not examples:
            print("❌ No deep questioning examples to process")
            return

        # Create output directory
        questioning_dir = self.fine_tuning_dir / "datasets/processed/deep_questioning"
        questioning_dir.mkdir(parents=True, exist_ok=True)

        # Categorize by depth level
        expert_examples = [
            ex
            for ex in examples
            if ex["deep_questioning_metadata"]["depth_level"] == "expert_level"
        ]
        advanced_examples = [
            ex
            for ex in examples
            if ex["deep_questioning_metadata"]["depth_level"] == "advanced"
        ]
        intermediate_examples = [
            ex
            for ex in examples
            if ex["deep_questioning_metadata"]["depth_level"] == "intermediate"
        ]

        print("\n📊 QUESTIONING DEPTH ANALYSIS:")
        print(f"Expert Level: {len(expert_examples)} examples")
        print(f"Advanced Level: {len(advanced_examples)} examples")
        print(f"Intermediate Level: {len(intermediate_examples)} examples")

        # Save expert-level questioning examples
        if expert_examples:
            expert_file = questioning_dir / "expert_level_questioning.jsonl"
            with open(expert_file, "w") as f:
                for example in expert_examples:
                    f.write(json.dumps(example) + "\n")
            print(f"✅ Expert questioning dataset: {len(expert_examples)} examples")

        # Save all deep questioning examples
        all_deep_file = questioning_dir / "deep_questioning_mastery.jsonl"
        with open(all_deep_file, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")

        # Create technique-specific datasets
        self._create_technique_datasets(examples, questioning_dir)

        # Generate analysis report
        self._create_questioning_analysis_report(examples, questioning_dir)

        return {
            "total_deep_examples": len(examples),
            "expert_level": len(expert_examples),
            "advanced_level": len(advanced_examples),
            "intermediate_level": len(intermediate_examples),
            "output_directory": questioning_dir,
        }

    def _create_technique_datasets(self, examples, output_dir):
        """Create datasets organized by questioning technique"""

        techniques_dir = output_dir / "techniques"
        techniques_dir.mkdir(parents=True, exist_ok=True)

        # Group by technique
        technique_groups = {
            "reasoning_probe": [],
            "evidence_inquiry": [],
            "assumption_challenge": [],
            "perspective_shift": [],
            "process_exploration": [],
            "intent_probing": [],
        }

        for example in examples:
            techniques = example["deep_questioning_metadata"]["techniques"]
            for technique in techniques:
                if technique in technique_groups:
                    technique_groups[technique].append(example)

        # Save technique-specific datasets
        for technique, technique_examples in technique_groups.items():
            if technique_examples:
                technique_file = techniques_dir / f"{technique}_examples.jsonl"
                with open(technique_file, "w") as f:
                    for example in technique_examples:
                        f.write(json.dumps(example) + "\n")
                print(
                    f"📋 {technique.replace('_', ' ').title()}: {len(technique_examples)} examples"
                )

    def _create_questioning_analysis_report(self, examples, output_dir):
        """Create detailed analysis of questioning techniques"""

        # Analyze technique distribution
        all_techniques = []
        for example in examples:
            all_techniques.extend(example["deep_questioning_metadata"]["techniques"])

        technique_counts = {}
        for technique in all_techniques:
            technique_counts[technique] = technique_counts.get(technique, 0) + 1

        # Analyze depth distribution
        depth_distribution = {}
        for example in examples:
            depth = example["deep_questioning_metadata"]["depth_level"]
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_deep_questioning_examples": len(examples),
            "depth_level_distribution": depth_distribution,
            "technique_distribution": technique_counts,
            "average_drill_down_score": sum(
                ex["deep_questioning_metadata"]["drill_down_score"] for ex in examples
            )
            / len(examples),
            "average_intent_probing_score": sum(
                ex["deep_questioning_metadata"]["intent_probing_score"]
                for ex in examples
            )
            / len(examples),
            "questioning_mastery_ready": len(
                [
                    ex
                    for ex in examples
                    if ex["deep_questioning_metadata"]["depth_level"]
                    in ["expert_level", "advanced"]
                ]
            ),
            "sample_expert_examples": [
                ex
                for ex in examples
                if ex["deep_questioning_metadata"]["depth_level"] == "expert_level"
            ][:5],
        }

        report_file = output_dir / "deep_questioning_analysis_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Analysis report saved: {report_file}")

    def show_sample_deep_questioning(self, examples, num_samples=5):
        """Show sample deep questioning sequences"""

        print("\n📋 SAMPLE DEEP QUESTIONING SEQUENCES:")
        print("=" * 70)

        expert_examples = [
            ex
            for ex in examples
            if ex["deep_questioning_metadata"]["depth_level"] == "expert_level"
        ]

        if not expert_examples:
            expert_examples = examples[:num_samples]

        for i, example in enumerate(expert_examples[:num_samples], 1):
            metadata = example["deep_questioning_metadata"]

            print(
                f"\nExample {i} - {metadata['depth_level'].replace('_', ' ').title()}:"
            )
            print(f"Drill-down Score: {metadata['drill_down_score']}")
            print(f"Intent Probing Score: {metadata['intent_probing_score']}")
            print(f"Techniques: {', '.join(metadata['techniques'])}")

            instruction = (
                example.get("instruction", "")[:150] + "..."
                if len(example.get("instruction", "")) > 150
                else example.get("instruction", "")
            )
            output = (
                example.get("output", "")[:300] + "..."
                if len(example.get("output", "")) > 300
                else example.get("output", "")
            )

            print(f"Instruction: {instruction}")
            print(f"Deep Questioning: {output}")
            print("-" * 50)


def main():
    """Extract and analyze deep Socratic questioning sequences"""

    extractor = DeepSocraticExtractor()

    print("🎯 DEEP SOCRATIC QUESTIONING EXTRACTION")
    print("=" * 70)
    print("Purpose: Extract drill-down questioning that probes true intent")
    print("Focus: Multi-level questioning sequences for mastery")
    print("=" * 70)

    # Extract deep questioning examples
    deep_examples = extractor.extract_deep_questioning_sequences()

    if deep_examples:
        # Create questioning mastery dataset
        dataset_stats = extractor.create_questioning_mastery_dataset(deep_examples)

        print("\n✅ DEEP QUESTIONING MASTERY DATASET CREATED:")
        print(f"Total Examples: {dataset_stats['total_deep_examples']}")
        print(f"Expert Level: {dataset_stats['expert_level']}")
        print(f"Advanced Level: {dataset_stats['advanced_level']}")
        print(f"Intermediate Level: {dataset_stats['intermediate_level']}")

        # Show samples
        extractor.show_sample_deep_questioning(deep_examples)

        print("\n🎯 READY FOR QUESTIONING MASTERY TRAINING!")
        print("=" * 60)
        print("✅ Deep questioning sequences extracted")
        print("✅ Technique-specific datasets created")
        print("✅ Expert-level examples identified")
        print("✅ Intent probing examples ready")
        print("🚀 Perfect for training drill-down questioning specialists!")

    else:
        print("❌ No deep questioning examples found. Check Socratic dataset first.")


if __name__ == "__main__":
    main()
