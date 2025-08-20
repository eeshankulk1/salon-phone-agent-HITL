import React from 'react';
import RequestCard from './RequestCard';
import { HelpRequest } from '../../types';

interface PendingRequestsSectionProps {
  requests: HelpRequest[];
  onViewDetails: (request: HelpRequest) => void;
  onRespond: (request: HelpRequest) => void;
}

const PendingRequestsSection: React.FC<PendingRequestsSectionProps> = ({
  requests,
  onViewDetails,
  onRespond,
}) => {
  const pendingRequests = requests.filter(req => req.status === 'pending');
  
  // Sort pending requests by created_at in descending order (newest first)
  const sortedPendingRequests = [...pendingRequests].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Pending Requests</h2>
        <span className="text-sm text-gray-500">{pendingRequests.length} total</span>
      </div>
      <div className="space-y-4">
        {sortedPendingRequests.length > 0 ? (
          sortedPendingRequests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              onViewDetails={onViewDetails}
              onRespond={onRespond}
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