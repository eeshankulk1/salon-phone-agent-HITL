import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import uuid


class TestHealthCheck:
    
    def test_health_check(self, client):
        """Test GET /healthz"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHelpRequestRoutes:
    
    @patch('database.crud.list_help_requests')
    def test_list_help_requests(self, mock_list_help_requests, client):
        """Test GET /api/help-requests"""
        # Mock the CRUD function return value
        mock_help_request = MagicMock()
        mock_help_request.id = uuid.uuid4()
        mock_help_request.customer_id = uuid.uuid4()
        mock_help_request.question_text = "How do I reset my password?"
        mock_help_request.status = "pending"
        mock_help_request.created_at = datetime.now(timezone.utc)
        mock_help_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_help_request.resolved_at = None
        
        mock_list_help_requests.return_value = [mock_help_request]
        
        response = client.get("/api/help-requests")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["question_text"] == "How do I reset my password?"
        assert data[0]["status"] == "pending"
        
        # Verify CRUD function was called without status filter
        mock_list_help_requests.assert_called_once_with(status=None)

    @patch('database.crud.list_help_requests')
    def test_list_help_requests_with_status_filter(self, mock_list_help_requests, client):
        """Test GET /api/help-requests with status filter"""
        mock_list_help_requests.return_value = []
        
        # Test with pending status
        response = client.get("/api/help-requests?status=pending")
        assert response.status_code == 200
        mock_list_help_requests.assert_called_with(status="pending")
        
        # Test with resolved status
        response = client.get("/api/help-requests?status=resolved")
        assert response.status_code == 200
        mock_list_help_requests.assert_called_with(status="resolved")

    @patch('database.crud.create_help_request')
    def test_create_help_request(self, mock_create_help_request, client):
        """Test POST /api/help-requests"""
        # Mock the CRUD function return value
        mock_help_request = MagicMock()
        mock_help_request.id = uuid.uuid4()
        mock_help_request.customer_id = uuid.uuid4()
        mock_help_request.question_text = "How do I change my email?"
        mock_help_request.status = "pending"
        mock_help_request.created_at = datetime.now(timezone.utc)
        mock_help_request.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_help_request.resolved_at = None
        
        mock_create_help_request.return_value = mock_help_request
        
        request_data = {
            "customer_id": str(uuid.uuid4()),
            "question_text": "How do I change my email?",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }
        
        response = client.post("/api/help-requests", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["question_text"] == "How do I change my email?"
        assert data["status"] == "pending"

    def test_create_help_request_invalid_data(self, client):
        """Test POST /api/help-requests with invalid data"""
        request_data = {
            "question_text": "Invalid request"
            # Missing required fields
        }
        
        response = client.post("/api/help-requests", json=request_data)
        assert response.status_code == 422  # Validation error


class TestKnowledgeBaseRoutes:
    
    @patch('database.crud.list_kb')
    def test_list_knowledge_base(self, mock_list_kb, client):
        """Test GET /api/knowledge-base"""
        # Mock the CRUD function return value
        mock_kb_entry = MagicMock()
        mock_kb_entry.id = uuid.uuid4()
        mock_kb_entry.question_text_example = "How to reset password?"
        mock_kb_entry.answer_text = "Go to settings and click reset password"
        mock_kb_entry.created_at = datetime.now(timezone.utc)
        mock_kb_entry.updated_at = datetime.now(timezone.utc)
        
        mock_list_kb.return_value = [mock_kb_entry]
        
        response = client.get("/api/knowledge-base")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["question_text_example"] == "How to reset password?"

    @patch('api.services.knowledge_base.embed_question')
    @patch('database.crud.create_kb')
    def test_create_knowledge_base_entry(self, mock_create_kb, mock_embed_question, client):
        """Test POST /api/knowledge-base"""
        # Mock the embedding function with proper 1536-dimension vector
        sample_embedding = [0.1] * 1536
        mock_embed_question.return_value = sample_embedding
        
        # Mock the CRUD function return value
        mock_kb_entry = MagicMock()
        mock_kb_entry.id = uuid.uuid4()
        mock_kb_entry.question_text_example = "How to login?"
        mock_kb_entry.answer_text = "Use your email and password"
        mock_kb_entry.created_at = datetime.now(timezone.utc)
        mock_kb_entry.updated_at = datetime.now(timezone.utc)
        
        mock_create_kb.return_value = mock_kb_entry
        
        kb_data = {
            "question_text_example": "How to login?",
            "answer_text": "Use your email and password",
            "categories": ["authentication", "login"]
        }
        
        response = client.post("/api/knowledge-base", json=kb_data)
        assert response.status_code == 200
        data = response.json()
        assert data["question_text_example"] == "How to login?"
        assert data["answer_text"] == "Use your email and password"
        
        # Verify that embed_question was called with the correct text
        mock_embed_question.assert_called_once_with("How to login?")
        
        # Verify that create_kb was called with embedding included
        args, kwargs = mock_create_kb.call_args
        kb_data_passed = args[0]
        assert "embedding" in kb_data_passed
        # For vector comparison, check length instead of direct equality
        assert len(kb_data_passed["embedding"]) == len(sample_embedding)

    def test_create_knowledge_base_entry_invalid_data(self, client):
        """Test POST /api/knowledge-base with invalid data"""
        kb_data = {
            "question_text_example": "Incomplete entry"
            # Missing answer_text
        }
        
        response = client.post("/api/knowledge-base", json=kb_data)
        assert response.status_code == 422  # Validation error

    @patch('api.services.knowledge_base.embed_question')
    def test_create_knowledge_base_entry_embedding_failure(self, mock_embed_question, client):
        """Test POST /api/knowledge-base when embedding generation fails"""
        # Mock embedding function to raise an exception
        mock_embed_question.side_effect = Exception("API rate limit exceeded")
        
        kb_data = {
            "question_text_example": "How to login?",
            "answer_text": "Use your email and password",
            "categories": ["authentication"]
        }
        
        response = client.post("/api/knowledge-base", json=kb_data)
        assert response.status_code == 500
        assert "API rate limit exceeded" in response.json()["detail"]
