import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from agent.watch_help_requests import HelpWatcher
from database import crud

logger = logging.getLogger("services.supervisor_response")

async def handle_supervisor_response(
    help_request_id: str,
    query: str,
    watcher: HelpWatcher,
    on_response_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> tuple[str, Dict[str, Any]]:
    """
    Handle supervisor response for a help request by listening for PostgreSQL notifications.
    
    Args:
        help_request_id: The ID of the help request to listen for
        query: The original query for logging purposes
        watcher: The HelpWatcher instance to use for listening
        on_response_callback: Optional callback function to execute when response is received
        
    Returns:
        Tuple of (answer_text, payload) when supervisor responds
        
    Raises:
        Exception: If there's an error waiting for or processing the supervisor response
    """
    try:
        logger.info("\n" + "="*60 +
                   f"\n🔔  WAITING FOR SUPERVISOR RESPONSE" +
                   f"\n📋  Help Request ID: {help_request_id}" +
                   f"\n❓  Query: {query}" +
                   "\n" + "="*60)
        
        # Wait for supervisor response (no timeout - wait indefinitely)
        answer_text, payload = await watcher.wait(help_request_id)
        
        # Fetch the full help request details to get the original question
        help_request_data = await asyncio.to_thread(
            crud.get_help_request_with_answer, 
            help_request_id
        )
        
        original_question = query  # fallback to the query parameter
        if help_request_data and help_request_data.get("help_request"):
            original_question = help_request_data["help_request"].question_text
        
        logger.info("\n" + "="*60 +
                   f"\nSorry for the delay, I've got an answer to your question: {original_question}" +
                   f"\nThe answer to your question is: {answer_text}" +
                   f"\n\n👨‍💼  Responder ID: {payload.get('responder_id', 'Unknown')}" +
                   f"\n📋  Help Request ID: {help_request_id}" +
                   "\n" + "="*60)
        
        # Execute callback if provided
        if on_response_callback:
            await on_response_callback(answer_text, payload)
        
        return answer_text, payload
        
    except Exception as e:
        logger.error(f"Error handling supervisor response for help request {help_request_id}: {e}")
        raise


async def simulate_text_supervisor(help_request_id: str) -> None:
    """
    Simulate texting the supervisor about a new help request.
    
    Args:
        help_request_id: The ID of the help request to send to supervisor
        
    Raises:
        Exception: If there's an error fetching help request details
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
    Synchronous wrapper to simulate texting the supervisor about a new help request.
    This function can be called from synchronous backend code.
    
    Args:
        help_request_id: The ID of the help request to send to supervisor
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
