# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Lê Văn Khoa
**Nhóm:** AI/RAG Data Foundations
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector embedding có high cosine similarity khi chúng chỉ gần cùng một hướng trong không gian vector. Với văn bản, điều này thường có nghĩa là hai câu/đoạn nói về cùng chủ đề hoặc cùng ý nghĩa, dù có thể dùng từ khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: Python is a programming language.
- Sentence B: Python is used to write software.
- Tại sao tương đồng: Cả hai câu đều nói về Python và vai trò của Python trong lập trình.

**Ví dụ LOW similarity:**
- Sentence A: Metadata filters narrow search results.
- Sentence B: Dogs are loyal animals.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau, một câu về retrieval/vector store và một câu về động vật.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector nên phù hợp để so sánh ý nghĩa/ngữ cảnh của text embeddings. Euclidean distance bị ảnh hưởng mạnh bởi độ lớn vector, trong khi với embedding văn bản ta thường quan tâm hai đoạn có cùng hướng nghĩa hay không.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((doc_length - overlap) / (chunk_size - overlap))`
> `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`, nên số chunk tăng từ 23 lên 25. Overlap nhiều hơn giúp giữ ngữ cảnh giữa hai chunk liền kề, nhưng cũng làm tăng số chunk cần embed và search.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Internal AI Knowledge Assistant / RAG Data Foundations

**Tại sao nhóm chọn domain này?**
> Bộ tài liệu này tập trung vào retrieval, vector store, RAG pipeline, chunking strategy, metadata và cách xây dựng trợ lý tri thức nội bộ. Domain này phù hợp với mục tiêu lab vì có đủ nội dung để kiểm tra Document -> Chunk -> Embed -> Store -> Query -> Answer. Các file cũng có cả tiếng Anh và tiếng Việt nên có thể kiểm tra metadata filtering theo `language`.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `python_intro.txt` | `data/python_intro.txt` | 1,944 | `language=en`, `category=python`, `doc_type=technical_overview` |
| 2 | `vector_store_notes.md` | `data/vector_store_notes.md` | 2,123 | `language=en`, `category=vector_store`, `doc_type=technical_notes` |
| 3 | `rag_system_design.md` | `data/rag_system_design.md` | 2,391 | `language=en`, `category=rag_architecture`, `doc_type=system_design` |
| 4 | `vi_retrieval_notes.md` | `data/vi_retrieval_notes.md` | 1,667 | `language=vi`, `category=retrieval`, `doc_type=vietnamese_notes` |
| 5 | `chunking_experiment_report.md` | `data/chunking_experiment_report.md` | 1,987 | `language=en`, `category=chunking`, `doc_type=experiment_report` |
| 6 | `customer_support_playbook.txt` | `data/customer_support_playbook.txt` | 1,692 | `language=en`, `category=support`, `doc_type=playbook` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `data/vector_store_notes.md` | Truy ngược kết quả retrieval về file gốc. |
| `language` | string | `en`, `vi` | Dùng để filter theo ngôn ngữ, đặc biệt với query tiếng Việt. |
| `category` | string | `vector_store`, `rag_architecture`, `chunking` | Giúp đánh giá query retrieve đúng nhóm nội dung hay không. |
| `doc_type` | string | `technical_notes`, `system_design`, `playbook` | Phân biệt loại tài liệu khi cần lọc theo mục đích sử dụng. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `python_intro.txt` | FixedSizeChunker (`fixed_size`) | 5 | 388.8 | Trung bình, đôi khi cắt ngang đoạn |
| `python_intro.txt` | SentenceChunker (`by_sentences`) | 5 | 387.0 | Tốt, giữ ranh giới câu |
| `python_intro.txt` | RecursiveChunker (`recursive`) | 6 | 321.8 | Tốt, ưu tiên đoạn/câu |
| `vector_store_notes.md` | FixedSizeChunker (`fixed_size`) | 5 | 424.6 | Trung bình |
| `vector_store_notes.md` | SentenceChunker (`by_sentences`) | 8 | 263.6 | Tốt nhưng chunk nhỏ hơn |
| `vector_store_notes.md` | RecursiveChunker (`recursive`) | 7 | 300.7 | Tốt, cân bằng kích thước/ngữ cảnh |
| `rag_system_design.md` | FixedSizeChunker (`fixed_size`) | 6 | 398.5 | Trung bình |
| `rag_system_design.md` | SentenceChunker (`by_sentences`) | 5 | 476.0 | Có chunk hơi dài |
| `rag_system_design.md` | RecursiveChunker (`recursive`) | 7 | 338.9 | Tốt nhất về độ đều và ngữ cảnh |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> Strategy của tôi ưu tiên `RecursiveChunker` vì nó thử tách văn bản theo các separator từ lớn đến nhỏ: đoạn văn, dòng mới, câu, khoảng trắng, rồi fallback sang cắt cứng theo ký tự. Nếu một đoạn sau khi tách vẫn dài hơn `chunk_size`, thuật toán tiếp tục đệ quy với separator nhỏ hơn. Cách này giúp giữ cấu trúc tự nhiên của tài liệu tốt hơn fixed-size chunking.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tôi chọn `RecursiveChunker` vì bộ tài liệu nhóm là markdown/text có cấu trúc đoạn, heading và câu tự nhiên. Strategy này khai thác cấu trúc đó tốt hơn fixed-size chunking vì nó ưu tiên tách theo đoạn rồi mới fallback xuống câu/khoảng trắng. Trong benchmark, `RecursiveChunker` retrieve đúng category trong top-3 cho 5/5 queries, dù top-1 chỉ đúng 4/5.

**Code snippet (nếu custom):**
```python
# Không dùng custom chunker ở phiên bản hiện tại.
# Strategy cá nhân dùng RecursiveChunker đã implement trong src/chunking.py.
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 6 docs AI/RAG | FixedSizeChunker | 32 | 409.5 | Top-1 đúng 5/5, top-3 đúng 5/5 |
| 6 docs AI/RAG | SentenceChunker | 32 | 367.0 | Top-1 đúng 5/5, top-3 đúng 5/5 |
| 6 docs AI/RAG | **RecursiveChunker của tôi** | 35 | 334.8 | Top-1 đúng 4/5, top-3 đúng 5/5 |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | 10 / 10 top-3 | Giữ ngữ cảnh theo cấu trúc văn bản, chunk khá đều | Query metadata filtering có top-1 chưa luôn đúng category mong muốn nếu query quá rộng |
| Baseline FixedSize | FixedSizeChunker | 10 / 10 top-3 | Đơn giản, ổn định, top-1 tốt trên benchmark này | Có thể cắt ngang ý hoặc câu |
| Baseline Sentence | SentenceChunker | 10 / 10 top-3 | Dễ đọc, giữ ranh giới câu | Một số chunk dài/ngắn không đều |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Với benchmark hiện tại, cả 3 strategy đều đạt top-3 relevant 5/5. Nếu ưu tiên top-1 thuần túy thì FixedSize/Sentence tốt hơn một chút, nhưng tôi vẫn chọn RecursiveChunker vì chunk dễ đọc, giữ cấu trúc markdown/text tốt hơn và phù hợp hơn khi tài liệu dài hoặc có nhiều heading/đoạn.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng regex `(?<=[.!?])\s+` để tách câu theo khoảng trắng sau dấu `.`, `!`, hoặc `?`, bao gồm cả newline sau dấu câu. Sau khi tách, tôi strip whitespace, bỏ câu rỗng, rồi nhóm tối đa `max_sentences_per_chunk` câu vào mỗi chunk. Nếu input rỗng thì trả về list rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `RecursiveChunker` nhận danh sách separator ưu tiên như `\n\n`, `\n`, `. `, space và chuỗi rỗng. Base case là text rỗng, text đã nhỏ hơn `chunk_size`, hoặc không còn separator thì fallback sang cắt cứng theo `chunk_size`. Sau khi `_split` tạo các mảnh nhỏ, `chunk()` merge các mảnh liên tiếp lại nếu vẫn nằm trong giới hạn kích thước.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi `Document` được chuẩn hóa thành record gồm `id`, `content`, `metadata`, và `embedding`; metadata luôn được thêm `doc_id` để phục vụ delete. `add_documents` embed nội dung bằng embedding function được inject, mặc định là `_mock_embed`, rồi lưu vào in-memory store. `search` embed query, tính dot product với từng vector đã lưu, sort giảm dần theo `score`, rồi trả về tối đa `top_k`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` lọc metadata trước, sau đó mới chạy similarity search trên tập candidate đã lọc; cách này đúng với yêu cầu metadata pre-filtering. `delete_document` xóa tất cả record có `metadata["doc_id"]` trùng với doc id được truyền vào và trả về `True` nếu có record bị xóa, `False` nếu không tìm thấy.

### KnowledgeBaseAgent

**`answer`** — approach:
> `KnowledgeBaseAgent.answer` gọi `store.search(question, top_k)` để lấy các chunk liên quan nhất. Prompt được tạo với phần context đánh số, có `source`, `score`, và nội dung chunk, sau đó mới đặt câu hỏi người dùng. Prompt cũng dặn LLM chỉ trả lời dựa trên context retrieved và nói không đủ thông tin nếu context không hỗ trợ câu trả lời.

### Test Results

```
pytest tests/ -v
============================= test session starts =============================
collected 42 items
...
============================= 42 passed in 0.08s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language. | Python is used to write software. | high | 0.0502 | Không |
| 2 | Vector stores retrieve similar embeddings. | A database can search vectors by similarity. | high | -0.1148 | Không |
| 3 | The weather is rainy today. | I need to buy a new laptop. | low | -0.0245 | Có |
| 4 | Metadata filters narrow search results. | Filters can restrict retrieval by category. | high | 0.2016 | Có |
| 5 | Dogs are loyal animals. | The deployment guide explains server setup. | low | -0.0143 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là pair 2: về mặt nghĩa, hai câu đều nói về vector store và similarity search, nhưng `_mock_embed` cho score âm. Điều này cho thấy mock embedding trong lab chỉ là fallback deterministic để test code, không thật sự hiểu ngữ nghĩa như embedding model thật. Với backend thật như `all-MiniLM-L6-v2` hoặc OpenAI embeddings, tôi kỳ vọng các cặp cùng nghĩa sẽ có score hợp lý hơn.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

