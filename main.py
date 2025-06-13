from db.init_db import init_db
from services.gmail_reader import authenticate_gmail, get_messages_gmail, process_gmail_messages
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

def main():
    init_db()
    gmail = authenticate_gmail()
    messages = get_messages_gmail(gmail)
    process_gmail_messages(messages, gmail)
        

if __name__ == '__main__':
    main()
