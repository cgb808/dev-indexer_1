// ZenGlow API Integration Stub
// This provides mock endpoints for development without CUDA server

export interface ModelResponse {
  model: string;
  response: string;
  confidence: number;
  processing_time: number;
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  model?: string;
}

class ZenGlowAPI {
  private baseUrl = 'http://localhost:8000'; // FastAPI backend

  async sendMessage(message: string, model: string): Promise<ModelResponse> {
    // Mock response for development
    const responses = {
      'Gemma 2B': `Gemma 2B response to: "${message}". This is a fast, efficient generation.`,
      'Phi-3': `Phi-3 analysis of: "${message}". Providing detailed reasoning and context.`,
      'Mistral 7B': `Mistral 7B insight on: "${message}". Drawing from extensive knowledge base.`,
      'Tiny Model': `Tiny Model classification: "${message}". Optimized for quick tool selection.`,
    };

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1000));

    return {
      model,
      response: responses[model as keyof typeof responses] || `Response from ${model}`,
      confidence: 0.85 + Math.random() * 0.14, // 0.85-0.99
      processing_time: 200 + Math.random() * 800, // 200-1000ms
    };
  }

  async getAvailableModels(): Promise<string[]> {
    // Return models that match our frontend
    return ['Gemma 2B', 'Phi-3', 'Mistral 7B', 'Tiny Model', 'BGE Small'];
  }

  async getModelStatus(model: string): Promise<{ loaded: boolean; memory_usage?: number }> {
    // Mock status - in real implementation, this would check actual model status
    return {
      loaded: true,
      memory_usage: Math.floor(Math.random() * 2000) + 500, // 500-2500 MB
    };
  }

  async getSystemHealth(): Promise<{
    cpu_usage: number;
    memory_usage: number;
    gpu_available: boolean;
    models_loaded: number;
  }> {
    return {
      cpu_usage: Math.floor(Math.random() * 30) + 10, // 10-40%
      memory_usage: Math.floor(Math.random() * 40) + 20, // 20-60%
      gpu_available: false, // Since user mentioned no CUDA server
      models_loaded: 5,
    };
  }
}

// Export singleton instance
export const zenGlowAPI = new ZenGlowAPI();

// Helper functions for integration
export const formatModelResponse = (response: ModelResponse): ChatMessage => ({
  id: Date.now().toString(),
  text: response.response,
  sender: 'assistant',
  timestamp: new Date(),
  model: response.model,
});

export const createUserMessage = (text: string): ChatMessage => ({
  id: Date.now().toString(),
  text,
  sender: 'user',
  timestamp: new Date(),
});
