import os

IS_LAMBDA = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

if not IS_LAMBDA:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        raise ImportError("Missing python-dotenv for local development")

def get_env(key: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable '{key}' is missing.")
    return value


IS_PRODUCTION = IS_LAMBDA or get_env("IS_PRODUCTION", required=False) == "1"
DATABASE_URL = get_env("DATABASE_URL", required=IS_PRODUCTION, default="sqlite:///./JobMonitorApp.db")
OPENAI_API_KEY = get_env("OPENAI_API_KEY", required=False)
STATE_BUCKET = get_env("STATE_BUCKET", required=IS_PRODUCTION)
