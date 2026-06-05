"""Chunking strategies and similarity helpers for the vector-store lab."""

from __future__ import annotations

import math
import re
from typing import Any, Callable, Iterable

from .models import Document


class FixedSizeChunker:
    """Split text into fixed-size overlapping character chunks."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document | str) -> list[str]:
        text = _get_text(document)
        if not text:
            return []

        chunks: list[str] = []
        step = self.chunk_size - self.overlap
        for start in range(0, len(text), step):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)
            if end >= len(text):
                break
        return chunks

    def chunk_text(self, text: str, metadata: dict[str, Any] | None = None) -> list[str]:
        return self.chunk(text)


class SentenceChunker:
    """Group complete sentences into chunks near a target character size."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_sentences: int = 0,
        overlap: int | None = None,
        max_sentences_per_chunk: int | None = None,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap is not None:
            overlap_sentences = overlap
        if max_sentences_per_chunk is not None and max_sentences_per_chunk <= 0:
            raise ValueError("max_sentences_per_chunk must be positive")
        if overlap_sentences < 0:
            raise ValueError("overlap_sentences must be non-negative")
        self.chunk_size = chunk_size
        self.overlap_sentences = overlap_sentences
        self.max_sentences_per_chunk = max_sentences_per_chunk

    def chunk(self, document: Document | str) -> list[str]:
        text = _get_text(document)
        sentences = _split_sentences(text)
        if not sentences:
            return []

        if self.max_sentences_per_chunk is not None:
            return [
                " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
                for i in range(0, len(sentences), self.max_sentences_per_chunk)
            ]

        chunks: list[str] = []
        current: list[str] = []

        for sentence in sentences:
            candidate = " ".join([*current, sentence]).strip()
            if current and len(candidate) > self.chunk_size:
                chunks.append(" ".join(current).strip())
                keep = self.overlap_sentences if self.overlap_sentences else 0
                current = current[-keep:] if keep else []
            current.append(sentence)

            if len(current) == 1 and len(current[0]) > self.chunk_size:
                chunks.append(current[0].strip())
                current = []

        if current:
            chunks.append(" ".join(current).strip())
        return chunks

    def chunk_text(self, text: str, metadata: dict[str, Any] | None = None) -> list[str]:
        return self.chunk(text)


class RecursiveChunker:
    """Recursively split text using coarse-to-fine separators."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        separators: list[str] | None = None,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, document: Document | str) -> list[str]:
        text = _get_text(document).strip()
        if not text:
            return []

        pieces = self._split_recursive(text, self.separators)
        return self._merge_pieces(pieces)

    def chunk_text(self, text: str, metadata: dict[str, Any] | None = None) -> list[str]:
        return self.chunk(text)

    def _split_recursive(self, text: str, separators: list[str]) -> list[str]:
        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text] if text else []
        if not separators:
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        separator = separators[0]
        if separator == "":
            parts = [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        else:
            raw_parts = text.split(separator)
            parts = []
            for i, part in enumerate(raw_parts):
                part = part.strip()
                if not part:
                    continue
                suffix = separator if i < len(raw_parts) - 1 and separator.strip() else ""
                parts.append(part + suffix)

        result: list[str] = []
        for part in parts:
            if len(part) <= self.chunk_size:
                result.append(part.strip())
            else:
                result.extend(self._split_recursive(part, separators[1:]))
        return [part for part in result if part]

    def _merge_pieces(self, pieces: Iterable[str]) -> list[str]:
        chunks: list[str] = []
        current = ""

        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            candidate = f"{current} {piece}".strip() if current else piece
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
                current = self._tail_overlap(current)
                candidate = f"{current} {piece}".strip() if current else piece
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                chunks.extend(FixedSizeChunker(self.chunk_size, self.overlap).chunk_text(piece))
                current = ""

        if current:
            chunks.append(current)
        return chunks

    def _tail_overlap(self, text: str) -> str:
        if self.overlap == 0:
            return ""
        return text[-self.overlap :].strip()


def compute_similarity(vector_a: Iterable[float], vector_b: Iterable[float]) -> float:
    """Return cosine similarity for two vectors."""

    a = list(vector_a)
    b = list(vector_b)
    if len(a) != len(b):
        raise ValueError("vectors must have the same dimension")
    if not a:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run multiple chunking strategies on the same documents and summarize them."""

    def __init__(self, strategies: dict[str, Any] | None = None):
        self.strategies = strategies or {
            "fixed": FixedSizeChunker(),
            "sentence": SentenceChunker(),
            "recursive": RecursiveChunker(),
        }

    def compare(
        self,
        documents: Document | list[Document] | str | list[str],
        chunk_size: int | None = None,
    ) -> dict[str, dict[str, Any]]:
        texts = [_get_text(doc) for doc in _normalize_documents(documents)]
        strategies = self.strategies
        if chunk_size is not None:
            strategies = {
                "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
                "by_sentences": SentenceChunker(chunk_size=chunk_size),
                "recursive": RecursiveChunker(chunk_size=chunk_size),
            }
        comparison: dict[str, dict[str, Any]] = {}

        for name, chunker in strategies.items():
            chunks: list[str] = []
            for text in texts:
                chunks.extend(chunker.chunk(text))
            lengths = [len(chunk) for chunk in chunks]
            comparison[name] = {
                "chunks": chunks,
                "count": len(chunks),
                "num_chunks": len(chunks),
                "avg_length": sum(lengths) / len(lengths) if lengths else 0,
                "avg_chunk_size": sum(lengths) / len(lengths) if lengths else 0,
                "min_chunk_size": min(lengths) if lengths else 0,
                "max_chunk_size": max(lengths) if lengths else 0,
            }
        return comparison

    def compare_strategies(self, documents: Document | list[Document] | str | list[str]):
        return self.compare(documents)


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _normalize_documents(documents: Document | list[Document] | str | list[str]) -> list[Document]:
    if isinstance(documents, Document):
        return [documents]
    if isinstance(documents, str):
        return [documents]
    normalized = []
    for item in documents:
        normalized.append(item)
    return normalized


def _get_text(document: Document | str) -> str:
    if isinstance(document, str):
        return document
    return getattr(document, "text", getattr(document, "content", "")) or ""
