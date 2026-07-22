import imaplib
import email
from email.header import decode_header
from strands import tool

from config import settings
from logger import get_logger

log = get_logger("gmail")

def decode_mime_words(s):
    if not s:
        return ""
    clean_parts = []
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                clean_parts.append(word.decode(encoding or "utf-8", errors="ignore"))
            except Exception:
                clean_parts.append(word.decode("utf-8", errors="ignore"))
        else:
            clean_parts.append(word)
    return "".join(clean_parts)

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode(errors="ignore")
        except Exception:
            pass
    return ""

@tool
def fetch_recent_emails_from_inbox(max_emails: int = 10) -> str:
    """
    Fetches the most recent unread emails (or all recent emails if there are no unread ones) from the user's Inbox.
    Returns a formatted summary list of emails including Sender, Date, Subject, and a content snippet.
    """
    email_addr = settings.GMAIL_EMAIL
    app_pwd = settings.GMAIL_APP_PASSWORD.get_secret_value()
    
    log.info(f"Connecting to Gmail IMAP server on behalf of {email_addr}...")
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_addr, app_pwd)
        
        # Select INBOX
        mail.select('INBOX')
        
        # Search for UNSEEN (unread) emails first
        log.info("Searching for unread (UNSEEN) emails in inbox...")
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        # If no unread emails, fall back to ALL (recent emails)
        if not email_ids or email_ids == [b'']:
            log.info("No unread emails found. Querying all recent emails from Inbox...")
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
        if not email_ids or email_ids == [b'']:
            mail.close()
            mail.logout()
            log.warning("No emails found in the mailbox.")
            return "No emails found in your Inbox."
            
        # Take the most recent ones (at the end of the list)
        recent_ids = email_ids[-max_emails:]
        recent_ids.reverse()  # Order from newest to oldest
        log.info(f"Retrieving content for the top {len(recent_ids)} recent emails...")
        
        results = []
        for index, e_id in enumerate(recent_ids, 1):
            typ, data = mail.fetch(e_id, '(RFC822)')
            if typ != 'OK':
                log.warning(f"Failed to fetch content for email ID {e_id.decode()}")
                continue
            
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            sender = decode_mime_words(msg.get("From"))
            subject = decode_mime_words(msg.get("Subject"))
            date = msg.get("Date")
            body = get_email_body(msg)
            
            snippet = body[:300].replace('\n', ' ').strip() + ("..." if len(body) > 300 else "")
            
            results.append(
                f"--- Email #{index} ---\n"
                f"From: {sender}\n"
                f"Date: {date}\n"
                f"Subject: {subject}\n"
                f"Content Snippet: {snippet}\n"
            )
            
        mail.close()
        mail.logout()
        log.info("Emails fetched and parsed successfully.")
        
        if not results:
            return "No emails could be parsed."
            
        return "\n".join(results)
        
    except Exception as e:
        log.error(f"Error occurred during IMAP execution: {str(e)}")
        return f"Error retrieving emails: {str(e)}"
