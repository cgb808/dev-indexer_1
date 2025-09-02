# Tool Control Architecture: Tiny Model + Phi-3 Specialization
*Date: August 30, 2025*

## 🎯 Overview: Dual-Model Tool Control System

### **Architecture Design**
```
User Input → WhisperCPP STT → Tiny Tool Controller → Tool Selection → Phi-3 Specialist → Action Execution
                                    ↓
                            Tool Classification & Routing
                                    ↓
                               Piper TTS Output
```

## 🧠 Dual-Model Specialization

### **Model 1: Tiny Quantized Tool Controller (Gemma-2B or Phi-3-Mini)**
- **Purpose**: Ultra-fast tool classification and routing
- **Size**: ~500MB-1GB quantized (Q4_K_M)
- **Latency**: <100ms inference
- **Specialization**: Tool selection, parameter extraction, workflow orchestration

### **Model 2: Phi-3 Domain Specialist (3.8B)**
- **Purpose**: Domain-specific expert reasoning
- **Size**: ~2-3GB quantized
- **Latency**: 200-500ms inference  
- **Specialization**: Mathematics, tutoring, explanations using our training data

## 🛠️ Tool Control Framework

### **Tool Categories & Actions**

```python
TOOL_CATEGORIES = {
    "MATHEMATICAL": {
        "tools": ["calculator", "graphing", "latex_renderer", "equation_solver"],
        "specialist": "phi3_mathematics_tutor",
        "training_data": "846_socratic + 500_methodology"
    },
    "VISUAL": {
        "tools": ["canvas_draw", "diagram_create", "chart_generate", "latex_display"],
        "specialist": "phi3_visual_explainer", 
        "training_data": "visual_explanation_dataset"
    },
    "AUDIO": {
        "tools": ["tts_speak", "voice_change", "audio_pause", "audio_resume"],
        "specialist": "phi3_conversation_handler",
        "training_data": "71_interruption + conversation_flow"
    },
    "SEARCH": {
        "tools": ["rag_search", "vector_query", "context_retrieve", "memory_access"],
        "specialist": "phi3_knowledge_retriever",
        "training_data": "knowledge_synthesis_dataset"
    },
    "WORKFLOW": {
        "tools": ["task_sequence", "multi_step", "context_switch", "session_manage"],
        "specialist": "phi3_workflow_orchestrator",
        "training_data": "workflow_coordination_dataset"
    }
}
```

## 🔧 Technical Implementation

### **1. Tiny Tool Controller Model**

**Training Objective**: Lightning-fast tool classification
```python
# Input format for tiny model training
{
    "user_input": "Can you graph the function y = x^2 + 2x - 3?",
    "tool_classification": {
        "primary_category": "MATHEMATICAL",
        "tools_needed": ["graphing", "latex_renderer"],
        "specialist_required": "phi3_mathematics_tutor",
        "confidence": 0.95,
        "parameters": {
            "function": "y = x^2 + 2x - 3",
            "visualization_type": "graph"
        }
    }
}

{
    "user_input": "Wait, let me think about this",
    "tool_classification": {
        "primary_category": "AUDIO", 
        "tools_needed": ["tts_pause"],
        "specialist_required": "phi3_conversation_handler",
        "confidence": 0.99,
        "parameters": {
            "interruption_type": "user_pause",
            "action": "graceful_pause"
        }
    }
}
```

### **2. Phi-3 Specialist Integration**

**Enhanced with Tool Awareness**:
```python
# Phi-3 receives tool context + domain expertise
{
    "system": "You are a mathematics tutor with access to graphing and LaTeX tools.",
    "user_input": "Can you graph the function y = x^2 + 2x - 3?",
    "available_tools": ["graphing", "latex_renderer"],
    "tool_context": {
        "function": "y = x^2 + 2x - 3",
        "visualization_type": "graph"
    },
    "expected_response": {
        "explanation": "Let's analyze this quadratic function...",
        "tool_calls": [
            {"tool": "latex_renderer", "content": "y = x^2 + 2x - 3"},
            {"tool": "graphing", "parameters": {"function": "x^2 + 2x - 3", "range": [-5, 5]}}
        ]
    }
}
```

## 📊 Current Infrastructure Integration

### **Existing Assets → Tool Control**

| **Component** | **Current Status** | **Tool Control Role** | **Integration** |
|---------------|-------------------|----------------------|-----------------|
| **WhisperCPP** | ✅ Operational | Speech input capture | Raw audio → text for tiny model |
| **Piper TTS** | ✅ Multi-voice | Speech output | Tool-triggered TTS with voice selection |
| **RAG System** | ✅ pgvector operational | Context retrieval tool | Tool-aware knowledge searches |
| **Leonardo** | ✅ Mistral 7B | High-level orchestrator | Delegates to tiny controller for tools |
| **Visual Framework** | ✅ Canvas/LaTeX | Rendering tools | Tool-controlled visual generation |

