import React, { useState } from 'react';
import { Search, BookOpen } from 'lucide-react';
import { KnowledgeBaseEntry } from '../types';
import { useKnowledgeBase } from '../hooks/useKnowledgeBase';
import KnowledgeBaseCard from '../components/KnowledgeBase/KnowledgeBaseCard';

const KnowledgeBase: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const { entries, loading, error, search, updateEntry, deleteEntry } = useKnowledgeBase();

  const categories = ['All Categories', 'Security', 'Operations'];

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    search(value); // Immediate local search
  };

  const filteredEntries = entries.filter(entry => {
    const matchesCategory = selectedCategory === 'All Categories' || 
      entry.categories?.includes(selectedCategory.toLowerCase());
    return matchesCategory;
  });

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
        <div className="text-lg text-red-500">Error loading knowledge base: {error}</div>
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

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:space-x-4 space-y-4 md:space-y-0">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search knowledge base..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex space-x-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Knowledge Base Entries */}
      <div className="space-y-6">
        {filteredEntries.length > 0 ? (
          filteredEntries.map((entry) => (
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
              {searchTerm ? 'Try adjusting your search terms or filters.' : 'Knowledge base entries will appear here as they are created.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase; 