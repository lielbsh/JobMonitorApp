import os
import pickle
import boto3
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


TOKEN_LOCAL_PATH = "/tmp/token.pickle"
S3_KEY = "token.pickle"
S3_BUCKET = os.environ.get("STATE_BUCKET")

s3 = boto3.client("s3")

def upload_token_to_s3():
    if not S3_BUCKET:
        raise ValueError("STATE_BUCKET env variable not set")
    try:
        s3.upload_file(TOKEN_LOCAL_PATH, S3_BUCKET, S3_KEY)
        logger.info("✅ Uploaded token.pickle to S3")
    except Exception as e:
        logger.error(f"❌ Failed to upload token to S3: {e}")
        raise

def download_token_from_s3():
    if not S3_BUCKET:
        raise ValueError("STATE_BUCKET env variable not set")
    try:
        s3.download_file(S3_BUCKET, S3_KEY, TOKEN_LOCAL_PATH)
        logger.info("📥 token.pickle downloaded from S3")
    except s3.exceptions.NoSuchKey:
        logger.warning("⚠️ token.pickle not found in S3 - please run init_token.py first")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to download token from S3: {e}")
        raise

def load_credentials() -> Credentials:
    try:
        download_token_from_s3()
        with open(TOKEN_LOCAL_PATH, "rb") as token:
            creds = pickle.load(token)
    except Exception:
        raise RuntimeError("🔒 Failed to load credentials from token.pickle")

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_LOCAL_PATH, "wb") as token:
            pickle.dump(creds, token)
        upload_token_to_s3()
        logger.info("🔁 Refreshed and re-uploaded token")

    return creds
