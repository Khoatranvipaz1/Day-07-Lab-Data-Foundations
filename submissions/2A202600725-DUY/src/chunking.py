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
        if not text:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(group).strip())
        return chunks
    


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
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        rest = remaining_separators[1:]
        if separator == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        parts = current_text.split(separator)
        if len(parts) == 1:
            return self._split(current_text, rest)

        chunks: list[str] = []
        buffer = ""
        for part in parts:
            if not part:
                continue

            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
            if len(part) <= self.chunk_size:
                buffer = part
            else:
                chunks.extend(self._split(part, rest))
                buffer = ""

        if buffer:
            chunks.append(buffer)
        return chunks


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
    dot_product = _dot(vec_a, vec_b)
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        overlap = max(0, chunk_size // 10)
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            comparison[name] = {
                "count": count,
                "avg_length": (sum(map(len, chunks)) / count) if count else 0,
                "chunks": chunks,
            }
        return comparison
