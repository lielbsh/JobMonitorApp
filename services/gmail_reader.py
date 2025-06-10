from datetime import datetime
import os.path
import pickle
import base64
import html
from bs4 import BeautifulSoup
from schemas import MessageData

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from datetime import datetime

from db.crud import email_exist, insert_email, update_or_create_job
from services.email_analysis import analyze_email, print_analysis

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

def extract_message_data(gmail_msg, gmail_id, gmail_thread_id) -> MessageData:
    """
    Extracts structured message information from Gmail API response.
    Returns a dict with from, subject, and body/snippet text.
    """
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
    date = datetime.fromtimestamp(int(gmail_msg.get('internalDate', 0)) // 1000)

    return MessageData(
        from_email=sender,
        subject=subject,
        date=date,
        body=body_text,
        gmail_id=gmail_id,
        thread_id=gmail_thread_id
    )          

def get_messages_gmail(service):
    number_of_messages = 6
    results = service.users().messages().list(userId='me', q=query, maxResults=number_of_messages).execute() # ids
    messages = results.get('messages', []) # [{id, threadId},...]
    print(f"{len(messages)} emails found") 

    return messages

def process_gmail_messages(messages, service):
    for idx, msg in enumerate(messages, start=1):
        gmail_id, gmail_thread_id = msg['id'], msg['threadId']
        gmail_msg_data = service.users().messages().get(userId='me', id=gmail_id, format='full').execute()
        if email_exist(gmail_id): continue

        message_data = extract_message_data(gmail_msg_data, gmail_id, gmail_thread_id)
        analysis = analyze_email(message_data)
        print_analysis(idx, analysis, message_data)

        # Saves to db  
        job_id = update_or_create_job(analysis, message_data)
        
        insert_email(
            message_data=message_data,
            job_id=job_id
        )
        


        