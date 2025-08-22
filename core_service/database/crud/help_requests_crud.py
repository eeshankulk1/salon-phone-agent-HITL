from typing import List, Optional
from sqlalchemy import and_
from datetime import datetime, timezone
from ..session import SessionLocal
from ..models import HelpRequest, SupervisorResponse


def list_help_requests(status: Optional[str] = None) -> List[HelpRequest]:
    """List help requests, optionally filtered by status
    
    For pending requests, automatically excludes expired requests
    (where expires_at <= current time)
    """
    session = SessionLocal()
    try:
        query = session.query(HelpRequest)
        if status:
            if status == "pending":
                # For pending requests, filter out expired ones
                current_time = datetime.now(timezone.utc)
                query = query.filter(
                    and_(
                        HelpRequest.status == status,
                        HelpRequest.expires_at > current_time
                    )
                )
            else:
                query = query.filter(HelpRequest.status == status)
        return query.order_by(HelpRequest.created_at.desc()).all()
    finally:
        session.close()


def create_help_request(data: dict) -> HelpRequest:
    """Create a new help request"""
    session = SessionLocal()
    try:
        help_request = HelpRequest(**data)
        session.add(help_request)
        session.commit()
        session.refresh(help_request)
        return help_request
    finally:
        session.close()


def create_supervisor_response(request_id: str, answer_text: str, responder_id: Optional[str] = None) -> Optional[SupervisorResponse]:
    """Create a supervisor response for a help request"""
    session = SessionLocal()
    try:
        # Verify help request exists
        help_request = session.query(HelpRequest).filter(HelpRequest.id == request_id).first()
        if not help_request:
            return None
        
        # Create supervisor response
        response = SupervisorResponse(
            help_request_id=request_id,
            responder_id=responder_id,
            answer_text=answer_text
        )
        session.add(response)
        session.commit()
        session.refresh(response)
        return response
    finally:
        session.close()


def update_help_request_status(request_id: str, status: str = "resolved", cancel_reason: Optional[str] = None) -> Optional[HelpRequest]:
    """Update help request status and resolved_at timestamp"""
    session = SessionLocal()
    try:
        help_request = session.query(HelpRequest).filter(HelpRequest.id == request_id).first()
        if not help_request:
            return None
        
        help_request.status = status
        if status == "resolved":
            help_request.resolved_at = datetime.now(timezone.utc)
        elif status == "cancelled":
            help_request.cancel_reason = cancel_reason or "cancelled by supervisor"
        
        session.commit()
        session.refresh(help_request)
        return help_request
    finally:
        session.close()


def get_help_request_with_answer(request_id: str) -> Optional[dict]:
    """Get help request with its supervisor response (answer)"""
    session = SessionLocal()
    try:
        help_request = session.query(HelpRequest).filter(HelpRequest.id == request_id).first()
        if not help_request:
            return None
        
        # Get supervisor response
        supervisor_response = session.query(SupervisorResponse).filter(
            SupervisorResponse.help_request_id == request_id
        ).first()
        
        return {
            "help_request": help_request,
            "supervisor_response": supervisor_response
        }
    finally:
        session.close() 