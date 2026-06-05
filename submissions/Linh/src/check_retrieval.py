from __future__ import annotations

from pathlib import Path
import re
import sys

from .embeddings import LocalEmbedder
from .models import Document
from .recursive_chunking import LawRecursiveChunker
from .store import EmbeddingStore


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
YEAR_PATTERN = re.compile(r"^law-(\d{4})-")

BENCHMARKS = [
    {
        "query": "Ngày toàn dân phòng cháy và chữa cháy là ngày nào?",
        "gold_answer": "Ngày 04 tháng 10 hằng năm.",
        "gold_source": "law-2001-luat-phong-chay-va-chua-chay.md",
        "gold_article": "Điều 11",
    },
    {
        "query": "Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu?",
        "gold_answer": (
            "Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí."
        ),
        "gold_source": "law-1989-luat-bao-ve-suc-khoe-nhan-dan.md",
        "gold_article": "Điều 23",
    },
    {
        "query": "Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc?",
        "gold_answer": "Ba cấp, mười hai bậc.",
        "gold_source": "law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md",
        "gold_article": "Điều 10",
    },
    {
        "query": "Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm?",
        "gold_answer": "Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới.",
        "gold_source": "law-2003-luat-bien-gioi-quoc-gia.md",
        "gold_article": "Điều 14",
    },
    {
        "query": "Ai quyết định tặng huân chương và huy chương?",
        "gold_answer": "Chủ tịch nước.",
        "gold_source": "law-2003-luat-thi-dua-khen-thuong.md",
        "gold_article": "Điều 77",
    },
]


def find_law_files(start_year: int = 1989, end_year: int = 2003) -> list[Path]:
    files = []
    for path in DATA_DIR.glob("law-*.md"):
        match = YEAR_PATTERN.match(path.name)
        if match and start_year <= int(match.group(1)) <= end_year:
            files.append(path)
    return sorted(files)


def build_documents(files: list[Path], chunk_size: int = 1200) -> list[Document]:
    chunker = LawRecursiveChunker(chunk_size=chunk_size)
    documents: list[Document] = []

    for path in files:
        year = int(YEAR_PATTERN.match(path.name).group(1))
        chunks = chunker.chunk(path.read_text(encoding="utf-8"))
        print(f"{path.name}: {len(chunks)} chunks")

        for number, chunk in enumerate(chunks, start=1):
            documents.append(
                Document(
                    id=f"{path.stem}-{number}",
                    content=chunk,
                    metadata={
                        "doc_id": path.stem,
                        "source": path.name,
                        "year": year,
                        "type": "law",
                        "language": "vi",
                        "chunk_number": number,
                        "chapter": chunker.get_chapter_heading(chunk) or "",
                        "article": chunker.get_article_heading(chunk) or "",
                    },
                )
            )
    return documents


def is_gold_result(result: dict, benchmark: dict) -> bool:
    metadata = result["metadata"]
    return (
        metadata["source"] == benchmark["gold_source"]
        and metadata["article"].startswith(benchmark["gold_article"])
    )


def main() -> None:
    files = find_law_files()
    documents = build_documents(files)
    print(f"\nIndexed {len(documents)} chunks from {len(files)} law files.")

    store = EmbeddingStore("law_retrieval_test", embedding_fn=LocalEmbedder())
    store.add_documents(documents)

    passed = 0
    for index, benchmark in enumerate(BENCHMARKS, start=1):
        print(f"\n{'=' * 20} Benchmark {index} {'=' * 20}")
        print(f"Query: {benchmark['query']}")
        print(f"Gold answer: {benchmark['gold_answer']}")
        print(
            f"Gold source: {benchmark['gold_source']} "
            f"({benchmark['gold_article']})"
        )

        results = store.search_with_filter(
            benchmark["query"],
            top_k=3,
            metadata_filter={"type": "law", "language": "vi"},
        )

        gold_rank = None
        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            relevant = is_gold_result(result, benchmark)
            if relevant and gold_rank is None:
                gold_rank = rank

            preview = " ".join(result["content"].split())[:180]
            print(
                f"  {rank}. score={result['score']:.4f} relevant={relevant}\n"
                f"     source={metadata['source']}\n"
                f"     article={metadata['article']}\n"
                f"     preview={preview}"
            )

        success = gold_rank is not None
        passed += success
        print(f"Relevant gold chunk in top-3: {success}")
        if gold_rank:
            print(f"Gold chunk rank: {gold_rank}")

    print(f"\nRetrieval score: {passed}/{len(BENCHMARKS)}")


if __name__ == "__main__":
    main()
