import React, { useState } from 'react';
import { Clock, User, MessageSquare, ChevronDown, ChevronRight, Phone, Calendar, X } from 'lucide-react';
import { HelpRequest } from '../../types';

interface RequestCardProps {
  request: HelpRequest;
  onViewDetails?: (request: HelpRequest) => void;
  onRespond?: (request: HelpRequest) => void;
  onCancel?: (request: HelpRequest) => void;
}

const RequestCard: React.FC<RequestCardProps> = ({ request, onViewDetails, onRespond, onCancel }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDateLong = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-orange-100 text-orange-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all duration-200"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex-1 mr-6">
            {/* Top section with customer info and timestamp */}
            <div className="flex items-center space-x-4 mb-3">
              <div className="flex items-center space-x-2">
                <User size={14} className="text-gray-400" />
                <span className="text-sm text-gray-600">{request.customer?.display_name || 'Unknown Customer'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock size={14} className="text-gray-400" />
                <span className="text-sm text-gray-600">{formatDate(request.created_at)}</span>
              </div>
            </div>
            
            {/* Question text */}
            <h3 className="text-lg font-medium text-gray-900 mb-4 leading-relaxed">{request.question_text}</h3>
            
            {/* Status badge at bottom */}
            <div className="flex items-center">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                {request.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="flex flex-col items-end space-y-2 flex-shrink-0">
            {/* Cancel Button - Small and positioned at top right */}
            <div className="h-6 w-6 flex items-center justify-center">
              {onCancel && request.status === 'pending' && (
                <button
                  onClick={() => onCancel(request)}
                  className={`p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-all duration-200 ${
                    isHovered ? 'opacity-100' : 'opacity-0'
                  }`}
                  title="Cancel request"
                >
                  <X size={14} />
                </button>
              )}
            </div>
            
            {/* Respond Button */}
            {onRespond && request.status === 'pending' && (
              <button
                onClick={() => onRespond(request)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              >
                <MessageSquare size={16} />
                <span>Respond</span>
              </button>
            )}
            
            {/* View Details Button */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
            >
              <span>View Details</span>
              {isExpanded ? (
                <ChevronDown size={16} />
              ) : (
                <ChevronRight size={16} />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Details Section */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Request Information</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Calendar size={16} className="text-gray-400" />
                  <span className="text-sm text-gray-600">Created: {formatDateLong(request.created_at)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock size={16} className="text-gray-400" />
                  <span className="text-sm text-gray-600">Expires: {formatDateLong(request.expires_at)}</span>
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Request ID:</span> {request.id}
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Customer Information</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <User size={16} className="text-gray-400" />
                  <span className="text-sm text-gray-600">{request.customer?.display_name || 'Unknown Customer'}</span>
                </div>
                {request.customer?.phone_e164 && (
                  <div className="flex items-center space-x-2">
                    <Phone size={16} className="text-gray-400" />
                    <span className="text-sm text-gray-600">{request.customer.phone_e164}</span>
                  </div>
                )}
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Customer ID:</span> {request.customer_id}
                </div>
              </div>
            </div>
          </div>
          
          {request.call_id && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Call Information</h4>
              <div className="text-sm text-gray-600">
                <span className="font-medium">Call ID:</span> {request.call_id}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RequestCard; 