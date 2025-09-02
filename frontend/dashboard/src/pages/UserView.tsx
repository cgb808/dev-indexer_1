import { ChatBubbleLeftIcon, HeartIcon, SparklesIcon, StarIcon } from '@heroicons/react/24/outline';
import React from 'react';

export const UserView: React.FC = () => {
  const userFeatures = [
    {
      icon: ChatBubbleLeftIcon,
      title: 'AI Chat',
      description: 'Natural conversations with advanced AI assistants',
      color: 'bg-blue-500',
    },
    {
      icon: SparklesIcon,
      title: 'Smart Features',
      description: 'Intelligent suggestions and automated workflows',
      color: 'bg-purple-500',
    },
    {
      icon: HeartIcon,
      title: 'Personalized',
      description: 'Tailored experiences based on your preferences',
      color: 'bg-pink-500',
    },
    {
      icon: StarIcon,
      title: 'Premium Tools',
      description: 'Advanced features and priority support',
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to ZenGlow</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Experience the future of AI-powered productivity with our beautiful and intuitive interface
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {userFeatures.map((feature, index) => (
          <div key={index} className="card hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center space-x-4 mb-4">
              <div className={`p-3 ${feature.color} rounded-xl`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
              </div>
            </div>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Start</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-semibold">1</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Start a Conversation</p>
                <p className="text-sm text-gray-600">Begin chatting with our AI assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-semibold">2</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Explore Features</p>
                <p className="text-sm text-gray-600">Discover powerful AI capabilities</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-semibold">3</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Customize Experience</p>
                <p className="text-sm text-gray-600">Personalize your AI interactions</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Conversations</h3>
          <div className="space-y-3">
            <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
              <p className="font-medium text-gray-900">AI Writing Assistant</p>
              <p className="text-sm text-gray-600">Help with creative writing and content generation</p>
              <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-100">
              <p className="font-medium text-gray-900">Code Review Helper</p>
              <p className="text-sm text-gray-600">Analyzing and improving code quality</p>
              <p className="text-xs text-gray-500 mt-1">Yesterday</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
              <p className="font-medium text-gray-900">Learning Companion</p>
              <p className="text-sm text-gray-600">Personalized learning and study assistance</p>
              <p className="text-xs text-gray-500 mt-1">3 days ago</p>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">AI Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Conversations Today</span>
              <span className="font-semibold text-gray-900">12</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Average Response Time</span>
              <span className="font-semibold text-green-600">1.2s</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Satisfaction Rate</span>
              <span className="font-semibold text-blue-600">98%</span>
            </div>
            <div className="mt-4">
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                  style={{ width: '85%' }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">85% of capacity used</p>
            </div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <button className="btn btn-primary text-lg px-8 py-3">Start Your AI Journey</button>
      </div>
    </div>
  );
};
