import React from 'react';
import { MessageSquare, History, BookOpen } from 'lucide-react';

type TabKey = 'dashboard' | 'history' | 'knowledge-base';

interface NavigationProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { key: 'dashboard' as TabKey, label: 'Handle Requests', icon: MessageSquare },
    { key: 'knowledge-base' as TabKey, label: 'Knowledge Base', icon: BookOpen },
    { key: 'history' as TabKey, label: 'History', icon: History },
  ];

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            
            return (
              <button
                key={tab.key}
                onClick={() => onTabChange(tab.key)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                  ${isActive 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default Navigation; 