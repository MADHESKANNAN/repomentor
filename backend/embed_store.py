"""RepoMentor - Week 1 Day 6: embed chunks and store them in Chroma."""
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DB_PATH = Path(__file__).parent / "chroma_db"
BATCH_SIZE = 64

_client = chromadb.PersistentClient(path=str(DB_PATH))
_embed = DefaultEmbeddingFunction()  # all-MiniLM-L6-v2, runs locally, free


def collection_name_for(url: str) -> str:
    """'https://github.com/pallets/click' -> 'pallets_click' (Chroma-safe)."""
    parts = url.rstrip("/").removesuffix(".git").split("/")
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", "_".join(parts[-2:]))
    return name[:60]


def store_chunks(chunks, collection_name: str) -> int:
    """Delete the old collection (no duplicates), embed in batches, store."""
    try:
        _client.delete_collection(collection_name)
    except Exception:
        pass  # collection did not exist yet

    col = _client.create_collection(collection_name, embedding_function=_embed)

    chunks = [c for c in chunks if c.text.strip()]
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        col.add(
            ids=[f"{i + j}:{c.file_path}:{c.start_line}-{c.end_line}" for j, c in enumerate(batch)],
            documents=[c.text for c in batch],
            metadatas=[{
                "file_path": c.file_path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "kind": c.kind,
            } for c in batch],
        )
    return len(chunks)


def search(collection_name: str, query: str, n_results: int = 5) -> list[dict]:
    col = _client.get_collection(collection_name, embedding_function=_embed)
    res = col.query(query_texts=[query], n_results=n_results)
    return [
        {"text": doc, "distance": dist, **meta}
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]
