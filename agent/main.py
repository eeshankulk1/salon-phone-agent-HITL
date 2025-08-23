from dotenv import load_dotenv
load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from agent.tools import search_knowledge_base
from core_service.api.services.customer import create_customer_for_session

import logging
logger = logging.getLogger("agent")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="""
                        You are a helpful voice AI assistant for a Salon. Your Salon's name is Beauty Palace. You are located in New York City. You will be asked questions by customers. 
                         
                         You have access to a search_knowledge_base tool to find answers to customer questions. When you use this tool:
                         - If the tool returns information, use it to formulate a natural, conversational response
                         - Do not repeat the exact text from the knowledge base verbatim
                         - Integrate the information smoothly into your answer
                         - If the tool returns None or empty result, it means the tool has already handled the response - do not generate additional responses
                         
                         Be conversational, helpful, and professional, but concise. But don't ask the user follow up questions. If you don't know the answer, don't make up an answer, use the search_knowledge_base tool to find the answer.
                         """,
                         tools=[search_knowledge_base]
                         )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    # Create a customer record for this session
    customer = create_customer_for_session(
        display_name="Voice Chat Customer"  # Default display name
        # In production, you might extract phone number from SIP trunk or other metadata
    )
    
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    # Store customer_id on the session for tool access
    setattr(session, "_app_ctx", {"customer_id": customer.id})

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
