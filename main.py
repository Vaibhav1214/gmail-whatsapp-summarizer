import os

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from strands import Agent
from strands.models.gemini import GeminiModel

from config import settings
from gmail_tools import fetch_recent_emails_from_inbox
from logger import get_logger
from whatsapp_tools import send_whatsapp_message

# Initialize Logger and FastAPI App
log = get_logger("orchestrator")
app = FastAPI(
    title="Email-to-WhatsApp Agent Service",
    description=(
        "FastAPI service hosting the Strands Agent "
        "for Gmail-to-WhatsApp notifications"
    ),
    version="1.0.0",
)


def run_agent_workflow() -> str:
    """Executes the core Strands Agent loop to fetch, summarize, and dispatch emails."""
    log.info("Starting Strands Email-to-WhatsApp Agent orchestrator...")

    # Retrieve decrypted Gemini Key
    gemini_key = settings.GEMINI_API_KEY.get_secret_value()

    # Initialize Gemini LLM Model
    log.info("Initializing Google Gemini model interface (gemini-3.5-flash)...")
    model = GeminiModel(
        client_args={"api_key": gemini_key}, model_id="gemini-3.5-flash"
    )

    # Initialize the Strands Agent with validated custom tools
    log.info("Creating Strands Agent reason loop...")
    agent = Agent(
        model=model, tools=[fetch_recent_emails_from_inbox, send_whatsapp_message]
    )

    prompt = (
        "Check my Gmail for recent unread important emails. "
        "If you find any, summarize the emails (including sender, "
        "subject, date, and key content) and send the summary to my WhatsApp."
    )

    log.info("Dispatched prompt workflow execution command to Strands Agent loop.")
    response = agent(prompt)
    log.info("Agent execution cycle finished successfully.")
    return str(response)


@app.get("/")
@app.get("/health")
def health_check():
    """Liveness probe endpoint for Cloud Run container health checks."""
    return {
        "status": "healthy",
        "service": "email-to-whatsapp-agent",
        "configured_email": settings.GMAIL_EMAIL,
    }


@app.post("/trigger")
def trigger_agent(background_tasks: BackgroundTasks):
    """
    Asynchronous endpoint to trigger the agent loop in the background.
    Recommended for production to avoid HTTP timeout limits on serverless runners.
    """
    log.info("Received background agent trigger request.")
    background_tasks.add_task(run_agent_workflow)
    return {"message": "Agent execution successfully triggered in the background."}


@app.post("/trigger/sync")
def trigger_agent_sync():
    """
    Synchronous endpoint to trigger the agent loop and return results immediately.
    """
    log.info("Received synchronous agent trigger request.")
    try:
        result = run_agent_workflow()
        return {"status": "success", "result": result}
    except Exception as e:
        log.error(f"Synchronous agent run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # If run directly as a script, start local uvicorn server on $PORT or default 8080
    port = int(os.getenv("PORT", 8080))
    log.info(f"Launching local development server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
