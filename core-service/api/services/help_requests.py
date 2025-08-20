from database import crud
from .knowledge_base import create_knowledge_base_from_text

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