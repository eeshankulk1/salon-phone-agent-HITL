import React from 'react';
import { Plus } from 'lucide-react';

interface AddItemButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

const AddItemButton: React.FC<AddItemButtonProps> = ({ onClick, disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Plus size={20} />
      <span className="font-medium">Add Item</span>
    </button>
  );
};

export default AddItemButton; 