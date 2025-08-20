import React, { useState } from 'react';
import { Edit2, Trash2, Save, X } from 'lucide-react';
import { KnowledgeBaseEntry } from '../../types';
import { updateKnowledgeBaseEntry, deleteKnowledgeBaseEntry } from '../../services/knowledgeBase';

interface KnowledgeBaseCardProps {
  entry: KnowledgeBaseEntry;
  onUpdate: (updatedEntry: KnowledgeBaseEntry) => void;
  onDelete: (entryId: string) => void;
}

const KnowledgeBaseCard: React.FC<KnowledgeBaseCardProps> = ({
  entry,
  onUpdate,
  onDelete,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [editData, setEditData] = useState({
    question_text_example: entry.question_text_example,
    answer_text: entry.answer_text,
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditData({
      question_text_example: entry.question_text_example,
      answer_text: entry.answer_text,
    });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData({
      question_text_example: entry.question_text_example,
      answer_text: entry.answer_text,
    });
  };

  const handleSave = async () => {
    if (!editData.question_text_example.trim() || !editData.answer_text.trim()) {
      alert('Question and answer cannot be empty');
      return;
    }

    setIsLoading(true);
    try {
      const updatedEntry = await updateKnowledgeBaseEntry(entry.id, editData);
      onUpdate(updatedEntry);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating knowledge base entry:', error);
      alert('Failed to update entry. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this knowledge base entry?')) {
      return;
    }

    setIsLoading(true);
    try {
      await deleteKnowledgeBaseEntry(entry.id);
      onDelete(entry.id);
    } catch (error) {
      console.error('Error deleting knowledge base entry:', error);
      alert('Failed to delete entry. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 relative">
      {/* Action Buttons */}
      <div className="absolute top-4 right-4 flex space-x-2">
        {isEditing ? (
          <>
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="p-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-md transition-colors disabled:opacity-50"
              title="Save changes"
            >
              <Save size={16} />
            </button>
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-md transition-colors disabled:opacity-50"
              title="Cancel editing"
            >
              <X size={16} />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={handleEdit}
              disabled={isLoading}
              className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50"
              title="Edit entry"
            >
              <Edit2 size={16} />
            </button>
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
              title="Delete entry"
            >
              <Trash2 size={16} />
            </button>
          </>
        )}
      </div>

      {/* Content */}
      <div className="pr-20"> {/* Add padding to avoid button overlap */}
        <div className="flex items-start justify-between mb-4">
          {isEditing ? (
            <input
              type="text"
              value={editData.question_text_example}
              onChange={(e) => setEditData({ ...editData, question_text_example: e.target.value })}
              className="text-lg font-semibold text-gray-900 border border-gray-300 rounded-md px-3 py-2 w-full mr-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Question text..."
            />
          ) : (
            <h3 className="text-lg font-semibold text-gray-900">
              {entry.question_text_example}
            </h3>
          )}
          {!isEditing && (
            <span className="text-sm text-gray-500 ml-4 flex-shrink-0">
              {formatDate(entry.created_at)}
            </span>
          )}
        </div>
        
        <div className="prose prose-sm max-w-none">
          {isEditing ? (
            <textarea
              value={editData.answer_text}
              onChange={(e) => setEditData({ ...editData, answer_text: e.target.value })}
              rows={4}
              className="w-full text-gray-700 leading-relaxed border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
              placeholder="Answer text..."
            />
          ) : (
            <p className="text-gray-700 leading-relaxed">
              {entry.answer_text}
            </p>
          )}
        </div>

        {!isEditing && entry.categories && entry.categories.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {entry.categories.map((category) => (
              <span
                key={category}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {category}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
          <div className="text-gray-600">Loading...</div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBaseCard; 