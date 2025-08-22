from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid


class KnowledgeBaseOut(BaseModel):
    id: uuid.UUID
    question_text_example: str
    answer_text: str
    categories: List[str] = []  # Will be parsed from comma-separated string
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseCreate(BaseModel):
    question_text_example: str
    answer_text: str
    categories: List[str] = []
    normalized_key: Optional[str] = None
    source_help_request_id: Optional[uuid.UUID] = None


class KnowledgeBaseUpdate(BaseModel):
    question_text_example: Optional[str] = None
    answer_text: Optional[str] = None
    categories: Optional[List[str]] = None
    normalized_key: Optional[str] = None 