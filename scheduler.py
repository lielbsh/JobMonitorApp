import os
import schedule
import time
import logging
from ingestion import run_ingestion_pipeline

STATE_FILE = "last_checked.txt"

logger = logging.getLogger(__name__)

def get_last_checked_ts() -> int | None:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    else:
        logging.info("State file not found.")
        return None

def update_last_checked_ts(curr_checked: int):
    with open(STATE_FILE, "w") as f:
        f.write(str(curr_checked))
        logging.info(f" Updated last_checked_ts to {curr_checked}")

def scheduled_job(event):
    mode = event.get("mode", "run")
    curr_check_time = int(time.time())

    if mode not in ["bootstrap", "run"]:
        logging.error(f"Invalid mode: {mode}. Must be 'bootstrap' or 'run'.")
        return
    
    if mode == "bootstrap":
        logging.info("Running bootstrap fetch for all messages.")
        run_ingestion_pipeline(mode="bootstrap", last_checked_ts=None)
        update_last_checked_ts(curr_check_time)
    else:
        last_checked = get_last_checked_ts()
        if last_checked is None:
            logging.warning("No previous timestamp found. Running bootstrap mode instead.")
            run_ingestion_pipeline(mode="bootstrap", last_checked_ts=None)
            update_last_checked_ts(curr_check_time)
            return
        
        try:
            logger.info(f"🔔 Running scheduled fetch from {last_checked} to {curr_check_time}")
            run_ingestion_pipeline(mode="run", last_checked_ts=last_checked)
            update_last_checked_ts(curr_check_time)
        except Exception as e:
            logger.error(f"Error occurred: {e}")

def run_scheduled_job_locally():
    scheduled_job({"mode": "run"})

schedule.every(1).minutes.do(run_scheduled_job_locally)

logger.info("🕒 Scheduler started. Running every 1 minutes. Press Ctrl+C to stop.")

# Run immediately once, for dev testing
# scheduled_job()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("🛑 Scheduler stopped.")


# To run this script, run:
# python scheduler.py  
# It will run the scheduled job every minute, fetching new emails and processing them.
# If this is the first run, you can set the mode to "bootstrap" to fetch all messages. 
