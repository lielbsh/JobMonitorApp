import boto3
import json
import logging
from settings import LAMBDA_DB_FUNCTION_NAME

logger = logging.getLogger(__name__)

client = boto3.client("lambda")

def invoke_lambda_db(job_data: dict, message_data: dict):
    serialize_datetime_fields(job_data, message_data)
    payload = {
        "job_data": job_data,
        "message_data": message_data
    }

    try:
        response = client.invoke(
            FunctionName=LAMBDA_DB_FUNCTION_NAME,
            InvocationType="Event",  # async invocation 
            Payload=json.dumps(payload).encode("utf-8")
        )
        logger.info(f"✅ Successfully invoked lambda {LAMBDA_DB_FUNCTION_NAME}")
        return response
    
    except Exception:
        logger.exception(f"❌ Failed to invoke lambda {LAMBDA_DB_FUNCTION_NAME}")
        raise


def serialize_datetime_fields(job_data: dict, message_data: dict):
    job_data["last_update"] = job_data["last_update"].isoformat()
    message_data["date"] = message_data["date"].isoformat()
