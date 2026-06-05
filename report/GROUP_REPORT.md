# Group Report: Retrieval Strategy Comparison

**Lab:** Day 7 - Embedding & Vector Store  
**Group domain:** Vietnamese law documents  
**Date:** 05/06/2026

---

## 1. Group Members

| # | Member | Student ID | Branch/folder | Strategy reported | Test status |
|---|--------|------------|---------------|-------------------|-------------|
| 1 | Trần Văn Khoa | 2A202600827 | `TVKhoa` / `submissions/khoa` | `SentenceChunker(chunk_size=1200)` | 42/42 passed |
| 2 | Lê Văn Khoa | 2A202600603 | `LV_Khoa` / `submissions/LV_Khoa` | `RecursiveChunker` | 42/42 passed |
| 3 | Nguyễn Văn Duy | 2A202600725 | `duy` / `submissions/2A202600725-DUY` | `MarkdownSectionChunker(chunk_size=900)` | 42/42 passed |
| 4 | Nghiêm Tuấn Linh | 2A202600897 | `Linh` / `submissions/Linh` | Recursive/section-based code present, report not fully finalized | 42/42 passed |
| 5 | Nguyễn Phúc Hiếu | 2A202600747 | `hieu` / `submissions/hieu` | Fixed/metadata-oriented retrieval reported | 42/42 passed |
| 6 | Lê Quang Hưng | 2A202600891 | `hungle` / `submissions/hungle` | `FixedSizeChunker(chunk_size=500, overlap=50)` | 42/42 passed |

All six submission folders have passing tests after adding missing `main.py` files for `hungle` and `hieu`.

---

## 2. Document Selection

### Domain

The group selected **Vietnamese legal documents** as the retrieval domain.

This domain is suitable for the lab because legal texts are long, structured, and contain precise answers tied to articles or clauses. It also creates realistic retrieval challenges: many documents share similar legal vocabulary, and a query may require locating a specific article rather than just a generally related document.

### Document Set

The group used Markdown documents converted from `docs/0000.parquet`. The group benchmark focuses on 5 core legal documents used by the benchmark queries, with additional law documents available for retrieval noise and comparison.

| # | Document | File | Approx. characters | Purpose in benchmark |
|---|----------|------|--------------------|----------------------|
| 1 | Luật Phòng cháy và chữa cháy | `law-2001-luat-phong-chay-va-chua-chay.md` | 43,459 | Query about National Fire Prevention and Fighting Day |
| 2 | Luật Bảo vệ sức khỏe nhân dân | `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md` | 27,939 | Query about emergency treatment |
| 3 | Luật Sĩ quan Quân đội nhân dân Việt Nam | `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md` | 31,961 | Query about officer rank system |
| 4 | Luật Biên giới quốc gia | `law-2003-luat-bien-gioi-quoc-gia.md` | 19,856 | Query about prohibited acts around border markers |
| 5 | Luật Thi đua, khen thưởng | `law-2003-luat-thi-dua-khen-thuong.md` | 53,943 | Query about authority to award orders and medals |

Additional documents used in some members' runs include laws on land-use tax, insurance business, cultural heritage, population, and national security. These extra documents make retrieval more realistic because they add similarly styled legal language.

### Metadata Schema

| Metadata field | Type | Example | Why it helps |
|----------------|------|---------|--------------|
| `source` | string | `law-2001-luat-phong-chay-va-chua-chay.md` | Tracks which legal document a chunk came from. |
| `chunk_index` | int | `17` | Helps inspect the exact retrieved chunk position. |
| `strategy` | string | `sentence_chunker_1200` | Allows comparing retrieval output by chunking strategy. |
| `article` | string | `Điều 11` | Useful when a strategy extracts article-level metadata. |
| `topic` | string | `national_border` | Useful for metadata filtering on targeted legal topics. |

The most useful metadata fields for this domain are `source`, `article`, and `topic`. Legal queries often refer to exact articles, so article-aware metadata would likely improve both precision and explainability.

---

## 3. Shared Benchmark Queries

The group agreed on the following 5 benchmark queries and gold answers.

| # | Query | Gold answer | Source |
|---|-------|-------------|--------|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Ngày 04 tháng 10 hằng năm | Luật PCCC, Điều 11 |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí | Luật Bảo vệ sức khỏe, Điều 23 |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Ba cấp, mười hai bậc | Luật Sĩ quan, Điều 10 |
| 4 | Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm? | Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới | Luật Biên giới, Điều 14 |
| 5 | Ai quyết định tặng huân chương và huy chương? | Chủ tịch nước | Luật Thi đua, khen thưởng, Điều 77 |

The queries are intentionally specific and verifiable. They require the retriever to find exact legal facts rather than broad topical similarity.

---

## 4. Strategy Comparison

### Strategies Tried

| Member | Strategy | Rationale | Expected strengths | Expected weaknesses |
|--------|----------|-----------|--------------------|--------------------|
| Trần Vũ Khoa | `SentenceChunker(chunk_size=1200)` | Preserve full sentence boundaries in legal text. | Chunks are readable and less likely to cut a sentence in half. | May split article-level context and does not understand legal headings. |
| Lê Văn Khoa | `RecursiveChunker` | Split by natural separators from large to small. | Better preserves paragraphs and sections than fixed-size chunking. | Quality depends on separator order and document formatting. |
| Duy | `MarkdownSectionChunker(chunk_size=900)` | Use Markdown headings and legal markers such as Chương/Điều. | Best aligned with legal document structure. | More custom logic, may require careful fallback on irregular documents. |
| Hùng Lê | `FixedSizeChunker(chunk_size=500, overlap=50)` | Simple baseline with stable chunk sizes and overlap. | Predictable chunk count and boundary overlap. | Can cut across articles, clauses, or sentences. |
| Hiếu | Metadata-oriented retrieval | Emphasizes filtering and source/topic metadata. | Can reduce noisy results when source/topic is known. | Depends on metadata quality and may over-filter. |
| Linh | Recursive/section-based code | Uses structure-aware retrieval experiments. | Good fit for semi-structured documents. | Report fields were not fully standardized. |

