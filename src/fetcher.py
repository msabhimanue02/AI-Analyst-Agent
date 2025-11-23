import time
from datetime import datetime

import requests

from src.config import NEWSAPI_KEY, RAW_DIR
from src.utils import make_article_record, save_raw_article

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_NEWSAPI_RETRIES = 3
_BACKOFF_SECONDS = 5


def fetch_news_newsapi(query="AI startups", page_size=20):
    """Fetch articles from NewsAPI and persist them under data/raw."""

    if not NEWSAPI_KEY:
        raise RuntimeError("NEWSAPI_KEY not set in environment or .env")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWSAPI_KEY,
    }

    data = None
    for attempt in range(1, _MAX_NEWSAPI_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            break
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else None
            if status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_NEWSAPI_RETRIES:
                wait = _BACKOFF_SECONDS * attempt
                print(f"[fetcher] HTTP {status_code} from NewsAPI. Retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"NewsAPI request failed (status={status_code}).") from exc
        except requests.RequestException as exc:
            if attempt < _MAX_NEWSAPI_RETRIES:
                wait = _BACKOFF_SECONDS * attempt
                print(f"[fetcher] Network error {exc}. Retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError("NewsAPI request failed due to network error.") from exc

    if data is None:
        raise RuntimeError("NewsAPI response was empty after retries.")
    saved = []
    for a in data.get("articles", []):
        title = a.get("title")
        url = a.get("url")
        source = a.get("source", {}).get("name")
        publishedAt = a.get("publishedAt") or datetime.utcnow().isoformat()
        content = a.get("content") or a.get("description") or ""
        record = make_article_record(title, url, source, publishedAt, content, a)
        save_raw_article(record, RAW_DIR)
        saved.append(record)
    return saved
