import { apiClient } from './index';
import { HelpRequest, RequestStatus } from '../types';

// Get all help requests with optional status filter
export const getHelpRequests = async (status?: RequestStatus): Promise<HelpRequest[]> => {
  const endpoint = status ? `/help-requests/?status=${status}` : '/help-requests/';
  return apiClient.get<HelpRequest[]>(endpoint);
};

// Get a specific help request by ID
export const getHelpRequest = async (id: string): Promise<HelpRequest> => {
  return apiClient.get<HelpRequest>(`/help-requests/${id}`);
};

// Resolve a help request with an answer
export const resolveHelpRequest = async (
  id: string,
  data: {
    answer_text: string;
    responder_id?: string;
  }
): Promise<HelpRequest> => {
  return apiClient.post<HelpRequest>(`/help-requests/${id}/resolve`, data);
};

// Cancel a help request
export const cancelHelpRequest = async (
  id: string,
  data?: {
    cancel_reason?: string;
  }
): Promise<HelpRequest> => {
  return apiClient.post<HelpRequest>(`/help-requests/${id}/cancel`, data || {});
}; 