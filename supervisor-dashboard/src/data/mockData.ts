import { HelpRequest, KnowledgeBaseEntry, Customer, DashboardStats } from '../types';

// Mock customers
const mockCustomers: Customer[] = [
  {
    id: '1',
    display_name: 'Sarah Chen',
    phone_e164: '+1234567890',
    created_at: '2024-01-15T09:30:00Z'
  },
  {
    id: '2',
    display_name: 'Mike Johnson',
    phone_e164: '+1234567891',
    created_at: '2024-01-15T08:15:00Z'
  },
  {
    id: '3',
    display_name: 'Emma Davis',
    phone_e164: '+1234567892',
    created_at: '2024-01-14T14:20:00Z'
  }
];

// Mock help requests
export const mockRequests: HelpRequest[] = [
  {
    id: '1',
    customer_id: '1',
    question_text: 'How to reset user password in the system?',
    status: 'pending',
    priority: 'HIGH',
    created_at: '2024-01-15T09:30:00Z',
    expires_at: '2024-01-15T17:30:00Z',
    customer: mockCustomers[0]
  },
  {
    id: '2',
    customer_id: '2',
    question_text: 'Database backup procedure clarification',
    status: 'in_progress',
    priority: 'MEDIUM',
    created_at: '2024-01-15T08:15:00Z',
    expires_at: '2024-01-15T16:15:00Z',
    customer: mockCustomers[1]
  },
  {
    id: '3',
    customer_id: '3',
    question_text: 'Unable to access admin panel after recent update',
    status: 'resolved',
    priority: 'HIGH',
    created_at: '2024-01-14T14:20:00Z',
    expires_at: '2024-01-14T22:20:00Z',
    resolved_at: '2024-01-14T16:45:00Z',
    customer: mockCustomers[2]
  },
  {
    id: '4',
    customer_id: '1',
    question_text: 'How to configure SSL certificates for the website?',
    status: 'pending',
    priority: 'MEDIUM',
    created_at: '2024-01-13T11:00:00Z',
    expires_at: '2024-01-13T19:00:00Z',
    customer: mockCustomers[0]
  },
  {
    id: '5',
    customer_id: '2',
    question_text: 'Email notification system not working properly',
    status: 'resolved',
    priority: 'LOW',
    created_at: '2024-01-12T10:30:00Z',
    expires_at: '2024-01-12T18:30:00Z',
    resolved_at: '2024-01-12T15:20:00Z',
    customer: mockCustomers[1]
  }
];

// Mock knowledge base entries
export const mockKnowledgeBase: KnowledgeBaseEntry[] = [
  {
    id: '1',
    question_text_example: 'How to handle user account lockouts?',
    answer_text: 'When a user account is locked due to multiple failed login attempts, follow these steps: 1) Verify the user\'s identity, 2) Check the security logs for any suspicious activity, 3) Reset the account lockout in the admin panel, 4) Have the user reset their password, 5) Document the incident in the security log.',
    created_at: '2024-01-10T10:00:00Z',
    updated_at: '2024-01-10T10:00:00Z',
    categories: ['security', 'accounts', 'lockout', 'authentication']
  },
  {
    id: '2',
    question_text_example: 'Standard backup verification process',
    answer_text: 'After each backup completes, verify its integrity by: 1) Checking the backup log for any errors, 2) Verifying file size matches expectations, 3) Running a test restore on a small dataset, 4) Documenting the verification in the backup log, 5) Alert the team if any issues are found.',
    created_at: '2024-01-08T09:00:00Z',
    updated_at: '2024-01-08T09:00:00Z',
    categories: ['operations', 'backup', 'verification', 'operations', 'data']
  }
];

// Mock dashboard stats
export const mockStats: DashboardStats = {
  pending: mockRequests.filter(req => req.status === 'pending').length,
  in_progress: mockRequests.filter(req => req.status === 'in_progress').length,
  resolved: mockRequests.filter(req => req.status === 'resolved').length
}; 