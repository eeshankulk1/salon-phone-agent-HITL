from typing import List, Optional
from datetime import datetime, timezone
from ..session import SessionLocal
from ..models import Followup


def create_followup(data: dict) -> Followup:
    """Create a new followup record"""
    session = SessionLocal()
    try:
        followup = Followup(**data)
        session.add(followup)
        session.commit()
        session.refresh(followup)
        return followup
    finally:
        session.close()


def get_followup_by_help_request(help_request_id: str) -> Optional[Followup]:
    """Get followup record by help request ID"""
    session = SessionLocal()
    try:
        return session.query(Followup).filter(Followup.help_request_id == help_request_id).first()
    finally:
        session.close()


def list_followups(status: Optional[str] = None, channel: Optional[str] = None) -> List[Followup]:
    """List followups, optionally filtered by status and/or channel"""
    session = SessionLocal()
    try:
        query = session.query(Followup)
        if status:
            query = query.filter(Followup.status == status)
        if channel:
            query = query.filter(Followup.channel == channel)
        return query.order_by(Followup.created_at.desc()).all()
    finally:
        session.close()


def update_followup_status(followup_id: str, status: str, sent_at: Optional[datetime] = None) -> Optional[Followup]:
    """Update followup status and optionally set sent_at timestamp"""
    session = SessionLocal()
    try:
        followup = session.query(Followup).filter(Followup.id == followup_id).first()
        if not followup:
            return None
        
        followup.status = status
        if sent_at:
            followup.sent_at = sent_at
        elif status == "sent":
            followup.sent_at = datetime.now(timezone.utc)
        
        session.commit()
        session.refresh(followup)
        return followup
    finally:
        session.close() 