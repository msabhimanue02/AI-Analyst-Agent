from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.normalizer import normalize_text


def jaccard(text_a, text_b):
    """Return Jaccard similarity between two whitespace-tokenized strings."""

    tokens_a = set(text_a.split())
    tokens_b = set(text_b.split())
    if not tokens_a and not tokens_b:
        return 1.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def dedupe_articles(articles, jaccard_thresh=0.6, tfidf_thresh=0.75):
    """Remove near-duplicate articles using Jaccard then TF-IDF cosine checks."""

    kept = []
    normalized_texts = []
    for article in sorted(articles, key=lambda x: x.get("publishedAt", ""), reverse=True):
        normalized = normalize_text(
            (article.get("title") or "") + " " + (article.get("content") or "")
        )
        is_duplicate = False
        for idx, _ in enumerate(kept):
            reference_text = normalized_texts[idx]
            if jaccard(normalized, reference_text) > jaccard_thresh:
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(article)
            normalized_texts.append(normalized)

    if len(normalized_texts) <= 1:
        return kept

    vectorizer = TfidfVectorizer().fit(normalized_texts)
    matrix = vectorizer.transform(normalized_texts)
    survivors = []
    for idx in range(matrix.shape[0]):
        row = matrix[idx]
        similarities = cosine_similarity(row, matrix).flatten()
        has_duplicate = any(
            other_idx != idx and similarities[other_idx] >= tfidf_thresh
            for other_idx in range(len(similarities))
        )
        if not has_duplicate:
            survivors.append(kept[idx])
    return survivors
