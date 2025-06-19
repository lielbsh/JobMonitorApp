import os.path
import pickle
from services.gmail_token_manager import load_credentials
from services.message_extractor import extract_message_data
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from services.email_analysis import get_job_data_from_email, print_job_details

import logging
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    if os.getenv("IS_PRODUCTION"):
        creds = load_credentials()
    else:
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


def get_messages_gmail(service, max_messages=80, query=None):
    email_list_response = service.users().messages().list(userId='me', q=query, maxResults=max_messages).execute()

    messages = email_list_response.get('messages', []) 
    logger.info(f"{len(messages)} emails found") 
    messages.reverse()

    return messages


from typing import Optional, Tuple

def process_gmail_message(idx, message, service, gmail_id) -> Tuple[dict, dict] | None:
    gmail_thread_id = message['threadId']
    gmail_msg_data = service.users().messages().get(userId='me', id=gmail_id, format='full').execute()
    
    message_data = extract_message_data(gmail_msg_data, gmail_id, gmail_thread_id)
    if message_data is None:
        print(f"[{idx}] Skipping email {gmail_id} – could not extract data.")
        return None
    
    print(f"\n[{idx}] 📧 EMAIL: {message_data.subject} | from {message_data.from_email}")

    job_data = get_job_data_from_email(message_data)
    if job_data is None:    
        logger.warning(f"[{idx}] Skipping message - analysis failed.")
        return None
    
    print_job_details(job_data)
    return job_data.to_dict(), message_data.to_dict()

        