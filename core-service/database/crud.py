from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timezone
from .session import SessionLocal
from .models import HelpRequest, KnowledgeBaseEntry, SupervisorResponse, Customer


def get_db_session():
    """Get database session with proper cleanup"""
    session = SessionLocal()
    try:
        return session
    finally:
        session.close()


# Helper functions for categories (list ↔ comma-separated string)

# Help Requests CRUD
def list_help_requests(status: Optional[str] = None) -> List[HelpRequest]:
    """List help requests, optionally filtered by status"""
    session = SessionLocal()
    try:
        query = session.query(HelpRequest)
        if status:
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


def update_help_request_status(request_id: str, status: str = "resolved") -> Optional[HelpRequest]:
    """Update help request status and resolved_at timestamp"""
    session = SessionLocal()
    try:
        help_request = session.query(HelpRequest).filter(HelpRequest.id == request_id).first()
        if not help_request:
            return None
        
        help_request.status = status
        if status == "resolved":
            help_request.resolved_at = datetime.now(timezone.utc)
        
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


# Knowledge Base CRUD
def list_kb(q: Optional[str] = None) -> List[KnowledgeBaseEntry]:
    """List knowledge base entries, optionally filtered by search query"""
    session = SessionLocal()
    try:
        query = session.query(KnowledgeBaseEntry)
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    KnowledgeBaseEntry.question_text_example.ilike(search_term),
                    KnowledgeBaseEntry.answer_text.ilike(search_term)
                )
            )
        return query.order_by(KnowledgeBaseEntry.created_at.desc()).all()
    finally:
        session.close()


def create_kb(data: dict) -> KnowledgeBaseEntry:
    """Create a new knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = KnowledgeBaseEntry(**data)
        session.add(kb_entry)
        session.commit()
        session.refresh(kb_entry)
        return kb_entry
    finally:
        session.close()


def update_kb(entry_id: str, data: dict) -> Optional[KnowledgeBaseEntry]:
    """Update a knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = session.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()
        if not kb_entry:
            return None
        
        for key, value in data.items():
            if hasattr(kb_entry, key):
                setattr(kb_entry, key, value)
        
        kb_entry.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(kb_entry)
        return kb_entry
    finally:
        session.close() 


def delete_kb(entry_id: str) -> bool:
    """Delete a knowledge base entry"""
    session = SessionLocal()
    try:
        kb_entry = session.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()
        if not kb_entry:
            return False
        
        session.delete(kb_entry)
        session.commit()
        return True
    finally:
        session.close()

def search_kb_by_embedding(query_vec: List[float], k: int = 5) -> List[dict]:
    """
    Vector KNN over knowledge_base using pgvector cosine distance, via SQLAlchemy's Vector comparator API.
    Returns rows with a 'sim' field (cosine similarity in [0,1]).
    """
    session = SessionLocal()
    try:
        # Use comparator for clarity; cosine_distance returns distance in [0, 2]
        distance_expr = KnowledgeBaseEntry.embedding.cosine_distance(query_vec)
        sim_expr = (1 - distance_expr).label('sim')

        rows = (
            session.query(
                KnowledgeBaseEntry.id,
                KnowledgeBaseEntry.question_text_example,
                KnowledgeBaseEntry.answer_text,
                sim_expr,
            )
            .filter(or_(KnowledgeBaseEntry.valid_to.is_(None), KnowledgeBaseEntry.valid_to > func.now()))
            .order_by(distance_expr)
            .limit(k)
            .all()
        )
        # convert to plain dicts
        return [
            {
                "id": r[0],
                "question_text_example": r[1],
                "answer_text": r[2],
                "sim": float(r[3]),
            }
            for r in rows
        ]
    finally:
        session.close()


# Customer CRUD
def create_customer(data: dict) -> Customer:
    """Create a new customer"""
    session = SessionLocal()
    try:
        customer = Customer(**data)
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer
    finally:
        session.close()