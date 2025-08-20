import React, { useState } from 'react';
import { Clock, AlertCircle, CheckCircle } from 'lucide-react';
import StatCard from '../components/Dashboard/StatCard';
import RequestCard from '../components/Requests/RequestCard';
import ResponseModal from '../components/Modals/ResponseModal';
import { HelpRequest } from '../types';
import { useAllHelpRequests } from '../hooks/useHelpRequests';

const HandleRequests: React.FC = () => {
  const [selectedRequest, setSelectedRequest] = useState<HelpRequest | null>(null);
  const [isResponseModalOpen, setIsResponseModalOpen] = useState(false);
  const { requests, stats, loading, error } = useAllHelpRequests();

  const pendingRequests = requests.filter(req => req.status === 'pending');
  const inProgressRequests = requests.filter(req => req.status === 'in_progress');
  const resolvedTodayRequests = requests.filter(req => 
    req.status === 'resolved' && 
    new Date(req.created_at).toDateString() === new Date().toDateString()
  );

  // Sort pending requests by created_at in descending order (newest first)
  const sortedPendingRequests = [...pendingRequests].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const handleViewDetails = (request: HelpRequest) => {
    setSelectedRequest(request);
    // Could open a details modal here
  };

  const handleRespond = (request: HelpRequest) => {
    setSelectedRequest(request);
    setIsResponseModalOpen(true);
  };

  const handleSubmitResponse = (response: string) => {
    console.log('Submitted response:', response, 'for request:', selectedRequest?.id);
    // In a real app, this would make an API call to submit the response
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-gray-500">Loading requests...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-red-500">Error loading requests: {error}</div>
      </div>
    );
  }

  return (
    <div>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Pending Requests"
          count={stats.pending}
          description="Awaiting response"
          icon={Clock}
          iconColor="bg-orange-500"
        />
        <StatCard
          title="In Progress"
          count={stats.in_progress}
          description="Being processed"
          icon={AlertCircle}
          iconColor="bg-blue-500"
        />
        <StatCard
          title="Resolved Today"
          count={resolvedTodayRequests.length}
          description="Completed requests"
          icon={CheckCircle}
          iconColor="bg-green-500"
        />
      </div>

      {/* Pending Requests Section */}
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
                onViewDetails={handleViewDetails}
                onRespond={handleRespond}
              />
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No pending requests
            </div>
          )}
        </div>
      </div>

      {/* Response Modal */}
      <ResponseModal
        isOpen={isResponseModalOpen}
        onClose={() => setIsResponseModalOpen(false)}
        request={selectedRequest}
        onSubmit={handleSubmitResponse}
      />
    </div>
  );
};

export default HandleRequests; 