"""Compare BM25 results with the old embedding results."""
from keyword_search import keyword_search
from retriever import retrieve

REPO = "https://github.com/pallets/markupsafe"

QUESTIONS = [
    "how are errors handled?",
    "what dependencies does the project use?",
    "is there a C speedups module?",
    "where is the main entry point?",
]

for q in QUESTIONS:
    print(f"\nQ: {q}")
    print("  BM25:")
    for c in keyword_search(REPO, q, 5):
        print(f"    {c['file_path']}:{c['start_line']}-{c['end_line']}  (score {c['score']:.2f})")
    print("  Embedding (old):")
    for c in retrieve(REPO, q, 5):
        print(f"    {c['file_path']}:{c['start_line']}-{c['end_line']}  (distance {c['distance']:.2f})")