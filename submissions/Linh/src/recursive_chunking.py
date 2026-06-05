from __future__ import annotations

import re

from .chunking import RecursiveChunker


class LawRecursiveChunker:
    """
    Chunk Vietnamese law documents by article while preserving legal context.

    Each chunk includes its current chapter and article headings. Oversized
    articles are recursively split, with both headings repeated in each part.
    """

    SECTION_PATTERN = re.compile(
        r"(?im)(?=^(?:chương\s+[^\n:]+:?|điều\s+\d+[a-z]?\s*[.:][^\n]*|điều\s+\d+[a-z]?\s*$))"
    )
    CHAPTER_PATTERN = re.compile(r"(?i)^chương\s+[^\n:]+:?")
    ARTICLE_PATTERN = re.compile(r"(?i)^điều\s+\d+[a-z]?\s*(?:[.:][^\n]*)?$")

    def __init__(
        self,
        chunk_size: int = 1200,
        separators: list[str] | None = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.separators = (
            ["\n\n", "\n", ". ", "; ", ", ", " ", ""]
            if separators is None
            else list(separators)
        )

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = [
            section.strip()
            for section in self.SECTION_PATTERN.split(text)
            if section.strip()
        ]
        chunks: list[str] = []
        chapter = ""

        for section in sections:
            heading = section.splitlines()[0].strip()
            if self.CHAPTER_PATTERN.match(heading):
                chapter = heading
                if len(section) > len(heading):
                    chunks.extend(self._split_with_context(section, ""))
                continue

            context = chapter if self.ARTICLE_PATTERN.match(heading) else ""
            chunks.extend(self._split_with_context(section, context))

        return chunks

    def _split_with_context(self, section: str, context: str) -> list[str]:
        prefix = f"{context}\n\n" if context else ""
        if len(prefix) + len(section) <= self.chunk_size:
            return [prefix + section]

        heading, _, body = section.partition("\n")
        repeated_prefix = f"{prefix}{heading.strip()}\n\n"
        available_size = max(1, self.chunk_size - len(repeated_prefix))
        body_chunks = RecursiveChunker(
            separators=self.separators,
            chunk_size=available_size,
        ).chunk(body.strip())
        return [repeated_prefix + part for part in body_chunks]

    @classmethod
    def get_article_heading(cls, chunk: str) -> str | None:
        for line in chunk.splitlines():
            line = line.strip()
            if cls.ARTICLE_PATTERN.match(line):
                return line
        return None

    @classmethod
    def get_chapter_heading(cls, chunk: str) -> str | None:
        for line in chunk.splitlines():
            line = line.strip()
            if cls.CHAPTER_PATTERN.match(line):
                return line
        return None
