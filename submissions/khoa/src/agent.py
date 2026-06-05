"""A minimal retrieval-augmented agent for the lab."""

from __future__ import annotations

from typing import Any, Callable

from .models import Document
from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """Answer questions by retrieving relevant context from an EmbeddingStore."""

    def __init__(
        self,
        store: EmbeddingStore | None = None,
        llm: Callable[[str], str] | None = None,
        llm_fn: Callable[[str], str] | None = None,
        top_k: int = 3,
    ):
        self.store = store or EmbeddingStore()
        self.llm = llm_fn or llm
        self.top_k = top_k

    def add_knowledge(self, document: Document | str, metadata: dict[str, Any] | None = None) -> list[str]:
        return self.store.add_document(document, metadata=metadata)

    def ask(
        self,
        question: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        k = top_k if top_k is not None else self.top_k
        results = (
            self.store.search_with_filter(question, filters=filters, top_k=k)
            if filters
            else self.store.search(question, top_k=k)
        )
        context = self._format_context(results)
        answer = self._generate_answer(question, context, results)
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": [result["document"] for result in results],
            "results": results,
        }

    def answer(self, question: str, top_k: int | None = None) -> str:
        return self.ask(question, top_k=top_k)["answer"]

    def answer_question(self, question: str, top_k: int | None = None) -> str:
        return self.answer(question, top_k=top_k)

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        return self.store.search(query, top_k=top_k or self.top_k)

    def _generate_answer(
        self,
        question: str,
        context: str,
        results: list[dict[str, Any]],
    ) -> str:
        if not results:
            return "I don't know based on the provided knowledge base."

        if self.llm is not None:
            prompt = (
                "Answer the question using only the context below.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            )
            return self.llm(prompt)

        return results[0]["content"].strip()

    def _format_context(self, results: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {}) or {}
            source = metadata.get("source") or result.get("id") or f"chunk_{index}"
            lines.append(f"[{index}] {source} (score={result['score']:.3f})\n{result['content']}")
        return "\n\n".join(lines)
