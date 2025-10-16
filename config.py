
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")
HISTORY_FILE = os.getenv("HISTORY_FILE", "history.json")
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() in ("1", "true", "yes")
