import os

IS_PRODUCTION = os.getenv("IS_PRODUCTION")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STATE_BUCKET = os.getenv("STATE_BUCKET")