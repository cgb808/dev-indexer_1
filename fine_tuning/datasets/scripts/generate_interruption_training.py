#!/usr/bin/env python3
"""
Interruption Handling Training Data Generator
Create training examples that teach models to handle user interruptions gracefully
"""

import json
from pathlib import Path


class InterruptionTrainingGenerator:
    """Generate training data for handling user interruptions"""

    def __init__(self, workspace_root="/home/cgbowen/AIWorkspace"):
        self.workspace_root = Path(workspace_root)
        self.fine_tuning_dir = self.workspace_root / "fine_tuning"

        # Interruption scenarios
        self.interruption_scenarios = [
            {
                "context": "Math tutoring - explaining algebra steps",
                "ongoing_explanation": "First, you need to isolate the variable by subtracting 3 from both sides. Second, you combine the like terms on the right side which gives you 2x = 8.",
                "interruption": "Okay, I see that, but I really need to know why we subtract 3 first and not divide by 2?",
                "graceful_response": "That's an excellent question, thanks for stopping me. It's a key concept. We subtract first to follow the order of operations, often remembered by PEMDAS, in reverse. We handle addition and subtraction before multiplication and division to isolate the 'x' term. Does that clarification help?",
                "pedagogy_strategy": "error_correction",
                "affect_focus": "curiosity",
            },
            {
                "context": "Science tutoring - explaining photosynthesis",
                "ongoing_explanation": "Photosynthesis occurs in two main stages. The light-dependent reactions happen first in the thylakoids, where chlorophyll absorbs sunlight and converts it to chemical energy.",
                "interruption": "Wait, sorry to interrupt, but what exactly is a thylakoid? I don't think I understand that part.",
                "graceful_response": "Absolutely, let me clarify that first - it's crucial to understand before we continue. A thylakoid is like a tiny disc-shaped compartment inside chloroplasts. Think of it as a specialized factory floor where the light reactions happen. Should I explain more about its structure before we move on?",
                "pedagogy_strategy": "clarification",
                "affect_focus": "understanding",
            },
            {
                "context": "History tutoring - explaining World War causes",
                "ongoing_explanation": "The assassination of Archduke Franz Ferdinand was the immediate trigger, but there were deeper causes. First, there was rising nationalism across Europe. Second, there were complex alliance systems that created a web of obligations.",
                "interruption": "Hold on, I'm confused about something. Who was this archduke guy exactly? Why did his death matter so much?",
                "graceful_response": "Great question - let me back up and explain who he was first, because that context is essential. Franz Ferdinand was the heir to the Austro-Hungarian throne, so his assassination wasn't just any murder - it was an attack on a future emperor. This made it a direct challenge to Austria-Hungary's power. Does that help explain why it had such massive consequences?",
                "pedagogy_strategy": "context_building",
                "affect_focus": "confusion_resolution",
            },
            {
                "context": "Programming tutoring - explaining loops",
                "ongoing_explanation": "In a for loop, we have three parts: initialization, condition, and increment. So 'for(int i=0; i<10; i++)' means we start i at 0, continue while i is less than 10, and increment i by 1 each time.",
                "interruption": "Sorry, can you pause there? I'm still not getting what 'increment' means in this context.",
                "graceful_response": "Of course! Let me clarify 'increment' right now since it's fundamental. In programming, increment means to increase a value by a specific amount - usually by 1. So 'i++' takes whatever value i currently has and adds 1 to it. If i was 0, it becomes 1. If i was 5, it becomes 6. Make sense now?",
                "pedagogy_strategy": "vocabulary_clarification",
                "affect_focus": "foundational_understanding",
            },
            {
                "context": "Literature tutoring - analyzing symbolism",
                "ongoing_explanation": "The green light in Gatsby represents several things. On the surface, it's literally the light at the end of Daisy's dock. But symbolically, it represents hope, the American Dream, and Gatsby's longing for the past.",
                "interruption": "Wait, I need to stop you there. How do we know it's symbolic? Like, how can you tell when something is a symbol versus just... a light?",
                "graceful_response": "Excellent critical thinking question! You're right to question that. We know it's symbolic because Fitzgerald deliberately draws our attention to it repeatedly throughout the novel, and he connects it to Gatsby's emotions and dreams. When authors mention specific objects multiple times and tie them to characters' deeper feelings, that's usually a signal that it's symbolic. Should we look at the specific passages where this happens?",
                "pedagogy_strategy": "critical_thinking",
                "affect_focus": "analytical_skepticism",
            },
        ]

        # Different types of interruption patterns
        self.interruption_triggers = [
            "Wait, sorry to interrupt, but",
            "Hold on, I'm confused about",
            "Can you pause there? I'm not getting",
            "Sorry, can you stop and explain",
            "Wait, before you continue,",
            "I need to stop you there.",
            "Hang on, I have a question about",
            "Sorry to cut in, but what",
            "Can we back up? I don't understand",
            "Hold up, what do you mean by",
        ]

        # Graceful interruption response patterns
        self.graceful_responses = [
            "That's an excellent question, thanks for stopping me.",
            "Absolutely, let me clarify that first - it's crucial to understand before we continue.",
            "Great question - let me back up and explain",
            "Of course! Let me clarify that right now since it's fundamental.",
            "Excellent critical thinking question! You're right to question that.",
            "Perfect timing for that question - it's important we get this clear.",
            "I'm glad you interrupted - that's a key point to understand.",
            "Thanks for stopping me there - this is worth exploring.",
            "Good catch! Let me address that confusion immediately.",
            "Absolutely right to pause there - this needs clarification.",
        ]

    def generate_interruption_training_data(self):
        """Generate comprehensive interruption handling training examples"""

        print("🎯 GENERATING INTERRUPTION HANDLING TRAINING DATA")
        print("=" * 60)
        print("Purpose: Teach models to handle user interruptions gracefully")
        print("Pattern: [USER_INTERRUPTION] token for technical integration")
        print("=" * 60)

        training_examples = []

        # Generate examples from base scenarios
        for scenario in self.interruption_scenarios:
            example = {
                "instruction": f"The tutor is explaining {scenario['context']} when the student interrupts with a clarifying question.",
                "input": f"{scenario['ongoing_explanation']} [USER_INTERRUPTION] {scenario['interruption']}",
                "output": scenario["graceful_response"],
                "pedagogy_strategy": scenario["pedagogy_strategy"],
                "affect_focus": scenario["affect_focus"],
                "interruption_handling": True,
                "context_domain": scenario["context"].split(" - ")[0],
            }
            training_examples.append(example)

        # Generate variations with different interruption patterns
        base_scenarios = [
            {
                "domain": "Mathematics",
                "explanation": "To solve this quadratic equation, we first need to get everything on one side. Then we can use the quadratic formula: x equals negative b plus or minus...",
                "student_confusion": "the quadratic formula",
                "clarification": "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a. It's a reliable method for solving any quadratic equation when factoring is difficult.",
            },
            {
                "domain": "Physics",
                "explanation": "Newton's second law states that force equals mass times acceleration. This means that if you increase the mass while keeping force constant, acceleration will decrease proportionally.",
                "student_confusion": "what acceleration actually means",
                "clarification": "Acceleration is how quickly velocity changes over time. If a car goes from 0 to 60 mph in 6 seconds, that's acceleration - the rate of change of speed.",
            },
            {
                "domain": "Chemistry",
                "explanation": "In this reaction, the hydrogen atoms are bonding with oxygen to form water molecules. The electrons are being shared between the atoms in what we call covalent bonds.",
                "student_confusion": "how electrons can be 'shared'",
                "clarification": "When atoms share electrons, they don't physically pass them back and forth. Instead, the electrons spend time around both atoms, creating an area of negative charge that holds the atoms together.",
            },
            {
                "domain": "English Literature",
                "explanation": "The author uses dramatic irony here because we as readers know something the character doesn't. This creates tension and engages us more deeply in the story.",
                "student_confusion": "the difference between dramatic irony and regular irony",
                "clarification": "Great distinction to make! Regular irony is when someone says one thing but means the opposite. Dramatic irony is when the audience knows something a character doesn't - like watching a horror movie and yelling 'Don't go in there!' because you see the danger they don't.",
            },
        ]

        # Generate variations
        for base in base_scenarios:
            for i, trigger in enumerate(self.interruption_triggers[:5]):
                for j, response_start in enumerate(self.graceful_responses[:3]):

                    interruption_text = f"{trigger} {base['student_confusion']}?"

                    example = {
                        "instruction": f"The tutor is explaining {base['domain']} concepts when the student interrupts with a clarifying question.",
                        "input": f"{base['explanation']} [USER_INTERRUPTION] {interruption_text}",
                        "output": f"{response_start} {base['clarification']}",
                        "pedagogy_strategy": "interruption_clarification",
                        "affect_focus": "confusion_resolution",
                        "interruption_handling": True,
                        "context_domain": base["domain"],
                    }
                    training_examples.append(example)

        print(f"✅ Generated {len(training_examples)} interruption handling examples")

        return training_examples

    def create_session_management_data(self):
        """Generate training data for session ending scenarios"""

        session_end_examples = []

        # Explicit ending scenarios
        explicit_endings = [
            {
                "user_input": "Okay, I'm done with math for today, thanks!",
                "expected_action": "end_session",
                "tutor_response": "You're very welcome! You made great progress today. Feel free to come back anytime you want to work on more math problems. Have a wonderful day!",
                "session_management": "explicit_end",
            },
            {
                "user_input": "I think that's enough chemistry for now, thank you so much!",
                "expected_action": "end_session",
                "tutor_response": "Excellent work today! Chemistry can be challenging, but you're really getting the hang of these concepts. Take your time to let this sink in, and we can pick up where we left off next time.",
                "session_management": "explicit_end",
            },
            {
                "user_input": "Thanks for the help with history, I need to go now.",
                "expected_action": "end_session",
                "tutor_response": "You're absolutely welcome! History is fascinating once you start connecting the dots. Keep thinking about those cause-and-effect relationships we discussed. See you next time!",
                "session_management": "explicit_end",
            },
        ]

        # Implicit topic change scenarios
        implicit_changes = [
            {
                "user_input": "Can you tell me a joke?",
                "expected_action": "switch_expert",
                "target_expert": "general_conversationalist",
                "tutor_response": "I notice you'd like to shift to something lighter! While I'm focused on tutoring, I can certainly share that learning should be fun. Would you like to continue with our lesson, or shall we wrap up here?",
                "session_management": "implicit_topic_change",
            },
            {
                "user_input": "What's the weather like today?",
                "expected_action": "clarify_intent",
                "tutor_response": "It seems like you might be ready for a break from our lesson. Would you like to continue working on these problems, or are you done studying for now?",
                "session_management": "implicit_topic_change",
            },
            {
                "user_input": "My mom is calling me for dinner.",
                "expected_action": "graceful_pause",
                "tutor_response": "Of course! Family time is important. We've made good progress today. When you're ready to continue studying, just let me know and we can pick up right where we left off.",
                "session_management": "natural_interruption",
            },
        ]

        # Add explicit endings
        for ending in explicit_endings:
            example = {
                "instruction": "Recognize when a student is explicitly ending the tutoring session and respond appropriately.",
                "input": ending["user_input"],
                "output": ending["tutor_response"],
                "session_action": ending["expected_action"],
                "session_management": ending["session_management"],
                "pedagogy_strategy": "session_closure",
                "affect_focus": "positive_closure",
            }
            session_end_examples.append(example)

        # Add implicit changes
        for change in implicit_changes:
            example = {
                "instruction": "Detect when a student is implicitly signaling they want to end or change the tutoring session.",
                "input": change["user_input"],
                "output": change["tutor_response"],
                "session_action": change["expected_action"],
                "session_management": change["session_management"],
                "pedagogy_strategy": "intent_clarification",
                "affect_focus": "transition_management",
            }
            session_end_examples.append(example)

        print(f"✅ Generated {len(session_end_examples)} session management examples")

        return session_end_examples

    def save_interruption_datasets(self, interruption_examples, session_examples):
        """Save interruption handling and session management datasets"""

        # Create output directory
        output_dir = self.fine_tuning_dir / "datasets/processed/interruption_handling"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save interruption handling dataset
        interruption_file = output_dir / "interruption_handling_training.jsonl"
        with open(interruption_file, "w") as f:
            for example in interruption_examples:
                f.write(json.dumps(example) + "\n")

        # Save session management dataset
        session_file = output_dir / "session_management_training.jsonl"
        with open(session_file, "w") as f:
            for example in session_examples:
                f.write(json.dumps(example) + "\n")

        # Save combined dataset
        combined_file = output_dir / "combined_interruption_session_training.jsonl"
        with open(combined_file, "w") as f:
            for example in interruption_examples + session_examples:
                f.write(json.dumps(example) + "\n")

        # Create technical integration guide
        integration_guide = {
            "interruption_token": "[USER_INTERRUPTION]",
            "purpose": "Technical marker for Application Controller to detect when user interrupts during TTS playback",
            "implementation": {
                "detection": "Monitor microphone during TTS playback",
                "action": "Immediately pause/stop TTS when user voice detected",
                "processing": "Send interrupted text + user input to model with [USER_INTERRUPTION] token",
            },
            "training_examples": len(interruption_examples),
            "session_management_examples": len(session_examples),
            "total_examples": len(interruption_examples) + len(session_examples),
            "file_locations": {
                "interruption_handling": str(interruption_file),
                "session_management": str(session_file),
                "combined_dataset": str(combined_file),
            },
        }

        guide_file = output_dir / "technical_integration_guide.json"
        with open(guide_file, "w") as f:
            json.dump(integration_guide, f, indent=2)

        print("\n📁 DATASETS SAVED:")
        print(f"📄 Interruption Handling: {len(interruption_examples)} examples")
        print(f"📄 Session Management: {len(session_examples)} examples")
        print(
            f"📄 Combined Dataset: {len(interruption_examples) + len(session_examples)} examples"
        )
        print(f"📄 Technical Guide: {guide_file}")

        return {
            "interruption_file": interruption_file,
            "session_file": session_file,
            "combined_file": combined_file,
            "guide_file": guide_file,
            "total_examples": len(interruption_examples) + len(session_examples),
        }


def main():
    """Generate interruption handling and session management training data"""

    generator = InterruptionTrainingGenerator()

    print("🎯 INTERRUPTION HANDLING & SESSION MANAGEMENT TRAINING DATA")
    print("=" * 70)
    print("Technical Solution: [USER_INTERRUPTION] token for Application Controller")
    print("AI Solution: Training models to handle interruptions gracefully")
    print("=" * 70)

    # Generate interruption handling data
    interruption_examples = generator.generate_interruption_training_data()

    # Generate session management data
    session_examples = generator.create_session_management_data()

    # Save datasets
    results = generator.save_interruption_datasets(
        interruption_examples, session_examples
    )

    print("\n🚀 TRAINING DATA READY FOR:")
    print("✅ Graceful interruption handling")
    print("✅ Session end detection")
    print("✅ Topic change management")
    print("✅ Technical integration with [USER_INTERRUPTION] token")

    print("\n📊 SUMMARY:")
    print(f"Total Training Examples: {results['total_examples']}")
    print(f"Combined Dataset: {results['combined_file']}")
    print(f"Technical Guide: {results['guide_file']}")


if __name__ == "__main__":
    main()
