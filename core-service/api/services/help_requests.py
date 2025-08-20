from database import crud
from .knowledge_base import create_knowledge_base_from_text
from .handle_supervisor_communication import text_supervisor_sync
from datetime import datetime, timezone, timedelta
import uuid

def resolve_hr_and_create_kb(request_id: str, answer_text: str, responder_id: str):
    """
    Resolve help request with proper flow:
    1. Create supervisor response record
    2. Use response data to create KB entry
    3. Update help request status to resolved
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
    # Default expiration: 24 hours from now
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
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
        "expires_at": expires_at,
        "status": "pending"
    }
    
    # Add call_id if provided
    if call_id:
        help_request_data["call_id"] = call_id
    
    # Create the help request
    help_request = crud.create_help_request(help_request_data)
    
    # If help request was created successfully, simulate texting the supervisor
    if help_request:
        try:
            text_supervisor_sync(str(help_request.id))
        except Exception as e:
            print(f"Error simulating supervisor text: {e}")
    
    return help_request

