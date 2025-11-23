"""Orchestrates fetching, deduping, extracting, and exporting AI news."""

import time

from src.fetcher import fetch_news_newsapi
from src.deduper import dedupe_articles
from src.extractor import extract_structured
from src.exporter import export_to_csv
from src.config import PROCESSED_DIR
from src.normalizer import normalize_text
from src.utils import passes_hype_filter


def run_pipeline(query="AI startups", page_size=30):
    """Execute the ingestion-to-export pipeline."""

    print("[pipeline] fetching...")
    articles = fetch_news_newsapi(query=query, page_size=page_size)
    print(f"[pipeline] fetched {len(articles)} articles (saved in data/raw).")

    print("[pipeline] deduplicating...")
    deduped = dedupe_articles(articles)
    print(f"[pipeline] after dedupe: {len(deduped)} articles.")

    final = []
    for idx, art in enumerate(deduped, start=1):
        snippet = (art.get("title", "") + "\n" + (art.get("content") or ""))[:800]
        snippet = normalize_text(snippet)
        informative, density_score = passes_hype_filter(snippet)
        if not informative:
            print(
                f"[pipeline] skipped low-info article: {art.get('title')[:60]}... "
                f"(density_score={density_score})"
            )
            continue

        try:
            extracted, usage = extract_structured(snippet)
            extracted.update(
                {
                    "url": art.get("url"),
                    "source": art.get("source"),
                    "publishedAt": art.get("publishedAt"),
                    "title": art.get("title"),
                }
            )
            final.append(extracted)
            print(f"[pipeline] extracted for: {art.get('title')[:60]}... tokens_used={usage.get('total_tokens') if usage else 'n/a'}")
        except Exception as e:
            print("[pipeline] extraction failed for", art.get("id"), e)

        # Stay within Gemini free-tier rate limit (≈10 req/min)
        if idx < len(deduped):
            time.sleep(6)

    out_path = export_to_csv(final, filename="final.csv")
    print("[pipeline] exported to", out_path)
    return out_path

if __name__ == "__main__":
    run_pipeline()
