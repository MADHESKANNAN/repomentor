import time

from repo_loader import clone_repo, get_code_files
from chunker import chunk_repo
from embed_store import collection_name_for, store_chunks, search

REPOS = [
    "https://github.com/pallets/markupsafe",  # small repo (unga own repo irundha maathikonga)
    "https://github.com/pallets/click",       # medium
    "https://github.com/expressjs/express",   # JavaScript
]

QUESTIONS = [
    "where is the main entry point?",
    "how are errors handled?",
]

if __name__ == "__main__":
    for url in REPOS:
        print(f"\n=== {url} ===")

        t = time.time()
        path = clone_repo(url)
        print(f"Clone: {time.time() - t:.1f}s")

        files = get_code_files(path)
        print(f"Files kept: {len(files)}")

        t = time.time()
        chunks = chunk_repo(path)
        print(f"Chunks: {len(chunks)} ({time.time() - t:.1f}s)")

        name = collection_name_for(url)
        t = time.time()
        stored = store_chunks(chunks, name)
        print(f"Embed + store: {stored} chunks in {time.time() - t:.1f}s")

        for q in QUESTIONS:
            print(f"\nQ: {q}")
            for r in search(name, q, n_results=3):
                print(f"  {r['file_path']}:{r['start_line']}-{r['end_line']}  (distance {r['distance']:.2f})")
