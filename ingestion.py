# ingestion.py
import os
import time
from config import BOOTSTRAP_QUERY, RUN_QUERY_TEMPLATE
from db.init_db import init_db
from db.crud import email_exist, insert_email, update_or_create_job
from services.gmail_fetcher import authenticate_gmail, get_messages_gmail, process_gmail_message
import logging
import argparse
from scripts.init_token import upload_token_to_s3
from services.state_manager import S3StateManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def run_ingestion_pipeline_locally(query: str):
    init_db()
    gmail = authenticate_gmail()
    messages = get_messages_gmail(service=gmail, query=query)

    for idx, message in enumerate(messages, start=1):
        gmail_id = message['id']
        
        if email_exist(gmail_id):
            continue

        job_data, message_data = process_gmail_message(idx, message, service=gmail, gmail_id=gmail_id)

        if job_data.get("status") == "Not Relevant":
            insert_email(
            message_data=message_data,
            job_id=None
            )
            continue

        # Saves to db  
        job_id = update_or_create_job(job_data, message_data)
        if not job_id:
            continue
        
        insert_email(
            message_data=message_data,
            job_id=job_id
        )

    logging.info("✅ Ingestion completed.")

   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['bootstrap', 'run'], default='bootstrap')
    args = parser.parse_args()

    if args.mode == 'run':
        query = RUN_QUERY_TEMPLATE.format(last_checked_ts=int(time.time()-60*60*24))
        run_ingestion_pipeline_locally(query=query)
    else:
        try:
            state = S3StateManager(bucket=os.environ["STATE_BUCKET"])
            curr_check_time = int(time.time())
            
            run_ingestion_pipeline_locally(query=BOOTSTRAP_QUERY)
            logging.info("✅ Bootstrap ingestion completed.")

            state.update_last_checked_ts(curr_check_time)
            logging.info(f"✅ Updated last checked timestamp to {curr_check_time} in S3.")
            
        except Exception as e:
            logging.error(f"❌  Error during bootstrap ingestion: {e}")
