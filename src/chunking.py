from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        raise NotImplementedError("Implement SentenceChunker.chunk")


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        raise NotImplementedError("Implement RecursiveChunker.chunk")

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        raise NotImplementedError("Implement RecursiveChunker._split")


class MarkdownSectionChunker:
    """
    Split markdown/legal documents by structural section markers.

    This custom strategy keeps headings, "Chuong", and "Dieu" blocks together
    when possible, then falls back to fixed-size splitting for oversized sections.
    """

    SECTION_PATTERN = re.compile(
        r"(?m)^(?=(?:#{1,6}\s+|Ch[uư]ong\s+[IVXLCDM0-9]+|[ĐD]i[eề]u\s+\d+\.))",
        flags=re.IGNORECASE,
    )

    def __init__(self, chunk_size: int = 900) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sections = [
            section.strip()
            for section in self.SECTION_PATTERN.split(text.strip())
            if section.strip()
        ]
        if not sections:
            return []

        chunks: list[str] = []
        buffer = ""
        for section in sections:
            candidate = section if not buffer else f"{buffer}\n\n{section}"
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.extend(self._split_oversized(buffer))
            chunks.extend(self._split_oversized(section))
            buffer = ""

        if buffer:
            chunks.extend(self._split_oversized(buffer))

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def _split_oversized(self, text: str) -> list[str]:
        return [
            text[start : start + self.chunk_size]
            for start in range(0, len(text), self.chunk_size)
        ]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    raise NotImplementedError("Implement compute_similarity")


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        raise NotImplementedError("Implement ChunkingStrategyComparator.compare")