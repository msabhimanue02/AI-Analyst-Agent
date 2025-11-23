"""Project-wide configuration helpers and environment loading."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or _GOOGLE_API_KEY

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
_DEFAULT_MODELS = {
    "gemini": "models/gemini-flash-latest",  # official name returned by list_models
    "openai": "gpt-4o-mini",
}
GEMINI_MODEL = os.getenv("LLM_MODEL") or _DEFAULT_MODELS.get(LLM_PROVIDER, "")

if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY must be set in .env")

if LLM_PROVIDER == "gemini" and not GEMINI_MODEL:
    raise RuntimeError("Set LLM_MODEL in .env or rely on default models/gemini-flash-latest")

GSPREAD_CREDS = os.getenv("GSPREAD_CREDS", "")

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
