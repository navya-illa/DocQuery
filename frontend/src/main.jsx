import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function uploadFile() {
    if (!file) return;
    setBusy(true);
    setStatus("Uploading and indexing document...");
    const body = new FormData();
    body.append("file", file);
    const response = await fetch(`${API_URL}/upload`, { method: "POST", body });
    const data = await response.json();
    setStatus(response.ok ? `${data.chunks_indexed} chunks indexed.` : data.detail);
    setBusy(false);
  }

  async function askQuestion(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setStatus("Searching documents and generating an answer...");
    const response = await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    setAnswer(response.ok ? data : { answer: data.detail, sources: [] });
    setStatus("");
    setBusy(false);
  }

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">DOCQUERY · RAG ASSISTANT</p>
        <h1>Ask your documents better questions.</h1>
        <p className="subtitle">
          Upload a PDF, retrieve relevant evidence, and receive a grounded answer with sources.
        </p>
      </section>

      <section className="card">
        <h2>1. Upload a document</h2>
        <div className="upload-row">
          <input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files[0])} />
          <button onClick={uploadFile} disabled={!file || busy}>Index PDF</button>
        </div>
        <p className="status">{status}</p>
      </section>

      <section className="card">
        <h2>2. Ask a question</h2>
        <form onSubmit={askQuestion}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What does the document say about...?"
            rows="4"
          />
          <button type="submit" disabled={!question.trim() || busy}>Ask DocQuery</button>
        </form>
      </section>

      {answer && (
        <section className="card answer-card">
          <h2>Answer</h2>
          <p className="answer">{answer.answer}</p>
          {answer.sources?.length > 0 && (
            <div>
              <h3>Sources</h3>
              <ul>
                {answer.sources.map((source, index) => (
                  <li key={`${source.filename}-${index}`}>
                    {source.filename} · chunk {source.chunk_index + 1}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

