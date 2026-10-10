"""RepoMentor - Week 3 Day 1: BM25 keyword search over stored chunks."""
import re

from rank_bm25 import BM25Okapi

from embed_store import _client, collection_name_for

_cache = {}  # collection name -> (bm25, docs, metas)


def _tokenize(text: str) -> list[str]:
    """Split code into lowercase words; also split camelCase."""
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 1]


def _build(name: str):
    col = _client.get_collection(name)
    data = col.get(include=["documents", "metadatas"])
    docs, metas = data["documents"], data["metadatas"]
    bm25 = BM25Okapi([_tokenize(d) for d in docs])
    _cache[name] = (bm25, docs, metas)
    return _cache[name]


def keyword_search(repo_url: str, query: str, n_results: int = 5) -> list[dict]:
    name = collection_name_for(repo_url)
    bm25, docs, metas = _cache.get(name) or _build(name)
    scores = bm25.get_scores(_tokenize(query))
    top = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:n_results]
    return [
        {"text": docs[i], "score": float(scores[i]), **metas[i]}
        for i in top
        if scores[i] > 0
    ]


def clear_cache(repo_url: str):
    """Call after re-ingesting a repo so BM25 rebuilds."""
    _cache.pop(collection_name_for(repo_url), None)