from database import crud
from .knowledge_base import create_knowledge_base_from_text
from .communication import create_supervisor_notification, create_customer_notification
from datetime import datetime, timezone, timedelta
import uuid
import logging

def resolve_hr_and_create_kb(
    request_id: str, 
    answer_text: str, 
    responder_id: str,
    notification_logger: logging.Logger
):
    """
    Resolve help request with proper flow:
    1. Create supervisor response record
    2. Use response data to create KB entry
    3. Update help request status to resolved
    4. Notify customer of resolution
    """
    # 1) Fetch help request to get question text
    help_request_with_answer = crud.get_help_request_with_answer(request_id)
    if not help_request_with_answer or not help_request_with_answer.get("help_request"):
        return None, None

    help_request = help_request_with_answer["help_request"]
    question_text = help_request.question_text

    # 2) Create supervisor response record FIRST
    supervisor_response = crud.create_supervisor_response(
        request_id=request_id,
        answer_text=answer_text,
        responder_id=responder_id,
    )
    
    if not supervisor_response:
        return None, None

    # 3) Use supervisor response data to create KB entry
    create_knowledge_base_from_text(
        question=question_text,
        answer=supervisor_response.answer_text,  # Use data from supervisor response
        source_help_request_id=request_id,
    )

    # 4) Update help request status to resolved
    resolved = crud.update_help_request_status(
        request_id=request_id,
        status="resolved"
    )

    # 5) Notify customer of resolution
    notification_success = create_customer_notification(
        help_request_id=request_id,
        answer_text=supervisor_response.answer_text,
        responder_id=responder_id,
        notification_logger=notification_logger
    )
    
    if not notification_success:
        notification_logger.warning(f"Failed to send customer notification for help request {request_id}")

    return resolved, supervisor_response


def create_help_request_for_escalation(question_text: str, customer_id: str = None, call_id: str = None):
    """
    Create a help request for escalation when knowledge base search fails.
    
    Args:
        question_text: The customer's question that needs escalation
        customer_id: Optional customer ID (defaults to a placeholder if not available)
        call_id: Optional call ID for the current call
    
    Returns:
        Created help request object or None if creation fails
    """
    
    # Require valid customer_id; convert string to UUID if needed
    if isinstance(customer_id, str):
        try:
            customer_id = uuid.UUID(customer_id)
        except ValueError:
            print(f"Invalid customer_id format: {customer_id}")
            return None
    
    help_request_data = {
        "customer_id": customer_id,
        "question_text": question_text,
        "status": "pending"
    }
    
    # Add call_id if provided
    if call_id:
        help_request_data["call_id"] = call_id
    
    # Create the help request
    help_request = crud.create_help_request(help_request_data)
    
    # If help request was created successfully, create supervisor notification
    if help_request:
        try:
            followup_id = create_supervisor_notification(str(help_request.id))
            if followup_id:
                print(f"Created supervisor notification followup {followup_id} for help request {help_request.id}")
            else:
                print(f"Warning: Failed to create supervisor notification for help request {help_request.id}")
        except Exception as e:
            print(f"Error creating supervisor notification: {e}")
    
    return help_request

