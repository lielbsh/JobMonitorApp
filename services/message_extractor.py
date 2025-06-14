import base64
from datetime import datetime
import html
from bs4 import BeautifulSoup
from schemas import MessageData

import logging
logger = logging.getLogger(__name__)

def extract_message_data(gmail_msg, gmail_id, gmail_thread_id) -> MessageData:
    """
    Extracts structured message information from Gmail API response.
    Returns a dict with from, subject, and body/snippet text.
    """
    try:
        payload = gmail_msg.get('payload', {})

        def decode_body(data):
            return html.unescape(base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8', errors='replace'))

        body_html = ""

        # Case 1: simple email
        if 'body' in payload and 'data' in payload['body']:
            body_html = decode_body(payload['body']['data'])

        # Case 2: multipart – check plain text first, then html
        elif 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                    body_html = decode_body(part['body']['data'])
                    break
            else:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                        body_html = decode_body(part['body']['data'])
                        break
        
        # Fallback: use snippet if body is empty
        if not body_html:
            snippet = gmail_msg.get('snippet', '') 
            print("Body is empty – using snippet instead")
            body_text = snippet.strip()[:500] if snippet else ""
        else:
            # Clean HTML into readable plain text
            soup = BeautifulSoup(body_html, "html.parser")
            text = soup.get_text(separator="\n").strip()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            body_text = "\n".join(lines)[:500]

        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        subject = headers.get('Subject', '')
        sender = headers.get('From', '')
        date = datetime.fromtimestamp(int(gmail_msg.get('internalDate', 0)) // 1000)

        return MessageData(
            from_email=sender,
            subject=subject,
            date=date,
            body=body_text,
            gmail_id=gmail_id,
            thread_id=gmail_thread_id
        )
    except Exception as e:
        logger.error(f"⚠️ Failed to extract message data for Gmail ID {gmail_id}: {e}")
        return None