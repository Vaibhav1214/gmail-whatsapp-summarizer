import functions_framework
from strands import Agent
from strands.models.gemini import GeminiModel

from config import settings
from logger import get_logger
from gmail_tools import fetch_recent_emails_from_inbox
from whatsapp_tools import send_whatsapp_message

log = get_logger("gcf_orchestrator")

@functions_framework.http
def run_agent_workflow(request):
    """
    HTTP Google Cloud Function entrypoint.
    Triggered periodically by Google Cloud Scheduler to check emails and notify.
    """
    log.info("Google Cloud Function triggered. Starting Strands Agent execution loop...")
    
    try:
        # Retrieve settings (Pydantic automatically reads standard environment variables injected by GCP)
        gemini_key = settings.GEMINI_API_KEY.get_secret_value()

        # Initialize Model
        model = GeminiModel(
            client_args={"api_key": gemini_key},
            model_id="gemini-3.5-flash"
        )
        
        # Initialize Agent
        agent = Agent(
            model=model,
            tools=[fetch_recent_emails_from_inbox, send_whatsapp_message]
        )
        
        prompt = (
            "Check my Gmail for recent unread important emails. "
            "If you find any, summarize the emails (including sender, subject, date, and key content) "
            "and send the summary to my WhatsApp."
        )
        
        log.info("Invoking Strands Agent reasoning loop inside Cloud Function...")
        response = agent(prompt)
        log.info("Agent execution completed successfully.")
        
        return {"status": "success", "agent_output": response}, 200
        
    except Exception as e:
        log.critical(f"Cloud Function event loop failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}, 500
