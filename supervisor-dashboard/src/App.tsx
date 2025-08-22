import React, { useState } from 'react';
import Header from './components/Layout/Header';
import Navigation from './components/Layout/Navigation';
import HandleRequests from './pages/HandleRequests';
import RequestHistory from './pages/RequestHistory';
import KnowledgeBase from './pages/KnowledgeBase';
import { useAllHelpRequests } from './hooks/useHelpRequests';

type TabKey = 'dashboard' | 'history' | 'knowledge-base';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');
  const { stats } = useAllHelpRequests();

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <HandleRequests />;
      case 'history':
        return <RequestHistory />;
      case 'knowledge-base':
        return <KnowledgeBase />;
      default:
        return <HandleRequests />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default App; 