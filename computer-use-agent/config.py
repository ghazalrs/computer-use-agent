import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("MODEL_ID", "anthropic/claude-sonnet-4-5")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_MAX_STEPS = 20
DEFAULT_TIMEOUT = 30
