import React from 'react';
import RequestCard from './RequestCard';
import { HelpRequest } from '../../types';

interface PendingRequestsSectionProps {
  requests: HelpRequest[];
  onViewDetails: (request: HelpRequest) => void;
  onRespond: (request: HelpRequest) => void;
  onCancel: (request: HelpRequest) => void;
  onRefresh: () => Promise<void>;
  isRefreshing?: boolean;
}

const PendingRequestsSection: React.FC<PendingRequestsSectionProps> = ({
  requests,
  onViewDetails,
  onRespond,
  onCancel,
  onRefresh,
  isRefreshing = false,
}) => {
  const pendingRequests = requests.filter(req => req.status === 'pending');
  
  // Sort pending requests by created_at in descending order (newest first)
  const sortedPendingRequests = [...pendingRequests].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const handleRefresh = async () => {
    try {
      await onRefresh();
    } catch (error) {
      console.error('Error refreshing requests:', error);
    }
  };

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Pending Requests</h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">{pendingRequests.length} total</span>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            aria-label="Refresh pending requests"
          >
            <svg
              className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
      <div className="space-y-4">
        {sortedPendingRequests.length > 0 ? (
          sortedPendingRequests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              onViewDetails={onViewDetails}
              onRespond={onRespond}
              onCancel={onCancel}
            />
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            No pending requests
          </div>
        )}
      </div>
    </div>
  );
};

export default PendingRequestsSection; 