# \# RepoMentor

# AI that understands any GitHub repo. Ask questions, get answers with file and line references.

# 

# \## Tech Stack

# FastAPI, React (Vite), Gemini API, ChromaDB, GitPython

# 

# \## Features

# \- Index any public GitHub repo (clone, chunk, embed)

# \- Ask questions, get answers with file:line sources

# \- Click a source to see highlighted code

# \- Says "Theriyala" when the repo does not contain the answer

# 

# \## Setup

# 1\. python -m venv venv

# 2\. venv\\Scripts\\activate

# 3\. pip install -r requirements.txt

# 4\. Copy backend/.env.example to backend/.env and add your Gemini key

# 5\. Backend: cd backend, then uvicorn main:app --reload

# 6\. Frontend: cd frontend, then npm install, then npm run dev

# 

# \## Status

# Week 1 and Week 2 done. Week 3: hybrid search, streaming, caching.

