import React from 'react';
import Layout from './components/Layout/Layout';
import HandleRequests from './pages/HandleRequests';
import RequestHistory from './pages/RequestHistory';
import KnowledgeBase from './pages/KnowledgeBase';
import { useAllHelpRequests } from './hooks/useHelpRequests';

const App: React.FC = () => {
  const { stats } = useAllHelpRequests();

  const renderContent = (activeTab: 'dashboard' | 'history' | 'knowledge-base') => {
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
    <Layout stats={stats} renderContent={renderContent} />
  );
};

export default App; 