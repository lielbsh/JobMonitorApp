import time
import os
from ingestion import run_ingestion_pipeline
from services.state_manager import S3StateManager
from config import BOOTSTRAP_QUERY, RUN_QUERY_TEMPLATE

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

state = S3StateManager(bucket=os.environ["STATE_BUCKET"])

def lambda_handler(event, context):
    start = time.time()
    mode = event.get("mode", "run")
    curr_check_time = int(start)
    
    try:
        if mode == "run":
            ts = state.get_last_checked_ts()
            if ts is None:
                logging.warning("No timestamp found, switching to bootstrap.")
                run_ingestion_pipeline(query=BOOTSTRAP_QUERY)
                state.update_last_checked_ts(curr_check_time)
            else:
                logging.info(f"Running scheduled fetch from {ts} to {curr_check_time}")
                run_ingestion_pipeline(query=RUN_QUERY_TEMPLATE.format(last_checked_ts=ts))
                state.update_last_checked_ts(curr_check_time)
        elif mode == "bootstrap":
            logging.info("Running bootstrap fetch for all messages.")
            run_ingestion_pipeline(query=BOOTSTRAP_QUERY)
            state.update_last_checked_ts(curr_check_time)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        return {
            "statusCode": 200,
            "body": f"Lambda executed in {time.time() - curr_check_time:.3f} seconds"
        }
    
    except Exception as e:
        logger.exception("❌ Lambda failed:")
        return {
            "statusCode": 500,
            "body": f"Lambda failed: {str(e)}"
        }
