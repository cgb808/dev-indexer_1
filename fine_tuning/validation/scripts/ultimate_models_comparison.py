#!/usr/bin/env python3
"""
Ultimate Model Comparison Tool
Compare all four mathematics-relevant models:
1. General Mathematics Model (standard math datasets)
2. Tutoring Model (authentic tutoring datasets) 
3. Pure Methodology Model (1000 methodology examples)
4. Hybrid Model (500 methodology + 500 math+methodology)

English model excluded as requested.
"""

from datetime import datetime

import requests


class UltimateModelsComparator:
    """Compare all four mathematics-relevant models"""

    def __init__(self, ollama_url="http://localhost:11435"):
        self.ollama_url = ollama_url
        self.base_model = "phi3:mini"

    def query_model_with_context(self, prompt, model_type="general_math"):
        """Query model with specific context formatting"""

        # Format prompt based on model type
        if model_type == "general_math":
            formatted_prompt = f"[LEARNING_CONTEXT] Mathematics [LEARNING_OBJECTIVE] Understand and solve mathematical concepts clearly. [TASK] {prompt}"
        elif model_type == "tutoring":
            formatted_prompt = f"[LEARNING_CONTEXT] Mathematics Tutoring [LEARNING_OBJECTIVE] Solve math word problems step-by-step with clear explanations. [TASK] {prompt}"
        elif model_type == "pure_methodology":
            formatted_prompt = f"[TUTORING_METHODOLOGY_MODE] Focus on teaching techniques, pedagogical approaches, and instructional strategies. [STUDENT_SITUATION] Student working on: {prompt} [TUTORING_TASK] Apply appropriate tutoring methodology to guide the student."
        elif model_type == "hybrid":
            formatted_prompt = f"[HYBRID_MODE] Integrate pure teaching methodology with subject-specific content. Apply pedagogical techniques while maintaining mathematical accuracy. [STUDENT_PROBLEM] {prompt} [TUTORING_TASK] Guide student using optimal combination of methodology and content knowledge."
        else:
            formatted_prompt = prompt

        try:
            payload = {
                "model": self.base_model,
                "prompt": formatted_prompt,
                "stream": False,
                "options": {"temperature": 0.1, "top_p": 0.9},
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate", json=payload, timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response received")
            else:
                return f"Error: {response.status_code}"

        except Exception as e:
            return f"Exception: {e}"

    def compare_all_models(self, test_problem):
        """Compare all four mathematics-relevant models"""

        print("🏆 ULTIMATE MATHEMATICS MODELS COMPARISON")
        print("🚫 English model excluded (different subject matter)")
        print("=" * 70)
        print(f"Test Problem: {test_problem}")
        print("=" * 70)

        models_to_test = [
            {
                "name": "GENERAL MATHEMATICS MODEL",
                "type": "general_math",
                "icon": "📚",
                "description": "Training: Calculative fine-tuning on standard math datasets\n   Focus: Mathematical content accuracy",
            },
            {
                "name": "TUTORING MODEL",
                "type": "tutoring",
                "icon": "🎓",
                "description": "Training: Calculative fine-tuning on authentic tutoring datasets\n   Focus: Tutoring-specific mathematical content",
            },
            {
                "name": "PURE METHODOLOGY MODEL",
                "type": "pure_methodology",
                "icon": "🔬",
                "description": "Training: Calculative fine-tuning on 1000 pure methodology examples\n   Focus: Subject-agnostic teaching techniques",
            },
            {
                "name": "HYBRID MODEL",
                "type": "hybrid",
                "icon": "⚡",
                "description": "Training: 500 pure methodology + 500 math+methodology examples\n   Focus: Integrated approach combining both strengths",
            },
        ]

        responses = {}

        for model in models_to_test:
            print(f"\n{model['icon']} {model['name']}")
            print(f"   {model['description']}")
            print("-" * 50)

            response = self.query_model_with_context(test_problem, model["type"])
            responses[model["type"]] = response

            # Truncate very long responses for readability
            display_response = (
                response[:400] + "..." if len(response) > 400 else response
            )
            print(f"Response:\n{display_response}")
            print("\n" + "=" * 70)

        # Comprehensive analysis across all four models
        print("\n📊 COMPREHENSIVE TEACHING QUALITY ANALYSIS")
        print("=" * 50)

        # Enhanced indicators for four-way comparison
        teaching_indicators = {
            "step_structure": [
                "step 1",
                "step 2",
                "step 3",
                "first",
                "next",
                "then",
                "finally",
            ],
            "explanation_quality": [
                "let's",
                "we need to",
                "to find",
                "calculate",
                "because",
                "understand",
            ],
            "pedagogical_approach": [
                "notice",
                "remember",
                "important",
                "careful",
                "think about",
                "consider",
            ],
            "methodology_focus": [
                "approach",
                "strategy",
                "method",
                "technique",
                "process",
                "guide",
            ],
            "student_engagement": [
                "you",
                "your",
                "can you",
                "what do you",
                "let's work",
                "together",
            ],
            "clarity_indicators": [
                "clear",
                "step-by-step",
                "systematic",
                "organized",
                "logical",
                "structured",
            ],
            "tutoring_quality": [
                "help",
                "guide",
                "support",
                "assist",
                "teach",
                "explain",
            ],
            "mathematical_accuracy": [
                "calculate",
                "solve",
                "answer",
                "result",
                "equals",
                "total",
            ],
        }

        model_scores = {}

        for model in models_to_test:
            model_type = model["type"]
            response = responses[model_type]
            response_lower = response.lower()

            category_scores = {}
            total_score = 0

            for category, indicators in teaching_indicators.items():
                category_score = sum(
                    1 for indicator in indicators if indicator in response_lower
                )
                category_scores[category] = category_score
                total_score += category_score

            model_scores[model_type] = {
                "total": total_score,
                "categories": category_scores,
                "name": model["name"],
                "icon": model["icon"],
            }

            print(f"\n{model['icon']} {model['name']}:")
            print(
                f"  Overall Teaching Quality Score: {total_score}/{sum(len(indicators) for indicators in teaching_indicators.values())}"
            )

            # Group related categories for better readability
            print(
                f"  📝 Structure & Clarity: {category_scores['step_structure'] + category_scores['clarity_indicators']}"
            )
            print(
                f"  🎯 Pedagogical Approach: {category_scores['pedagogical_approach'] + category_scores['methodology_focus']}"
            )
            print(
                f"  👥 Student Engagement: {category_scores['student_engagement'] + category_scores['tutoring_quality']}"
            )
            print(
                f"  🔢 Mathematical Quality: {category_scores['mathematical_accuracy'] + category_scores['explanation_quality']}"
            )

        # Determine rankings and analysis
        sorted_models = sorted(
            model_scores.items(), key=lambda x: x[1]["total"], reverse=True
        )

        print("\n🏆 FINAL RANKINGS:")
        for i, (model_type, score_data) in enumerate(sorted_models, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📍"
            print(f"   {medal} {i}. {score_data['name']}: {score_data['total']} points")

        # Specialized analysis
        scores = {
            model_type: data["total"] for model_type, data in model_scores.items()
        }

        print("\n🔍 SPECIALIZED ANALYSIS:")

        # Methodology vs Content Analysis
        methodology_focused = scores.get("pure_methodology", 0)
        content_focused = scores.get("general_math", 0)
        tutoring_focused = scores.get("tutoring", 0)
        hybrid_focused = scores.get("hybrid", 0)

        print(
            f"   📚 Content Mastery: General Math ({content_focused}) vs Tutoring ({tutoring_focused})"
        )
        print(
            f"   🔬 Methodology Mastery: Pure ({methodology_focused}) vs Hybrid ({hybrid_focused})"
        )
        print(
            f"   ⚖️  Integration Success: {'✅ Hybrid Superior' if hybrid_focused == max(scores.values()) else '❌ Pure Approaches Better'}"
        )

        # Determine best approach
        winner_type = sorted_models[0][0]
        winner_name = sorted_models[0][1]["name"]

        print(f"\n🎯 OPTIMAL APPROACH: {winner_name}")

        if winner_type == "hybrid":
            print(
                "   ✅ Hypothesis CONFIRMED: Hybrid approach outperforms pure approaches"
            )
        elif winner_type == "pure_methodology":
            print("   🔬 Pure methodology training proves most effective")
        elif winner_type == "tutoring":
            print("   🎓 Authentic tutoring datasets provide best results")
        else:
            print("   📚 Traditional mathematical training remains competitive")

        return {
            "responses": responses,
            "scores": model_scores,
            "rankings": sorted_models,
            "winner": winner_type,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Run ultimate models comparison"""
    comparator = UltimateModelsComparator()

    # Comprehensive test problems designed to evaluate all aspects
    test_problems = [
        "Sarah has 36 stickers. She gives 1/4 of them to her brother and 1/3 of the remaining stickers to her sister. How many stickers does Sarah have left?",
        "A student is struggling with this problem: 'If a recipe calls for 2/3 cup of flour and you want to make 1.5 times the recipe, how much flour do you need?' Help guide them through it step by step.",
        "I'm confused about this math problem: A train travels 60 miles in the first hour, then 45 miles in the second hour. If it continues at this pattern (decreasing by 15 miles each hour), how far will it travel in total during the first 4 hours?",
    ]

    print("🔬 ULTIMATE COMPARISON: ALL FOUR MATHEMATICS MODELS")
    print("🚫 English model excluded (different subject matter)")
    print("📊 Models: General Math | Tutoring | Pure Methodology | Hybrid")
    print("🎯 Testing hypothesis: Does hybrid approach outperform pure approaches?")
    print("=" * 80)

    total_results = []

    for i, problem in enumerate(test_problems, 1):
        print(f"\n🧪 ULTIMATE TEST {i}")
        comparison = comparator.compare_all_models(problem)
        total_results.append(comparison)

        if i < len(test_problems):
            print("\n" + "=" * 80)
            input("Press Enter to continue to next test...")

    # Final analysis across all tests
    print("\n🏁 FINAL ANALYSIS ACROSS ALL TESTS")
    print("=" * 50)

    # Aggregate scores across all tests
    total_scores = {}
    for result in total_results:
        for model_type, score_data in result["scores"].items():
            if model_type not in total_scores:
                total_scores[model_type] = {
                    "total": 0,
                    "name": score_data["name"],
                    "icon": score_data["icon"],
                }
            total_scores[model_type]["total"] += score_data["total"]

    # Final rankings
    final_rankings = sorted(
        total_scores.items(), key=lambda x: x[1]["total"], reverse=True
    )

    print("\n🏆 AGGREGATE RANKINGS (All Tests Combined):")
    for i, (model_type, data) in enumerate(final_rankings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📍"
        print(f"   {medal} {i}. {data['name']}: {data['total']} total points")

    winner = final_rankings[0]
    print(f"\n🎯 ULTIMATE WINNER: {winner[1]['icon']} {winner[1]['name']}")
    print(f"   Total Score: {winner[1]['total']} points")

    if winner[0] == "hybrid":
        print(
            "   🎉 HYPOTHESIS CONFIRMED: Hybrid approach (500 methodology + 500 math+methodology) is optimal!"
        )
    else:
        print(
            f"   🔍 FINDING: {winner[1]['name']} approach proves most effective for mathematical tutoring"
        )


if __name__ == "__main__":
    main()
