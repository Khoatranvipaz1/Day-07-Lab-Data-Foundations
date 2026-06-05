# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai đoạn văn bản có vector embedding gần cùng hướng, cho thấy nội dung hoặc ý nghĩa của chúng tương đồng. Hai câu không nhất thiết phải dùng chính xác cùng từ ngữ nhưng vẫn có thể đạt similarity cao nếu cùng diễn đạt một ý.

**Ví dụ HIGH similarity:**
- Sentence A: Người bệnh trong trường hợp cấp cứu được tiếp nhận tại bất kỳ cơ sở khám chữa bệnh nào.
- Sentence B: Khi có tình trạng khẩn cấp, bệnh nhân có thể đến mọi cơ sở y tế để được cấp cứu.
- Tại sao tương đồng: Hai câu sử dụng từ ngữ khác nhau nhưng đều nói về quyền được cấp cứu tại bất kỳ cơ sở y tế nào.

**Ví dụ LOW similarity:**
- Sentence A: Ngày toàn dân phòng cháy và chữa cháy là ngày 04 tháng 10.
- Sentence B: Hệ thống cấp bậc quân hàm sĩ quan gồm ba cấp và mười hai bậc.
- Tại sao khác: Một câu nói về phòng cháy chữa cháy, còn câu kia nói về cấp bậc quân hàm, nên chúng thuộc hai chủ đề pháp luật khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào góc giữa hai vector, tức hướng biểu diễn ý nghĩa, thay vì khoảng cách tuyệt đối hoặc độ dài vector. Vì vậy, nó phù hợp để so sánh hai văn bản có độ dài khác nhau nhưng vẫn diễn đạt nội dung tương tự.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
>
> Thay số: `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.11) = 23`.
>
> **Đáp án: 23 chunks.**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap bằng 100, số chunk là `ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = ceil(24.75) = 25 chunks`. Số chunk tăng từ 23 lên 25 vì bước nhảy giữa hai chunk giảm; overlap lớn hơn giúp giữ ngữ cảnh ở vị trí cắt nhưng đồng thời làm tăng dữ liệu trùng lặp và chi phí lưu trữ, tìm kiếm.

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
| Luật Phòng cháy và chữa cháy | FixedSizeChunker (`fixed_size`) | 97 | 497.52 | Một số chunk bị cắt giữa Điều hoặc Khoản |
| Luật Phòng cháy và chữa cháy | SentenceChunker (`by_sentences`) | 146 | 295.37 | Giữ trọn câu nhưng có thể tách một Điều thành nhiều chunk |
| Luật Phòng cháy và chữa cháy | RecursiveChunker (`recursive`) | 106 | 407.87 | Giữ cấu trúc đoạn tốt hơn fixed-size |
| Luật Biên giới quốc gia | FixedSizeChunker (`fixed_size`) | 45 | 490.13 | Có thể mất tiêu đề Điều tại điểm cắt |
| Luật Biên giới quốc gia | SentenceChunker (`by_sentences`) | 49 | 402.57 | Giữ trọn câu, kích thước chunk không đều |
| Luật Biên giới quốc gia | RecursiveChunker (`recursive`) | 51 | 387.27 | Khá tốt, ưu tiên ranh giới đoạn và câu |
| Luật Thi đua, khen thưởng | FixedSizeChunker (`fixed_size`) | 120 | 499.11 | Ổn định kích thước nhưng đôi lúc cắt ngang ý |
| Luật Thi đua, khen thưởng | SentenceChunker (`by_sentences`) | 126 | 425.61 | Dễ đọc nhưng một Điều dài có thể bị phân tách |
| Luật Thi đua, khen thưởng | RecursiveChunker (`recursive`) | 131 | 409.69 | Giữ ngữ cảnh tự nhiên tốt hơn fixed-size |

### Strategy Của Tôi

**Loại:** `FixedSizeChunker(chunk_size=500, overlap=50)`

