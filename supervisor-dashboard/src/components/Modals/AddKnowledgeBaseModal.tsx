import React, { useState } from 'react';
import { X, Save } from 'lucide-react';
import { createKnowledgeBaseEntry } from '../../services/knowledgeBase';
import { KnowledgeBaseEntry } from '../../types';

interface AddKnowledgeBaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newEntry: KnowledgeBaseEntry) => void;
}

interface FormData {
  question_text_example: string;
  answer_text: string;
}

interface FormErrors {
  question_text_example?: string;
  answer_text?: string;
  general?: string;
}

const AddKnowledgeBaseModal: React.FC<AddKnowledgeBaseModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<FormData>({
    question_text_example: '',
    answer_text: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.question_text_example.trim()) {
      newErrors.question_text_example = 'Question is required';
    }

    if (!formData.answer_text.trim()) {
      newErrors.answer_text = 'Answer is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const newEntry = await createKnowledgeBaseEntry({
        question_text_example: formData.question_text_example.trim(),
        answer_text: formData.answer_text.trim(),
      });
      
      onSuccess(newEntry);
      handleClose();
    } catch (error) {
      console.error('Error creating knowledge base entry:', error);
      setErrors({ 
        general: 'Failed to create knowledge base entry. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      setFormData({ question_text_example: '', answer_text: '' });
      setErrors({});
      onClose();
    }
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Add Knowledge Base Entry</h2>
          <button
            onClick={handleClose}
            disabled={isLoading}
            title="Close modal"
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
          >
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* General Error */}
          {errors.general && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{errors.general}</p>
            </div>
          )}

          {/* Question Field */}
          <div className="mb-4">
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Question <span className="text-red-500">*</span>
            </label>
            <input
              id="question"
              type="text"
              value={formData.question_text_example}
              onChange={(e) => handleInputChange('question_text_example', e.target.value)}
              placeholder="Enter the example question..."
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.question_text_example ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {errors.question_text_example && (
              <p className="mt-1 text-sm text-red-600">{errors.question_text_example}</p>
            )}
          </div>

          {/* Answer Field */}
          <div className="mb-6">
            <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
              Answer <span className="text-red-500">*</span>
            </label>
            <textarea
              id="answer"
              value={formData.answer_text}
              onChange={(e) => handleInputChange('answer_text', e.target.value)}
              placeholder="Enter the answer..."
              rows={4}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical ${
                errors.answer_text ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {errors.answer_text && (
              <p className="mt-1 text-sm text-red-600">{errors.answer_text}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <Save size={16} />
              <span>{isLoading ? 'Creating...' : 'Create Entry'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddKnowledgeBaseModal; 