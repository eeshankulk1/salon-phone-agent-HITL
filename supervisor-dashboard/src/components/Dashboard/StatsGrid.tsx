import React from 'react';
import { Clock, X, CheckCircle } from 'lucide-react';
import StatCard from './StatCard';
import { DashboardStats, HelpRequest } from '../../types';

interface StatsGridProps {
  stats: DashboardStats;
  requests: HelpRequest[];
}

const StatsGrid: React.FC<StatsGridProps> = ({ stats, requests }) => {
  const resolvedTodayRequests = requests.filter(req => 
    req.status === 'resolved' && 
    new Date(req.created_at).toDateString() === new Date().toDateString()
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <StatCard
        title="Pending Requests"
        count={stats.pending}
        description="Awaiting response"
        icon={Clock}
        iconColor="bg-orange-500"
      />
      <StatCard
        title="Cancelled"
        count={stats.cancelled}
        description="Cancelled requests"
        icon={X}
        iconColor="bg-red-500"
      />
      <StatCard
        title="Resolved Today"
        count={resolvedTodayRequests.length}
        description="Completed requests"
        icon={CheckCircle}
        iconColor="bg-green-500"
      />
    </div>
  );
};

export default StatsGrid; 