import json
import logging
from db.init_db import init_db
from db.crud import insert_email, update_or_create_job
from dateutil.parser import parse as parse_date

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        init_db()

        job_data = event["job_data"]
        job_data["last_update"] = parse_date(job_data["last_update"]).timestamp() 

        message_data = event["message_data"]
        message_data["date"] = parse_date(message_data["date"]).timestamp()
        
        if job_data.get("status") == "Not Relevant":
            insert_email(message_data=message_data, job_id=None)
            logger.info("Skipped non-relevant job.")
            return {"status": "skipped"}

        job_id = update_or_create_job(job_data, message_data)
        if not job_id:
            logger.warning("Failed to insert job.")
            return {"status": "error"}

        insert_email(message_data=message_data, job_id=job_id)
        logger.info("Successfully inserted job and email.")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error in lambda_db: {e}")
        return {"status": "error", "message": str(e)}
