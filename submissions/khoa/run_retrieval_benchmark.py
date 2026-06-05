from pathlib import Path

from src import Document, EmbeddingStore
from src.chunking import SentenceChunker


ROOT = Path(__file__).resolve().parent
DOC_DIR = ROOT / "data" / "parquet_docs"
OUT_PATH = ROOT / "data" / "retrieval_results.md"

QUERIES = [
    {
        "query": "Ngày toàn dân phòng cháy và chữa cháy là ngày nào?",
        "gold": "Ngày 04 tháng 10 hằng năm.",
        "relevant": "law-2001-luat-phong-chay-va-chua-chay.md",
    },
    {
        "query": "Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu?",
        "gold": "Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí.",
        "relevant": "law-1989-luat-bao-ve-suc-khoe-nhan-dan.md",
    },
    {
        "query": "Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc?",
        "gold": "Ba cấp, mười hai bậc.",
        "relevant": "law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md",
    },
    {
        "query": "Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm?",
        "gold": "Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới.",
        "relevant": "law-2003-luat-bien-gioi-quoc-gia.md",
    },
    {
        "query": "Ai quyết định tặng huân chương và huy chương?",
        "gold": "Chủ tịch nước.",
        "relevant": "law-2003-luat-thi-dua-khen-thuong.md",
    },
]

STRATEGY_NAME = "sentence_chunker_1200"
CHUNKER = SentenceChunker(chunk_size=1200)


def load_source_docs() -> list[tuple[Path, str]]:
    docs: list[tuple[Path, str]] = []
    for path in sorted(DOC_DIR.glob("*.md")):
        docs.append((path, path.read_text(encoding="utf-8")))
    return docs


def build_store() -> EmbeddingStore:
    store = EmbeddingStore(collection_name=STRATEGY_NAME)
    chunk_docs: list[Document] = []

    for path, content in load_source_docs():
        chunks = CHUNKER.chunk(content)
        for chunk_index, chunk in enumerate(chunks):
            chunk_docs.append(
                Document(
                    id=f"{path.stem}__chunk_{chunk_index}",
                    content=chunk,
                    metadata={
                        "source": path.name,
                        "chunk_index": chunk_index,
                        "strategy": STRATEGY_NAME,
                    },
                )
            )

    store.add_documents(chunk_docs)
    return store


def render_result_row(rank: int, result: dict) -> str:
    source = result["metadata"].get("source", result["id"])
    chunk_index = result["metadata"].get("chunk_index", "")
    preview = " ".join(result["content"].split())[:120]
    return f"| {rank} | `{source}` | {chunk_index} | {result['score']:.4f} | {preview}... |"


def main() -> None:
    lines = [
        "# Retrieval Benchmark Results",
        "",
        "Domain: Vietnamese law documents converted from `docs/0000.parquet`.",
        "",
        "Evaluation: a query is counted as a Top-3 hit when at least one retrieved chunk comes from the expected document.",
        "",
        f"Chosen personal strategy: `{STRATEGY_NAME}`.",
        "",
        "Design rationale: sentence-based chunks preserve sentence boundaries, which fits legal documents where answers are often stated as complete clauses or articles.",
        "",
    ]

    store = build_store()
    hits = 0

    lines.extend(
        [
            "## Strategy Run",
            "",
            f"Chunks indexed: {store.get_collection_size()}",
            "",
        ]
    )

    for index, item in enumerate(QUERIES, start=1):
        results = store.search(item["query"], top_k=3)
        retrieved_sources = [result["metadata"].get("source", "") for result in results]
        is_hit = item["relevant"] in retrieved_sources
        hits += int(is_hit)

        lines.extend(
            [
                f"### Query {index}",
                "",
                f"**Query:** {item['query']}",
                "",
                f"**Gold answer:** {item['gold']}",
                "",
                f"**Expected document:** `{item['relevant']}`",
                "",
                f"**Top-3 hit:** {'yes' if is_hit else 'no'}",
                "",
                "| Rank | Retrieved document | Chunk | Score | Preview |",
                "|---|---|---:|---:|---|",
            ]
        )
        for rank, result in enumerate(results, start=1):
            lines.append(render_result_row(rank, result))
        lines.append("")

    lines.extend(
        [
            "## Summary",
            "",
            "| Strategy | Top-3 recall | Chunks indexed |",
            "|---|---:|---:|",
            f"| {STRATEGY_NAME} | {hits}/{len(QUERIES)} | {store.get_collection_size()} |",
            "",
            f"Result: `{STRATEGY_NAME}` retrieved the expected document in the top 3 for {hits}/{len(QUERIES)} benchmark queries.",
            "",
            "Note: this benchmark uses the mock embedder, so it validates the retrieval pipeline but does not fully measure semantic quality. A real Vietnamese-capable embedding model should improve retrieval quality.",
            "",
        ]
    )

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"{STRATEGY_NAME}: Top-3 recall {hits}/{len(QUERIES)}, chunks={store.get_collection_size()}")


if __name__ == "__main__":
    main()
