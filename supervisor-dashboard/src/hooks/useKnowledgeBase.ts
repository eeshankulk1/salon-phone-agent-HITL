import { useState, useEffect, useCallback, useMemo } from 'react';
import { KnowledgeBaseEntry } from '../types';
import { getKnowledgeBaseEntries } from '../services/knowledgeBase';

interface UseKnowledgeBaseReturn {
  entries: KnowledgeBaseEntry[];
  allEntries: KnowledgeBaseEntry[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  search: (query: string) => void;
}

export const useKnowledgeBase = (): UseKnowledgeBaseReturn => {
  const [allEntries, setAllEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Load all entries once on mount
  const fetchAllEntries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetch all entries without search query
      const data = await getKnowledgeBaseEntries();
      setAllEntries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch knowledge base entries');
      console.error('Error fetching knowledge base entries:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load data only once on mount
  useEffect(() => {
    fetchAllEntries();
  }, [fetchAllEntries]);

  // Local search filtering - no API calls, no loading states
  const search = useCallback((query: string) => {
    setSearchQuery(query.trim());
  }, []);

  // Filter entries locally based on search query
  const filteredEntries = useMemo(() => {
    if (!searchQuery) {
      return allEntries;
    }

    const query = searchQuery.toLowerCase();
    return allEntries.filter(entry => {
      // Search in question text and answer text
      const questionMatch = entry.question_text_example?.toLowerCase().includes(query);
      const answerMatch = entry.answer_text?.toLowerCase().includes(query);
      const categoryMatch = entry.categories?.some(cat => 
        cat.toLowerCase().includes(query)
      );
      
      return questionMatch || answerMatch || categoryMatch;
    });
  }, [allEntries, searchQuery]);

  const refetch = useCallback(async () => {
    await fetchAllEntries();
  }, [fetchAllEntries]);

  return {
    entries: filteredEntries,
    allEntries,
    loading,
    error,
    refetch,
    search,
  };
}; 