import os
import logging
import boto3
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# --- Abstract Interface ---
class StateManager(ABC):
    @abstractmethod
    def get_last_checked_ts(self) -> int | None:
        pass

    @abstractmethod
    def update_last_checked_ts(self, ts: int):
        pass


# --- Local Implementation (for dev) ---
class LocalStateManager(StateManager):
    def __init__(self, filepath: str = "last_checked.txt"):
        self.filepath = filepath

    def get_last_checked_ts(self) -> int | None:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                return int(f.read().strip())
        logger.info("Local state file not found.")
        return None

    def update_last_checked_ts(self, ts: int):
        with open(self.filepath, "w") as f:
            f.write(str(ts))
        logger.info(f"Updated local timestamp to {ts}")


# --- S3 Implementation (for Lambda) ---
class S3StateManager(StateManager):
    def __init__(self, bucket: str, key: str = "last_checked.txt"):
        self.bucket = bucket
        self.key = key
        self.s3 = boto3.client("s3")

    def get_last_checked_ts(self) -> int | None:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=self.key)
            return int(response["Body"].read().decode().strip())
        except self.s3.exceptions.NoSuchKey:
            logger.warning("No timestamp found in S3 – first run injection.py in bootstrap mode.")
            return None
        except Exception as e:
            logger.exception(f"Failed to get timestamp from S3: {e}")
            raise

    def update_last_checked_ts(self, ts: int):
        try:
            self.s3.put_object(Bucket=self.bucket, Key=self.key, Body=str(ts))
            logger.info(f"Updated timestamp in S3 to {ts}")
        except Exception as e:
            logger.exception(f"Failed to update timestamp in S3: {e}")
            raise
