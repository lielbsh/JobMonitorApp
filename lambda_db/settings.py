import os

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

IS_PRODUCTION = "1"
DATABASE_URL = require_env("DATABASE_URL")