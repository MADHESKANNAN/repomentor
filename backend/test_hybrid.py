"""Compare embedding-only vs hybrid on the 10 sample questions."""
from retriever import retrieve
from hybrid import hybrid_search

REPO = "https://github.com/pallets/markupsafe"

QUESTIONS = [
    "where is the main entry point?",
    "how are errors handled?",
    "what does the escape function do?",
    "how is HTML escaping implemented?",
    "what is the Markup class?",
    "where are the tests for escaping?",
    "how does string formatting work with Markup?",
    "is there a C speedups module?",
    "how is the package built?",
    "what dependencies does the project use?",
]

for q in QUESTIONS:
    print(f"\nQ: {q}")
    print("  Embedding only:")
    for c in retrieve(REPO, q, 5):
        print(f"    {c['file_path']}:{c['start_line']}-{c['end_line']}")
    print("  Hybrid (RRF):")
    for c in hybrid_search(REPO, q, 5):
        print(f"    {c['file_path']}:{c['start_line']}-{c['end_line']}  (rrf {c['rrf_score']:.4f})")