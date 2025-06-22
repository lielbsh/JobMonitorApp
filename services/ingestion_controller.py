import time, logging
from config import RUN_QUERY_TEMPLATE
from settings import STATE_BUCKET

from services.gmail_fetcher import authenticate_gmail, get_messages_gmail, process_gmail_message
from services.lambda_invoker import invoke_lambda_db
from services.state_manager import S3StateManager

logger = logging.getLogger(__name__)

state = S3StateManager(STATE_BUCKET)

def run_analysis_lambda_handler(event):
    curr_check_time = int(time.time())

    try:
        ts = state.get_last_checked_ts()
        if ts is None:
            return {
                "status": "bootstrap_required", 
                "message": "No timestamp found, please run bootstrap."
            }
        
        logger.info(f"Running scheduled fetch at {curr_check_time} from {ts}")

        query = RUN_QUERY_TEMPLATE.format(timestamp=ts)
        gmail = authenticate_gmail()
        messages = get_messages_gmail(service=gmail, query=query)

        processed_count = 0

        for idx, message in enumerate(messages, start=1):
            gmail_id = message['id']
            result = process_gmail_message(idx, message, service=gmail, gmail_id=gmail_id)
            if result is None:
                continue
            
            job_data, message_data = result
            invoke_lambda_db(job_data, message_data)
            processed_count += 1

        state.update_last_checked_ts(curr_check_time)

        return {
            "status": "done",
            "fetched": len(messages),
            "processed": processed_count
        }
    
    except Exception:
        logger.exception(f"Error during analysis")
        raise
