import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock
from sqlalchemy.orm import sessionmaker
import uuid

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
            # Create proper 1536-dimension embedding vector
            sample_embedding = [0.1] * 1536
            kb_data = {
                "question_text_example": "How to login?",
                "answer_text": "Use your email and password",
                "embedding": sample_embedding
            }
            
            created_entry = crud.create_kb(kb_data)
            assert created_entry.question_text_example == "How to login?"
            assert created_entry.answer_text == "Use your email and password"
            # For vector comparison, check length and a few values instead of direct equality
            assert len(created_entry.embedding) == len(sample_embedding)
            assert created_entry.embedding[0] == sample_embedding[0]

    def test_create_supervisor_response(self, test_engine, sample_help_request):
        """Test creating a supervisor response"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            response = crud.create_supervisor_response(
                request_id=sample_help_request.id,  # Pass UUID object directly
                answer_text="Your password has been reset",
                responder_id="supervisor123"
            )
            
            assert response is not None
            assert response.help_request_id == sample_help_request.id
            assert response.answer_text == "Your password has been reset"
            assert response.responder_id == "supervisor123"

    def test_update_help_request_status(self, test_engine, sample_help_request):
        """Test updating help request status"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        with patch('database.crud.SessionLocal', TestSessionLocal):
            # Initially pending
            assert sample_help_request.status == "pending"
            assert sample_help_request.resolved_at is None
            
            # Update to resolved
            updated = crud.update_help_request_status(
                request_id=sample_help_request.id,  # Pass UUID object directly
                status="resolved"
            )
            
            assert updated is not None
            assert updated.status == "resolved"
            assert updated.resolved_at is not None


class TestFollowupCRUD:
    """Test suite for followup CRUD operations"""

    def test_create_followup(self):
        """Test creating a new followup record"""
        help_request_id = uuid.uuid4()
        customer_id = uuid.uuid4()
        
        followup_data = {
            "help_request_id": help_request_id,
            "customer_id": customer_id,
            "channel": "supervisor_sms",
            "payload": {"message": "Test notification"},
            "status": "pending"
        }
        
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            # Mock the created followup
            mock_followup = Mock()
            mock_followup.id = uuid.uuid4()
            mock_followup.help_request_id = help_request_id
            mock_followup.customer_id = customer_id
            mock_followup.channel = "supervisor_sms"
            mock_followup.status = "pending"
            
            # Setup session expectations
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None
            
            # Test create_followup function
            result = crud.create_followup(followup_data)
            
            # Verify session operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_followup_by_help_request(self):
        """Test retrieving followup by help request ID"""
        help_request_id = str(uuid.uuid4())
        
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_followup = Mock()
            mock_followup.help_request_id = help_request_id
            mock_followup.channel = "supervisor_sms"
            
            mock_session.query.return_value.filter.return_value.first.return_value = mock_followup
            
            result = crud.get_followup_by_help_request(help_request_id)
            
            assert result == mock_followup
            mock_session.query.assert_called_once()
            mock_session.close.assert_called_once()

    def test_list_followups_all(self):
        """Test listing all followups"""
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_followups = [Mock(), Mock()]
            mock_session.query.return_value.order_by.return_value.all.return_value = mock_followups
            
            result = crud.list_followups()
            
            assert result == mock_followups
            mock_session.close.assert_called_once()

    def test_list_followups_filtered(self):
        """Test listing followups with filters"""
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_query = Mock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value.all.return_value = []
            
            # Test with status filter
            crud.list_followups(status="pending")
            mock_query.filter.assert_called()
            
            # Test with channel filter  
            crud.list_followups(channel="supervisor_sms")
            
            # Test with both filters
            crud.list_followups(status="pending", channel="supervisor_sms")
            
            mock_session.close.assert_called()

    def test_update_followup_status(self):
        """Test updating followup status"""
        followup_id = str(uuid.uuid4())
        
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_followup = Mock()
            mock_followup.id = followup_id
            mock_followup.status = "pending"
            mock_followup.sent_at = None
            
            mock_session.query.return_value.filter.return_value.first.return_value = mock_followup
            
            result = crud.update_followup_status(followup_id, "sent")
            
            assert mock_followup.status == "sent"
            assert mock_followup.sent_at is not None
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
            mock_session.close.assert_called_once()

    def test_update_followup_status_not_found(self):
        """Test updating followup status when followup not found"""
        followup_id = str(uuid.uuid4())
        
        with patch('database.crud.SessionLocal') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = crud.update_followup_status(followup_id, "sent")
            
            assert result is None
            mock_session.close.assert_called_once() 