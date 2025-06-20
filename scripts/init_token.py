import os
import pickle
import logging
import boto3
from google_auth_oauthlib.flow import InstalledAppFlow
from settings import STATE_BUCKET

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILENAME = "token.pickle"
S3_KEY = "token.pickle"

s3 = boto3.client("s3")

def authenticate_and_create_token():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("credentials.json not found in the project root.")
    
    if os.path.exists(TOKEN_FILENAME):
        logging.info("🔑 token.pickle already exists. Skipping authentication flow.")
        return

    logging.info("🔐 Starting Gmail authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILENAME, "wb") as token_file:
        pickle.dump(creds, token_file)
    logging.info("✅ token.pickle created successfully.")


def upload_token_to_s3():
    if not STATE_BUCKET:
        raise ValueError("STATE_BUCKET environment variable not set.")

    try:
        s3.upload_file(TOKEN_FILENAME, STATE_BUCKET, S3_KEY)
        logging.info(f"☁️ token.pickle uploaded to S3 bucket '{STATE_BUCKET}'")
    except Exception as e:
        logging.error(f"❌ Failed to upload token to S3: {e}")
        raise


def main():
    """Script to authenticate Gmail and upload token to S3 initially."""
    authenticate_and_create_token()
    upload_token_to_s3()


if __name__ == "__main__":
    main()
