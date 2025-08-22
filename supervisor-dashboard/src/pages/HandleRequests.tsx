import React, { useState } from 'react';
import StatsGrid from '../components/Dashboard/StatsGrid';
import PendingRequestsSection from '../components/Requests/PendingRequestsSection';
import ResponseModal from '../components/Modals/ResponseModal';
import Notification from '../components/UI/Notification';
import { HelpRequest } from '../types';
import { useAllHelpRequests } from '../hooks/useHelpRequests';
import { resolveHelpRequest, cancelHelpRequest } from '../services/helpRequests';
import { notificationConfig } from '../styles/notifications';

const HandleRequests: React.FC = () => {
  const [selectedRequest, setSelectedRequest] = useState<HelpRequest | null>(null);
  const [isResponseModalOpen, setIsResponseModalOpen] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { requests, stats, loading, error, refetch } = useAllHelpRequests();

  const handleViewDetails = (request: HelpRequest) => {
    setSelectedRequest(request);
    // Could open a details modal here
  };

  const handleRespond = (request: HelpRequest) => {
    setSelectedRequest(request);
    setIsResponseModalOpen(true);
  };

  const handleCancel = async (request: HelpRequest) => {
    if (!window.confirm('Are you sure you want to cancel this help request?')) {
      return;
    }

    setIsSubmitting(true);
    try {
      await cancelHelpRequest(request.id, {
        cancel_reason: 'cancelled by supervisor'
      });
      
      // Show success notification
      setNotification({
        message: 'Request cancelled successfully!',
        type: 'success'
      });
      
      // Refresh the data to show updated status
      await refetch();
      
      // Auto-close notification after configured duration
      setTimeout(() => setNotification(null), notificationConfig.successDuration);
      
    } catch (error) {
      console.error('Error cancelling help request:', error);
      setNotification({
        message: 'Failed to cancel request. Please try again.',
        type: 'error'
      });
      
      // Auto-close error notification after configured duration
      setTimeout(() => setNotification(null), notificationConfig.errorDuration);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitResponse = async (response: string) => {
    if (!selectedRequest) return;
    
    setIsSubmitting(true);
    try {
      await resolveHelpRequest(selectedRequest.id, {
        answer_text: response,
        responder_id: 'supervisor-1' // TODO: Replace with actual user ID from auth context
      });
      
      // Show success notification
      setNotification({
        message: 'Request resolved successfully and knowledge base entry created!',
        type: 'success'
      });
      
      // Refresh the data to show updated status
      await refetch();
      
      // Auto-close notification after configured duration
      setTimeout(() => setNotification(null), notificationConfig.successDuration);
      
    } catch (error) {
      console.error('Error resolving help request:', error);
      setNotification({
        message: 'Failed to resolve request. Please try again.',
        type: 'error'
      });
      
      // Auto-close error notification after configured duration
      setTimeout(() => setNotification(null), notificationConfig.errorDuration);
    } finally {
      setIsSubmitting(false);
    }
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
      <StatsGrid stats={stats} requests={requests} />

      {/* Pending Requests Section */}
      <PendingRequestsSection
        requests={requests}
        onViewDetails={handleViewDetails}
        onRespond={handleRespond}
        onCancel={handleCancel}
      />

      {/* Response Modal */}
      <ResponseModal
        isOpen={isResponseModalOpen}
        onClose={() => setIsResponseModalOpen(false)}
        request={selectedRequest}
        onSubmit={handleSubmitResponse}
        isSubmitting={isSubmitting}
      />
      
      {/* Notification */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
};

export default HandleRequests; 