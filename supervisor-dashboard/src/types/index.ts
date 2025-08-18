export interface Customer {
  id: string;
  display_name?: string;
  phone_e164?: string;
  created_at: string;
}

export interface Call {
  id: string;
  customer_id: string;
  livekit_room_id?: string;
  started_at: string;
  ended_at?: string;
  status?: string;
  created_at: string;
}

export type RequestStatus = 'pending' | 'in_progress' | 'resolved' | 'cancelled';
export type RequestPriority = 'LOW' | 'MEDIUM' | 'HIGH';

export interface HelpRequest {
  id: string;
  call_id?: string;
  customer_id: string;
  question_text: string;
  normalized_key?: string;
  status: RequestStatus;
  priority?: RequestPriority;
  created_at: string;
  expires_at: string;
  resolved_at?: string;
  cancel_reason?: string;
  customer?: Customer;
}

export interface SupervisorResponse {
  id: string;
  help_request_id: string;
  responder_id?: string;
  answer_text: string;
  created_at: string;
}

export interface KnowledgeBaseEntry {
  id: string;
  normalized_key?: string;
  question_text_example: string;
  answer_text: string;
  source_help_request_id?: string;
  valid_to?: string;
  created_at: string;
  updated_at: string;
  metadata?: any;
  categories?: string[];
}

export interface Followup {
  id: string;
  help_request_id: string;
  customer_id: string;
  channel: string;
  payload?: any;
  status: 'pending' | 'sent';
  created_at: string;
  sent_at?: string;
}

export interface DashboardStats {
  pending: number;
  in_progress: number;
  resolved: number;
} 