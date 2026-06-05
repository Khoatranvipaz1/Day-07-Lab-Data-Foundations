from __future__ import annotations

import re

from .chunking import RecursiveChunker


class FAQRecursiveChunker:
    """
    Split FAQ documents while keeping each question with its answer.

    If an answer is oversized, repeat the question in every resulting chunk.
    """

    QUESTION_PATTERN = re.compile(
        r"(?im)(?=^(?:question|câu hỏi)\s*:\s*.+$|^\d+\.\s+.+\?\s*$)"
    )

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
    ) -> None:
        self.separators = (
            RecursiveChunker.DEFAULT_SEPARATORS
            if separators is None
            else list(separators)
        )
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sections = [
            section.strip()
            for section in self.QUESTION_PATTERN.split(text)
            if section.strip()
        ]
        if len(sections) <= 1:
            return self._recursive_chunk(text, self.chunk_size)

        chunks: list[str] = []
        for section in sections:
            first_line, _, answer = section.partition("\n")
            if not self._is_question(first_line) or len(section) <= self.chunk_size:
                chunks.extend(self._recursive_chunk(section, self.chunk_size))
                continue

            question = first_line.strip()
            available_size = max(1, self.chunk_size - len(question) - 2)
            chunks.extend(
                f"{question}\n\n{part}"
                for part in self._recursive_chunk(answer.strip(), available_size)
            )
        return chunks

    def _recursive_chunk(self, text: str, chunk_size: int) -> list[str]:
        return RecursiveChunker(
            separators=self.separators,
            chunk_size=chunk_size,
        ).chunk(text)

    @staticmethod
    def _is_question(line: str) -> bool:
        return bool(
            re.match(r"(?i)^(?:question|câu hỏi)\s*:", line)
            or re.match(r"^\d+\.\s+.+\?\s*$", line)
        )
