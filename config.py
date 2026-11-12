import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from the project root.
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()


def validate_config():
    """Check that required configuration is available."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add your API key to the .env file."
        )

    if GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "Replace the placeholder in .env with your actual Gemini API key."
        )

    if not GEMINI_MODEL:
        raise ValueError("GEMINI_MODEL cannot be empty.")

    return True
