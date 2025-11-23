"""Model-powered extraction utilities."""

import json
import re
import time

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

PROMPT_TEMPLATE = """
Extract structured JSON from the following news text.

Return ONLY valid JSON with the following keys:
- company_name (string or null)
- category (one of: 'Video AI','Generative AI','Funding','Product','People','Other')
- sentiment_score (float between -1.0 and 1.0)
- is_funding_news (true or false)

Text:
{text}

Return ONLY the JSON object. No explanation.
"""


_MAX_GEMINI_RETRIES = 3


def _generate_with_retry(model, prompt):
    for attempt in range(1, _MAX_GEMINI_RETRIES + 1):
        try:
            return model.generate_content(prompt)
        except google_exceptions.ResourceExhausted as exc:
            wait = getattr(getattr(exc, "retry_delay", None), "seconds", None)
            wait = wait or 10 * attempt
            print(f"[extractor] Gemini quota exhausted. Retrying in {wait}s...")
            time.sleep(wait)
        except google_exceptions.GoogleAPICallError as exc:
            if attempt == _MAX_GEMINI_RETRIES:
                raise RuntimeError(f"Gemini API error: {exc.message}") from exc
            wait = 5 * attempt
            print(f"[extractor] Gemini error {exc.message}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Gemini API did not respond after retries.")


def extract_structured(text):
    """Call Gemini to extract structured attributes from raw text."""

    prompt = PROMPT_TEMPLATE.format(text=text)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = _generate_with_retry(model, prompt)
    content = (response.text or "").strip()

    usage = {"tokens_used": "gemini_free"}
    try:
        return json.loads(content), usage
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.S)
        if match:
            return json.loads(match.group(0)), usage
        raise ValueError("Gemini response did not contain valid JSON.")
