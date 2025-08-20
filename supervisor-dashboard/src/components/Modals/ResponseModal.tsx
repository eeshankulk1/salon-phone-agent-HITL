import React, { useState } from 'react';
import { X, Send } from 'lucide-react';
import { HelpRequest } from '../../types';

interface ResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  request: HelpRequest | null;
  onSubmit: (response: string) => void;
  isSubmitting?: boolean;
}

const ResponseModal: React.FC<ResponseModalProps> = ({ 
  isOpen, 
  onClose, 
  request, 
  onSubmit, 
  isSubmitting = false 
}) => {
  const [response, setResponse] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (response.trim() && !isSubmitting) {
      onSubmit(response);
      setResponse('');
      onClose();
    }
  };

  if (!isOpen || !request) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Respond to Request</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close modal"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Request Details</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>Customer:</strong> {request.customer?.display_name || 'Unknown Customer'}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>Question:</strong>
              </p>
              <p className="text-gray-800">{request.question_text}</p>
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="response" className="block text-sm font-medium text-gray-700 mb-2">
                Your Response
              </label>
              <textarea
                id="response"
                rows={6}
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your response to help the customer..."
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!response.trim() || isSubmitting}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-400"
              >
                <Send size={16} />
                <span>{isSubmitting ? 'Sending...' : 'Send Response'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ResponseModal; 