"""A small in-memory embedding store used by the lab exercises."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from .chunking import compute_similarity
from .models import Document

try:
    from .embeddings import _mock_embed
except ImportError:  # pragma: no cover - compatibility fallback
    def _mock_embed(text: str) -> list[float]:
        buckets = [0.0] * 16
        for index, char in enumerate(text.lower()):
            buckets[(ord(char) + index) % len(buckets)] += 1.0
        return buckets


Embedder = Callable[[str], list[float]]


class EmbeddingStore:
    """Store embedded documents and retrieve them with cosine similarity."""

    def __init__(
        self,
        collection_name: str = "default",
        embedder: Embedder | None = None,
        embedding_fn: Embedder | None = None,
        chunker: Any | None = None,
    ):
        self.collection_name = collection_name
        self.embedder = embedding_fn or embedder or _mock_embed
        self.chunker = chunker
        self.documents: list[Document] = []
        self.embeddings: list[list[float]] = []

    def add_document(self, document: Document | str, metadata: dict[str, Any] | None = None) -> str:
        """Add one document and return its id."""

        doc = document if isinstance(document, Document) else _make_document(self._next_id(), document, metadata or {})
        if metadata:
            doc = _with_metadata(doc, {**_get_metadata(doc), **metadata})

        self.documents.append(doc)
        self.embeddings.append(self.embedder(_get_content(doc)))
        return _get_id(doc)

    def add_documents(self, documents: Iterable[Document | str]) -> list[str]:
        ids: list[str] = []
        for document in documents:
            ids.append(self.add_document(document))
        return ids

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Return top-k documents with similarity scores."""

        if top_k <= 0 or not self.documents:
            return []
        query_embedding = self.embedder(query)
        scored = [
            self._result(document, compute_similarity(query_embedding, embedding))
            for document, embedding in zip(self.documents, self.embeddings)
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def search_with_filter(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search only chunks whose metadata matches all filter key/value pairs."""

        active_filter = filters or metadata_filter or {}
        if not active_filter:
            return self.search(query, top_k=top_k)
        if top_k <= 0:
            return []

        query_embedding = self.embedder(query)
        scored: list[dict[str, Any]] = []
        for document, embedding in zip(self.documents, self.embeddings):
            metadata = _get_metadata(document)
            if all(metadata.get(key) == value for key, value in active_filter.items()):
                scored.append(self._result(document, compute_similarity(query_embedding, embedding)))
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def delete_document(self, document_id: str) -> bool:
        return bool(self.delete(document_id))

    def delete(self, document_id: str | None = None, **filters: Any) -> bool:
        """Delete documents by id or by arbitrary metadata filters."""

        if document_id is not None:
            filters = {"id": document_id, **filters}
        if not filters:
            return False

        kept_docs: list[Document] = []
        kept_embeddings: list[list[float]] = []
        deleted = False
        for document, embedding in zip(self.documents, self.embeddings):
            metadata = {**_get_metadata(document), "id": _get_id(document)}
            if all(metadata.get(key) == value for key, value in filters.items()):
                deleted = True
            else:
                kept_docs.append(document)
                kept_embeddings.append(embedding)
        self.documents = kept_docs
        self.embeddings = kept_embeddings
        return deleted

    def clear(self) -> None:
        self.documents.clear()
        self.embeddings.clear()

    def count(self) -> int:
        return len(self.documents)

    def size(self) -> int:
        return len(self.documents)

    def get_collection_size(self) -> int:
        return len(self.documents)

    @property
    def collection_size(self) -> int:
        return len(self.documents)

    def get_stats(self) -> dict[str, Any]:
        return {
            "num_documents": len(self.documents),
            "num_embeddings": len(self.embeddings),
            "embedding_dim": len(self.embeddings[0]) if self.embeddings else 0,
        }

    def _next_id(self) -> str:
        return f"doc_{len(self.documents)}"

    def _result(self, document: Document, score: float) -> dict[str, Any]:
        return {
            "id": _get_id(document),
            "content": _get_content(document),
            "metadata": _get_metadata(document),
            "score": score,
            "document": document,
        }


def _with_metadata(document: Document, metadata: dict[str, Any]) -> Document:
    return _make_document(_get_id(document), _get_content(document), metadata)


def _make_document(doc_id: str, content: str, metadata: dict[str, Any]) -> Document:
    try:
        return Document(doc_id, content, metadata)
    except TypeError:
        try:
            return Document(id=doc_id, content=content, metadata=metadata)
        except TypeError:
            return Document(text=content, metadata={**metadata, "id": doc_id})


def _get_id(document: Document) -> str:
    metadata = _get_metadata(document)
    return getattr(document, "id", metadata.get("id", ""))


def _get_content(document: Document) -> str:
    return getattr(document, "content", getattr(document, "text", "")) or ""


def _get_metadata(document: Document) -> dict[str, Any]:
    return dict(getattr(document, "metadata", {}) or {})
