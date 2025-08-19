from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .session import Base
import uuid


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(Text)
    phone_e164 = Column(Text, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    livekit_room_id = Column(Text)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True))
    status = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HelpRequest(Base):
    __tablename__ = "help_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    normalized_key = Column(Text)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    cancel_reason = Column(Text)
    
    # Relationships
    customer = relationship("Customer")
    call = relationship("Call")


class SupervisorResponse(Base):
    __tablename__ = "supervisor_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    help_request_id = Column(UUID(as_uuid=True), ForeignKey("help_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    responder_id = Column(Text)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    help_request = relationship("HelpRequest")


class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    normalized_key = Column(Text)
    question_text_example = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    source_help_request_id = Column(UUID(as_uuid=True), ForeignKey("help_requests.id"))
    valid_to = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Note: metadata and embedding fields omitted for simplicity as per user requirements


class Followup(Base):
    __tablename__ = "followups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    help_request_id = Column(UUID(as_uuid=True), ForeignKey("help_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    channel = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    
    # Relationships
    help_request = relationship("HelpRequest")
    customer = relationship("Customer") 