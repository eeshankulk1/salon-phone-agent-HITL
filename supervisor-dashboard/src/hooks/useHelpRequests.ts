import { useState, useEffect } from 'react';
import { HelpRequest, RequestStatus, DashboardStats } from '../types';
import { getHelpRequests } from '../services/helpRequests';

interface UseHelpRequestsReturn {
  requests: HelpRequest[];
  stats: DashboardStats;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useHelpRequests = (statusFilter?: RequestStatus): UseHelpRequestsReturn => {
  const [requests, setRequests] = useState<HelpRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getHelpRequests(statusFilter);
      setRequests(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch help requests');
      console.error('Error fetching help requests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [statusFilter]);

  // Calculate stats from the requests data
  const stats: DashboardStats = {
    pending: requests.filter(req => req.status === 'pending').length,
    in_progress: requests.filter(req => req.status === 'in_progress').length,
    resolved: requests.filter(req => req.status === 'resolved').length,
  };

  return {
    requests,
    stats,
    loading,
    error,
    refetch: fetchRequests,
  };
};

// Hook for getting all requests (no status filter) -  for stats and history
export const useAllHelpRequests = (): UseHelpRequestsReturn => {
  return useHelpRequests();
};

// Hook for getting requests by specific status
export const useHelpRequestsByStatus = (status: RequestStatus): UseHelpRequestsReturn => {
  return useHelpRequests(status);
}; 