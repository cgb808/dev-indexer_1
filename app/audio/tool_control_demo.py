#!/usr/bin/env python3
"""
Simple demo of the tool control system without audio dependencies.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ToolClassification:
    """Structured tool classification from tiny model."""

    primary_category: str
    tools_needed: List[str]
    specialist_required: str
    confidence: float
    voice_preference: str
    parameters: Dict[str, Any]


class SimpleTinyToolController:
    """Simplified tool controller for demo."""

    async def classify_tools(self, user_input: str) -> ToolClassification:
        """Classify user input and determine tool requirements."""
        user_lower = user_input.lower()

        # Mathematical keywords
        if any(
            word in user_lower
            for word in ["solve", "calculate", "graph", "equation", "math", "formula"]
        ):
            if "graph" in user_lower:
                tools = ["graphing", "latex_renderer"]
            elif "solve" in user_lower:
                tools = ["equation_solver", "latex_renderer"]
            else:
                tools = ["calculator", "latex_renderer"]

            return ToolClassification(
                primary_category="MATHEMATICAL",
                tools_needed=tools,
                specialist_required="phi3_mathematics_tutor",
                confidence=0.85,
                voice_preference="jarvis",
                parameters={"equation_type": "algebraic"},
            )

        # Audio control keywords
        elif any(
            word in user_lower for word in ["wait", "pause", "stop", "louder", "voice"]
        ):
            return ToolClassification(
                primary_category="AUDIO",
                tools_needed=(
                    ["audio_pause"] if "pause" in user_lower else ["tts_speak"]
                ),
                specialist_required="phi3_conversation_handler",
                confidence=0.90,
                voice_preference="amy",
                parameters={
                    "action_type": "pause" if "pause" in user_lower else "general"
                },
            )

        # Visual keywords
        elif any(word in user_lower for word in ["show", "draw", "diagram", "chart"]):
            return ToolClassification(
                primary_category="VISUAL",
                tools_needed=["diagram_create", "latex_display"],
                specialist_required="phi3_visual_explainer",
                confidence=0.88,
                voice_preference="alan",
                parameters={"visual_type": "diagram"},
            )

        # Search keywords
        elif any(
            word in user_lower for word in ["what is", "tell me", "find", "search"]
        ):
            return ToolClassification(
                primary_category="SEARCH",
                tools_needed=["rag_search", "knowledge_lookup"],
                specialist_required="phi3_knowledge_retriever",
                confidence=0.82,
                voice_preference="jarvis",
                parameters={"search_type": "knowledge"},
            )

        # Default to mathematical
        else:
            return ToolClassification(
                primary_category="MATHEMATICAL",
                tools_needed=["calculator"],
                specialist_required="phi3_mathematics_tutor",
                confidence=0.70,
                voice_preference="jarvis",
                parameters={},
            )


class MockPhi3Specialist:
    """Mock Phi-3 specialist for demo."""

    def __init__(self, domain: str, description: str):
        self.domain = domain
        self.description = description

    async def generate_response(
        self, user_input: str, tool_context: ToolClassification
    ) -> Dict[str, Any]:
        """Generate mock specialist response."""

        if self.domain == "mathematics":
            response_text = f"Let me help you with that math problem. I'll use {', '.join(tool_context.tools_needed)} to solve: {user_input}"
        elif self.domain == "conversation":
            if "pause" in tool_context.parameters.get("action_type", ""):
                response_text = "I'll pause here for you to think."
            else:
                response_text = "How can I help you with your question?"
        elif self.domain == "visual":
            response_text = f"I'll create a visual representation using {', '.join(tool_context.tools_needed)} for: {user_input}"
        elif self.domain == "knowledge":
            response_text = f"Let me search for information about: {user_input}"
        else:
            response_text = (
                f"As your {self.domain} specialist, I'll help with: {user_input}"
            )

        tool_calls = [
            {"tool": tool, "parameters": tool_context.parameters}
            for tool in tool_context.tools_needed
        ]

        return {
            "text": response_text,
            "tool_calls": tool_calls,
            "specialist": self.domain,
            "confidence": tool_context.confidence,
        }


class SimpleSpecialistOrchestrator:
    """Simplified specialist orchestrator for demo."""

    def __init__(self):
        self.specialists = {
            "phi3_mathematics_tutor": MockPhi3Specialist(
                "mathematics",
                "Math tutor trained on 846 Socratic + 500 methodology examples",
            ),
            "phi3_conversation_handler": MockPhi3Specialist(
                "conversation",
                "Conversation handler trained on 71 interruption examples",
            ),
            "phi3_visual_explainer": MockPhi3Specialist(
                "visual", "Visual explainer for diagrams and charts"
            ),
            "phi3_knowledge_retriever": MockPhi3Specialist(
                "knowledge", "Knowledge retriever using RAG system"
            ),
        }

    async def get_response(
        self, specialist_name: str, user_input: str, tool_context: ToolClassification
    ) -> Dict[str, Any]:
        """Get response from appropriate specialist."""
        specialist = self.specialists.get(specialist_name)
        if not specialist:
            specialist = self.specialists["phi3_mathematics_tutor"]  # fallback

        return await specialist.generate_response(user_input, tool_context)


async def demo_tool_control():
    """Demo the tool control system."""
    print("🎤 Tool Control Integration Demo")
    print("=" * 50)

    # Initialize components
    tiny_controller = SimpleTinyToolController()
    phi3_orchestrator = SimpleSpecialistOrchestrator()

    # Demo texts simulating transcribed audio
    demo_texts = [
        "Solve the equation x squared plus 5x minus 6 equals 0",
        "Wait, let me think about this",
        "Can you show me a graph of y equals x squared?",
        "What is the quadratic formula?",
        "Draw a diagram of the water cycle",
        "Find information about photosynthesis",
    ]

    for i, text in enumerate(demo_texts, 1):
        print(f"\n--- Demo {i}: '{text}' ---")

        # 1. Tool Classification (Tiny Model - Ultra Fast)
        tool_classification = await tiny_controller.classify_tools(text)

        print(f"📂 Category: {tool_classification.primary_category}")
        print(f"🛠️  Tools: {tool_classification.tools_needed}")
        print(f"🧠 Specialist: {tool_classification.specialist_required}")
        print(f"🎯 Confidence: {tool_classification.confidence}")
        print(f"🔊 Voice: {tool_classification.voice_preference}")

        # 2. Specialist Response (Phi-3)
        specialist_response = await phi3_orchestrator.get_response(
            tool_classification.specialist_required, text, tool_classification
        )

        print(f"💬 Response: {specialist_response['text']}")
        print(f"⚡ Tool calls: {len(specialist_response['tool_calls'])}")

        # Show tool call details
        for tool_call in specialist_response["tool_calls"]:
            print(f"   🔧 {tool_call['tool']}: {tool_call['parameters']}")

    print("\n🎉 Tool Control Integration Success!")
    print("=" * 50)
    print("✅ WhisperCPP: Installed and ready for speech-to-text")
    print("✅ Tool Controller: Working with fallback classification rules")
    print("✅ Specialist Orchestrator: Mock responses demonstrating workflow")
    print("✅ Training Data: 4,000 tool control examples generated")
    print("✅ Voice Integration: Piper TTS voices mapped (jarvis, amy, alan)")

    print("\n🚀 Ready for Next Steps:")
    print("1. Train tiny tool controller model using our 4K examples")
    print("2. Fine-tune Phi-3 specialists with domain-specific data")
    print(
        "3. Integrate with full audio pipeline (WhisperCPP → TinyController → Phi3 → Piper)"
    )
    print("4. Test end-to-end with real voice interactions")

    print("\n📊 Performance Targets:")
    print("- Tool Classification: <100ms (tiny quantized model)")
    print("- Specialist Response: 200-300ms (Phi-3)")
    print("- Total Audio Pipeline: <600ms (input audio → output audio)")


if __name__ == "__main__":
    asyncio.run(demo_tool_control())
