import React, { useState } from 'react';
import { History as HistoryIcon, Filter } from 'lucide-react';
import RequestCard from '../components/Requests/RequestCard';
import { HelpRequest } from '../types';
import { mockRequests } from '../data/mockData';

const History: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const statusOptions = [
    { value: 'all', label: 'All Requests' },
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'cancelled', label: 'Cancelled' }
  ];

  const filteredRequests = statusFilter === 'all' 
    ? mockRequests
    : mockRequests.filter(req => req.status === statusFilter);

  const sortedRequests = [...filteredRequests].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const resolvedCount = mockRequests.filter(req => req.status === 'resolved').length;
  const totalCount = mockRequests.length;

  const handleViewDetails = (request: HelpRequest) => {
    console.log('View details for request:', request.id);
    // Could open a details modal here
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <HistoryIcon className="text-blue-500" size={24} />
          <h1 className="text-2xl font-bold text-gray-900">Request History</h1>
        </div>
        <div className="text-sm text-gray-600">
          {totalCount} total • {resolvedCount} resolved
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center space-x-4">
          <Filter className="text-gray-400" size={20} />
          <div className="flex space-x-2">
            {statusOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setStatusFilter(option.value)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  statusFilter === option.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Request History */}
      <div className="space-y-4">
        {sortedRequests.length > 0 ? (
          sortedRequests.map((request) => (
            <div key={request.id} className="relative">
              <RequestCard
                request={request}
                onViewDetails={handleViewDetails}
              />
              {/* Add a subtle indicator for high priority requests */}
              {request.priority === 'HIGH' && (
                <div className="absolute top-0 left-0 w-1 h-full bg-red-500 rounded-l-lg"></div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <HistoryIcon className="mx-auto text-gray-300 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No requests found</h3>
            <p className="text-gray-500">
              No requests match the current filter. Try selecting a different status.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default History; 