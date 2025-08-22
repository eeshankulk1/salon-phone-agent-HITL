import React, { useState } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { DashboardStats } from '../../types';

type TabKey = 'dashboard' | 'history' | 'knowledge-base';

interface LayoutProps {
  renderContent: (activeTab: TabKey) => React.ReactNode;
  stats: DashboardStats;
}

const Layout: React.FC<LayoutProps> = ({ renderContent, stats }) => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');

  return (
    <div className="bg-gray-50" style={{ minHeight: 'calc(100vh / 0.9)' }}>
      <Header stats={stats} />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderContent(activeTab)}
      </main>
    </div>
  );
};

export default Layout; 