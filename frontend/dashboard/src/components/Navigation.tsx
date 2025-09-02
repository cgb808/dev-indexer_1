import {
  ChartBarIcon,
  ChatBubbleLeftIcon,
  CpuChipIcon,
  MoonIcon,
  SunIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from './ThemeProvider';

interface NavigationProps {
  isDevMode: boolean;
  onToggleMode: (isDev: boolean) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ isDevMode, onToggleMode }) => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const navItems = [
    {
      path: isDevMode ? '/dev' : '/user',
      label: isDevMode ? 'Dev View' : 'User View',
      icon: isDevMode ? CpuChipIcon : UserIcon,
    },
    {
      path: '/chat',
      label: 'Chat',
      icon: ChatBubbleLeftIcon,
    },
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: ChartBarIcon,
    },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-gray-900">ZenGlow</h1>
            <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {isDevMode ? 'Developer' : 'User'} Mode
            </span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-6">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </Link>
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Dev/User Mode Toggle */}
            <button
              onClick={() => onToggleMode(!isDevMode)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isDevMode ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'
              }`}
            >
              {isDevMode ? (
                <>
                  <CpuChipIcon className="w-4 h-4" />
                  <span>Dev</span>
                </>
              ) : (
                <>
                  <UserIcon className="w-4 h-4" />
                  <span>User</span>
                </>
              )}
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              {theme === 'light' ? <MoonIcon className="w-5 h-5" /> : <SunIcon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
