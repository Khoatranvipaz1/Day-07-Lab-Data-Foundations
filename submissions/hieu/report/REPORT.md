# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Nguyễn Phúc Hiếu]
**Nhóm:** [Tên nhóm]
**Ngày:** [05/06/2026]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai đoạn văn bản có vector embedding gần cùng hướng, tức là chúng gần nhau về ý nghĩa hoặc chủ đề. Điểm càng gần 1 thì mức độ tương đồng ngữ nghĩa càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: Python được dùng nhiều trong phân tích dữ liệu và machine learning.
- Sentence B: Các nhà khoa học dữ liệu dùng Python để huấn luyện mô hình và xử lý dữ liệu.
- Tại sao tương đồng: Cả hai câu đều nói về vai trò của Python trong dữ liệu và học máy.

**Ví dụ LOW similarity:**
- Sentence A: Python là một ngôn ngữ lập trình bậc cao.
- Sentence B: Gấu nâu sống trong các khu rừng phương Bắc.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau: lập trình và động vật.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, nên phù hợp khi đo mức độ giống nhau về nghĩa giữa các đoạn text. Euclidean distance bị ảnh hưởng nhiều bởi độ lớn vector, trong khi với text embeddings thì hướng thường quan trọng hơn độ dài.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((doc_length - overlap) / (chunk_size - overlap))`  
> Tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`  
> Đáp án: 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`, nên tăng từ 23 lên 25 chunks. Overlap nhiều hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng sẽ làm tăng số chunk cần lưu và tính embedding.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Em dùng regex `(?<=[.!?])(?:\s+|\n+)` để tách câu sau các dấu `.`, `!`, `?` khi gặp khoảng trắng hoặc xuống dòng. Sau khi tách, em `strip()` từng câu, bỏ câu rỗng và gom mỗi `max_sentences_per_chunk` câu thành một chunk. Với text rỗng, hàm trả về danh sách rỗng để tránh tạo chunk không có nội dung.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `RecursiveChunker` thử tách văn bản theo thứ tự separator từ lớn đến nhỏ: đoạn văn, dòng, câu, từ, rồi ký tự. Base case là khi đoạn hiện tại đã ngắn hơn hoặc bằng `chunk_size` thì trả về luôn; nếu một phần vẫn quá dài, `_split` tiếp tục gọi đệ quy với separator nhỏ hơn. Khi hết separator, hàm fallback bằng cách cắt fixed-size để bảo đảm không bị kẹt.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi `Document` được chuyển thành một record gồm `id`, `content`, `metadata` và `embedding`; metadata được thêm `doc_id` để dễ truy vết và xóa. Khi search, store embed query, tính dot product giữa query embedding và từng document embedding, sau đó sắp xếp giảm dần theo score để trả về `top_k`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` lọc metadata trước, rồi mới chạy similarity search trên tập record đã lọc để giảm nhiễu. `delete_document` xóa tất cả record có `metadata["doc_id"]` trùng với `doc_id` được truyền vào và trả về `True` nếu có ít nhất một record bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Agent lấy `top_k` chunk liên quan từ `EmbeddingStore`, ghép chúng vào phần `Context`, rồi tạo prompt gồm instruction, context, question và phần `Answer:`. Prompt yêu cầu LLM chỉ trả lời dựa trên retrieved context; nếu context không đủ thì phải nói là knowledge base không có câu trả lời.

### Test Results

