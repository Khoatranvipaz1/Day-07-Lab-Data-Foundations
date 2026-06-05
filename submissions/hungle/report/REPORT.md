# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu: High cosine similarity nghĩa là hai đoạn văn bản có ý nghĩa gần nhau trong không gian embedding. Nói đơn giản, dù dùng từ khác nhau, nếu chúng nói về cùng một chủ đề hoặc cùng một ý thì điểm similarity sẽ cao.

**Ví dụ HIGH similarity:**
- Sentence A:
- Sentence B:
- Tại sao tương đồng:

**Ví dụ LOW similarity:**
- Sentence A:
- Sentence B:
- Tại sao khác:

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Pháp luật Việt Nam

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain pháp luật Việt Nam vì văn bản luật có cấu trúc rõ ràng theo Chương, Điều, Khoản và Điểm, phù hợp để thử nghiệm nhiều chiến lược chunking. Bộ dữ liệu cũng chứa các chủ đề khác nhau như y tế, quân đội, phòng cháy chữa cháy, biên giới và thi đua khen thưởng, giúp đánh giá khả năng retrieval và metadata filtering trên những câu hỏi cụ thể.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Luật Bảo vệ sức khỏe nhân dân | `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md` (file Markdown nhóm thu thập) | 27,939 | `law_number=21-LCT/HĐNN8`, `year=1989`, `topic=health` |
| 2 | Luật Sĩ quan Quân đội nhân dân Việt Nam | `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md` (file Markdown nhóm thu thập) | 31,961 | `law_number=16/1999/QH10`, `year=1999`, `topic=military` |
| 3 | Luật Phòng cháy và chữa cháy | `law-2001-luat-phong-chay-va-chua-chay.md` (file Markdown nhóm thu thập) | 43,459 | `law_number=27/2001/QH10`, `year=2001`, `topic=fire_safety` |
| 4 | Luật Biên giới quốc gia | `law-2003-luat-bien-gioi-quoc-gia.md` (file Markdown nhóm thu thập) | 19,856 | `law_number=06/2003/QH11`, `year=2003`, `topic=national_border` |
| 5 | Luật Thi đua, khen thưởng | `law-2003-luat-thi-dua-khen-thuong.md` (file Markdown nhóm thu thập) | 53,943 | `law_number=15/2003/QH11`, `year=2003`, `topic=awards` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `law-2001-luat-phong-chay-va-chua-chay` | Nhóm tất cả chunk thuộc cùng một văn bản và hỗ trợ xóa theo document. |
| `title` | `str` | `Luật Phòng cháy và chữa cháy` | Xác định tên luật chứa thông tin được retrieve. |
| `law_number` | `str` | `27/2001/QH10` | Cho phép tìm hoặc lọc chính xác theo số hiệu văn bản. |
| `year` | `int` | `2001` | Hỗ trợ lọc và so sánh văn bản theo năm ban hành. |
| `topic` | `str` | `fire_safety` | Thu hẹp phạm vi search vào đúng lĩnh vực pháp luật. |
| `document_type` | `str` | `law` | Phân biệt luật với nghị định, nghị quyết hoặc loại tài liệu khác nếu mở rộng dataset. |
| `language` | `str` | `vi` | Hỗ trợ lọc theo ngôn ngữ khi dữ liệu có nhiều ngôn ngữ. |
| `source_file` | `str` | `law-2001-luat-phong-chay-va-chua-chay.md` | Giúp truy vết kết quả về file nguồn để kiểm chứng. |
| `chapter` | `str` | `Chương 1` | Giữ vị trí cấu trúc của chunk trong văn bản luật. |
| `article` | `str` | `Điều 11` | Cho phép chỉ ra chính xác điều luật làm căn cứ cho câu trả lời. |
| `chunk_index` | `int` | `10` | Xác định thứ tự chunk và hỗ trợ kiểm tra lại quá trình chunking. |
| `strategy` | `str` | `by_article` | Giúp so sánh kết quả retrieval giữa các chiến lược chunking. |

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
> Tôi dùng regex `(?<=[.!?])(?:\s+|\n+)` để nhận diện ranh giới câu sau các dấu `.`, `!`, `?`, sau đó loại bỏ khoảng trắng thừa và các phần rỗng. Các câu được gom theo từng nhóm có tối đa `max_sentences_per_chunk` câu; nếu đầu vào rỗng thì hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán thử các separator theo thứ tự ưu tiên: đoạn văn (`\n\n`), dòng (`\n`), câu (`. `), từ (` `), rồi cuối cùng là ký tự. Base case là khi đoạn hiện tại không vượt quá `chunk_size`; nếu không còn separator phù hợp, hàm dùng `FixedSizeChunker` với overlap bằng 0 để đảm bảo văn bản vẫn được chia nhỏ.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `add_documents` chuyển từng `Document` thành một record gồm id, content, metadata, doc_id và embedding, sau đó lưu vào danh sách in-memory. Khi search, câu query cũng được embedding, hệ thống tính dot product giữa query embedding và từng document embedding, sắp xếp score giảm dần rồi trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` lọc record theo tất cả cặp key-value trong `metadata_filter` trước, sau đó mới tính similarity trên tập kết quả đã lọc. `delete_document` loại bỏ mọi record có `metadata["doc_id"]` trùng với id cần xóa và trả về `True` nếu kích thước store giảm, ngược lại trả về `False`.

### KnowledgeBaseAgent

**`answer`** — approach:
> `answer` gọi `store.search()` để retrieve các chunk liên quan nhất, sau đó đánh số và ghép nội dung các chunk thành phần `Context` trong prompt. Prompt gồm context, câu hỏi và vị trí để sinh answer; cuối cùng agent gọi `llm_fn(prompt)`, giúp câu trả lời được tạo dựa trên dữ liệu đã retrieve.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
collected 42 items

tests/test_solution.py ..........................................        [100%]

============================= 42 passed in 2.53s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

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
