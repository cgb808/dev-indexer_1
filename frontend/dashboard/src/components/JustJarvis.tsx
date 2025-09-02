import { BoltIcon, CpuChipIcon, CubeIcon, MicrophoneIcon, SparklesIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useState } from 'react';

interface JarvisModel {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  capabilities: string[];
  status: 'active' | 'standby' | 'training';
  emoji: string;
}

const jarvisModels: JarvisModel[] = [
  {
    id: 'gemma-2b',
    name: 'Gemma 2B',
    description: 'Fast and efficient text generation',
    icon: CpuChipIcon,
    color: '#10b981',
    capabilities: ['Text Generation', 'Code Analysis', 'Quick Responses'],
    status: 'active',
    emoji: '🤖',
  },
  {
    id: 'phi-3',
    name: 'Phi-3',
    description: 'Advanced reasoning and mathematics',
    icon: CubeIcon,
    color: '#8b5cf6',
    capabilities: ['Mathematics', 'Reasoning', 'Problem Solving'],
    status: 'active',
    emoji: '🧠',
  },
  {
    id: 'mistral-7b',
    name: 'Mistral 7B',
    description: 'Powerful open-source language model',
    icon: SparklesIcon,
    color: '#f59e0b',
    capabilities: ['General Knowledge', 'Creative Writing', 'Analysis'],
    status: 'standby',
    emoji: '⚡',
  },
  {
    id: 'tiny-model',
    name: 'Tiny Model',
    description: 'Lightweight model for tooling tasks',
    icon: BoltIcon,
    color: '#3b82f6',
    capabilities: ['Tool Classification', 'Quick Actions', 'Automation'],
    status: 'active',
    emoji: '🎯',
  },
  {
    id: 'bge-small',
    name: 'BGE Small',
    description: 'Optimized for embeddings and retrieval',
    icon: CpuChipIcon,
    color: '#ef4444',
    capabilities: ['Embeddings', 'Retrieval', 'Search'],
    status: 'standby',
    emoji: '🔍',
  },
];

