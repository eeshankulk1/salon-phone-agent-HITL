import { apiClient } from './index';
import { KnowledgeBaseEntry } from '../types';

// Get all knowledge base entries with optional search query
export const getKnowledgeBaseEntries = async (searchQuery?: string): Promise<KnowledgeBaseEntry[]> => {
  const endpoint = searchQuery ? `/knowledge-base/?q=${encodeURIComponent(searchQuery)}` : '/knowledge-base/';
  return apiClient.get<KnowledgeBaseEntry[]>(endpoint);
};

// Get a specific knowledge base entry by ID
export const getKnowledgeBaseEntry = async (id: string): Promise<KnowledgeBaseEntry> => {
  return apiClient.get<KnowledgeBaseEntry>(`/knowledge-base/${id}`);
};

// Create a new knowledge base entry
export const createKnowledgeBaseEntry = async (data: {
  question_text_example: string;
  answer_text: string;
  categories?: string[];
  normalized_key?: string;
  source_help_request_id?: string;
}): Promise<KnowledgeBaseEntry> => {
  return apiClient.post<KnowledgeBaseEntry>('/knowledge-base', data);
};

// Update a knowledge base entry
export const updateKnowledgeBaseEntry = async (
  id: string,
  data: {
    question_text_example?: string;
    answer_text?: string;
    categories?: string[];
    normalized_key?: string;
  }
): Promise<KnowledgeBaseEntry> => {
  return apiClient.put<KnowledgeBaseEntry>(`/knowledge-base/${id}`, data);
}; 