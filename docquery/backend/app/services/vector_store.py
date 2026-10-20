import chromadb
from openai import OpenAI

from app.config import CHROMA_DIR, EMBEDDING_MODEL


class VectorStore:
    def __init__(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection("docquery")
        self._openai = None

    @property
    def openai(self) -> OpenAI:
        if self._openai is None:
            self._openai = OpenAI()
        return self._openai

    def embed(self, texts: list[str]) -> list[list[float]]:
        result = self.openai.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in result.data]

    def add_document(self, filename: str, chunks: list[str]) -> int:
        if not chunks:
            return 0

        embeddings = self.embed(chunks)
        ids = [f"{filename}-{index}" for index in range(len(chunks))]
        metadatas = [{"filename": filename, "chunk_index": index} for index in range(len(chunks))]
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embed([query])[0]
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {
                "text": document,
                "filename": metadata.get("filename", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "distance": distance,
            }
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