export const JustJarvis: React.FC = () => {
  const [activeModel, setActiveModel] = useState('gemma-2b');
  const [isListening, setIsListening] = useState(false);
  const [currentCommand, setCurrentCommand] = useState('');
  const [systemStatus, setSystemStatus] = useState('Ready');
  const [tokensPerSecond, setTokensPerSecond] = useState(0);
  const [cpuUsage, setCpuUsage] = useState(23);
  const [memoryUsage, setMemoryUsage] = useState(15);
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    // Simulate system heartbeat
    const interval = setInterval(() => {
      setSystemStatus((prev) => (prev === 'Ready' ? 'Active' : prev === 'Active' ? 'Processing' : 'Ready'));
      setTokensPerSecond(Math.random() * 30 + 10);
      setCpuUsage(Math.random() * 20 + 15);
      setMemoryUsage(Math.random() * 10 + 10);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleModelSelect = (modelId: string) => {
    setActiveModel(modelId);
    setCurrentCommand(`Switching to ${jarvisModels.find((m) => m.id === modelId)?.name}...`);
    setTimeout(() => setCurrentCommand(''), 2000);
  };

  const toggleListening = () => {
    setIsListening(!isListening);
    setCurrentCommand(isListening ? 'Listening stopped' : 'Listening for commands...');
  };

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'standby':
        return '#f59e0b';
      case 'training':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const currentTheme = {
    background: isDarkMode ? '#0f0f0f' : '#F5F5F5',
    text: isDarkMode ? '#E1E1E1' : '#000000',
    textSecondary: isDarkMode ? '#888' : '#555',
    card: isDarkMode ? '#1E1E1E' : '#FFFFFF',
    border: isDarkMode ? '#333' : '#DDD',
    primary: '#007AFF',
    green: '#34C759',
    red: '#FF3B30',
    orange: '#FF9500',
  };

  const activeModelData = jarvisModels.find((m) => m.id === activeModel);

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: currentTheme.background,
        color: currentTheme.text,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      }}
    >
      {/* Header */}
      <div style={{ backgroundColor: currentTheme.card, borderBottom: `1px solid ${currentTheme.border}` }}>
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'linear-gradient(135deg, #007AFF, #8b5cf6)' }}
              >
                <span className="text-xl font-bold" style={{ color: 'white' }}>
                  J
                </span>
              </div>
              <div>
                <h1
                  className="text-2xl font-bold"
                  style={{
                    background: 'linear-gradient(135deg, #007AFF, #8b5cf6)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  JustJarvis
                </h1>
                <p style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>AI Assistant Control Center</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getStatusColor(systemStatus.toLowerCase()) }}
                ></div>
                <span style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>{systemStatus}</span>
              </div>
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg transition-colors"
                style={{ color: currentTheme.text }}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
              <button
                onClick={toggleListening}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-300"
                style={{
                  backgroundColor: isListening ? '#dc2626' : '#007AFF',
                  color: 'white',
                }}
              >
                <MicrophoneIcon className="w-5 h-5" />
                <span>{isListening ? 'Stop' : 'Listen'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Model Display */}
          <div className="lg:col-span-2">
            <div
              style={{
                backgroundColor: currentTheme.card,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '12px',
                padding: '24px',
              }}
            >
              <h2 style={{ color: currentTheme.text, fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
                Active Assistant
              </h2>
              {activeModelData && (
                <div className="flex items-center space-x-4 mb-6">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-2xl"
                    style={{ backgroundColor: `${activeModelData.color}20` }}
                  >
                    {activeModelData.emoji}
                  </div>
                  <div>
                    <h3 style={{ color: currentTheme.text, fontSize: '20px', fontWeight: '600' }}>
                      {activeModelData.name}
                    </h3>
                    <p style={{ color: currentTheme.textSecondary }}>{activeModelData.description}</p>
                  </div>
                </div>
              )}

              {/* Capabilities */}
              <div className="mb-6">
                <h4
                  style={{
                    color: currentTheme.textSecondary,
                    fontSize: '14px',
                    fontWeight: '500',
                    marginBottom: '12px',
                  }}
                >
                  Capabilities
                </h4>
                <div className="flex flex-wrap gap-2">
                  {activeModelData?.capabilities.map((capability, index) => (
                    <span
                      key={index}
                      style={{
                        backgroundColor: `${activeModelData?.color}20`,
                        color: activeModelData?.color,
                        padding: '6px 12px',
                        borderRadius: '20px',
                        fontSize: '14px',
                        border: `1px solid ${activeModelData?.color}40`,
                      }}
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </div>

              {/* Current Command */}
              {currentCommand && (
                <div
                  style={{
                    backgroundColor: `${currentTheme.card}80`,
                    border: `1px solid ${currentTheme.border}`,
                    borderRadius: '8px',
                    padding: '16px',
                  }}
                >
                  <p style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>{currentCommand}</p>
                </div>
              )}
            </div>
          </div>

          {/* Model Selection */}
          <div className="space-y-4">
            <h2 style={{ color: currentTheme.text, fontSize: '20px', fontWeight: '600' }}>Available Models</h2>
            {jarvisModels.map((model) => (
              <button
                key={model.id}
                onClick={() => handleModelSelect(model.id)}
                className="w-full p-4 rounded-xl border transition-all duration-300 text-left"
                style={{
                  backgroundColor: activeModel === model.id ? `${model.color}20` : currentTheme.card,
                  border: `1px solid ${activeModel === model.id ? model.color : currentTheme.border}`,
                  color: currentTheme.text,
                }}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                    style={{ backgroundColor: `${model.color}20` }}
                  >
                    {model.emoji}
                  </div>
                  <div className="flex-1">
                    <h3 style={{ color: currentTheme.text, fontWeight: '500' }}>{model.name}</h3>
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: getStatusColor(model.status) }}
                      ></div>
                      <span
                        style={{ color: currentTheme.textSecondary, fontSize: '12px', textTransform: 'capitalize' }}
                      >
                        {model.status}
                      </span>
                    </div>
                  </div>
                </div>
                <p style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>{model.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* System Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            style={{
              backgroundColor: currentTheme.card,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '12px',
              padding: '24px',
            }}
          >
            <div className="flex items-center space-x-3 mb-4">
              <span className="text-xl">🖥️</span>
              <h3 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '500' }}>CPU Usage</h3>
            </div>
            <div style={{ color: currentTheme.primary, fontSize: '30px', fontWeight: 'bold' }}>
              {cpuUsage.toFixed(0)}%
            </div>
            <div style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>4 cores active</div>
            <div className="mt-3">
              <div style={{ width: '100%', height: '8px', backgroundColor: currentTheme.border, borderRadius: '4px' }}>
                <div
                  style={{
                    width: `${cpuUsage}%`,
                    height: '8px',
                    backgroundColor: currentTheme.primary,
                    borderRadius: '4px',
                  }}
                />
              </div>
            </div>
          </div>

          <div
            style={{
              backgroundColor: currentTheme.card,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '12px',
              padding: '24px',
            }}
          >
            <div className="flex items-center space-x-3 mb-4">
              <span className="text-xl">🧠</span>
              <h3 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '500' }}>Memory</h3>
            </div>
            <div style={{ color: currentTheme.green, fontSize: '30px', fontWeight: 'bold' }}>
              {memoryUsage.toFixed(1)}GB
            </div>
            <div style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>of 8GB used</div>
            <div className="mt-3">
              <div style={{ width: '100%', height: '8px', backgroundColor: currentTheme.border, borderRadius: '4px' }}>
                <div
                  style={{
                    width: `${(memoryUsage / 8) * 100}%`,
                    height: '8px',
                    backgroundColor: currentTheme.green,
                    borderRadius: '4px',
                  }}
                />
              </div>
            </div>
          </div>

          <div
            style={{
              backgroundColor: currentTheme.card,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '12px',
              padding: '24px',
            }}
          >
            <div className="flex items-center space-x-3 mb-4">
              <span className="text-xl">⚡</span>
              <h3 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '500' }}>Tokens/sec</h3>
            </div>
            <div style={{ color: '#8b5cf6', fontSize: '30px', fontWeight: 'bold' }}>{tokensPerSecond.toFixed(1)}</div>
            <div style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>processing speed</div>
            <div className="mt-3">
              <div style={{ width: '100%', height: '8px', backgroundColor: currentTheme.border, borderRadius: '4px' }}>
                <div
                  style={{
                    width: `${Math.min(tokensPerSecond * 3, 100)}%`,
                    height: '8px',
                    backgroundColor: '#8b5cf6',
                    borderRadius: '4px',
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
