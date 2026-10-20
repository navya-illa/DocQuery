import json

from openai import OpenAI

from app.config import CHAT_MODEL
from app.services.vector_store import VectorStore


class AnsweringService:
    def __init__(self, vector_store: VectorStore) -> None:
        self._client = None
        self.vector_store = vector_store

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def answer(self, question: str) -> dict:
        response = self.client.responses.create(
            model=CHAT_MODEL,
            input=[{"role": "user", "content": question}],
            tools=[
                {
                    "type": "function",
                    "name": "search_documents",
                    "description": "Search uploaded documents for evidence relevant to the user's question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "top_k": {"type": "integer", "minimum": 1, "maximum": 8},
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            ],
        )

        tool_outputs = []
        for item in response.output:
            if item.type != "function_call":
                continue
            arguments = json.loads(item.arguments)
            results = self.vector_store.search(arguments["query"], arguments.get("top_k", 5))
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(results),
                }
            )

        if not tool_outputs:
            return {"answer": response.output_text, "sources": []}

        final_response = self.client.responses.create(
            model=CHAT_MODEL,
            previous_response_id=response.id,
            input=tool_outputs,
            instructions=(
                "Answer using only the retrieved document evidence. "
                "If the evidence is insufficient, say so clearly. "
                "Include short source references using the filenames provided."
            ),
        )

        sources = []
        for output in tool_outputs:
            sources.extend(json.loads(output["output"]))
        return {"answer": final_response.output_text, "sources": sources}

