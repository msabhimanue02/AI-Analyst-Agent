# Analyst Agent Flow

```
NewsAPI Fetch --> Raw JSON Snapshot --> Deduper --> Hype Filter --> Gemini Extraction --> CSV Export
        |                                                       ^
        +-- retry/backoff if HTTP 429/5xx ---------------------+
```

1. **Fetch** – Pull latest "AI startups" articles (with retry on HTTP errors).
2. **Deduplicate** – Remove near-duplicates via Jaccard + TF-IDF cosine.
3. **Hype Filter** – Drop low-density snippets (length + keyword heuristics).
4. **Extract** – Call Gemini with retries/backoff; parse structured JSON.
5. **Export** – Append clean rows to `data/processed/final.csv`.
