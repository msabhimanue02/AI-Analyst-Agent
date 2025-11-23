# AI Analyst Agent

Automation pipeline that fetches AI news, deduplicates overlapping stories, and extracts structured insights with Google Gemini before exporting an analyst-ready CSV.

---

## Selected Challenge Task
- **Track:** Automation Logic (Generative AI focus)
- **Task:** Option 2 – “Analyst” Agent (Advanced Automation)
- **Goal:** Build an automated flow that ingests unstructured content and produces structured intelligence with minimal manual effort.

## Project Overview
1. **Fetch:** Pulls the latest AI/startup articles via NewsAPI with retry/backoff on 429/5xx errors.
2. **Deduplicate:** Runs Jaccard overlap then TF-IDF cosine checks to eliminate near-identical stories.
3. **Normalize:** Cleans and truncates article snippets (≈800 chars) before any downstream calls.
4. **Hype filter:** Scores information density (length + keyword diversity) and skips marketing fluff.
5. **Extract:** Calls Gemini (`models/gemini-flash-latest`) with a strict JSON prompt and automatic retries.
6. **Export:** Writes consolidated insights to `data/processed/final.csv` (or other sinks in the future).

```
src/
  fetcher.py      # NewsAPI client
  deduper.py      # Similarity-based deduplication
  normalizer.py   # Text cleaning helpers
  extractor.py    # Gemini prompt + parsing logic
  exporter.py     # CSV writer
  pipeline.py     # Orchestrates the end-to-end run
data/
  raw/            # Filled at runtime
  processed/      # Filled at runtime
```

### Component details
- `fetcher.py` – handles NewsAPI auth, retries, and persists every response to `data/raw/` for auditing.
- `deduper.py` – keeps only one article per event using Jaccard + TF-IDF cosine checks.
- `utils.py` – hosts the information-density "hype" filter plus helpers for raw snapshot storage.
- `extractor.py` – prompts Gemini for the `company_name`, `category`, `sentiment_score`, and `is_funding_news` fields and retries on quota errors.
- `pipeline.py` – glues everything together, throttling LLM calls to respect free-tier limits (~6s spacing).

## Prerequisites
- Python 3.10+ (Google recommends 3.11, but 3.10.11 works today)
- NewsAPI key (`NEWSAPI_KEY`)
- Gemini key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)

## Setup
1. **Clone & enter repo**
   ```bash
   git clone <repo-url>
   cd ai-analyst-agent
   ```
2. **Create and activate virtual env**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**
   ```bash
   copy .env.example .env
   ```
   Fill in:
   - `NEWSAPI_KEY=<your key>`
   - `GEMINI_API_KEY=<your key>` (or rely on `GOOGLE_API_KEY`)
   - Optional overrides: `LLM_PROVIDER=gemini`, `LLM_MODEL=models/gemini-flash-latest`

## Running the Pipeline
```bash
python -m src.pipeline
```
- Defaults fetch 30 “AI startups” articles and write to `data/processed/final.csv`.
- To customize the query or page size, invoke the helper from a Python shell:
  ```python
  from src.pipeline import run_pipeline
  run_pipeline(query="AI infrastructure", page_size=20)
  ```
- Raw snapshots remain under `data/raw/*.json` for traceability.

## Libraries & Model Choices
| Component | Choice | Justification |
|-----------|--------|---------------|
| LLM | `models/gemini-flash-latest` | Low-latency JSON generation with latest public Gemini release. |
| HTTP | `requests` | Reliable, lightweight REST client. |
| Deduplication | `scikit-learn`, `fuzzywuzzy`, `python-Levenshtein` | Combine TF-IDF cosine similarity with token overlap to minimize duplicates. |
| Data | `pandas` | Simple tabular export before CSV write. |
| Config | `python-dotenv` | Keep secrets outside source files. |

## Demo Video
  - **Demo Video:** https://www.loom.com/share/2cff85474845416a80fa7c1cc2ddaafa

## Logic Flow Diagram
- See `docs/flow.md` for the high-level pipeline diagram and step-by-step description.

## Resetting Outputs
- Raw fetches live in `data/raw/` and final CSVs in `data/processed/`.
- To re-run from a clean slate, delete both directories’ contents (e.g., `Remove-Item data\raw\* -Recurse -Force` on PowerShell) before executing the pipeline again.

## Submission Checklist
- [ ] README updated with task selection, setup, reasoning (this file ✅)
- [ ] `.env` filled locally (not committed)
- [ ] `data/raw` & `data/processed` contain only runtime artifacts (clean by default)
- [ ] Demo link or screenshots included
- [ ] Reply to recruiter with repo link and subject `Submission: AI Intern Challenge - <Your Name>`

## Coding Standards & Notes
- Code follows PEP 8 and is modular (`src/*`).
- No unused folders/files remain (docs, notebooks, tests removed as requested).
- Future improvements: retry logic on 429 with exponential backoff, richer categorization taxonomy, Dockerfile for reproducible runtime.
