export const notificationStyles = {
  container: 'fixed top-4 right-4 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-3 z-50',
  success: 'bg-green-500',
  error: 'bg-red-500',
  closeButton: 'text-white hover:text-gray-200',
} as const;

export const notificationConfig = {
  successDuration: 5000,
  errorDuration: 7000,
} as const; 