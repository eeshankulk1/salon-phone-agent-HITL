import React from 'react';
import { X } from 'lucide-react';
import { notificationStyles } from '../../styles/notifications';

export interface NotificationProps {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
}

const Notification: React.FC<NotificationProps> = ({ message, type, onClose }) => {
  const bgColor = type === 'success' ? notificationStyles.success : notificationStyles.error;
  
  return (
    <div className={`${notificationStyles.container} ${bgColor}`}>
      <span>{message}</span>
      <button
        onClick={onClose}
        className={notificationStyles.closeButton}
        aria-label="Close notification"
      >
        <X size={18} />
      </button>
    </div>
  );
};

export default Notification; 