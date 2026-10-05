"""RepoMentor - Week 2 Day 1: retrieve top chunks for a question."""
from embed_store import search, collection_name_for


def retrieve(repo_url: str, question: str, k: int = 5) -> list[dict]:
    """Return top-k chunks: text, distance, file_path, start_line, end_line, kind."""
    name = collection_name_for(repo_url)
    return search(name, question, n_results=k)


def format_context(chunks: list[dict]) -> str:
    """Turn chunks into one text block for the LLM (used on Day 2)."""
    parts = []
    for c in chunks:
        header = f"[{c['file_path']}:{c['start_line']}-{c['end_line']}]"
        parts.append(f"{header}\n{c['text']}")
    return "\n\n---\n\n".join(parts)