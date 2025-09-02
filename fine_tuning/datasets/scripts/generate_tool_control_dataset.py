#!/usr/bin/env python3
"""
Generate tool control training dataset for tiny quantized model.
This model will be ultra-fast at classifying user inputs and routing to appropriate tools.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List


class ToolControlDatasetGenerator:
    def __init__(self):
        self.tool_categories = {
            "MATHEMATICAL": {
                "tools": [
                    "calculator",
                    "graphing",
                    "latex_renderer",
                    "equation_solver",
                    "formula_display",
                ],
                "specialist": "phi3_mathematics_tutor",
                "keywords": [
                    "solve",
                    "calculate",
                    "graph",
                    "equation",
                    "formula",
                    "math",
                    "algebra",
                    "calculus",
                    "geometry",
                ],
                "voice_preference": "jarvis",  # Analytical voice for math
            },
            "VISUAL": {
                "tools": [
                    "canvas_draw",
                    "diagram_create",
                    "chart_generate",
                    "latex_display",
                    "image_annotate",
                ],
                "specialist": "phi3_visual_explainer",
                "keywords": [
                    "show",
                    "draw",
                    "diagram",
                    "chart",
                    "visualize",
                    "illustrate",
                    "display",
                    "picture",
                ],
                "voice_preference": "alan",  # Clear voice for explanations
            },
            "AUDIO": {
                "tools": [
                    "tts_speak",
                    "voice_change",
                    "audio_pause",
                    "audio_resume",
                    "volume_adjust",
                ],
                "specialist": "phi3_conversation_handler",
                "keywords": [
                    "wait",
                    "pause",
                    "stop",
                    "continue",
                    "louder",
                    "quieter",
                    "repeat",
                    "speak",
                ],
                "voice_preference": "amy",  # Default conversational voice
            },
            "SEARCH": {
                "tools": [
                    "rag_search",
                    "vector_query",
                    "context_retrieve",
                    "memory_access",
                    "knowledge_lookup",
                ],
                "specialist": "phi3_knowledge_retriever",
                "keywords": [
                    "find",
                    "search",
                    "lookup",
                    "remember",
                    "what is",
                    "tell me about",
                    "explain",
                ],
                "voice_preference": "jarvis",  # Authoritative for facts
            },
            "WORKFLOW": {
                "tools": [
                    "task_sequence",
                    "multi_step",
                    "context_switch",
                    "session_manage",
                    "progress_track",
                ],
                "specialist": "phi3_workflow_orchestrator",
                "keywords": [
                    "next",
                    "then",
                    "after",
                    "sequence",
                    "steps",
                    "workflow",
                    "process",
                    "continue",
                ],
                "voice_preference": "alan",  # Organized for workflows
            },
        }

        self.examples = []

    def generate_mathematical_examples(self, count: int = 1000) -> List[Dict]:
        """Generate examples for mathematical tool control."""
        examples = []

        # Basic calculations
        calculations = [
            "What's 15 * 23?",
            "Calculate the square root of 144",
            "What's 2^8?",
            "Find 25% of 400",
            "What's the area of a circle with radius 5?",
            "Convert 75 degrees Fahrenheit to Celsius",
        ]

        # Equation solving
        equations = [
            "Solve x^2 + 5x - 6 = 0",
            "Find x when 2x + 7 = 15",
            "Solve the system: x + y = 5, 2x - y = 1",
            "Factor x^2 - 9",
            "Solve for y: 3y - 4 = 2y + 8",
            "Find the roots of x^2 - 4x + 3 = 0",
        ]

        # Graphing requests
        graphs = [
            "Graph the function y = x^2 + 2x - 3",
            "Plot y = sin(x)",
            "Show me the graph of y = 2x + 1",
            "Graph the parabola y = -x^2 + 4",
            "Plot the exponential function y = 2^x",
            "Graph y = |x - 2|",
        ]

        # LaTeX rendering
        latex_requests = [
            "Show me the quadratic formula",
            "Display the Pythagorean theorem",
            "Write out the derivative of x^3",
            "Show me the binomial theorem",
            "Display Einstein's mass-energy equation",
            "Show the formula for compound interest",
        ]

        all_math_inputs = calculations + equations + graphs + latex_requests

        for i in range(count):
            user_input = random.choice(all_math_inputs)

            # Determine specific tools needed based on input type
            if any(
                word in user_input.lower()
                for word in ["calculate", "what's", "find", "convert"]
            ):
                tools_needed = ["calculator"]
                if "area" in user_input or "formula" in user_input:
                    tools_needed.append("latex_renderer")
            elif any(
                word in user_input.lower() for word in ["solve", "factor", "roots"]
            ):
                tools_needed = ["equation_solver", "latex_renderer"]
            elif any(word in user_input.lower() for word in ["graph", "plot"]):
                tools_needed = ["graphing", "latex_renderer"]
            elif any(
                word in user_input.lower() for word in ["show", "display", "write"]
            ):
                tools_needed = ["latex_renderer"]
            else:
                tools_needed = ["calculator", "latex_renderer"]

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": "MATHEMATICAL",
                    "tools_needed": tools_needed,
                    "specialist_required": "phi3_mathematics_tutor",
                    "confidence": round(random.uniform(0.85, 0.99), 2),
                    "voice_preference": "jarvis",
                    "parameters": self._extract_math_parameters(user_input),
                },
            }
            examples.append(example)

        return examples

    def generate_audio_control_examples(self, count: int = 500) -> List[Dict]:
        """Generate examples for audio/conversation control."""
        examples = []

        # Interruption patterns
        interruptions = [
            "Wait",
            "Hold on",
            "Stop",
            "Pause",
            "Let me think",
            "Wait a minute",
            "Hold on a second",
            "Actually, wait",
            "Can you pause?",
            "Stop talking for a moment",
            "Give me a second",
        ]

        # Volume/speed control
        audio_controls = [
            "Speak louder",
            "Can you speak quieter?",
            "Slow down",
            "Talk faster",
            "Lower your voice",
            "Increase volume",
            "Speak more clearly",
            "Can you repeat that?",
            "Say that again",
        ]

        # Voice change requests
        voice_changes = [
            "Change your voice",
            "Use a different voice",
            "Switch to jarvis voice",
            "Can you use the British voice?",
            "Use the southern accent",
            "Switch to the female voice",
            "Use the male voice",
        ]

        # Continuation commands
        continuations = [
            "Continue",
            "Go on",
            "Keep going",
            "What's next?",
            "Proceed",
            "Continue where you left off",
            "Resume",
            "Keep talking",
            "Go ahead",
            "Carry on",
        ]

        all_audio_inputs = (
            interruptions + audio_controls + voice_changes + continuations
        )

        for i in range(count):
            user_input = random.choice(all_audio_inputs)

            # Determine specific audio tools needed
            if any(
                word in user_input.lower() for word in ["wait", "hold", "stop", "pause"]
            ):
                tools_needed = ["audio_pause"]
                action_type = "pause"
            elif any(
                word in user_input.lower() for word in ["louder", "quieter", "volume"]
            ):
                tools_needed = ["volume_adjust"]
                action_type = "volume_control"
            elif any(
                word in user_input.lower()
                for word in ["voice", "accent", "british", "jarvis"]
            ):
                tools_needed = ["voice_change"]
                action_type = "voice_selection"
            elif any(
                word in user_input.lower() for word in ["continue", "resume", "go on"]
            ):
                tools_needed = ["audio_resume"]
                action_type = "resume"
            elif any(word in user_input.lower() for word in ["repeat", "again"]):
                tools_needed = ["tts_speak"]
                action_type = "repeat"
            else:
                tools_needed = ["tts_speak"]
                action_type = "general_audio"

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": "AUDIO",
                    "tools_needed": tools_needed,
                    "specialist_required": "phi3_conversation_handler",
                    "confidence": round(random.uniform(0.90, 0.99), 2),
                    "voice_preference": "amy",
                    "parameters": {
                        "action_type": action_type,
                        "immediate_execution": True,
                    },
                },
            }
            examples.append(example)

        return examples

    def generate_visual_examples(self, count: int = 800) -> List[Dict]:
        """Generate examples for visual tool control."""
        examples = []

        # Drawing requests
        drawings = [
            "Draw a triangle",
            "Show me a circle",
            "Create a diagram of a cell",
            "Draw the water cycle",
            "Illustrate a food chain",
            "Draw a house",
            "Show me a family tree",
            "Create a flowchart",
            "Draw a coordinate plane",
        ]

        # Chart/graph requests (different from mathematical graphing)
        charts = [
            "Create a pie chart",
            "Make a bar graph",
            "Show me a timeline",
            "Create a Venn diagram",
            "Make a scatter plot",
            "Show data in a table",
            "Create an organizational chart",
            "Make a comparison chart",
        ]

        # Annotation requests
        annotations = [
            "Label this diagram",
            "Add arrows to show the flow",
            "Highlight the important parts",
            "Mark the key points",
            "Add text to explain",
            "Show the steps visually",
            "Point out the differences",
            "Circle the main idea",
        ]

        # Display requests
        displays = [
            "Show me an image of the solar system",
            "Display the periodic table",
            "Show a map of Europe",
            "Display the human skeleton",
            "Show me a world map",
            "Display the parts of a flower",
            "Show the layers of the Earth",
        ]

        all_visual_inputs = drawings + charts + annotations + displays

        for i in range(count):
            user_input = random.choice(all_visual_inputs)

            # Determine specific visual tools needed
            if any(word in user_input.lower() for word in ["draw", "create", "make"]):
                if any(
                    word in user_input.lower() for word in ["chart", "graph", "plot"]
                ):
                    tools_needed = ["chart_generate"]
                else:
                    tools_needed = ["canvas_draw", "diagram_create"]
            elif any(word in user_input.lower() for word in ["show", "display"]):
                tools_needed = ["latex_display", "diagram_create"]
            elif any(
                word in user_input.lower()
                for word in ["label", "arrow", "highlight", "mark"]
            ):
                tools_needed = ["image_annotate"]
            else:
                tools_needed = ["canvas_draw"]

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": "VISUAL",
                    "tools_needed": tools_needed,
                    "specialist_required": "phi3_visual_explainer",
                    "confidence": round(random.uniform(0.88, 0.97), 2),
                    "voice_preference": "alan",
                    "parameters": {
                        "visual_type": self._determine_visual_type(user_input),
                        "complexity": "medium",
                    },
                },
            }
            examples.append(example)

        return examples

    def generate_search_examples(self, count: int = 700) -> List[Dict]:
        """Generate examples for search/knowledge retrieval."""
        examples = []

        # Knowledge queries
        knowledge = [
            "What is photosynthesis?",
            "Tell me about the American Revolution",
            "Explain quantum mechanics",
            "What are black holes?",
            "Define democracy",
            "How does DNA work?",
            "What is machine learning?",
            "Explain gravity",
        ]

        # Memory/context retrieval
        memory = [
            "What did we discuss yesterday?",
            "Remember our last conversation about math?",
            "What was that formula we used before?",
            "Recall what I learned about history",
            "What topics have we covered?",
            "Show me my progress",
            "What did I struggle with?",
        ]

        # Search requests
        searches = [
            "Find information about climate change",
            "Look up the capital of France",
            "Search for examples of metaphors",
            "Find the definition of osmosis",
            "Look up recent news about space",
            "Search for primary sources",
            "Find scholarly articles about education",
        ]

        all_search_inputs = knowledge + memory + searches

        for i in range(count):
            user_input = random.choice(all_search_inputs)

            # Determine specific search tools needed
            if any(
                word in user_input.lower()
                for word in ["remember", "recall", "discussed", "conversation"]
            ):
                tools_needed = ["memory_access", "context_retrieve"]
                search_type = "memory"
            elif any(
                word in user_input.lower() for word in ["find", "search", "look up"]
            ):
                tools_needed = ["rag_search", "vector_query"]
                search_type = "external"
            else:
                tools_needed = ["knowledge_lookup", "vector_query"]
                search_type = "knowledge"

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": "SEARCH",
                    "tools_needed": tools_needed,
                    "specialist_required": "phi3_knowledge_retriever",
                    "confidence": round(random.uniform(0.85, 0.95), 2),
                    "voice_preference": "jarvis",
                    "parameters": {
                        "search_type": search_type,
                        "query_complexity": "medium",
                    },
                },
            }
            examples.append(example)

        return examples

    def generate_workflow_examples(self, count: int = 500) -> List[Dict]:
        """Generate examples for workflow orchestration."""
        examples = []

        # Multi-step processes
        processes = [
            "Let's work through this step by step",
            "What's the next step?",
            "Take me through the process",
            "Show me the sequence",
            "What comes after this?",
            "Let's continue with the next part",
            "Walk me through this procedure",
            "What's the workflow here?",
        ]

        # Context switching
        switches = [
            "Let's switch to a different topic",
            "Can we change subjects?",
            "Move on to the next lesson",
            "Let's talk about something else",
            "Switch to math now",
            "Change to history mode",
            "Let's do science instead",
            "Can we work on writing?",
        ]

        # Session management
        sessions = [
            "Save my progress",
            "Remember where we left off",
            "Start a new session",
            "End this lesson",
            "Take a break",
            "Resume our session",
            "Track my learning",
            "Show my achievements",
            "What's my status?",
        ]

        all_workflow_inputs = processes + switches + sessions

        for i in range(count):
            user_input = random.choice(all_workflow_inputs)

            # Determine specific workflow tools needed
            if any(
                word in user_input.lower()
                for word in ["step", "sequence", "process", "workflow"]
            ):
                tools_needed = ["task_sequence", "multi_step"]
                workflow_type = "process"
            elif any(
                word in user_input.lower()
                for word in ["switch", "change", "move", "different"]
            ):
                tools_needed = ["context_switch"]
                workflow_type = "context_switch"
            elif any(
                word in user_input.lower()
                for word in ["save", "progress", "session", "track"]
            ):
                tools_needed = ["session_manage", "progress_track"]
                workflow_type = "session"
            else:
                tools_needed = ["task_sequence"]
                workflow_type = "general"

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": "WORKFLOW",
                    "tools_needed": tools_needed,
                    "specialist_required": "phi3_workflow_orchestrator",
                    "confidence": round(random.uniform(0.82, 0.94), 2),
                    "voice_preference": "alan",
                    "parameters": {
                        "workflow_type": workflow_type,
                        "complexity": "medium",
                    },
                },
            }
            examples.append(example)

        return examples

    def _extract_math_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract mathematical parameters from user input."""
        params = {}

        # Function detection
        if "y =" in user_input or "f(x)" in user_input:
            # Extract function if present
            import re

            func_match = re.search(r"y\s*=\s*([^,]+)", user_input)
            if func_match:
                params["function"] = func_match.group(1).strip()

        # Equation detection
        if any(op in user_input for op in ["=", "solve"]):
            params["equation_type"] = "algebraic"

        # Number extraction
        import re

        numbers = re.findall(r"-?\d+\.?\d*", user_input)
        if numbers:
            params["numbers"] = [float(n) for n in numbers[:3]]  # Limit to 3 numbers

        return params

    def _determine_visual_type(self, user_input: str) -> str:
        """Determine the type of visual needed."""
        if any(word in user_input.lower() for word in ["chart", "graph", "plot"]):
            return "chart"
        elif any(
            word in user_input.lower() for word in ["diagram", "flowchart", "tree"]
        ):
            return "diagram"
        elif any(word in user_input.lower() for word in ["draw", "sketch"]):
            return "drawing"
        else:
            return "general"

    def generate_mixed_examples(self, count: int = 500) -> List[Dict]:
        """Generate examples that might require multiple tool categories."""
        examples = []

        mixed_inputs = [
            "Solve x^2 + 3x = 10 and show me the graph",  # MATH + VISUAL
            "Find information about calculus and explain with diagrams",  # SEARCH + VISUAL
            "Let me work through this math problem step by step",  # MATH + WORKFLOW
            "Search for examples of quadratic equations and graph them",  # SEARCH + MATH + VISUAL
            "Pause while I write this down, then continue with the next step",  # AUDIO + WORKFLOW
            "Show me a diagram of photosynthesis and explain each step",  # VISUAL + SEARCH + WORKFLOW
        ]

        for i in range(count):
            user_input = random.choice(mixed_inputs)

            # Determine primary category (first mentioned/most important)
            if any(
                word in user_input.lower() for word in ["solve", "equation", "math"]
            ):
                primary = "MATHEMATICAL"
                specialist = "phi3_mathematics_tutor"
                tools = ["equation_solver", "graphing", "latex_renderer"]
            elif any(
                word in user_input.lower() for word in ["find", "search", "information"]
            ):
                primary = "SEARCH"
                specialist = "phi3_knowledge_retriever"
                tools = ["rag_search", "vector_query"]
            elif any(
                word in user_input.lower() for word in ["show", "diagram", "graph"]
            ):
                primary = "VISUAL"
                specialist = "phi3_visual_explainer"
                tools = ["diagram_create", "chart_generate"]
            elif any(
                word in user_input.lower() for word in ["step", "process", "workflow"]
            ):
                primary = "WORKFLOW"
                specialist = "phi3_workflow_orchestrator"
                tools = ["task_sequence", "multi_step"]
            else:
                primary = "MATHEMATICAL"
                specialist = "phi3_mathematics_tutor"
                tools = ["calculator"]

            example = {
                "user_input": user_input,
                "tool_classification": {
                    "primary_category": primary,
                    "tools_needed": tools,
                    "specialist_required": specialist,
                    "confidence": round(
                        random.uniform(0.75, 0.90), 2
                    ),  # Lower confidence for mixed
                    "voice_preference": self.tool_categories[primary][
                        "voice_preference"
                    ],
                    "parameters": {"complexity": "high", "multi_category": True},
                },
            }
            examples.append(example)

        return examples

    def generate_complete_dataset(self, total_examples: int = 4000) -> List[Dict]:
        """Generate the complete tool control dataset."""
        print(f"Generating {total_examples} tool control examples...")

        # Distribute examples across categories
        math_count = int(total_examples * 0.30)  # 30% mathematical
        visual_count = int(total_examples * 0.20)  # 20% visual
        audio_count = int(total_examples * 0.15)  # 15% audio control
        search_count = int(total_examples * 0.20)  # 20% search/knowledge
        workflow_count = int(total_examples * 0.10)  # 10% workflow
        mixed_count = int(total_examples * 0.05)  # 5% mixed category

        print(f"Mathematical: {math_count}")
        print(f"Visual: {visual_count}")
        print(f"Audio: {audio_count}")
        print(f"Search: {search_count}")
        print(f"Workflow: {workflow_count}")
        print(f"Mixed: {mixed_count}")

        all_examples = []
        all_examples.extend(self.generate_mathematical_examples(math_count))
        all_examples.extend(self.generate_visual_examples(visual_count))
        all_examples.extend(self.generate_audio_control_examples(audio_count))
        all_examples.extend(self.generate_search_examples(search_count))
        all_examples.extend(self.generate_workflow_examples(workflow_count))
        all_examples.extend(self.generate_mixed_examples(mixed_count))

        # Shuffle for good training distribution
        random.shuffle(all_examples)

        print(f"Generated {len(all_examples)} total examples")
        return all_examples

    def save_dataset(self, examples: List[Dict], output_file: str):
        """Save dataset in JSONL format for training."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")

        print(f"Saved {len(examples)} examples to {output_path}")

        # Also save a sample for inspection
        sample_file = output_path.with_name(f"sample_{output_path.name}")
        with open(sample_file, "w") as f:
            for example in examples[:10]:
                f.write(json.dumps(example, indent=2) + "\n\n")

        print(f"Saved sample to {sample_file}")


def main():
    """Generate tool control training dataset."""
    generator = ToolControlDatasetGenerator()

    # Generate dataset
    examples = generator.generate_complete_dataset(total_examples=4000)

    # Save to file
    output_file = "fine_tuning/datasets/tool_control/tool_control_training.jsonl"
    generator.save_dataset(examples, output_file)

    # Generate statistics
    categories = {}
    for example in examples:
        cat = example["tool_classification"]["primary_category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nDataset Statistics:")
    for category, count in sorted(categories.items()):
        percentage = (count / len(examples)) * 100
        print(f"{category}: {count} examples ({percentage:.1f}%)")

    # Print tool distribution
    tools = {}
    for example in examples:
        for tool in example["tool_classification"]["tools_needed"]:
            tools[tool] = tools.get(tool, 0) + 1

    print("\nTop Tools:")
    for tool, count in sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{tool}: {count} uses")


if __name__ == "__main__":
    main()
