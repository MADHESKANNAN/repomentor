"""Test LLM answers. Last question is NOT in the repo: it must say Theriyala."""
import time
from answerer import answer

REPO = "https://github.com/pallets/markupsafe"

QUESTIONS = [
    "What does the escape function do?",
    "What is the Markup class?",
    "How does string formatting work with Markup?",
    "Is there a C speedups module?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    print("\n" + "=" * 60)
    print("Q:", q)
    print("A:", answer(REPO, q))
    time.sleep(3)