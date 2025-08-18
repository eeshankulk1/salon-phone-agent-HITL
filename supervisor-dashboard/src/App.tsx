import React, { useState } from 'react';
import Header from './components/Layout/Header';
import Navigation from './components/Layout/Navigation';
import HandleRequests from './pages/Dashboard';
import History from './pages/History';
import KnowledgeBase from './pages/KnowledgeBase';
import { mockStats } from './data/mockData';

type TabKey = 'dashboard' | 'history' | 'knowledge-base';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <HandleRequests />;
      case 'history':
        return <History />;
      case 'knowledge-base':
        return <KnowledgeBase />;
      default:
        return <HandleRequests />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={mockStats} />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default App; 