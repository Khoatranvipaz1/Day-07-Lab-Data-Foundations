# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Lê Văn Khoa
**Nhóm:** [Chưa điền tên nhóm]
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

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> Chưa có dữ liệu nhóm. Phần này sẽ điền sau khi nhóm thống nhất domain và bộ tài liệu chung.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Chưa có dữ liệu nhóm | | | |
| 2 | Chưa có dữ liệu nhóm | | | |
| 3 | Chưa có dữ liệu nhóm | | | |
| 4 | Chưa có dữ liệu nhóm | | | |
| 5 | Chưa có dữ liệu nhóm | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| Chưa có dữ liệu nhóm | | | |
| Chưa có dữ liệu nhóm | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Chưa có tài liệu nhóm | FixedSizeChunker (`fixed_size`) | | | |
| Chưa có tài liệu nhóm | SentenceChunker (`by_sentences`) | | | |
| Chưa có tài liệu nhóm | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> Strategy của tôi ưu tiên `RecursiveChunker` vì nó thử tách văn bản theo các separator từ lớn đến nhỏ: đoạn văn, dòng mới, câu, khoảng trắng, rồi fallback sang cắt cứng theo ký tự. Nếu một đoạn sau khi tách vẫn dài hơn `chunk_size`, thuật toán tiếp tục đệ quy với separator nhỏ hơn. Cách này giúp giữ cấu trúc tự nhiên của tài liệu tốt hơn fixed-size chunking.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tôi tạm chọn `RecursiveChunker` làm strategy cá nhân vì phù hợp với các tài liệu dạng hướng dẫn, ghi chú kỹ thuật, FAQ hoặc policy, nơi đoạn văn và câu thường giữ trọn một ý. Khi nhóm chốt domain cụ thể, tôi sẽ chạy benchmark để xác nhận strategy này có thật sự tốt hơn baseline hay không.

**Code snippet (nếu custom):**
```python
# Không dùng custom chunker ở phiên bản hiện tại.
# Strategy cá nhân dùng RecursiveChunker đã implement trong src/chunking.py.
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Chưa có tài liệu nhóm | best baseline | | | |
| Chưa có tài liệu nhóm | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | Chưa chạy benchmark nhóm | Giữ ngữ cảnh theo cấu trúc văn bản | Có thể tạo chunk chưa đều nếu tài liệu thiếu separator rõ |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Chưa kết luận vì cần chạy cùng 5 benchmark queries của nhóm trên từng strategy của các thành viên.

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

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Chưa có benchmark query nhóm | Chưa có gold answer |
| 2 | Chưa có benchmark query nhóm | Chưa có gold answer |
| 3 | Chưa có benchmark query nhóm | Chưa có gold answer |
| 4 | Chưa có benchmark query nhóm | Chưa có gold answer |
| 5 | Chưa có benchmark query nhóm | Chưa có gold answer |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chưa có benchmark query nhóm | | | | |
| 2 | Chưa có benchmark query nhóm | | | | |
| 3 | Chưa có benchmark query nhóm | | | | |
| 4 | Chưa có benchmark query nhóm | | | | |
| 5 | Chưa có benchmark query nhóm | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** Chưa chạy / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Chưa có phần so sánh nhóm/demo. Tôi sẽ cập nhật sau khi nhóm chạy benchmark và mỗi thành viên trình bày strategy riêng.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Chưa có phần demo liên nhóm.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Từ phần implementation cá nhân, tôi thấy metadata và chunk boundary ảnh hưởng trực tiếp đến retrieval. Khi có dữ liệu nhóm, tôi sẽ ưu tiên chọn metadata có thể filter thật sự hữu ích như `category`, `source`, `language`, hoặc `doc_type`, thay vì chỉ gắn metadata cho đủ số lượng.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | Chưa có dữ liệu nhóm / 10 |
| Chunking strategy | Nhóm | Chưa chạy benchmark nhóm / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | Chưa có benchmark queries nhóm / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | Chưa demo / 5 |
| **Tổng** | | **50 / 100 tạm thời, chưa tính các phần phụ thuộc nhóm** |
