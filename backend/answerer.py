"""RepoMentor - Week 3 Day 2: answer a question using hybrid search + return sources."""
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from retriever import format_context
from hybrid import hybrid_search

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.5-flash-lite"  # if 404, use "gemini-flash-latest"

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """You are RepoMentor, an assistant that explains a GitHub repository.

Rules:
1. Answer ONLY using the code context below.
2. Mention the file name (and line numbers) you used, like src/app.py:10-25.
3. If the context partly answers the question, answer with what is there.
4. Only if the context has nothing relevant, reply exactly:
   Theriyala - indha repo context la answer illa.
5. Do not make up files, functions, or behavior.

CODE CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def answer(repo_url: str, question: str, k: int = 5) -> dict:
    chunks = hybrid_search(repo_url, question, k=k)
    context = format_context(chunks)
    prompt = PROMPT.format(context=context, question=question)

    text = None
    last_error = None
    for attempt in range(5):
        try:
            resp = _client.models.generate_content(model=MODEL, contents=prompt)
            text = resp.text
            break
        except Exception as e:
            last_error = e
            msg = str(e)
            if "503" in msg or "429" in msg or "UNAVAILABLE" in msg:
                wait = 10 * (attempt + 1)  # 10, 20, 30, 40, 50 sec
                print(f"  (Gemini busy, retry {attempt + 1}/5 in {wait}s...)")
                time.sleep(wait)
            else:
                raise
    if text is None:
        raise last_error

    # If the model says it does not know, do not show sources
    if text.strip().startswith("Theriyala"):
        sources = []
    else:
        sources = [
            {
                "file_path": c["file_path"],
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "snippet": c["text"],
            }
            for c in chunks
        ]

    return {"answer": text, "sources": sources}