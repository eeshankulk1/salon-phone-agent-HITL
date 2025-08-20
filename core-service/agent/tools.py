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

    # Gate the status update so it does not trigger another LLM planning cycle
    search_done = asyncio.Event()

    async def _speak_status_update(timeout_s: float = 0.5) -> None:
        try:
            # If the search finishes before the timeout, do nothing
            await asyncio.wait_for(search_done.wait(), timeout=timeout_s)
            return
        except asyncio.TimeoutError:
            # Speak a brief status update directly without involving the LLM
            await context.session.say(
                "Let me check that for you… one moment.",
                allow_interruptions=True,
                add_to_chat_ctx=False,
            )

    status_update_task = asyncio.create_task(_speak_status_update(0.5))

    # Perform search off the event loop
    result = await asyncio.to_thread(search_knowledge_base_by_question, query, 1, 0.7)

    # Signal completion to cancel any pending status update
    search_done.set()

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
        
        # Inform the user directly; do not add to chat context to avoid extra LLM replies
        await context.session.say(
            "Let me check with my supervisor and get back to you.",
            allow_interruptions=False,
            add_to_chat_ctx=False,
        )

        # Cancel status update task if still pending
        status_update_task.cancel()
        return None
    
    # Cancel status update if search completed before timeout
    status_update_task.cancel()
    
    return result[0]["answer_text"]