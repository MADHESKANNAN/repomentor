"""Check retrieval quality with 10 sample questions."""
from retriever import retrieve

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
    for c in retrieve(REPO, q, k=5):
        print(f"  {c['file_path']}:{c['start_line']}-{c['end_line']}  (distance {c['distance']:.2f})")