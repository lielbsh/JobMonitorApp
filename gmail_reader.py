from datetime import datetime
import os.path
import pickle
import base64
import html
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

query = (
    '("application was sent" OR "application for" OR applied OR applying OR '
    '"application has been received" OR "thank you for applying" OR "received your CV" OR "submitting your resume" OR '
    '"thanks for your interest" OR "following the interview" OR "update regarding your application" OR '
    '"recruiting team" OR "job application") '
    '-subject:(newsletter OR promotion OR "get started" OR reset OR verify) '
    'newer_than:1m'
)

# query = (
#     'subject:("application was" OR "application for" OR applied OR applying OR opportunity OR interest OR         interview OR position OR "thanks for your interest" OR joining) '
#     '-subject:(newsletter OR promotion OR "get started") '
#     'newer_than:1m'
# )


def extract_message_info(msg_data):
    """
    Extracts structured message information from Gmail API response.
    Returns a dict with from, subject, and body/snippet text.
    """
    payload = msg_data.get('payload', {})

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
        snippet = msg_data.get('snippet', '') 
        print("** Body is empty – using snippet instead **")
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
    date = datetime.fromtimestamp(int(msg_data.get('internalDate', 0)) // 1000)

    return {
        "from": sender,
        "subject": subject,
        "body": body_text,
        "date": date
    }          

def get_messages_gmail(service):
    results = service.users().messages().list(userId='me', q=query, maxResults=3).execute() # ids
    messages = results.get('messages', []) # [{id, threadId},...]
    print(f"{len(messages)} emails found") 

    return messages

def process_gmail_messages(messages, service):
    for idx, msg in enumerate(messages, start=1):
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        msg_info = extract_message_info(msg_data)

        print("")
        print(f"\n[{idx}] 📧 EMAIL: {msg_info['subject']} | from {msg_info['from']}")
        print(msg_info['body'])


        