### Baseline Observations

On Vietnamese legal texts, chunk boundary quality matters a lot:

- Fixed-size chunks are simple and stable, but they often cut across legal article boundaries.
- Sentence chunks are readable, but a legal answer may depend on the article title plus several sentences.
- Recursive chunks work better when documents have useful separators such as headings, paragraph breaks, or article markers.
- Custom section/article chunking is the most domain-aligned approach because legal documents are naturally organized by article.

---

## 5. Retrieval Results

The group used Top-3 retrieval as the primary metric. A query counts as a hit if at least one of the top-3 chunks comes from the expected document and supports the gold answer.

| Member | Strategy | Top-3 result reported | Notes |
|--------|----------|----------------------|-------|
| Trần Vũ Khoa | SentenceChunker | 1/5 | Mock embedder ranked many semantically wrong legal chunks above the correct source. |
| Lê Văn Khoa | RecursiveChunker | Not fully run on shared legal benchmark in report | Code and tests pass; report still says benchmark group data was not finalized. |
| Duy | MarkdownSectionChunker | 1/5 by mock ranking, but 5/5 answer chunks exist after filtering/inspection | Custom section chunking is promising, but mock embedding rank quality is weak. |
| Hùng Lê | FixedSizeChunker + metadata filter | 5/5 with metadata filter, 4/5 without filter | Metadata filtering improved query 4 about national border markers. |
| Hiếu | Metadata-oriented retrieval | 5/5 reported | Report indicates strong benchmark result, but strategy fields are not fully filled. |
| Linh | Recursive/section-based code | Not standardized in report | Code passes tests; report remains mostly template, so benchmark result is not reliable. |

### Best Performing Approach

Based on the available reports, the strongest practical result came from **Hùng Lê's FixedSizeChunker with metadata filtering**: 5/5 with a targeted metadata filter and 4/5 without filter.

However, the best domain fit appears to be **article/section-aware chunking**, such as Duy's `MarkdownSectionChunker`, because legal documents naturally organize facts by article. This strategy should improve further if combined with stronger embeddings and article metadata.

---

## 6. Metadata Filtering

Metadata filtering helped most when the query had a narrow legal scope.

The clearest case was:

```text
Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm?
```

Without metadata, the query can retrieve chunks from other legal documents that share words such as "nghiêm cấm", "quốc gia", or "bảo vệ". With metadata such as `topic=national_border` or `source=law-2003-luat-bien-gioi-quoc-gia.md`, the candidate set becomes much cleaner.

For legal retrieval, the group recommends adding:

- `law_title`
- `year`
- `article`
- `chapter`
- `topic`
- `source`

These fields would make both search and result verification easier.

---

## 7. Failure Analysis

### Failure Case

Khoa's SentenceChunker run failed query 5:

```text
Ai quyết định tặng huân chương và huy chương?
```

Expected source:

```text
Luật Thi đua, khen thưởng, Điều 77
```

Top-1 retrieved source:

```text
Luật Bảo vệ sức khỏe nhân dân
```

### Why It Failed

The main reason is the mock embedder. It validates the vector-store pipeline but does not understand Vietnamese legal semantics well. As a result, chunks with overlapping character patterns can outrank truly relevant legal chunks.

The second reason is chunk design. Sentence-based chunks preserve sentences, but they do not guarantee that article number, article title, and answer sentence stay together. For legal documents, losing the article header can make chunks less self-contained.

### Improvement Plan

The group would improve retrieval by:

1. Chunking by legal article rather than only by sentence or character size.
2. Adding metadata for `article`, `chapter`, `topic`, and `law_title`.
3. Using a real Vietnamese-capable embedding model instead of `_mock_embed`.
4. Using metadata filtering for queries that mention a known law/topic.
5. Evaluating both Top-3 recall and answer correctness, not only score.

---

## 8. Lessons Learned

1. **Strategy matters, but data structure matters more.** Legal documents have strong natural boundaries, so chunking by Article/Section is likely better than purely fixed-size chunking.

2. **Metadata is not optional in legal retrieval.** It helps explain where answers come from and can sharply reduce noise.

3. **Mock embeddings are useful for tests, not final quality.** Several semantically similar Vietnamese sentence pairs received weak or negative scores with `_mock_embed`.

4. **Top-3 retrieval and answer quality should both be checked.** A relevant chunk in Top-3 is useful, but the agent answer still needs to be grounded in that chunk.

5. **Folder-per-student worked well for Git.** Merging multiple branches caused no major conflict because each member worked mostly inside their own `submissions/<name>/` folder.

---

## 9. Submission Checklist

| Requirement | Status |
|-------------|--------|
| 6 student submissions merged | Done |
| Tests checked for all 6 submissions | Done |
| Shared domain selected | Done |
| 5-10 documents prepared | Done |
| 5 benchmark queries agreed | Done |
| Multiple retrieval strategies compared | Done |
| Failure case analyzed | Done |
| Group report created | Done |

### Test Summary

| Submission | Result |
|------------|--------|
| `submissions/LV_Khoa` | 42 passed |
| `submissions/Linh` | 42 passed |
| `submissions/khoa` | 42 passed |
| `submissions/2A202600725-DUY` | 42 passed |
| `submissions/hungle` | 42 passed |
| `submissions/hieu` | 42 passed |
