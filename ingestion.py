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

def run_ingestion_pipeline(query: str):
    init_db()
    gmail = authenticate_gmail()
    messages = get_messages_gmail(service=gmail, query=query)
    process_gmail_messages(messages, gmail)
    logging.info("✅ Ingestion completed.")

   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['bootstrap', 'run'], default='bootstrap')
    args = parser.parse_args()

    query = RUN_QUERY_TEMPLATE.format(last_checked_ts=int(time.time() - 60 * 60 * 24)) if args.mode == 'run' else BOOTSTRAP_QUERY
    run_ingestion_pipeline(query=query)