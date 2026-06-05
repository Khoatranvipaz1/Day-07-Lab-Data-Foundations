from pathlib import Path
import sys

from .embeddings import LocalEmbedder
from .faq_chunking import FAQRecursiveChunker
from .models import Document
from .store import EmbeddingStore


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parents[3]
text = (project_root / "data" / "Phap-Luat-FAQ-Luat-Dau-Tu.txt").read_text(
    encoding="utf-8"
)
chunks = FAQRecursiveChunker(chunk_size=800).chunk(text)

documents = [
    Document(
        id=f"faq-{index}",
        content=chunk,
        metadata={
            "doc_id": "phap-luat-faq",
            "category": "legal_faq",
            "language": "vi",
            "chunk_number": index,
        },
    )
    for index, chunk in enumerate(chunks, start=1)
]

store = EmbeddingStore("faq_retrieval_test", embedding_fn=LocalEmbedder())
store.add_documents(documents)

queries = [
    ("Nghị định áp dụng cho những đối tượng nào?", {6, 7}),
    ("Hồ sơ đăng ký đầu tư cần những tài liệu gì?", {11, 12, 13}),
    ("Nhà đầu tư phải nộp hồ sơ ở đâu?", {14}),
    ("Nhà đầu tư cần thực hiện nghĩa vụ bảo đảm nào?", {19, 20, 21}),
    ("Phải thông báo trước khi khởi công bao nhiêu ngày?", {22}),
]

passed = 0

for query, gold_chunks in queries:
    results = store.search_with_filter(
        query,
        top_k=3,
        metadata_filter={"category": "legal_faq", "language": "vi"},
    )

    retrieved = {result["metadata"]["chunk_number"] for result in results}
    relevant = bool(retrieved & gold_chunks)
    passed += relevant

    print(f"\nQuery: {query}")
    print(f"Gold chunks: {sorted(gold_chunks)}")
    print(f"Retrieved chunks: {sorted(retrieved)}")
    print(f"Relevant in top-3: {relevant}")

    for rank, result in enumerate(results, start=1):
        number = result["metadata"]["chunk_number"]
        print(f"  {rank}. Chunk {number}, score={result['score']:.4f}")

print(f"\nRetrieval score: {passed}/5")
