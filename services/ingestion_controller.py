import json
import os
from services.gmail_fetcher import authenticate_gmail, get_messages_gmail, process_gmail_message
from config import RUN_QUERY_TEMPLATE
import time, logging

from services.lambda_invoker import invoke_lambda_db
from services.state_manager import S3StateManager

logger = logging.getLogger(__name__)

state = S3StateManager(bucket=os.environ["STATE_BUCKET"])

def run_analysis_lambda_handler(event):
    start = time.time()
    curr_check_time = int(start)

    ts = state.get_last_checked_ts()
    if ts is None:
            logger.warning("No timestamp found, switching to bootstrap.")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No timestamp found, please run bootstrap."})
            }
    
    logger.info(f"Running scheduled fetch at {curr_check_time} from {ts}")
    
    query = RUN_QUERY_TEMPLATE.format(timestamp=ts)
    gmail = authenticate_gmail()
    messages = get_messages_gmail(service=gmail, query=query)

    for idx, message in enumerate(messages, start=1):
        gmail_id = message['id']

        result = process_gmail_message(idx, message, service=gmail, gmail_id=gmail_id)
        if result is None:
            continue
        
        job_data, message_data = result
        invoke_lambda_db(job_data, message_data)

    
    state.update_last_checked_ts(curr_check_time)

    return {"status": "done", "processed": len(messages)}
