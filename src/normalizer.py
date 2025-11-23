"""Text normalization utilities for downstream NLP tasks."""

import re


def normalize_text(text: str) -> str:
    """Return a cleaned version of the input text."""

    if not text:
        return ""
    normalized = text.replace("\n", " ").strip()
    normalized = re.sub(r"(Read more:.*$)|(Continue reading.*$)", "", normalized, flags=re.I)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
