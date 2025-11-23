import json
import re
import uuid
from datetime import datetime
from pathlib import Path

_INFORMATION_KEYWORDS = {
    "raise",
    "funding",
    "launch",
    "release",
    "product",
    "research",
    "partnership",
    "acquire",
    "deal",
    "seed",
    "series",
    "merger",
    "platform",
}


def make_article_record(title, url, source, publishedAt, content, raw):
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "url": url,
        "source": source,
        "publishedAt": publishedAt,
        "content": content,
        "raw": raw,
    }


def save_raw_article(record, raw_dir):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    path = Path(raw_dir) / f"{ts}_{record['id']}.json"
    with open(path, "w", encoding="utf8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return str(path)


def load_json(path):
    import json

    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def information_density_score(text: str) -> float:
    """Return a heuristic score (0-1) estimating how information-dense the text is."""

    if not text:
        return 0.0
    tokens = [tok for tok in re.findall(r"[A-Za-z0-9']+", text.lower()) if tok]
    if not tokens:
        return 0.0
    unique_ratio = len(set(tokens)) / len(tokens)
    keyword_hits = sum(1 for tok in tokens if tok in _INFORMATION_KEYWORDS)
    keyword_score = min(keyword_hits / 3, 1.0)
    length_score = min(len(text) / 900, 1.0)
    score = (0.45 * unique_ratio) + (0.35 * keyword_score) + (0.2 * length_score)
    return round(score, 3)


def passes_hype_filter(text: str, min_chars: int = 280, min_score: float = 0.4) -> tuple[bool, float]:
    """Return whether text is informative enough plus the computed score."""

    score = information_density_score(text)
    passes = len(text or "") >= min_chars and score >= min_score
    return passes, score
