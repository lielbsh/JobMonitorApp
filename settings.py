import os

IS_LAMBDA = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

if not IS_LAMBDA:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        raise ImportError("Missing python-dotenv for local development")

def get_env(key: str, require: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if value is None and require:
        raise EnvironmentError(f"Required environment variable '{key}' is missing.")
    return value


IS_PRODUCTION = get_env("IS_PRODUCTION", default="0")
DATABASE_URL = get_env("DATABASE_URL", default="sqlite:///./JobMonitorApp.db")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
STATE_BUCKET = get_env("STATE_BUCKET", require=IS_LAMBDA, default=None)