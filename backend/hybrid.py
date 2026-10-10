"""RepoMentor - Week 3 Day 2: hybrid search (embedding + BM25) using RRF."""
from retriever import retrieve
from keyword_search import keyword_search

RRF_K = 60  # standard constant


def _key(c: dict) -> tuple:
    return (c["file_path"], c["start_line"], c["end_line"])


def hybrid_search(repo_url: str, query: str, k: int = 5, pool: int = 20) -> list[dict]:
    """Merge embedding and BM25 results with Reciprocal Rank Fusion."""
    semantic = retrieve(repo_url, query, k=pool)
    keyword = keyword_search(repo_url, query, n_results=pool)

    scores = {}
    chunks = {}
    for results in (semantic, keyword):
        for rank, c in enumerate(results):
            key = _key(c)
            scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
            chunks.setdefault(key, c)

    ranked = sorted(scores, key=lambda key: scores[key], reverse=True)[:k]
    out = []
    for key in ranked:
        c = dict(chunks[key])
        c["rrf_score"] = scores[key]
        out.append(c)
    return out