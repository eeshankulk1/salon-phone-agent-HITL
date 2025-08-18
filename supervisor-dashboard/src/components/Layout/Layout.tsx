import React, { useState } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { DashboardStats } from '../../types';

type TabKey = 'dashboard' | 'history' | 'knowledge-base';

interface LayoutProps {
  children: React.ReactNode;
  stats: DashboardStats;
}

const Layout: React.FC<LayoutProps> = ({ children, stats }) => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header stats={stats} />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {React.cloneElement(children as React.ReactElement, { activeTab })}
      </main>
    </div>
  );
};

export default Layout; 