import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import schedule
import time
import logging
from config import RUN_QUERY_TEMPLATE, BOOTSTRAP_QUERY
from ingestion import run_ingestion_pipeline
from services.state_manager import LocalStateManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize the state manager
state = LocalStateManager(filepath="last_checked.txt")

def scheduled_job(event):
    mode = event.get("mode", "run")
    curr_check_time = int(time.time())

    if mode not in ["bootstrap", "run"]:
        logger.error(f"Invalid mode: {mode}. Must be 'bootstrap' or 'run'.")
        return

    if mode == "bootstrap":
        logger.info("🚀 Running bootstrap fetch for all messages.")
        run_ingestion_pipeline(query=BOOTSTRAP_QUERY)
        state.update_last_checked_ts(curr_check_time)

    else:
        last_checked = state.get_last_checked_ts()
        if last_checked is None:
            logger.warning("No previous timestamp found. Running bootstrap mode instead.")
            run_ingestion_pipeline(query=BOOTSTRAP_QUERY)
            state.update_last_checked_ts(curr_check_time)
            return

        try:
            logger.info(f"🔁 Running scheduled fetch from {last_checked} to {curr_check_time}")
            query = RUN_QUERY_TEMPLATE.format(timestamp=last_checked)
            run_ingestion_pipeline(query=query)
            state.update_last_checked_ts(curr_check_time)
        except Exception as e:
            logger.error(f"❌ Error occurred during run: {e}")


def run_scheduled_job_locally():
    scheduled_job({"mode": "run"})


schedule.every(1).minutes.do(run_scheduled_job_locally)

logger.info("🕒 Scheduler started. Running every 1 minutes. Press Ctrl+C to stop.")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("🛑 Scheduler stopped.")
