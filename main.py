from strands import Agent
from strands.models.gemini import GeminiModel

from config import settings
from logger import get_logger
from gmail_tools import fetch_recent_emails_from_inbox
from whatsapp_tools import send_whatsapp_message

log = get_logger("orchestrator")

def main():
    log.info("Starting Strands Email-to-WhatsApp Agent orchestrator...")
    
    # Retrieve decrypted Gemini Key
    gemini_key = settings.GEMINI_API_KEY.get_secret_value()

    # Initialize Gemini LLM Model
    log.info("Initializing Google Gemini model interface (gemini-3.5-flash)...")
    model = GeminiModel(
        client_args={"api_key": gemini_key},
        model_id="gemini-3.5-flash"
    )
    
    # Initialize the Strands Agent with validated custom tools
    log.info("Creating Strands Agent reason loop...")
    agent = Agent(
        model=model,
        tools=[fetch_recent_emails_from_inbox, send_whatsapp_message]
    )
    
    prompt = (
        "Check my Gmail for recent unread important emails. "
        "If you find any, summarize the emails (including sender, subject, date, and key content) "
        "and send the summary to my WhatsApp."
    )
    
    log.info("Dispatched prompt workflow execution command to Strands Agent loop.")
    try:
        response = agent(prompt)
        log.info("Agent execution cycle finished successfully.")
        
        print("\n=== Agent Execution Log Output ===")
        print(response)
        print("==================================\n")
        
    except Exception as e:
        log.critical(f"Unhandled exception crashed Strands Agent event loop: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
