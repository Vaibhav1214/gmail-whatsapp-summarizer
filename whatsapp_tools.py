from strands import tool
from twilio.rest import Client

from config import settings
from logger import get_logger

log = get_logger("whatsapp")

@tool
def send_whatsapp_message(message: str) -> str:
    """
    Sends a notification text message to the user's WhatsApp number.
    Use this tool to dispatch email summaries or execution statuses.
    """
    twilio_sid = settings.TWILIO_ACCOUNT_SID
    twilio_token = settings.TWILIO_AUTH_TOKEN.get_secret_value()
    twilio_from = settings.TWILIO_FROM_NUMBER
    twilio_to = settings.TWILIO_TO_NUMBER
    
    log.info(f"Preparing to send WhatsApp message via Twilio to {twilio_to}...")
    try:
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(
            body=message,
            from_=twilio_from,
            to=twilio_to
        )
        log.info(f"WhatsApp message dispatched successfully. Twilio SID: {msg.sid}")
        return f"WhatsApp message successfully sent via Twilio. Message SID: {msg.sid}"
    except Exception as e:
        log.error(f"Failed to dispatch WhatsApp message via Twilio: {str(e)}")
        return f"Error sending via Twilio: {str(e)}"