Benchmark setup: tôi dùng 6 file AI/RAG trong `data/`, chunk bằng `RecursiveChunker(chunk_size=450)`, gắn metadata `source`, `language`, `category`, `doc_type`, rồi index vào `EmbeddingStore`. Do local `sentence-transformers` không chạy được trong môi trường hiện tại vì lỗi NumPy/SciPy, benchmark dùng một lexical embedding nhỏ dựa trên bag-of-words + MD5 hash và inject qua `embedding_fn`; core implementation vẫn pass test với `_mock_embed`.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What are the four stages in a vector search pipeline? | Chunk documents, embed each chunk, store vectors with metadata, then embed the query and rank by similarity. |
| 2 | When should metadata filtering be used in retrieval? | Use metadata filters to narrow search by source, language, department, product area, date, or access level so retrieval avoids wrong/noisy documents. |
| 3 | How does the RAG assistant use retrieved context to answer? | Retrieve relevant chunks, inject them into a prompt, and instruct the model to answer only from supplied evidence or admit insufficient context. |
| 4 | Which chunking strategy preserved context best in the experiment? | Recursive chunking preserved context best by splitting on larger structural boundaries first and falling back to smaller separators. |
| 5 | Metadata ngôn ngữ (`metadata_filter={"language": "vi"}`) | Metadata filtering can restrict retrieval to Vietnamese technical documents and avoid unrelated marketing or English documents. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Vector search pipeline stages | `vector_store_notes.md` chunk 1/2: vector store workflow and four-stage pipeline | 0.4777 | Yes | Answer should list chunk, embed, store, embed query/rank. |
| 2 | Metadata filtering use case | `rag_system_design.md` chunk 3 top-1; `vector_store_notes.md` relevant in top-3 | 0.2357 | Partial | Answer should explain metadata narrowing and noise reduction; relevant chunk appears in top-3, not top-1. |
| 3 | RAG context injection | `rag_system_design.md` chunk 2: assistant grounds responses in retrieved text | 0.3032 | Yes | Answer should describe retrieve -> prompt context -> answer from evidence. |
| 4 | Best chunking strategy | `chunking_experiment_report.md` chunk 1/4: recursive chunking and experiment result | 0.3333 | Yes | Answer should say recursive chunking preserves context best. |
| 5 | Metadata filter for Vietnamese docs | `vi_retrieval_notes.md` chunk 4: metadata labels language/category/date and filters Vietnamese technical docs | 0.1127 | Yes | Answer should mention filtering to Vietnamese technical docs and avoiding unrelated docs. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Chưa có phần demo/thành viên khác thật. Tạm thời, từ so sánh baseline, tôi học được rằng strategy có top-1 tốt nhất chưa chắc là strategy dễ giải thích hoặc giữ ngữ cảnh tốt nhất. RecursiveChunker có top-1 thấp hơn một query nhưng vẫn giữ top-3 tốt và chunk dễ đọc hơn.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Chưa có phần demo liên nhóm.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ tách rõ hơn các file theo domain thay vì để lẫn tài liệu AI/RAG với văn bản pháp lý/giáo dục trong cùng thư mục `data/`. Metadata nên được chuẩn hóa ngay từ đầu, đặc biệt là `language`, `category`, `doc_type`, để query có thể filter trước khi search. Tôi cũng sẽ thử embedding thật nếu môi trường Python ổn định hơn, vì `_mock_embed` chỉ phù hợp để test code chứ không đo semantic retrieval tốt.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 12 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | Chưa demo / 5 |
| **Tổng** | | **82 / 100 tạm thời, chưa tính demo thật và so sánh thành viên thật** |
