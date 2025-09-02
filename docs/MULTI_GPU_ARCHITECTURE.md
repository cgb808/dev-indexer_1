# Multi-GPU AI Architecture

## Overview
This document describes the multi-GPU setup for the ZenGlow RAG infrastructure, optimizing different AI workloads across specialized hardware.

## Hardware Configuration

### Primary GPU: RTX 3060 Ti (8GB VRAM) - "Leonardo"
- **Model**: Mistral 7B Q5_K_M
- **Personality**: Leonardo - The analytical thinker and problem solver
- **Role**: Primary reasoning and analysis bot
- **Memory Usage**: ~6.5GB (optimal for Q5_K_M quantization)
- **Workload**: Complex reasoning, document analysis, knowledge synthesis
- **Avatar**: Text-based interface (future: sophisticated analytical visualization)
- **Voice**: Analytical British TTS with Piper, Whisper speech recognition
- **Audio Capabilities**: `/leonardo/speak`, `/leonardo/think`, `/leonardo/listen`

### Secondary GPU: GTX 1660 Super (6GB VRAM) - "Jarvis"
- **Model**: Phi3 quantized (Q4_0)
- **Personality**: Jarvis - The responsive conversational assistant
- **Role**: Chat interface and TTS processing
- **Memory Usage**: ~3.5GB (efficient quantized model)
- **Workload**: Conversational responses, text-to-speech, real-time chat
- **Avatar**: Mira - 3D visual avatar with facial animation and lip sync
- **Voice**: Conversational TTS with multiple voice options

## Architecture Benefits

### 1. Workload Specialization
- **Reasoning (Leonardo/Mistral)**: Handles complex analytical tasks requiring larger context
- **Conversation (Jarvis/Phi3)**: Manages real-time chat and audio generation

### 2. Performance Optimization
- **Parallel Processing**: Both GPUs can work simultaneously
- **Resource Efficiency**: Each GPU optimized for its specific task
- **Reduced Latency**: TTS on dedicated GPU prevents interference with reasoning

### 3. Scalability
- **Model Isolation**: Issues with one model don't affect the other
- **Independent Scaling**: Can upgrade or replace GPUs independently
- **Future Expansion**: Easy to add more specialized models

## Implementation Details

### Ollama Configuration
```bash
# Primary GPU (RTX 3060 Ti) - Mistral 7B
ollama pull mistral:7b-instruct-q5_k_m

# Secondary GPU (GTX 1660 Super) - Phi3
ollama pull phi3:3.8b-mini-4k-instruct-q4_0
```

### Docker Compose Updates
```yaml
services:
  ollama:
    environment:
      - CUDA_VISIBLE_DEVICES=0,1  # Both GPUs visible
      - OLLAMA_GPU_LAYERS=35      # Mistral layers on primary
      - OLLAMA_PHI3_GPU=1         # Phi3 on secondary GPU
```

### Backend Routing
- **Heavy reasoning queries** → RTX 3060 Ti (Leonardo/Mistral)
- **Chat interface requests** → GTX 1660 Super (Jarvis/Phi3)
- **TTS generation** → GTX 1660 Super (Jarvis audio pipeline)

## Model Specifications

### Mistral 7B Q5_K_M
- **Parameters**: 7 billion
- **Quantization**: Q5_K_M (balanced quality/size)
- **Context Length**: 8K tokens
- **Strengths**: Reasoning, analysis, code generation

### Phi3 Q4_0
- **Parameters**: 3.8 billion
- **Quantization**: Q4_0 (optimized for speed)
- **Context Length**: 4K tokens
- **Strengths**: Conversational AI, quick responses, TTS integration

## Monitoring and Maintenance

### GPU Memory Monitoring
```bash
# Check GPU utilization
nvidia-smi

# Monitor specific GPU
nvidia-smi -i 0  # RTX 3060 Ti
nvidia-smi -i 1  # GTX 1660 Super
```

### Model Health Checks
```bash
# Test Leonardo (Mistral) on primary GPU
curl -X POST "http://localhost:11434/api/chat" \
  -d '{"model": "mistral:7b-instruct-q5_k_m", "messages": [{"role": "user", "content": "Leonardo, analyze this complex problem"}]}'

# Test Jarvis (Phi3) on secondary GPU
curl -X POST "http://localhost:11434/api/chat" \
  -d '{"model": "phi3:3.8b-mini-4k-instruct-q4_0", "messages": [{"role": "user", "content": "Jarvis, how can I help you today?"}]}'
```

## Future Enhancements

### Planned Improvements
1. **Dynamic Load Balancing**: Route requests based on current GPU utilization
2. **Model Warm-up**: Keep both models loaded for instant responses
3. **Fallback Logic**: Automatic failover if one GPU becomes unavailable
4. **Performance Metrics**: Detailed logging of response times per GPU

### Potential Expansions
- **Third GPU**: Add embedding model for faster vector generation
- **Model Variants**: Deploy different quantization levels based on use case
- **Specialized Models**: Add domain-specific models (code, math, creative writing)

## Troubleshooting

### Common Issues
1. **GPU Memory Exhaustion**: Monitor with `nvidia-smi`, adjust model sizes
2. **Model Loading Failures**: Check CUDA drivers and Ollama configuration
3. **Routing Problems**: Verify backend model selection logic

### Performance Tuning
- **Batch Sizes**: Optimize based on available VRAM
- **Concurrent Requests**: Limit simultaneous requests per GPU
- **Model Unloading**: Configure aggressive unloading for memory management
