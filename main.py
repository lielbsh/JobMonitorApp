import time
from db.init_db import init_db
from services.gmail_fetcher import authenticate_gmail, get_messages_gmail, process_gmail_messages
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def main(mode: str, last_checked_ts: int):
    init_db()
    gmail = authenticate_gmail()

    if mode == "run":
        if last_checked_ts is None:
            raise ValueError("last_checked_ts must be provided in 'run' mode.")
        
        logging.info("🔁 Running regular fetch: recent emails only.")
        query = (
        f'after:{last_checked_ts} '
        '("application was sent" OR "application for" OR applied OR applying OR "your application to" OR '
        '"application has been received" OR "received your CV" OR "submitting your resume" OR '
        '"thanks for your interest" OR "interview" OR "job application" OR '
        '"recruiting team" OR "hr team" OR "Talent Acquisition Team") '
        '-subject:(newsletter OR promotion OR "get started" OR reset OR verify) '
    )
    else:
        logging.info("Running in bootstrap mode, fetching all messages.")
        query = (
            '("application was sent" OR "application for" OR applied OR applying OR '
            '"application has been received" OR "thank you for applying" OR "received your CV" OR "submitting your resume" OR '
            '"thanks for your interest" OR "following the interview" OR "update regarding your application" OR '
            '"recruiting team" OR "job application") '
            '-subject:(newsletter OR promotion OR "get started" OR reset OR verify) '
            'newer_than:60d ' # For development, adjust as needed
        )
    try:
        messages = get_messages_gmail(service=gmail, query=query)
        process_gmail_messages(messages, gmail)
    except Exception as e:
        logging.error(f"An error occurred while processing emails: {e}")
        raise

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['bootstrap', 'run'], default='bootstrap')
    args = parser.parse_args()
    
    main(mode=args.mode, last_checked_ts=None if args.mode == 'bootstrap' else int(time.time() - 60 * 60 * 24))