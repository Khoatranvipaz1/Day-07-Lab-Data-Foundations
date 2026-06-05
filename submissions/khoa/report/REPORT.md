# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trần Văn Khoa  
**MSV:** 2A202600827  
**Nhóm:** Nhóm benchmark văn bản luật Việt Nam  
**Ngày:** 05/06/2026

---

## 1. Warm-up

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
Hai text chunks có cosine similarity cao nghĩa là vector embedding của chúng gần cùng hướng, tức hai đoạn có nội dung hoặc ý nghĩa tương tự nhau. Trong retrieval, chunk có score cao thường được xem là liên quan hơn với query.

**Ví dụ HIGH similarity:**
- Sentence A: "Người bệnh cấp cứu phải được tiếp nhận tại cơ sở khám chữa bệnh."
- Sentence B: "Cơ sở y tế phải xử trí kịp thời khi có bệnh nhân cấp cứu."
- Tại sao tương đồng: Cả hai câu đều nói về cấp cứu và trách nhiệm của cơ sở y tế.

**Ví dụ LOW similarity:**
- Sentence A: "Ngày toàn dân phòng cháy và chữa cháy là ngày 04 tháng 10."
- Sentence B: "Thuế sử dụng đất nông nghiệp được tính theo diện tích đất."
- Tại sao khác: Hai câu thuộc hai chủ đề luật khác nhau, một câu về phòng cháy chữa cháy và một câu về thuế đất.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector, nên phù hợp để đo độ giống nhau về nghĩa hơn là độ lớn tuyệt đối. Với text embeddings, độ dài vector có thể bị ảnh hưởng bởi cách model biểu diễn, còn hướng vector thường phản ánh ngữ nghĩa tốt hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Formula:

```text
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / (500 - 50))
           = ceil(9950 / 450)
           = 23 chunks
```

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```text
num_chunks = ceil((10000 - 100) / (500 - 100))
           = ceil(9900 / 400)
           = 25 chunks
```

Overlap tăng làm số chunk tăng vì mỗi bước trượt ngắn hơn. Overlap hữu ích khi câu hoặc điều khoản bị cắt ngang giữa hai chunk, giúp giữ thêm ngữ cảnh ở biên chunk.

---

## 2. Document Selection

### Domain & Lý Do Chọn

**Domain:** Văn bản luật Việt Nam.

Nhóm chọn domain luật vì tài liệu có cấu trúc rõ ràng theo điều, khoản, chương và có nhiều câu hỏi benchmark kiểm chứng được trực tiếp từ nội dung. Đây cũng là domain phù hợp để quan sát retrieval hoạt động tốt hay thất bại khi văn bản dài, nhiều thuật ngữ, nhiều điều khoản gần giống nhau.

### Data Inventory

Bộ dữ liệu được convert từ `docs/0000.parquet` sang Markdown, lưu trong `submissions/khoa/data/parquet_docs/`.

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Luật Bảo vệ sức khỏe nhân dân | `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md` | 27,939 | `source`, `chunk_index`, `strategy` |
| 2 | Luật Thuế sử dụng đất nông nghiệp | `law-1993-luat-thue-su-dung-dat-nong-nghiep.md` | 29,879 | `source`, `chunk_index`, `strategy` |
| 3 | Luật Sĩ quan Quân đội nhân dân Việt Nam | `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md` | 31,961 | `source`, `chunk_index`, `strategy` |
| 4 | Luật Phòng cháy và chữa cháy | `law-2001-luat-phong-chay-va-chua-chay.md` | 43,459 | `source`, `chunk_index`, `strategy` |
| 5 | Luật Biên giới quốc gia | `law-2003-luat-bien-gioi-quoc-gia.md` | 19,856 | `source`, `chunk_index`, `strategy` |
| 6 | Luật Thi đua, khen thưởng | `law-2003-luat-thi-dua-khen-thuong.md` | 53,943 | `source`, `chunk_index`, `strategy` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `law-2001-luat-phong-chay-va-chua-chay.md` | Biết chunk được lấy từ văn bản luật nào, dùng để đánh giá query có retrieve đúng tài liệu không. |
| `chunk_index` | int | `12` | Xác định vị trí chunk trong tài liệu, giúp truy vết thông tin và phân tích failure case. |
| `strategy` | string | `sentence_chunker_1200` | Ghi lại strategy đã tạo chunk, giúp so sánh kết quả giữa các thành viên. |

---

## 3. Chunking Strategy

### Baseline Analysis

