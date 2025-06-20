import json
import logging
from services.ingestion_controller import run_analysis_lambda_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        response = run_analysis_lambda_handler(event)
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except Exception as e:
        logger.exception("❌ Error in lambda_handler")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)})
        }
