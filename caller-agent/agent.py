import logging
import os
import asyncio
import datetime
from datetime import timedelta
import json
from typing import Dict, Any, List

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import (
    cartesia,
    openai,
    deepgram,
    noise_cancellation,
    silero,
    turn_detector,
)

# Import our custom modules
from calendar_integration import CalendarIntegration
from twilio_integration import TwilioIntegration

# Load environment variables
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("task-followup-agent")

# Initialize integrations
calendar = CalendarIntegration(
    credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE"),
    calendar_id=os.getenv("CALENDAR_ID")
)

twilio = TwilioIntegration(
    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
    from_phone=os.getenv("TWILIO_PHONE_NUMBER")
)

# Store active calls and task contexts
active_calls = {}
task_contexts = {}

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def schedule_follow_up_calls():
    """
    Check for tasks that need follow-up and initiate calls
    """
    try:
        logger.info("Checking for tasks that need follow-up...")
        tasks = calendar.get_upcoming_tasks(days_ahead=7)
        
        for task in tasks:
            # Determine if this task needs a follow-up call
            due_date = datetime.datetime.fromisoformat(task['due'].replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # For example, call 2 days before the due date
            if now + timedelta(days=2) >= due_date:
                phone_number = task['assignee_phone']
                
                if phone_number:
                    logger.info(f"Initiating follow-up call for task '{task['title']}' to {phone_number}")
                    
                    # Generate LiveKit URL for this task
                    livekit_url = generate_livekit_url(task)
                    
                    # Make the call using Twilio
                    call_sid = twilio.make_call(phone_number, livekit_url, task)
                    
                    if call_sid:
                        # Store task context for this call
                        task_contexts[call_sid] = task
    
    except Exception as e:
        logger.error(f"Error scheduling follow-up calls: {str(e)}")
    
    # Schedule the next check
    asyncio.create_task(asyncio.sleep(3600))  # Check every hour
    asyncio.create_task(schedule_follow_up_calls())

def generate_livekit_url(task: Dict[str, Any]) -> str:
    """
    Generate a LiveKit URL with task data embedded
    """
    # In a real implementation, you would generate a secure LiveKit URL
    # This is a simplified version
    base_url = os.getenv("LIVEKIT_WEBHOOK_URL", "wss://your-livekit-instance.livekit.cloud")
    room_name = f"task-followup-{task['id']}"
    
    # In production, you would use a proper token generation here
    return f"{base_url}/{room_name}?task_id={task['id']}"

async def create_task_followup_system_prompt(task: Dict[str, Any]) -> str:
    """
    Create a system prompt for the follow-up call based on task data
    """
    return f"""
    You are a friendly and professional voice assistant making a follow-up call about a task.
    
    Task details:
    - Task title: {task['title']}
    - Due date: {task['due']}
    - Description: {task['description']}
    - Assigned to: {task['assignee']}
    
    Your goal is to:
    1. Verify you're speaking with the right person in a natural way
    2. Ask about the progress of the task
    3. If the task is not complete, ask when they expect to complete it
    4. If there are any blockers, note them
    5. Be friendly, conversational and human-like
    6. Keep responses brief and natural for a phone conversation
    7. End the call politely once you have the necessary information
    
    Avoid using robot-like language or identifying yourself as an AI. Speak like a helpful human assistant.
    """

async def update_task_from_conversation(task_id: str, conversation_context: llm.ChatContext) -> None:
    """
    Generate a summary of the conversation and update the task
    """
    try:
        # Generate a summary using OpenAI
        summary_prompt = llm.ChatContext().append(
            role="system",
            text="Summarize this task follow-up conversation. Extract: 1) Current status of the task, 2) Expected completion date if mentioned, 3) Any blockers or issues mentioned."
        )
        
        # Add the conversation messages
        for msg in conversation_context.messages:
            summary_prompt.append(role=msg.role, text=msg.text)
            
        # Use the same LLM as the agent to generate a summary
        llm_client = openai.LLM(model="gpt-4o-mini")
        summary_response = await llm_client.chat_completion(summary_prompt)
        summary = summary_response.message.text
        
        # Parse the summary for structured data
        # In a real implementation, you would use more robust parsing
        status = "in_progress"
        if "complete" in summary.lower():
            status = "completed"
        elif "not started" in summary.lower():
            status = "not_started"
        
        # Extract expected completion date with simple heuristics
        expected_completion = None
        if "expect" in summary.lower() and "complet" in summary.lower():
            # This is a simple extraction - in production use more robust methods
            for line in summary.split('\n'):
                if "expect" in line.lower() and "complet" in line.lower():
                    expected_completion = line
        
        # Update the task in Google Calendar
        status_update = {
            "status": status,
            "expected_completion": expected_completion,
            "notes": summary
        }
        
        calendar.update_task_status(task_id, status_update)
        logger.info(f"Updated task {task_id} with status: {status}")
        
    except Exception as e:
        logger.error(f"Error updating task from conversation: {str(e)}")

async def entrypoint(ctx: JobContext):
    # Get task information from context
    task_id = ctx.metadata.get("task_id")
    
    # Find the task data
    task_data = None
    for sid, data in task_contexts.items():
        if data['id'] == task_id:
            task_data = data
            break
    
    if not task_data:
        # Try to get task data from Google Calendar directly
        tasks = calendar.get_upcoming_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task_data = task
                break
    
    if not task_data:
        logger.error(f"Task data not found for task_id {task_id}")
        return
    
    # Create system prompt based on task
    system_prompt = await create_task_followup_system_prompt(task_data)
    
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=system_prompt,
    )

    logger.info(f"connecting to room {ctx.room.name} for task follow-up")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the participant to connect (should be the phone call recipient)
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        turn_detector=turn_detector.EOUModel(),
        min_endpointing_delay=0.5,
        max_endpointing_delay=5.0,
        noise_cancellation=noise_cancellation.BVC(),
        chat_ctx=initial_ctx,
    )

    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
        metrics.log_metrics(agent_metrics)
        usage_collector.collect(agent_metrics)
    
    # Store conversation for later analysis
    conversation_history = initial_ctx.copy()
    
    @agent.on("transcribed")
    def on_transcribed(transcript: str):
        conversation_history.append(role="user", text=transcript)
    
    @agent.on("response_sent")
    def on_response_sent(response: str):
        conversation_history.append(role="assistant", text=response)
    
    @agent.on("conversation_ended")
    async def on_conversation_ended():
        # Process conversation and update task
        await update_task_from_conversation(task_id, conversation_history)

    agent.start(ctx.room, participant)

    # Initial greeting based on task
    initial_greeting = f"Hello, this is a follow-up call about the task '{task_data['title']}'. Am I speaking with {task_data['assignee']}?"
    await agent.say(initial_greeting, allow_interruptions=True)


