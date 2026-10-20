# DocQuery

DocQuery is a document question-answering assistant built with React, FastAPI, OpenAI embeddings, Chroma, and OpenAI function calling.

## Current milestone

- Upload PDF documents
- Extract and chunk text
- Store embeddings in Chroma
- Search relevant chunks
- Generate grounded answers with source references
- React interface for upload and question answering

## Run the backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
uvicorn app.main:app --reload
```

Add your API key to `backend/.env` before using upload or question endpoints.

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

