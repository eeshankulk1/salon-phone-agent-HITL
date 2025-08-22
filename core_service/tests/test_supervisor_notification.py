import pytest
import uuid
from unittest.mock import Mock, patch

from api.services.communication import create_supervisor_notification
from api.services.help_requests import create_help_request_for_escalation


class TestSupervisorNotification:
    """Test suite for supervisor notification functionality"""

    def test_create_supervisor_notification_success(self):
        """Test successful creation of supervisor notification"""
        help_request_id = str(uuid.uuid4())
        customer_id = uuid.uuid4()
        question_text = "How do I reset my password?"
        
        mock_help_request = Mock()
        mock_help_request.question_text = question_text
        mock_help_request.customer_id = customer_id
        
        mock_followup = Mock()
        mock_followup.id = uuid.uuid4()
        
        with patch('api.services.communication.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('api.services.communication.crud.create_followup') as mock_create_followup:
            
            mock_get_hr.return_value = {'help_request': mock_help_request}
            mock_create_followup.return_value = mock_followup
            
            result = create_supervisor_notification(help_request_id)
            
            assert result == str(mock_followup.id)
            
            # Verify followup creation with correct data
            mock_create_followup.assert_called_once()
            call_args = mock_create_followup.call_args[0][0]
            
            assert call_args["help_request_id"] == help_request_id
            assert call_args["customer_id"] == customer_id
            assert call_args["channel"] == "supervisor_sms"
            assert call_args["status"] == "pending"
            
            # Verify payload structure
            payload = call_args["payload"]
            assert question_text in payload["message"]
            assert payload["help_request_id"] == help_request_id

    def test_create_supervisor_notification_help_request_not_found(self):
        """Test supervisor notification when help request is not found"""
        help_request_id = str(uuid.uuid4())
        
        with patch('api.services.communication.crud.get_help_request_with_answer') as mock_get_hr:
            mock_get_hr.return_value = None
            
            result = create_supervisor_notification(help_request_id)
            
            assert result is None


class TestEscalationFlow:
    """Test suite for escalation flow"""

    def test_create_help_request_for_escalation_success(self):
        """Test successful escalation with notification"""
        question_text = "Test question"
        customer_id = str(uuid.uuid4())
        
        mock_help_request = Mock()
        mock_help_request.id = uuid.uuid4()
        followup_id = str(uuid.uuid4())
        
        with patch('api.services.help_requests.crud.create_help_request') as mock_create_hr, \
             patch('api.services.help_requests.create_supervisor_notification') as mock_create_notification, \
             patch('builtins.print'):
            
            mock_create_hr.return_value = mock_help_request
            mock_create_notification.return_value = followup_id
            
            result = create_help_request_for_escalation(
                question_text=question_text,
                customer_id=customer_id
            )
            
            assert result == mock_help_request
            mock_create_hr.assert_called_once()
            mock_create_notification.assert_called_once_with(str(mock_help_request.id))

    def test_escalation_with_notification_failure(self):
        """Test escalation when notification fails"""
        question_text = "Test question"
        customer_id = str(uuid.uuid4())
        
        mock_help_request = Mock()
        mock_help_request.id = uuid.uuid4()
        
        with patch('api.services.help_requests.crud.create_help_request') as mock_create_hr, \
             patch('api.services.help_requests.create_supervisor_notification') as mock_create_notification, \
             patch('builtins.print'):
            
            mock_create_hr.return_value = mock_help_request
            mock_create_notification.return_value = None  # Notification fails
            
            result = create_help_request_for_escalation(
                question_text=question_text,
                customer_id=customer_id
            )
            
            # Help request still created despite notification failure
            assert result == mock_help_request 