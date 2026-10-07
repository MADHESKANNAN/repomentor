"""RepoMentor API - Week 2 Day 4: /ingest and /ask."""
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from repo_loader import clone_repo
from chunker import chunk_repo
from embed_store import collection_name_for, store_chunks, _client
from answerer import answer

app = FastAPI(title="RepoMentor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestRequest(BaseModel):
    repo_url: str


class AskRequest(BaseModel):
    repo_url: str
    question: str


@app.get("/")
def root():
    return {"message": "RepoMentor API is running"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    url = req.repo_url.strip()
    if not url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Please give a valid GitHub repo link (https://github.com/owner/repo)")
    try:
        t = time.time()
        path = clone_repo(url)
        chunks = chunk_repo(path)
        if not chunks:
            raise HTTPException(status_code=422, detail="No code files found in this repo")
        stored = store_chunks(chunks, collection_name_for(url))
        return {"repo_url": url, "chunks_stored": stored, "seconds": round(time.time() - t, 1)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")


@app.post("/ask")
def ask(req: AskRequest):
    url = req.repo_url.strip()
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")

    name = collection_name_for(url)
    existing = [c if isinstance(c, str) else c.name for c in _client.list_collections()]
    if name not in existing:
        raise HTTPException(status_code=404, detail="This repo is not indexed yet. Call /ingest first.")

    try:
        return answer(url, req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer failed: {e}")