### **Enhanced Audio Pipeline with Tool Control**

```python
class ToolAwareAudioPipeline:
    def __init__(self):
        self.whisper = WhisperCPPTranscriber()
        self.tiny_controller = TinyToolController()  # New!
        self.phi3_specialists = {
            'mathematics': Phi3MathTutor(),
            'conversation': Phi3ConversationHandler(),
            'visual': Phi3VisualExplainer()
        }
        self.piper = PiperTTSEngine()
        self.tools = ToolExecutor()
        
    async def process_audio_input(self, audio_file):
        # 1. Speech to Text
        text = await self.whisper.transcribe(audio_file)
        
        # 2. Tiny Model: Tool Classification (Ultra-fast)
        tool_plan = await self.tiny_controller.classify(text)
        
        # 3. Phi-3 Specialist: Domain Expertise
        specialist = self.phi3_specialists[tool_plan.category]
        response = await specialist.generate(text, tool_plan.context)
        
        # 4. Tool Execution
        tool_results = await self.tools.execute(response.tool_calls)
        
        # 5. Text to Speech with Voice Selection
        audio_output = await self.piper.synthesize(
            response.text, 
            voice=tool_plan.voice_preference
        )
        
        return {
            'audio': audio_output,
            'visual': tool_results.visual_outputs,
            'text': response.text
        }
```

## 🚀 Implementation Roadmap

### **Phase 1: Tiny Tool Controller (Week 1-2)**

1. **Data Generation**: Create 5,000+ tool classification examples
```bash
# Generate tool control training data
python scripts/generate_tool_control_dataset.py \
    --output fine_tuning/datasets/tool_control/ \
    --examples 5000 \
    --categories mathematical,visual,audio,search,workflow
```

2. **Model Selection & Quantization**: 
   - Base model: Gemma-2B or Phi-3-Mini
   - Quantization: Q4_K_M for speed
   - Target size: <1GB

3. **Fine-tuning Pipeline**:
```bash
# Fine-tune tiny controller
python scripts/finetune_tool_controller.py \
    --model microsoft/Phi-3-mini-4k-instruct \
    --dataset fine_tuning/datasets/tool_control/ \
    --output models/tiny_tool_controller/ \
    --quantize Q4_K_M
```

### **Phase 2: Phi-3 Specialist Enhancement (Week 2-3)**

1. **Tool-Aware Training**: Enhance existing Phi-3 models with tool context
```python
# Extend our existing training data with tool awareness
enhanced_training = {
    "mathematics_tutor": "846_socratic + 500_methodology + tool_context",
    "conversation_handler": "71_interruption + tool_control",
    "visual_explainer": "new_visual_dataset + tool_integration"
}
```

2. **Integration Training**: Train Phi-3 models to work with tool outputs

### **Phase 3: Production Integration (Week 3-4)**

1. **Audio Pipeline Enhancement**: Integrate tiny controller with existing WhisperCPP/Piper
2. **Performance Optimization**: <100ms tool classification, <500ms full response
3. **Tool Execution Framework**: Connect to existing visual/mathematical tools

## 🎯 Expected Performance

### **Speed Benchmarks**
- **Total Latency**: <600ms (audio input → audio output)
  - WhisperCPP STT: ~100ms
  - Tiny Tool Controller: <100ms 
  - Phi-3 Specialist: ~200-300ms
  - Tool Execution: ~50-100ms
  - Piper TTS: ~100ms

### **Accuracy Targets**
- **Tool Classification**: >95% accuracy
- **Parameter Extraction**: >90% accuracy  
- **Specialist Routing**: >98% accuracy

## 💎 Unique Advantages

### **Why This Architecture Excels**

1. **Ultra-Fast Response**: Tiny model handles immediate classification
2. **Expert Quality**: Phi-3 provides domain expertise using our specialized training
3. **Tool Integration**: Seamless visual/audio/mathematical tool coordination
4. **Scalable**: Add new tools without retraining large models
5. **Efficient**: Minimal compute overhead for tool control layer

### **Real-World Scenario**
```
Student: "Can you show me how to solve x² + 4x = 12 and graph it?"

1. WhisperCPP: Audio → "Can you show me how to solve x² + 4x = 12 and graph it?"
2. Tiny Controller: 85ms → {category: "MATHEMATICAL", tools: ["equation_solver", "graphing", "latex"], specialist: "phi3_mathematics_tutor"}
3. Phi-3 Math Tutor: 250ms → Generates step-by-step solution with tool calls
4. Tool Execution: 75ms → Solves equation, renders LaTeX, creates graph
5. Piper TTS: 100ms → "Let's solve this step by step. First, I'll rearrange the equation..."

Total: ~510ms for complete mathematical tutoring with visual aids
```

---

*This dual-model architecture provides the perfect balance of speed and intelligence, leveraging our existing infrastructure while adding lightning-fast tool control capabilities.*
