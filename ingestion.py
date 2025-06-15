import time
from config import BOOTSTRAP_QUERY, RUN_QUERY_TEMPLATE
from db.init_db import init_db
from services.gmail_fetcher import authenticate_gmail, get_messages_gmail, process_gmail_messages
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def run_ingestion_pipeline(mode: str, last_checked_ts: int):
    init_db()
    gmail = authenticate_gmail()

    if mode == "run":
        logging.info("🔁 Running regular fetch: recent emails only.")
        query = RUN_QUERY_TEMPLATE.format(timestamp=last_checked_ts)
    else:
        logging.info("Running in bootstrap mode, fetching all messages.")
        query = BOOTSTRAP_QUERY

        messages = get_messages_gmail(service=gmail, query=query)
        process_gmail_messages(messages, gmail)

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['bootstrap', 'run'], default='bootstrap')
    args = parser.parse_args()
    
    run_ingestion_pipeline(mode=args.mode, last_checked_ts=None if args.mode == 'bootstrap' else int(time.time() - 60 * 60 * 24))