Chạy thử 3 chunking strategies trên 3 tài liệu đầu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Luật Bảo vệ sức khỏe nhân dân | FixedSizeChunker | 33 | 991.8 | Trung bình, có thể cắt ngang câu |
| Luật Bảo vệ sức khỏe nhân dân | SentenceChunker | 26 | 1066.4 | Tốt, giữ biên câu |
| Luật Bảo vệ sức khỏe nhân dân | RecursiveChunker | 38 | 874.9 | Tốt, linh hoạt theo separator |
| Luật Thuế sử dụng đất nông nghiệp | FixedSizeChunker | 35 | 998.9 | Trung bình |
| Luật Thuế sử dụng đất nông nghiệp | SentenceChunker | 28 | 1061.3 | Tốt |
| Luật Thuế sử dụng đất nông nghiệp | RecursiveChunker | 39 | 904.9 | Tốt |
| Luật Sĩ quan Quân đội nhân dân Việt Nam | FixedSizeChunker | 38 | 986.7 | Trung bình |
| Luật Sĩ quan Quân đội nhân dân Việt Nam | SentenceChunker | 31 | 1026.3 | Tốt |
| Luật Sĩ quan Quân đội nhân dân Việt Nam | RecursiveChunker | 42 | 898.8 | Tốt |

### Strategy Của Tôi

**Loại:** SentenceChunker

**Tham số:** `SentenceChunker(chunk_size=1200)`

**Mô tả cách hoạt động:**  
Strategy này tách văn bản theo ranh giới câu bằng dấu câu như `.`, `!`, `?`, sau đó gom nhiều câu vào một chunk cho đến gần giới hạn `chunk_size`. Nếu thêm câu mới làm chunk vượt quá giới hạn, chunk hiện tại được đóng lại và bắt đầu chunk tiếp theo. Cách này tránh cắt ngang câu, giúp chunk dễ đọc và dễ kiểm chứng hơn.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Văn bản luật thường trình bày ý theo câu hoàn chỉnh trong từng điều khoản. Câu trả lời cho benchmark query thường nằm trong một hoặc vài câu liền nhau, nên giữ nguyên ranh giới câu sẽ giúp context mạch lạc hơn so với fixed-size chunking. Tôi chọn `chunk_size=1200` để mỗi chunk đủ dài giữ ngữ cảnh điều luật nhưng không quá lớn.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 3 tài liệu đầu | FixedSizeChunker | 106 | 992.5 | Dễ cắt ngang câu nhưng số chunk ổn định |
| 3 tài liệu đầu | RecursiveChunker | 119 | 892.9 | Tách linh hoạt, nhiều chunk hơn |
| 3 tài liệu đầu | **SentenceChunker của tôi** | 85 | 1051.3 | Chunk dễ đọc, giữ câu hoàn chỉnh |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | SentenceChunker, chunk_size=1200 | 2/10 | Chunk dễ đọc, ít cắt ngang câu | Với mock embedder, recall thấp |
| Thành viên khác | FixedSizeChunker | Chưa tổng hợp | Dễ cấu hình, kiểm soát kích thước tốt | Có thể cắt ngang điều khoản |
| Thành viên khác | RecursiveChunker | Chưa tổng hợp | Hợp văn bản có heading, đoạn, điều khoản | Cần chọn separator phù hợp |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
Trong kết quả cá nhân của tôi, SentenceChunker tạo chunk dễ đọc nhưng Top-3 recall chỉ đạt 1/5 với mock embedder. Nếu chỉ xét chất lượng retrieval, nhóm nên so sánh thêm với RecursiveChunker vì văn bản luật có nhiều separator tự nhiên như tiêu đề, xuống dòng, điều và khoản.

---

## 4. My Approach

### Chunking Functions

**`SentenceChunker.chunk` approach:**  
Tôi dùng regex để tách câu theo dấu kết thúc câu, sau đó gom câu vào chunk theo giới hạn kích thước. Edge cases gồm text rỗng, câu đơn dài hơn chunk size, và tham số `max_sentences_per_chunk` để tương thích test.

**`RecursiveChunker.chunk` / `_split` approach:**  
RecursiveChunker thử tách văn bản theo separator từ lớn đến nhỏ như `\n\n`, `\n`, `. `, space và cuối cùng là ký tự. Base case là đoạn đã nhỏ hơn `chunk_size` hoặc không còn separator, khi đó fallback sang fixed-size slicing.

### EmbeddingStore

**`add_documents` + `search` approach:**  
Store lưu document và embedding trong list in-memory. Khi add document, tôi embed `content` bằng embedding function, mặc định là `_mock_embed`. Khi search, query cũng được embed và các document được xếp hạng bằng cosine similarity.

**`search_with_filter` + `delete_document` approach:**  
`search_with_filter` lọc metadata trước, sau đó mới tính similarity cho các document phù hợp. `delete_document` xóa document dựa trên `id`, rebuild lại list document và embedding để collection size giảm đúng.

### KnowledgeBaseAgent

**`answer` approach:**  
Agent retrieve top-k context từ `EmbeddingStore`, format context kèm source và score, rồi gọi `llm_fn` nếu có. Nếu không có LLM thật, agent trả về content của chunk tốt nhất để đảm bảo pipeline RAG vẫn chạy được.

### Test Results

