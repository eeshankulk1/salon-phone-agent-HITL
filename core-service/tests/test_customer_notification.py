import pytest
import logging
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from database import crud
from api.services.handle_supervisor_communication import notify_customer_of_resolution
from api.services.help_requests import resolve_hr_and_create_kb


class TestCustomerNotification:
    """Test suite for customer notification functionality"""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger with captured output"""
        # Create a StringIO object to capture log output
        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        
        # Create a test logger
        logger = logging.getLogger('test_customer_notification')
        logger.setLevel(logging.INFO)
        logger.addHandler(ch)
        
        # Store the string capture for assertions
        logger.log_capture = log_capture_string
        return logger

    @pytest.fixture
    def sample_customer_data(self):
        """Sample customer data for testing"""
        return {
            'id': uuid.uuid4(),
            'display_name': 'John Doe',
            'phone_e164': '+1234567890'
        }

    @pytest.fixture
    def sample_help_request_data(self, sample_customer_data):
        """Sample help request data for testing"""
        return {
            'id': uuid.uuid4(),
            'customer_id': sample_customer_data['id'],
            'question_text': 'How do I reset my password?',
            'status': 'pending',
            'created_at': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=24)
        }

    def test_notify_customer_of_resolution_success(self, mock_logger, sample_customer_data, sample_help_request_data):
        """Test successful customer notification"""
        help_request_id = str(sample_help_request_data['id'])
        answer_text = "You can reset your password by clicking 'Forgot Password' on the login page."
        responder_id = "supervisor123"

        # Mock the database calls
        mock_help_request = Mock()
        mock_help_request.question_text = sample_help_request_data['question_text']
        mock_help_request.customer_id = sample_customer_data['id']

        mock_customer = Mock()
        mock_customer.display_name = sample_customer_data['display_name']
        mock_customer.phone_e164 = sample_customer_data['phone_e164']

        with patch('api.services.handle_supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('database.session.SessionLocal') as mock_session_class:
            
            # Setup help request mock
            mock_get_hr.return_value = {
                'help_request': mock_help_request,
                'supervisor_response': None
            }
            
            # Setup database session mock
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_customer

            # Call the function
            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify result
            assert result is True

            # Verify the session was closed
            mock_session.close.assert_called_once()

            # Verify log message contains expected content
            log_output = mock_logger.log_capture.getvalue()
            assert "SENDING RESOLUTION NOTIFICATION TO CUSTOMER" in log_output
            assert sample_customer_data['display_name'] in log_output
            assert sample_customer_data['phone_e164'] in log_output
            assert sample_help_request_data['question_text'] in log_output
            assert answer_text in log_output
            assert responder_id in log_output
            assert f"Hi {sample_customer_data['display_name']}!" in log_output

    def test_notify_customer_of_resolution_help_request_not_found(self, mock_logger):
        """Test notification when help request is not found"""
        help_request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor123"

        with patch('api.services.handle_supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr:
            # Mock help request not found
            mock_get_hr.return_value = None

            # Call the function
            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify result
            assert result is False

            # Verify error log
            log_output = mock_logger.log_capture.getvalue()
            assert f"Help request {help_request_id} not found for customer notification" in log_output

    def test_notify_customer_with_missing_customer_details(self, mock_logger, sample_help_request_data):
        """Test notification when customer details are missing"""
        help_request_id = str(sample_help_request_data['id'])
        answer_text = "Test answer"
        responder_id = "supervisor123"

        # Mock the database calls
        mock_help_request = Mock()
        mock_help_request.question_text = sample_help_request_data['question_text']
        mock_help_request.customer_id = sample_help_request_data['customer_id']

        with patch('api.services.handle_supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('database.session.SessionLocal') as mock_session_class:
            
            # Setup help request mock
            mock_get_hr.return_value = {
                'help_request': mock_help_request,
                'supervisor_response': None
            }
            
            # Setup database session mock - customer not found
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None

            # Call the function
            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify result
            assert result is True

            # Verify fallback customer info is used
            log_output = mock_logger.log_capture.getvalue()
            assert f"Customer {sample_help_request_data['customer_id']}" in log_output
            assert "No phone on file" in log_output

    def test_resolve_hr_and_create_kb_with_notification(self, mock_logger):
        """Test the complete resolution flow including customer notification"""
        request_id = str(uuid.uuid4())
        answer_text = "Test answer for resolution"
        responder_id = "supervisor456"

        # Mock data
        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"
        mock_help_request.customer_id = uuid.uuid4()

        mock_supervisor_response = Mock()
        mock_supervisor_response.answer_text = answer_text

        mock_resolved_request = Mock()

        with patch('api.services.help_requests.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('api.services.help_requests.crud.create_supervisor_response') as mock_create_resp, \
             patch('api.services.help_requests.create_knowledge_base_from_text') as mock_create_kb, \
             patch('api.services.help_requests.crud.update_help_request_status') as mock_update_status, \
             patch('api.services.help_requests.notify_customer_of_resolution') as mock_notify:

            # Setup mocks
            mock_get_hr.return_value = {'help_request': mock_help_request}
            mock_create_resp.return_value = mock_supervisor_response
            mock_update_status.return_value = mock_resolved_request
            mock_notify.return_value = True

            # Call the function
            resolved, supervisor_response = resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify all steps were called
            mock_get_hr.assert_called_once_with(request_id)
            mock_create_resp.assert_called_once_with(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id
            )
            mock_create_kb.assert_called_once()
            mock_update_status.assert_called_once_with(
                request_id=request_id,
                status="resolved"
            )
            mock_notify.assert_called_once_with(
                help_request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify results
            assert resolved == mock_resolved_request
            assert supervisor_response == mock_supervisor_response

    def test_resolve_hr_with_notification_failure(self, mock_logger):
        """Test resolution flow when customer notification fails"""
        request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor456"

        # Mock data
        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"

        mock_supervisor_response = Mock()
        mock_supervisor_response.answer_text = answer_text

        mock_resolved_request = Mock()

        with patch('api.services.help_requests.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('api.services.help_requests.crud.create_supervisor_response') as mock_create_resp, \
             patch('api.services.help_requests.create_knowledge_base_from_text'), \
             patch('api.services.help_requests.crud.update_help_request_status') as mock_update_status, \
             patch('api.services.help_requests.notify_customer_of_resolution') as mock_notify:

            # Setup mocks - notification fails
            mock_get_hr.return_value = {'help_request': mock_help_request}
            mock_create_resp.return_value = mock_supervisor_response
            mock_update_status.return_value = mock_resolved_request
            mock_notify.return_value = False

            # Call the function
            resolved, supervisor_response = resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify warning was logged
            log_output = mock_logger.log_capture.getvalue()
            assert f"Failed to send customer notification for help request {request_id}" in log_output

            # Verify results are still returned despite notification failure
            assert resolved == mock_resolved_request
            assert supervisor_response == mock_supervisor_response

    def test_notification_exception_handling(self, mock_logger):
        """Test that exceptions in notification are properly handled"""
        help_request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor123"

        with patch('api.services.handle_supervisor_communication.crud.get_help_request_with_answer') as mock_get_hr:
            # Mock an exception during database access
            mock_get_hr.side_effect = Exception("Database connection error")

            # Call the function
            result = notify_customer_of_resolution(
                help_request_id=help_request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify result
            assert result is False

            # Verify error log
            log_output = mock_logger.log_capture.getvalue()
            assert f"Error sending customer notification for help request {help_request_id}" in log_output
            assert "Database connection error" in log_output 