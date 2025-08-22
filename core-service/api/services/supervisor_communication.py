import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from database import crud

logger = logging.getLogger("services.supervisor_response")

def notify_customer_of_resolution(
    help_request_id: str, 
    answer_text: str, 
    responder_id: str,
    notification_logger: logging.Logger
) -> bool:
    """
    Notify the customer about the resolution of their help request via simulated text.
    
    Args:
        help_request_id: The ID of the resolved help request
        answer_text: The answer provided by the supervisor
        responder_id: The ID of the person who provided the response
        notification_logger: Logger instance to use for the simulated text notification
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
        
    Raises:
        Exception: If there's an error fetching help request or customer details
    """
    try:
        # Fetch the help request with customer details
        help_request_data = crud.get_help_request_with_answer(help_request_id)
        
        if not help_request_data or not help_request_data.get("help_request"):
            notification_logger.error(f"Help request {help_request_id} not found for customer notification")
            return False
        
        help_request = help_request_data["help_request"]
        customer_question = help_request.question_text
        customer_id = help_request.customer_id
        
        # Get customer details for enhanced notification
        from database.session import SessionLocal
        from database.models import Customer
        
        session = SessionLocal()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            customer_name = customer.display_name if customer and customer.display_name else f"Customer {customer_id}"
            customer_phone = customer.phone_e164 if customer and customer.phone_e164 else "No phone on file"
        finally:
            session.close()
        
        # Send simulated text notification to customer
        notification_logger.info("\n" + "="*80 +
                                f"\n📱  SENDING RESOLUTION NOTIFICATION TO CUSTOMER" +
                                f"\n👤  Customer: {customer_name} ({customer_id})" +
                                f"\n📞  Phone: {customer_phone}" +
                                f"\n📋  Help Request ID: {help_request_id}" +
                                f"\n❓  Original Question: {customer_question}" +
                                f"\n✅  Resolution Answer: {answer_text}" +
                                f"\n👨‍💼  Resolved by: {responder_id}" +
                                f"\n💬  Text Message: Hi {customer_name}! We've got an answer to your question: '{customer_question}'. " +
                                f"Here's the response: {answer_text}. Thanks for your patience!" +
                                "\n" + "="*80)
        
        return True
        
    except Exception as e:
        notification_logger.error(f"Error sending customer notification for help request {help_request_id}: {e}")
        return False


def create_supervisor_notification(help_request_id: str) -> Optional[str]:
    """
    Create a followup record to notify the supervisor about a new help request.
    
    Args:
        help_request_id: The ID of the help request to notify supervisor about
        
    Returns:
        Optional[str]: The ID of the created followup record, or None if creation failed
        
    Raises:
        Exception: If there's an error fetching help request details or creating followup
    """
    try:
        # Fetch the help request details
        help_request_data = crud.get_help_request_with_answer(help_request_id)
        
        if not help_request_data or not help_request_data.get("help_request"):
            logger.error(f"Help request {help_request_id} not found for supervisor notification")
            return None
        
        help_request = help_request_data["help_request"]
        customer_question = help_request.question_text
        customer_id = help_request.customer_id
        
        # Create the supervisor notification payload
        notification_payload = {
            "message": f"Hey, I need help answering {customer_question}",
            "help_request_id": help_request_id,
            "customer_id": str(customer_id),
            "question": customer_question
        }
        
        # Create followup record for supervisor notification
        followup_data = {
            "help_request_id": help_request_id,
            "customer_id": customer_id,
            "channel": "supervisor_sms",
            "payload": notification_payload,
            "status": "pending"
        }
        
        followup = crud.create_followup(followup_data)
        
        if followup:
            logger.info(f"Created supervisor notification followup {followup.id} for help request {help_request_id}")
            return str(followup.id)
        else:
            logger.error(f"Failed to create supervisor notification for help request {help_request_id}")
            return None
        
    except Exception as e:
        logger.error(f"Error creating supervisor notification for help request {help_request_id}: {e}")
        return None


# Legacy functions - kept for backward compatibility during transition
async def simulate_text_supervisor(help_request_id: str) -> None:
    """
    DEPRECATED: Legacy function that logs supervisor texts.
    Use create_supervisor_notification instead for new implementations.
    """
    try:
        # Fetch the help request details
        help_request_data = await asyncio.to_thread(
            crud.get_help_request_with_answer, 
            help_request_id
        )
        
        if not help_request_data or not help_request_data.get("help_request"):
            logger.error(f"Help request {help_request_id} not found for supervisor text")
            return
        
        help_request = help_request_data["help_request"]
        customer_question = help_request.question_text
        customer_id = help_request.customer_id
        
        logger.info("\n" + "="*60 +
                   f"\n📱  TEXTING SUPERVISOR" +
                   f"\n📋  Help Request ID: {help_request_id}" +
                   f"\n👤  Customer ID: {customer_id}" +
                   f"\n❓  Customer Question: {customer_question}" +
                   f"\n💬  Text Message: Hey! A customer needs help with: '{customer_question}'. Can you provide an answer?" +
                   "\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error simulating text to supervisor for help request {help_request_id}: {e}")
        raise


def text_supervisor_sync(help_request_id: str) -> None:
    """
    DEPRECATED: Legacy synchronous wrapper for supervisor text simulation.
    Use create_supervisor_notification instead for new implementations.
    """
    try:
        # Fetch the help request details synchronously
        help_request_data = crud.get_help_request_with_answer(help_request_id)
        
        if not help_request_data or not help_request_data.get("help_request"):
            logger.error(f"Help request {help_request_id} not found for supervisor text")
            return
        
        help_request = help_request_data["help_request"]
        customer_question = help_request.question_text
        customer_id = help_request.customer_id
        
        logger.info("\n" + "="*60 +
                   f"\n📱  TEXTING SUPERVISOR" +
                   f"\n📋  Help Request ID: {help_request_id}" +
                   f"\n👤  Customer ID: {customer_id}" +
                   f"\n❓  Customer Question: {customer_question}" +
                   f"\n💬  Text Message: Hey! A customer needs help with: '{customer_question}'. Can you provide an answer?" +
                   "\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error simulating text to supervisor for help request {help_request_id}: {e}")
