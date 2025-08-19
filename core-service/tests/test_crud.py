import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker

from database import crud


class TestHelpRequestsCRUD:
    
    def test_list_help_requests_all(self, test_engine, sample_help_request):
        """Test listing all help requests"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            requests = crud.list_help_requests()
            assert len(requests) == 1
            assert requests[0].question_text == "How do I reset my password?"

    def test_list_help_requests_by_status(self, test_engine, sample_help_request):
        """Test filtering help requests by status"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            # Test pending requests
            pending_requests = crud.list_help_requests(status="pending")
            assert len(pending_requests) == 1
            
            # Test resolved requests (should be empty)
            resolved_requests = crud.list_help_requests(status="resolved")
            assert len(resolved_requests) == 0

    def test_create_help_request(self, test_engine, sample_customer):
        """Test creating a new help request"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            request_data = {
                "customer_id": sample_customer.id,
                "question_text": "Test question",
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=2)
            }
            
            created_request = crud.create_help_request(request_data)
            assert created_request.question_text == "Test question"
            assert created_request.status == "pending"
            assert created_request.customer_id == sample_customer.id


class TestKnowledgeBaseCRUD:
    
    def test_list_kb_all(self, test_engine, sample_kb_entry):
        """Test listing all knowledge base entries"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            entries = crud.list_kb()
            assert len(entries) == 1
            assert entries[0].question_text_example == "How to reset password?"

    def test_list_kb_with_search(self, test_engine, sample_kb_entry):
        """Test searching knowledge base entries"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            # Search for matching term
            results = crud.list_kb(q="password")
            assert len(results) == 1
            
            # Search for non-matching term
            results = crud.list_kb(q="login")
            assert len(results) == 0

    def test_create_kb_entry(self, test_engine):
        """Test creating a new knowledge base entry"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            kb_data = {
                "question_text_example": "How to login?",
                "answer_text": "Use your email and password"
            }
            
            created_entry = crud.create_kb(kb_data)
            assert created_entry.question_text_example == "How to login?"
            assert created_entry.answer_text == "Use your email and password" 