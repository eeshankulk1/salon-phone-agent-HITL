import pytest
import logging
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from io import StringIO

from api.services.supervisor_communication import notify_customer_of_resolution


class TestCustomerNotification:
    """Test suite for customer notification functionality"""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger with captured output"""
        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        
        logger = logging.getLogger('test_customer_notification')
        logger.setLevel(logging.INFO)
        logger.addHandler(ch)
        
        logger.log_capture = log_capture_string
        return logger

    def test_notify_customer_success(self, mock_logger):
        """Test successful customer notification"""
        help_request_id = str(uuid.uuid4())
        customer_id = uuid.uuid4()
        answer_text = "Test answer"
        responder_id = "supervisor123"

        # Mock the database calls
        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"
        mock_help_request.customer_id = customer_id

        mock_customer = Mock()
        mock_customer.display_name = "John Doe"
        mock_customer.phone_e164 = "+1234567890"

        mock_followup = Mock()
        mock_followup.id = uuid.uuid4()

        with patch('api.services.supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('api.services.supervisor_communication.SessionLocal') as mock_session_class, \
             patch('api.services.supervisor_communication.crud.create_followup') as mock_create_followup:
            
            mock_get_hr.return_value = {'help_request': mock_help_request}
            
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_customer

            mock_create_followup.return_value = mock_followup

            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            assert result is True
            mock_session.close.assert_called_once()

            # Verify followup creation was called
            mock_create_followup.assert_called_once()
            followup_data = mock_create_followup.call_args[0][0]
            assert followup_data["help_request_id"] == help_request_id
            assert followup_data["customer_id"] == customer_id
            assert followup_data["channel"] == "customer_sms"
            assert followup_data["status"] == "sent"

            # Verify log contains key elements
            log_output = mock_logger.log_capture.getvalue()
            assert "SENDING RESOLUTION NOTIFICATION TO CUSTOMER" in log_output
            assert "John Doe" in log_output

    def test_notify_customer_help_request_not_found(self, mock_logger):
        """Test notification when help request is not found"""
        help_request_id = str(uuid.uuid4())

        with patch('api.services.supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr:
            mock_get_hr.return_value = None

            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text="Test answer",
                responder_id="supervisor123",
                notification_logger=mock_logger
            )

            assert result is False

    def test_notify_customer_exception_handling(self, mock_logger):
        """Test exception handling during notification"""
        help_request_id = str(uuid.uuid4())

        with patch('api.services.supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr:
            mock_get_hr.side_effect = Exception("Database error")

            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text="Test answer",
                responder_id="supervisor123",
                notification_logger=mock_logger
            )

            assert result is False 