**Mô tả cách hoạt động:**
> Strategy chia văn bản thành các đoạn có tối đa 500 ký tự. Mỗi chunk mới bắt đầu sau 450 ký tự, vì 50 ký tự cuối của chunk trước được lặp lại làm overlap. Cách chia không phụ thuộc vào ranh giới Chương, Điều hoặc câu, nên kích thước chunk ổn định nhưng có thể cắt ngang cấu trúc pháp luật.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tôi chọn FixedSizeChunker làm baseline đơn giản để đánh giá ảnh hưởng của việc cắt thuần theo kích thước đối với văn bản luật. Overlap 50 ký tự giúp giảm nguy cơ mất hoàn toàn ngữ cảnh ở điểm cắt, đồng thời cấu hình này dễ so sánh với SentenceChunker, RecursiveChunker và strategy custom theo Điều của các thành viên khác.

**Code snippet (nếu custom):**
```python
# Không dùng custom strategy
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 5 văn bản luật | **FixedSizeChunker của tôi** | 395 | khoảng 496 | Gold evidence xuất hiện trong top-3 ở 5/5 query khi dùng metadata filter cho query mơ hồ |
| 3 văn bản baseline | RecursiveChunker | 288 | khoảng 402 | Chunk coherent hơn; cần chạy cùng benchmark của nhóm để so sánh retrieval trực tiếp |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | FixedSizeChunker (500/50) | 8/10 | Kích thước ổn định, triển khai đơn giản, 5/5 query có evidence trong top-3 khi filter đúng | Có thể cắt giữa Điều; một đáp án chỉ ở top-3 và agent thiếu chi tiết ở query mơ hồ |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Chưa thể kết luận strategy tốt nhất trước khi nhận kết quả benchmark của các thành viên khác trên cùng 5 query. Dự đoán strategy chunk theo Điều hoặc RecursiveChunker sẽ giữ cấu trúc pháp luật tốt hơn FixedSizeChunker, nhưng kết luận cuối cùng phải dựa trên bảng so sánh top-3 của cả nhóm.

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
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Ngày 04 tháng 10 hằng năm. |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Tại bất kỳ cơ sở khám bệnh, chữa bệnh nào. |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Gồm ba cấp và mười hai bậc. |
| 4 | Các hành vi bị nghiêm cấm gồm những gì? | Trong phạm vi Luật Biên giới quốc gia: xê dịch, phá hoại mốc quốc giới hoặc làm sai lệch đường biên giới quốc gia. |
| 5 | Ai quyết định tặng huân chương và huy chương? | Chủ tịch nước. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Luật PCCC, chunk 13, chứa Điều 11 và ngày 04/10 | 0.6027 | Có | Trả lời đúng: ngày 04 tháng 10 hằng năm |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Luật Bảo vệ sức khỏe nhân dân, chunk 29, chứa Điều 23 | 0.3452 | Có | Trả lời đúng: tại bất kỳ cơ sở khám bệnh, chữa bệnh nào |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Top-1 nói về khái niệm phong/thăng quân hàm; gold evidence nằm ở top-3, chunk 12 | 0.6731 | Không ở top-1, có ở top-3 | Trả lời đúng: ba cấp, mười hai bậc |
| 4 | Các hành vi bị nghiêm cấm gồm những gì? | Sau filter `topic=national_border`, chunk 18 của Luật Biên giới quốc gia chứa Điều 14 | 0.1864 | Có sau filter | Answer còn thiếu chi tiết; retrieval đã tìm đúng đoạn về phá hoại mốc quốc giới |
| 5 | Ai quyết định tặng huân chương và huy chương? | Luật Thi đua, khen thưởng, chunk 97, chứa Điều 77 | 0.4497 | Có | Trả lời đúng: Chủ tịch nước |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5 khi áp dụng metadata filter `topic=national_border` cho query số 4; nếu không filter thì 4 / 5.

**Embedding dùng cho benchmark:** lexical hash embedding không cần dependency ngoài. `_mock_embed` mặc định chỉ kiểm tra pipeline và cho kết quả 0/5 trên bộ câu hỏi tiếng Việt vì không biểu diễn quan hệ ngữ nghĩa.

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
