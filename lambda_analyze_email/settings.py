import os

def require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

IS_PRODUCTION = "1"
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
STATE_BUCKET = require_env("STATE_BUCKET")
LAMBDA_DB_FUNCTION_NAME = require_env("LAMBDA_DB_FUNCTION_NAME", "lambda_db")