from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..schemas.help_request import HelpRequestOut, HelpRequestCreate, HelpRequestResolve
from database import crud
from database.models import SupervisorResponse
from ..services.help_requests import resolve_hr_and_create_kb
import logging

router = APIRouter()
logger = logging.getLogger("routes.help_requests")


def _help_request_to_out(help_request, supervisor_response: Optional[SupervisorResponse] = None) -> HelpRequestOut:
    """Convert database model to output schema"""
    return HelpRequestOut(
        id=help_request.id,
        customer_id=help_request.customer_id,
        question_text=help_request.question_text,
        status=help_request.status,
        created_at=help_request.created_at,
        expires_at=help_request.expires_at,
        resolved_at=help_request.resolved_at,
        answer_text=supervisor_response.answer_text if supervisor_response else None
    )


@router.get("/", response_model=List[HelpRequestOut])
def list_help_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, resolved")
):
    """List help requests, optionally filtered by status"""
    try:
        help_requests = crud.list_help_requests(status=status)
        
        # Get supervisor responses for resolved requests to include answer_text
        results = []
        for hr in help_requests:
            supervisor_response = None
            if hr.status == "resolved":
                # Get the supervisor response for resolved requests
                result = crud.get_help_request_with_answer(str(hr.id))
                if result and result["supervisor_response"]:
                    supervisor_response = result["supervisor_response"]
            
            results.append(_help_request_to_out(hr, supervisor_response))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=HelpRequestOut)
def create_help_request(help_request: HelpRequestCreate):
    """Create a new help request"""
    try:
        help_request_data = help_request.model_dump()
        created_request = crud.create_help_request(help_request_data)
        return _help_request_to_out(created_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/resolve", response_model=HelpRequestOut)
def resolve_help_request(request_id: str, resolve_data: HelpRequestResolve):
    """Resolve a help request and notify the customer"""
    resolved, supervisor_response = resolve_hr_and_create_kb(
        request_id=request_id,
        answer_text=resolve_data.answer_text,
        responder_id=resolve_data.responder_id,
        notification_logger=logger,
    )
    if not resolved:
        raise HTTPException(status_code=404, detail="Help request not found")
    return _help_request_to_out(resolved, supervisor_response)


@router.get("/{request_id}", response_model=HelpRequestOut)
def get_help_request(request_id: str):
    """Get a specific help request by ID"""
    try:
        result = crud.get_help_request_with_answer(request_id)
        if not result:
            raise HTTPException(status_code=404, detail="Help request not found")
        
        help_request = result["help_request"]
        supervisor_response = result["supervisor_response"]
        
        return _help_request_to_out(help_request, supervisor_response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 