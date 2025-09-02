import { BeakerIcon, ChartBarIcon, CpuChipIcon, WrenchScrewdriverIcon } from '@heroicons/react/24/outline';
import React from 'react';

export const DevView: React.FC = () => {
  const devFeatures = [
    {
      icon: CpuChipIcon,
      title: 'System Monitoring',
      description: 'Real-time metrics, performance tracking, and system health monitoring',
      status: 'active',
    },
    {
      icon: WrenchScrewdriverIcon,
      title: 'API Testing',
      description: 'Interactive API testing tools, request/response inspection, and debugging',
      status: 'active',
    },
    {
      icon: BeakerIcon,
      title: 'Experimentation',
      description: 'A/B testing, feature flags, and experimental feature development',
      status: 'beta',
    },
    {
      icon: ChartBarIcon,
      title: 'Analytics Dashboard',
      description: 'Advanced analytics, data visualization, and performance insights',
      status: 'active',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Developer Dashboard</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Advanced tools and insights for development, testing, and system monitoring
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {devFeatures.map((feature, index) => (
          <div key={index} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <feature.icon className="w-6 h-6 text-blue-600" />
              </div>
              <div
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  feature.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {feature.status}
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-gray-600 text-sm">{feature.description}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="btn btn-primary w-full">Run Tests</button>
            <button className="btn btn-secondary w-full">Deploy to Staging</button>
            <button className="btn btn-secondary w-full">View Logs</button>
            <button className="btn btn-secondary w-full">System Diagnostics</button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">API Health Check</p>
                <p className="text-xs text-gray-500">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Database Migration</p>
                <p className="text-xs text-gray-500">15 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Cache Invalidation</p>
                <p className="text-xs text-gray-500">1 hour ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
