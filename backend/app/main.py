import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.answering import AnsweringService
from app.services.documents import chunk_text, extract_pdf_text
from app.services.vector_store import VectorStore


app = FastAPI(title="DocQuery API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
vector_store = VectorStore()
answering_service = AnsweringService(vector_store)


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    destination = UPLOAD_DIR / Path(file.filename).name
    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    text = extract_pdf_text(destination)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No readable text was found in the PDF.")

    count = vector_store.add_document(destination.name, chunks)
    return {"filename": destination.name, "chunks_indexed": count}


@app.post("/ask")
def ask_question(request: QuestionRequest) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return answering_service.answer(request.question)