if __name__ == "__main__":
    # Start the scheduled task for checking calendar and making calls
    asyncio.create_task(schedule_follow_up_calls())
    
    # Run the LiveKit agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )

# import logging

# from dotenv import load_dotenv
# from livekit.agents import (
#     AutoSubscribe,
#     JobContext,
#     JobProcess,
#     WorkerOptions,
#     cli,
#     llm,
#     metrics,
# )
# from livekit.agents.pipeline import VoicePipelineAgent
# from livekit.plugins import (
#     cartesia,
#     openai,
#     deepgram,
#     noise_cancellation,
#     silero,
#     turn_detector,
# )


# load_dotenv(dotenv_path=".env.local")
# logger = logging.getLogger("voice-agent")


# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()


# async def entrypoint(ctx: JobContext):
#     initial_ctx = llm.ChatContext().append(
#         role="system",
#         text=(
#             "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
#             "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
#             "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
#         ),
#     )

#     logger.info(f"connecting to room {ctx.room.name}")
#     await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

#     # Wait for the first participant to connect
#     participant = await ctx.wait_for_participant()
#     logger.info(f"starting voice assistant for participant {participant.identity}")

#     # This project is configured to use Deepgram STT, OpenAI LLM and Cartesia TTS plugins
#     # Other great providers exist like Cerebras, ElevenLabs, Groq, Play.ht, Rime, and more
#     # Learn more and pick the best one for your app:
#     # https://docs.livekit.io/agents/plugins
#     agent = VoicePipelineAgent(
#         vad=ctx.proc.userdata["vad"],
#         stt=deepgram.STT(),
#         llm=openai.LLM(model="gpt-4o-mini"),
#         tts=cartesia.TTS(),
#         # use LiveKit's transformer-based turn detector
#         turn_detector=turn_detector.EOUModel(),
#         # minimum delay for endpointing, used when turn detector believes the user is done with their turn
#         min_endpointing_delay=0.5,
#         # maximum delay for endpointing, used when turn detector does not believe the user is done with their turn
#         max_endpointing_delay=5.0,
#         # enable background voice & noise cancellation, powered by Krisp
#         # included at no additional cost with LiveKit Cloud
#         noise_cancellation=noise_cancellation.BVC(),
#         chat_ctx=initial_ctx,
#     )

#     usage_collector = metrics.UsageCollector()

#     @agent.on("metrics_collected")
#     def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
#         metrics.log_metrics(agent_metrics)
#         usage_collector.collect(agent_metrics)

#     agent.start(ctx.room, participant)

#     # The agent should be polite and greet the user when it joins :)
#     await agent.say("Hey, how can I help you today?", allow_interruptions=True)


# if __name__ == "__main__":
#     cli.run_app(
#         WorkerOptions(
#             entrypoint_fnc=entrypoint,
#             prewarm_fnc=prewarm,
#         ),
#     )
