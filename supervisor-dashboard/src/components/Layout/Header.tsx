import React from 'react';
import { Shield } from 'lucide-react';
import { DashboardStats } from '../../types';

interface HeaderProps {
  stats: DashboardStats;
}

const Header: React.FC<HeaderProps> = ({ stats }) => {
  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-40 py-4">
        <div className="flex items-center">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Shield className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Supervisor Dashboard</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                Manage pending requests, track progress, and build your organizational knowledge base
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header; 