import React, { useState } from 'react';
import { BookOpen } from 'lucide-react';
import { KnowledgeBaseEntry } from '../types';
import { useKnowledgeBase } from '../hooks/useKnowledgeBase';
import KnowledgeBaseCard from '../components/KnowledgeBase/KnowledgeBaseCard';
import SearchBar from '../components/KnowledgeBase/SearchBar';
import AddItemButton from '../components/KnowledgeBase/AddItemButton';
import AddKnowledgeBaseModal from '../components/Modals/AddKnowledgeBaseModal';
import Notification from '../components/UI/Notification';
import { notificationConfig } from '../styles/notifications';

const KnowledgeBase: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const { entries, loading, error, search, updateEntry, deleteEntry, addEntry } = useKnowledgeBase();

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    search(value); // Immediate local search
  };

  // Handle successful creation of new entry
  const handleAddSuccess = (newEntry: KnowledgeBaseEntry) => {
    addEntry(newEntry); // Add the new entry to the local state
    
    // Show success notification
    setNotification({
      message: 'Knowledge base entry created successfully!',
      type: 'success'
    });
    
    // Auto-close notification after configured duration
    setTimeout(() => setNotification(null), notificationConfig.successDuration);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-gray-500">Loading knowledge base...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-lg text-red-500">Error loading knowledge base (make sure backend is running): {error}</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BookOpen className="text-blue-500" size={24} />
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
        </div>
      </div>

      {/* Search and Add Item */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:space-x-4 space-y-4 md:space-y-0">
          <SearchBar 
            searchTerm={searchTerm}
            onSearchChange={handleSearchChange}
          />
          <AddItemButton 
            onClick={() => setIsAddModalOpen(true)}
          />
        </div>
      </div>

      {/* Knowledge Base Entries */}
      <div className="space-y-6">
        {entries.length > 0 ? (
          entries.map((entry) => (
            <KnowledgeBaseCard
              key={entry.id}
              entry={entry}
              onUpdate={updateEntry}
              onDelete={deleteEntry}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <BookOpen className="mx-auto text-gray-300 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No knowledge base entries found</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Try adjusting your search terms.' : 'Knowledge base entries will appear here as they are created.'}
            </p>
          </div>
        )}
      </div>

      {/* Add Item Modal */}
      <AddKnowledgeBaseModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={handleAddSuccess}
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

export default KnowledgeBase; 