"""Test answer + sources. France question must give Theriyala and no sources."""
import time
from answerer import answer

REPO = "https://github.com/pallets/markupsafe"

QUESTIONS = [
    "What is the Markup class?",
    "Is there a C speedups module?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    print("\n" + "=" * 60)
    print("Q:", q)
    result = answer(REPO, q)
    print("A:", result["answer"])
    print("SOURCES:")
    for s in result["sources"]:
        print(f"  - {s['file_path']}:{s['start_line']}-{s['end_line']}")
    time.sleep(3)