```
============================= test session starts =============================
collected 42 items
tests/test_solution.py ...                                             [100%]
============================= 42 passed in 0.09s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python được dùng cho phân tích dữ liệu và machine learning. | Data scientists use Python to train models and analyze data. | high | 0.1484 | Đúng một phần |
| 2 | Vector stores rank embeddings by similarity. | A vector database retrieves semantically similar items. | high | 0.1976 | Đúng một phần |
| 3 | Nhóm support review các truy vấn thất bại hằng tuần. | Billing problems should be escalated when documents are missing. | high | -0.1441 | Sai |
| 4 | Python là một ngôn ngữ lập trình bậc cao. | Brown bears live in northern forests. | low | 0.1565 | Sai |
| 5 | Metadata filters improve retrieval precision. | Flask exposes application logic over HTTP. | low | 0.1975 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là một số cặp em dự đoán “low” lại có score dương khá cao, trong khi một cặp có vẻ liên quan lại ra score âm. Điều này xảy ra vì lab đang dùng `_mock_embed`, vector được tạo deterministic từ hash chứ không thật sự hiểu nghĩa câu. Nếu dùng embedding model thật, kết quả high/low thường sẽ phản ánh ngữ nghĩa tốt hơn.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Vì sao các nhóm thường chọn Python? | Vì Python dễ đọc, dễ tiếp cận với lập trình viên mới và có hệ sinh thái công cụ trưởng thành để prototype nhanh. |
| 2 | Bốn bước trong một pipeline vector search phổ biến là gì? | Chia tài liệu thành chunk, embed từng chunk, lưu vector kèm metadata, rồi embed query và xếp hạng theo similarity. |
| 3 | Assistant nên làm gì nếu retrieval yếu hoặc mâu thuẫn? | Assistant nên nói rõ rằng bằng chứng không đủ thay vì giả vờ trả lời chắc chắn. |
| 4 | Vì sao nội dung support nên tránh các câu mơ hồ? | Vì hướng dẫn cụ thể về page, button hoặc log source giúp retriever khớp tốt hơn với từ khóa troubleshooting trong câu hỏi. |
| 5 | Strategy chunking nào cân bằng tốt nhất trong experiment? | Recursive chunking cân bằng tốt nhất vì ưu tiên giữ ngữ cảnh theo cấu trúc lớn rồi mới tách nhỏ khi cần. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Vì sao các nhóm thường chọn Python? | `python_intro`: Python dùng cho AI, data, model integration | 0.2422 | Có | Python dễ đọc, dễ học, tooling tốt |
| 2 | Bốn bước trong một pipeline vector search phổ biến là gì? | `vector_store_notes`: workflow vector search và metadata | 0.1401 | Có, dùng filter `domain=vector_store` | Chunk, embed, store vector/metadata, embed query và rank |
| 3 | Assistant nên làm gì nếu retrieval yếu hoặc mâu thuẫn? | `rag_system_design`: yêu cầu assistant dựa trên evidence | 0.2229 | Có | Nói context không đủ thay vì tự bịa câu trả lời |
| 4 | Vì sao nội dung support nên tránh các câu mơ hồ? | `customer_support_playbook`: cần chỉ rõ page, button, log source | 0.0018 | Có, dùng filter `domain=support` | Hướng dẫn cụ thể giúp retrieval khớp tốt hơn |
| 5 | Strategy chunking nào cân bằng tốt nhất trong experiment? | `chunking_experiment_report`: recursive chunking giữ context tốt | 0.2099 | Có, dùng filter `domain=chunking` | Recursive chunking cân bằng tốt nhất |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Em học được rằng sentence-based chunking rất dễ kiểm tra bằng mắt và khá phù hợp với tài liệu FAQ ngắn. Tuy nhiên, khi tài liệu có nhiều heading và paragraph, recursive chunking thường giữ được ngữ cảnh tốt hơn.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Em thấy metadata không chỉ là thông tin phụ mà có thể quyết định retrieval đúng hay sai. Khi query có phạm vi hẹp, filter theo domain, language hoặc source giúp giảm nhiều kết quả gần nghĩa nhưng sai ngữ cảnh.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, em sẽ thiết kế benchmark queries trước khi chọn chunk size để tránh tối ưu theo cảm tính. Em cũng sẽ thêm metadata chi tiết hơn như `audience`, `section_title` và `updated_at` để search/filter chính xác hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
