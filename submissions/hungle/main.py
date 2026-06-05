from __future__ import annotations

from pathlib import Path

from src.agent import KnowledgeBaseAgent
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


SAMPLE_FILES = [
    "data/law-1989-luat-bao-ve-suc-khoe-nhan-dan.md",
    "data/law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md",
    "data/law-2001-luat-phong-chay-va-chua-chay.md",
    "data/law-2003-luat-bien-gioi-quoc-gia.md",
    "data/law-2003-luat-thi-dua-khen-thuong.md",
]


def load_documents(file_paths: list[str]) -> list[Document]:
    documents: list[Document] = []
    for raw_path in file_paths:
        path = Path(raw_path)
        if not path.exists() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        documents.append(
            Document(
                id=path.stem,
                content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path), "extension": path.suffix.lower()},
            )
        )
    return documents


def demo_llm(prompt: str) -> str:
    return "Demo answer based on retrieved context."


def main() -> int:
    docs = load_documents(SAMPLE_FILES)
    store = EmbeddingStore(collection_name="manual_demo", embedding_fn=_mock_embed)
    store.add_documents(docs)

    question = "Ngày toàn dân phòng cháy và chữa cháy là ngày nào?"
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    print(agent.answer(question, top_k=3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