```text
42 passed in 0.09s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions

Các score dưới đây dùng `_mock_embed`, nên kết quả có thể không phản ánh tốt ngữ nghĩa tiếng Việt.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Cấp cứu người bệnh tại cơ sở khám chữa bệnh. | Người bệnh cấp cứu được tiếp nhận và xử trí ở cơ sở y tế. | high | -0.0024 | Không |
| 2 | Ngày toàn dân phòng cháy và chữa cháy là ngày 04 tháng 10. | Ngày 04 tháng 10 hằng năm là ngày toàn dân phòng cháy chữa cháy. | high | -0.2613 | Không |
| 3 | Chủ tịch nước quyết định tặng huân chương. | Người dân phải nộp thuế sử dụng đất nông nghiệp. | low | 0.0227 | Có |
| 4 | Mốc quốc giới không được xê dịch hoặc phá hoại. | Cấm làm sai lệch đường biên giới và phá hoại mốc giới. | high | -0.0962 | Không |
| 5 | Di sản văn hóa gồm vật thể và phi vật thể. | Bảo hiểm là hoạt động kinh doanh dựa trên hợp đồng. | low | -0.0462 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Cặp 2 rất giống nhau về nghĩa nhưng mock embedder lại cho score âm. Điều này cho thấy mock embedder chỉ phù hợp để kiểm tra pipeline code, không đủ mạnh để đánh giá semantic retrieval thật, đặc biệt với tiếng Việt và văn bản luật.

---

## 6. Results

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer | Nguồn |
|---|-------|-------------|-------|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Ngày 04 tháng 10 hằng năm | Luật PCCC, Điều 11 |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí | Luật Bảo vệ sức khỏe, Điều 23 |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Ba cấp, mười hai bậc | Luật Sĩ quan, Điều 10 |
| 4 | Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm? | Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới | Luật Biên giới, Điều 14 |
| 5 | Ai quyết định tặng huân chương và huy chương? | Chủ tịch nước | Luật Thi đua, khen thưởng, Điều 77 |

### Kết Quả Của Tôi

Strategy cá nhân: `sentence_chunker_1200`  
Chunks indexed: 285

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Luật Thi đua, khen thưởng, chunk 14 | 0.3671 | No | Không trả đúng nguồn PCCC |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Luật Thi đua, khen thưởng, chunk 11 | 0.3208 | No | Không trả đúng nguồn bảo vệ sức khỏe |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Luật Sĩ quan, chunk 0 | 0.2830 | Yes | Trả về đúng tài liệu liên quan |
| 4 | Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm? | Luật An ninh quốc gia, chunk 19 | 0.3350 | No | Không trả đúng nguồn biên giới |
| 5 | Ai quyết định tặng huân chương và huy chương? | Luật Bảo vệ sức khỏe nhân dân, chunk 6 | 0.3691 | No | Không trả đúng nguồn thi đua khen thưởng |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 1 / 5

---

## 7. What I Learned

**Failure case:**  
Query 5 hỏi "Ai quyết định tặng huân chương và huy chương?" nhưng top-1 lại là chunk của Luật Bảo vệ sức khỏe nhân dân. Đây là failure vì query đáng lẽ phải retrieve Luật Thi đua, khen thưởng.

**Tại sao thất bại?**  
Nguyên nhân chính là mock embedder không hiểu semantic tiếng Việt tốt. Ngoài ra SentenceChunker giữ câu hoàn chỉnh nhưng chưa tận dụng cấu trúc điều luật như "Điều 77", nên thông tin pháp lý cụ thể chưa được ưu tiên.

**Đề xuất cải thiện:**  
Nếu làm lại, tôi sẽ thử RecursiveChunker hoặc custom chunker theo heading/Điều/Khoản để mỗi chunk bám sát cấu trúc văn bản luật hơn. Tôi cũng sẽ dùng embedding model thật hỗ trợ tiếng Việt, ví dụ multilingual sentence transformer, thay vì mock embedder.

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Mỗi strategy có trade-off khác nhau: fixed-size dễ kiểm soát kích thước, recursive hợp tài liệu có cấu trúc, còn sentence chunker dễ đọc. Việc so sánh trên cùng 5 query giúp thấy strategy tốt không chỉ phụ thuộc code mà còn phụ thuộc domain và embedding model.

**Điều hay nhất tôi học được từ nhóm khác qua demo:**  
Các nhóm khác có thể chọn metadata giàu hơn, ví dụ `law_name`, `article`, `year`, `topic`. Metadata tốt giúp filter chính xác hơn và giảm nhiễu khi nhiều tài liệu có từ ngữ giống nhau.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Tôi sẽ parse văn bản luật thành chunk theo từng điều thay vì theo câu thuần túy. Tôi cũng sẽ gán metadata `article_number`, `law_title`, `year`, `topic` để hỗ trợ metadata filtering, đặc biệt vì đề yêu cầu ít nhất một query nên dùng filter để trả lời tốt hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 8 / 10 |
| Chunking strategy | Nhóm | 12 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **81 / 100** |
