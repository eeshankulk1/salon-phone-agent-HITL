import asyncio
import json
from livekit.agents import function_tool, RunContext
from api.services.knowledge_base import search_knowledge_base_by_question
from api.services.help_requests import create_help_request_for_escalation
from api.services.customer import create_customer_for_session

@function_tool()
async def search_knowledge_base(context: RunContext, query: str) -> str:
    """Look up information in the knowledge base.
        
        Args:
            query: The question to look up in the knowledge base. Most likely a question from a customer. Output of this should be the answer to the question.
        """

    # Send a verbal status update to the user after a short delay
    async def _speak_status_update(delay: float = 0.5):
        await asyncio.sleep(delay)
        await context.session.generate_reply(instructions=f"""
            You are searching the knowledge base for \"{query}\" but it is taking a little while.
            Update the user on your progress, but be very brief.
        """)
    
    status_update_task = asyncio.create_task(_speak_status_update(0.5))

    # Perform search off the event loop
    result = await asyncio.to_thread(search_knowledge_base_by_question, query, 1, 0.7)

    if not result:
        # Prefer session-scoped app context
        customer_id = None
        app_ctx = getattr(context.session, "_app_ctx", None)
        if isinstance(app_ctx, dict):
            customer_id = app_ctx.get("customer_id")
        
        # Create help request for escalation
        help_request = await asyncio.to_thread(
            create_help_request_for_escalation,
            query,
            customer_id=customer_id
            # TODO: In practice, also pass call_id from context when available
            # call_id=context.call_id
        )
        
        await context.session.say(
            "Let me check with my supervisor and get back to you.",
            allow_interruptions=False,
            add_to_chat_ctx=True
        )
        return "No relevant entry found in knowledge base. Escalated to supervisor."
    
    
    # Cancel status update if search completed before timeout
    status_update_task.cancel()
    
    return result[0]["answer_text"]