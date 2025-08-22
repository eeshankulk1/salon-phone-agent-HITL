import pytest
import logging
import uuid
from unittest.mock import Mock, patch
from io import StringIO

from api.services.help_requests import resolve_hr_and_create_kb


class TestHelpRequestResolution:
    """Test suite focused on help request resolution flow"""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger with captured output"""
        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        
        logger = logging.getLogger('test_help_request_resolution')
        logger.setLevel(logging.INFO)
        logger.addHandler(ch)
        
        logger.log_capture = log_capture_string
        return logger

    def test_resolve_hr_and_create_kb_success(self, mock_logger):
        """Test successful complete resolution flow with customer notification"""
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

            # Verify all steps were called in correct order
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

    def test_resolve_hr_help_request_not_found(self, mock_logger):
        """Test resolution flow when help request is not found"""
        request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor456"

        with patch('api.services.help_requests.crud.get_help_request_with_answer') as mock_get_hr:
            # Mock help request not found
            mock_get_hr.return_value = None

            # Call the function
            resolved, supervisor_response = resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify results
            assert resolved is None
            assert supervisor_response is None

    def test_resolve_hr_supervisor_response_creation_fails(self, mock_logger):
        """Test resolution flow when supervisor response creation fails"""
        request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor456"

        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"

        with patch('api.services.help_requests.crud.get_help_request_with_answer') as mock_get_hr, \
             patch('api.services.help_requests.crud.create_supervisor_response') as mock_create_resp:

            # Setup mocks
            mock_get_hr.return_value = {'help_request': mock_help_request}
            mock_create_resp.return_value = None  # Creation fails

            # Call the function
            resolved, supervisor_response = resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify results
            assert resolved is None
            assert supervisor_response is None

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

            # Verify resolution still succeeds despite notification failure
            assert resolved == mock_resolved_request
            assert supervisor_response == mock_supervisor_response

    def test_knowledge_base_creation_with_supervisor_response_data(self, mock_logger):
        """Test that knowledge base entry is created with data from supervisor response"""
        request_id = str(uuid.uuid4())
        answer_text = "Original answer text"
        responder_id = "supervisor456"

        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"

        mock_supervisor_response = Mock()
        mock_supervisor_response.answer_text = "Modified answer text"  # Different from input

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
            resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify KB creation was called with supervisor response data
            mock_create_kb.assert_called_once()
            call_args = mock_create_kb.call_args
            
            # Check that it uses question from help request and answer from supervisor response
            assert call_args[1]['question'] == "Test question"
            assert call_args[1]['answer'] == "Modified answer text"  # From supervisor response
            assert call_args[1]['source_help_request_id'] == request_id

    def test_resolution_step_order(self, mock_logger):
        """Test that resolution steps execute in the correct order"""
        request_id = str(uuid.uuid4())
        answer_text = "Test answer"
        responder_id = "supervisor456"

        mock_help_request = Mock()
        mock_help_request.question_text = "Test question"

        mock_supervisor_response = Mock()
        mock_supervisor_response.answer_text = answer_text

        mock_resolved_request = Mock()

        call_order = []

        def track_get_hr(*args, **kwargs):
            call_order.append("get_help_request")
            return {'help_request': mock_help_request}

        def track_create_resp(*args, **kwargs):
            call_order.append("create_supervisor_response")
            return mock_supervisor_response

        def track_create_kb(*args, **kwargs):
            call_order.append("create_knowledge_base")

        def track_update_status(*args, **kwargs):
            call_order.append("update_status")
            return mock_resolved_request

        def track_notify(*args, **kwargs):
            call_order.append("notify_customer")
            return True

        with patch('api.services.help_requests.crud.get_help_request_with_answer', side_effect=track_get_hr), \
             patch('api.services.help_requests.crud.create_supervisor_response', side_effect=track_create_resp), \
             patch('api.services.help_requests.create_knowledge_base_from_text', side_effect=track_create_kb), \
             patch('api.services.help_requests.crud.update_help_request_status', side_effect=track_update_status), \
             patch('api.services.help_requests.notify_customer_of_resolution', side_effect=track_notify):

            # Call the function
            resolve_hr_and_create_kb(
                request_id=request_id,
                answer_text=answer_text,
                responder_id=responder_id,
                notification_logger=mock_logger
            )

            # Verify correct execution order
            expected_order = [
                "get_help_request",
                "create_supervisor_response", 
                "create_knowledge_base",
                "update_status",
                "notify_customer"
            ]
            assert call_order == expected_order 