import { ChatBubbleLeftRightIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import * as React from 'react';
import { JustJarvis } from './JustJarvis';
import { ZenGlowChat } from './ZenGlowChat';

type ViewType = 'chat' | 'jarvis';

export const AppRouter = () => {
  const [currentView, setCurrentView] = React.useState<ViewType>('chat');
  const [isDarkMode, setIsDarkMode] = React.useState(true);

  const currentTheme = {
    background: isDarkMode ? '#0f0f0f' : '#F5F5F5',
    text: isDarkMode ? '#E1E1E1' : '#000000',
    textSecondary: isDarkMode ? '#888' : '#555',
    card: isDarkMode ? '#1E1E1E' : '#FFFFFF',
    border: isDarkMode ? '#333' : '#DDD',
    primary: '#007AFF',
    secondary: '#8b5cf6',
  };

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  return (
    <div
      className="h-screen flex flex-col"
      style={{
        backgroundColor: currentTheme.background,
        color: currentTheme.text,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      }}
    >
      {/* Navigation Bar */}
      <nav
        style={{
          backgroundColor: currentTheme.card,
          borderBottom: `1px solid ${currentTheme.border}`,
          padding: '16px 24px',
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'linear-gradient(135deg, #007AFF, #8b5cf6)' }}
              >
                <span className="text-lg font-bold" style={{ color: 'white' }}>
                  ZG
                </span>
              </div>
              <h1
                className="text-2xl font-bold"
                style={{
                  background: 'linear-gradient(135deg, #007AFF, #8b5cf6)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                ZenGlow
              </h1>
            </div>

            {/* Navigation Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentView('chat')}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-300"
                style={{
                  backgroundColor: currentView === 'chat' ? currentTheme.primary : 'transparent',
                  color: currentView === 'chat' ? 'white' : currentTheme.text,
                  border: `1px solid ${currentView === 'chat' ? currentTheme.primary : currentTheme.border}`,
                }}
              >
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                <span>Chat Interface</span>
              </button>
              <button
                onClick={() => setCurrentView('jarvis')}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-300"
                style={{
                  backgroundColor: currentView === 'jarvis' ? currentTheme.secondary : 'transparent',
                  color: currentView === 'jarvis' ? 'white' : currentTheme.text,
                  border: `1px solid ${currentView === 'jarvis' ? currentTheme.secondary : currentTheme.border}`,
                }}
              >
                <CpuChipIcon className="w-5 h-5" />
                <span>JustJarvis</span>
              </button>
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <div className="text-sm" style={{ color: currentTheme.textSecondary }}>
              {currentView === 'chat' ? 'AI Chat Assistant' : 'AI Control Center'}
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors"
              style={{ color: currentTheme.text }}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#10b981' }}></div>
              <span style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>Online</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">{currentView === 'chat' ? <ZenGlowChat /> : <JustJarvis />}</div>
    </div>
  );
};
