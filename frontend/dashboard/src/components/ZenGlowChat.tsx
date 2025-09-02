import React, { useEffect, useRef, useState } from 'react';
import { createUserMessage, formatModelResponse, zenGlowAPI, type ChatMessage } from '../lib/api';
import { ModelRouter } from './ModelRouter';

interface Theme {
  background: string;
  text: string;
  textSecondary: string;
  card: string;
  border: string;
  primary: string;
  placeholder: string;
  green: string;
  red: string;
  orange: string;
}

const theme: Theme = {
  background: '#121212',
  text: '#E1E1E1',
  textSecondary: '#888',
  card: '#1E1E1E',
  border: '#333',
  primary: '#007AFF',
  placeholder: '#888',
  green: '#34C759',
  red: '#FF3B30',
  orange: '#FF9500',
};

export const ZenGlowChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: "Hello! I'm ZenGlow, your AI assistant. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date(),
      model: 'Gemma 2B',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentModel, setCurrentModel] = useState('Gemma 2B');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isDevPanelVisible, setDevPanelVisible] = useState(true);
  const [tokensPerSecond, setTokensPerSecond] = useState(0);
  const scrollViewRef = useRef<HTMLDivElement>(null);

  // Simulate live metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setTokensPerSecond(Math.random() * 30 + 10);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage = createUserMessage(message);
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Call API with current model
      const response = await zenGlowAPI.sendMessage(message, currentModel);

      // Format and add AI response
      const aiMessage = formatModelResponse(response);
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('API Error:', error);
      // Fallback response
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        text: `Sorry, I encountered an error. Please try again. (Model: ${currentModel})`,
        sender: 'assistant',
        timestamp: new Date(),
        model: currentModel,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleModelChange = (model: string) => {
    setCurrentModel(model);
    // Add system message about model change
    const systemMessage: ChatMessage = {
      id: Date.now().toString(),
      text: `Switched to ${model} model`,
      sender: 'assistant',
      timestamp: new Date(),
      model: 'System',
    };
    setMessages((prev) => [...prev, systemMessage]);
  };

  const toggleTheme = () => setIsDarkMode(!isDarkMode);
  const toggleDevPanel = () => setDevPanelVisible(!isDevPanelVisible);

  const currentTheme = {
    ...theme,
    background: isDarkMode ? '#121212' : '#F5F5F5',
    text: isDarkMode ? '#E1E1E1' : '#000000',
    textSecondary: isDarkMode ? '#888' : '#555',
    card: isDarkMode ? '#1E1E1E' : '#FFFFFF',
    border: isDarkMode ? '#333' : '#DDD',
    placeholder: isDarkMode ? '#888' : '#AAA',
  };

  return (
    <div
      className="h-screen flex"
      style={{
        backgroundColor: currentTheme.background,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      }}
    >
      {/* Model Router Sidebar */}
      <div
        className="w-80 flex flex-col"
        style={{ backgroundColor: currentTheme.card, borderRight: `1px solid ${currentTheme.border}` }}
      >
        <div className="p-4" style={{ borderBottom: `1px solid ${currentTheme.border}` }}>
          <h2 className="text-lg font-semibold" style={{ color: currentTheme.text }}>
            AI Models
          </h2>
          <p className="text-sm" style={{ color: currentTheme.textSecondary }}>
            Select your assistant
          </p>
        </div>
        <div className="flex-1 overflow-hidden">
          <ModelRouter onModelChange={handleModelChange} />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div
          className="flex justify-between items-center px-4 py-3"
          style={{ backgroundColor: currentTheme.card, borderBottom: `1px solid ${currentTheme.border}` }}
        >
          <h1 className="text-lg font-bold" style={{ color: currentTheme.text }}>
            ZenGlow AI Assistant
          </h1>
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-opacity-20 transition-colors"
              style={{ color: currentTheme.text }}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
            <button
              onClick={toggleDevPanel}
              className="p-2 rounded-lg hover:bg-opacity-20 transition-colors"
              style={{ color: currentTheme.text }}
            >
              {`</>`}
            </button>
          </div>
        </div>

        {/* Chat Content */}
        <div className="flex-1 flex">
          {/* Messages Area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div
              ref={scrollViewRef}
              className="flex-1 overflow-y-auto p-4 space-y-4"
              style={{ backgroundColor: isDarkMode ? '#0f0f0f' : '#fafafa' }}
            >
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                      message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-xs opacity-70">{message.timestamp.toLocaleTimeString()}</span>
                      {message.model && <span className="text-xs opacity-70 ml-2">{message.model}</span>}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start mb-4">
                  <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-2xl">
                    <p className="text-sm">ZenGlow is typing...</p>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div
              className="p-4"
              style={{ backgroundColor: currentTheme.card, borderTop: `1px solid ${currentTheme.border}` }}
            >
              <div className="flex items-center space-x-2">
                <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
                  <span className="text-lg">📎</span>
                </button>
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend(inputMessage)}
                  placeholder={`Ask ${currentModel} anything...`}
                  className="flex-1 px-4 py-2 rounded-full border focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{
                    backgroundColor: currentTheme.background,
                    color: currentTheme.text,
                    borderColor: currentTheme.border,
                  }}
                />
                <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
                  <span className="text-lg">🎤</span>
                </button>
                <button
                  onClick={() => handleSend(inputMessage)}
                  disabled={!inputMessage.trim()}
                  className="px-6 py-2 rounded-full font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ backgroundColor: currentTheme.primary, color: 'white' }}
                >
                  Send
                </button>
              </div>
            </div>
          </div>

          {/* Dev Panel */}
          {isDevPanelVisible && (
            <div
              className="w-72 p-4 overflow-y-auto"
              style={{ backgroundColor: currentTheme.card, borderLeft: `1px solid ${currentTheme.border}` }}
            >
              {/* Live Metrics */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold" style={{ color: currentTheme.text }}>
                    Live Metrics
                  </h3>
                  <span style={{ color: currentTheme.text }}>▼</span>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl font-light" style={{ color: currentTheme.text }}>
                    {tokensPerSecond.toFixed(1)}{' '}
                    <span className="text-sm" style={{ color: currentTheme.textSecondary }}>
                      tokens/sec
                    </span>
                  </div>
                  <div className="text-xs" style={{ color: currentTheme.textSecondary }}>
                    TTS/STT Usage: 1,234 chars
                  </div>
                </div>
              </div>

              {/* Health Checks */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold" style={{ color: currentTheme.text }}>
                    Health Checks
                  </h3>
                  <span style={{ color: currentTheme.text }}>▼</span>
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Docker', status: 'ok' },
                    { label: 'Supabase DB', status: 'ok' },
                    { label: 'Remote API', status: 'degraded' },
                    { label: 'Local Network', status: 'ok' },
                  ].map((check, index) => (
                    <div key={index} className="flex items-center">
                      <div
                        className="w-2 h-2 rounded-full mr-3"
                        style={{
                          backgroundColor:
                            check.status === 'ok'
                              ? currentTheme.green
                              : check.status === 'error'
                                ? currentTheme.red
                                : currentTheme.orange,
                        }}
                      />
                      <span className="text-sm" style={{ color: currentTheme.textSecondary }}>
                        {check.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Local Resources */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold" style={{ color: currentTheme.text }}>
                    Local Resources
                  </h3>
                  <span style={{ color: currentTheme.text }}>▼</span>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm mb-1" style={{ color: currentTheme.textSecondary }}>
                      CPU Usage (85%)
                    </div>
                    <div className="w-full h-2 bg-gray-600 rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '85%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="text-sm mb-1" style={{ color: currentTheme.textSecondary }}>
                      RAM Usage (60%)
                    </div>
                    <div className="w-full h-2 bg-gray-600 rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '60%' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* RAG Ingestion */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold" style={{ color: currentTheme.text }}>
                    RAG Ingestion
                  </h3>
                  <span style={{ color: currentTheme.text }}>▼</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-3" />
                    <span className="text-sm" style={{ color: currentTheme.textSecondary }}>
                      Status: Idle
                    </span>
                  </div>
                  <div className="text-xs" style={{ color: currentTheme.textSecondary }}>
                    Docs Indexed: 1,492
                  </div>
                  <div className="text-xs" style={{ color: currentTheme.textSecondary }}>
                    Last Update: 5:42 AM
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
