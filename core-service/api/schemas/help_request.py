from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class HelpRequestOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    question_text: str
    status: str
    priority: str = "LOW"  # Default priority as mentioned in requirements
    created_at: datetime
    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    answer_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class HelpRequestCreate(BaseModel):
    customer_id: uuid.UUID
    question_text: str
    expires_at: datetime
    call_id: Optional[uuid.UUID] = None
    normalized_key: Optional[str] = None


class HelpRequestResolve(BaseModel):
    answer_text: str
    responder_id: Optional[str] = None 