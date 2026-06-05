from __future__ import annotations

import heapq
from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        index = self._next_index
        self._next_index = index + 1

        metadata = dict(doc.metadata)
        metadata["doc_id"] = doc.id
        content = doc.content

        return {
            "id": f"{doc.id}:{index}",
            "content": content,
            "metadata": metadata,
            "embedding": self._embedding_fn(content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        scored = (
            (_dot(query_embedding, record["embedding"]), record)
            for record in records
        )
        return [
            {**record, "score": score}
            for score, record in heapq.nlargest(top_k, scored, key=lambda item: item[0])
        ]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        start_index = self._next_index
        ids = [f"{doc.id}-{start_index + i}" for i, doc in enumerate(docs)]
        contents = [doc.content for doc in docs]
        embeddings = [self._embedding_fn(content) for content in contents]
        metadatas = []

        for doc in docs:
            metadata = dict(doc.metadata)
            metadata.setdefault("doc_id", doc.id)
            metadatas.append(metadata)

        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        else:
            self._store.extend(
                {
                    "id": ids[i],
                    "content": contents[i],
                    "metadata": metadatas[i],
                    "embedding": embeddings[i],
                }
                for i in range(len(docs))
            )

        self._next_index += len(docs)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if top_k <= 0:
            return []

        if self._use_chroma and self._collection is not None:
            result = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
            )
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            ids = result.get("ids", [[]])[0]
            return [
                {
                    "id": ids[i] if i < len(ids) else None,
                    "content": content,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "score": -distances[i] if i < len(distances) else 0.0,
                }
                for i, content in enumerate(documents)
            ]

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if top_k <= 0:
            return []

        if not metadata_filter:
            return self.search(query, top_k=top_k)

        if self._use_chroma and self._collection is not None:
            result = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=top_k,
                where=metadata_filter,
            )
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            ids = result.get("ids", [[]])[0]
            return [
                {
                    "id": ids[i] if i < len(ids) else None,
                    "content": content,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "score": -distances[i] if i < len(distances) else 0.0,
                }
                for i, content in enumerate(documents)
            ]

        filter_items = metadata_filter.items()
        filtered_records = [
            record
            for record in self._store
            if all(record.get("metadata", {}).get(key) == value for key, value in filter_items)
        ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            results = self._collection.get(where={"doc_id": doc_id})
            ids = results.get("ids", [])
            if not ids:
                return False
            self._collection.delete(ids=ids)
            return True

        original_size = len(self._store)
        self._store[:] = [
            record
            for record in self._store
            if record.get("metadata", {}).get("doc_id") != doc_id
        ]
        return len(self._store) != original_size
