# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nghiêm Tuấn Linh
**Nhóm:** G10 - 111 Bàn B6
**Ngày:** 5/6/2026 (Day )
---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector/đoạn văn/bản ghi có hướng rất giống nhau, nên về mặt ngữ nghĩa hoặc đặc trưng chúng được xem là rất tương đồng. Giá trị càng gần 1 thì càng giống; gần 0 thì ít liên quan; gần -1 thì đối lập.

**Ví dụ HIGH similarity:**
- Sentence A: Tôi muốn đặt vé máy bay từ Hà Nội đi Bangkok vào tuần tới.
- Sentence B:  Tôi cần mua vé bay từ Hà Nội đến Bangkok cho tuần sau.
- Tại sao tương đồng: Hai câu dùng từ khác nhau một chút, nhưng cùng nói về nhu cầu mua/đặt vé máy bay, cùng điểm đi–điểm đến, và cùng thời gian gần tương đương.

**Ví dụ LOW similarity:**
- Sentence A: Tôi muốn đặt vé máy bay từ Hà Nội đi Bangkok vào tuần tới.
- Sentence B: Hôm nay tôi nấu phở bò cho bữa tối.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau: một câu về đặt vé máy bay/du lịch, câu kia về nấu ăn/bữa tối.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:* Vì text embeddings thường quan trọng “hướng” hơn “độ dài” vector: cosine similarity đo mức giống nhau về ngữ nghĩa bất kể vector dài/ngắn ra sao. Euclidean distance dễ bị ảnh hưởng bởi độ lớn vector, nên có thể đánh giá sai khi hai câu cùng nghĩa nhưng embedding có magnitude khác nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
> 223

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap = 100:
num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks.

> Overlap nhiều hơn làm chunk count tăng vì mỗi chunk tiến lên ít ký tự hơn; đổi lại, nó giúp giữ ngữ cảnh bị cắt ở ranh giới chunk, nên retrieval ít bỏ sót thông tin liên quan.
---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Nhóm đã chọn **văn bản pháp luật Việt Nam** làm miền truy xuất.



**Tại sao nhóm chọn domain này?**
> Miền này phù hợp với bài lab vì văn bản pháp luật thường dài, có cấu trúc rõ ràng và chứa các câu trả lời chính xác gắn với điều hoặc khoản cụ thể. Nó cũng tạo ra những thách thức truy xuất thực tế: nhiều văn bản dùng chung hệ thuật ngữ pháp lý tương tự nhau, và một truy vấn có thể yêu cầu tìm đúng một điều luật cụ thể thay vì chỉ tìm một văn bản có liên quan chung chung.

### Data Inventory

| # | Document | File | Approx. characters | Purpose in benchmark |
|---|----------|------|--------------------|----------------------|
| 1 | Luật Phòng cháy và chữa cháy | `law-2001-luat-phong-chay-va-chua-chay.md` | 43,459 | Query about National Fire Prevention and Fighting Day |
| 2 | Luật Bảo vệ sức khỏe nhân dân | `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md` | 27,939 | Query about emergency treatment |
| 3 | Luật Sĩ quan Quân đội nhân dân Việt Nam | `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md` | 31,961 | Query about officer rank system |
| 4 | Luật Biên giới quốc gia | `law-2003-luat-bien-gioi-quoc-gia.md` | 19,856 | Query about prohibited acts around border markers |
| 5 | Luật Thi đua, khen thưởng | `law-2003-luat-thi-dua-khen-thuong.md` | 53,943 | Query about authority to award orders and medals |

### Metadata Schema

| Metadata field | Type | Example | Why it helps |
|----------------|------|---------|--------------|
| `source` | string | `law-2001-luat-phong-chay-va-chua-chay.md` | Tracks which legal document a chunk came from. |
| `chunk_index` | int | `17` | Helps inspect the exact retrieved chunk position. |
| `strategy` | string | `sentence_chunker_1200` | Allows comparing retrieval output by chunking strategy. |
| `article` | string | `Điều 11` | Useful when a strategy extracts article-level metadata. |
| `topic` | string | `national_border` | Useful for metadata filtering on targeted legal topics. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

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

### Strategy Của Tôi

**Loại:** Loại: Recursive strategy – LawRecursiveChunker(chunk_size=1200)
**Mô tả cách hoạt động:**
> Strategy của tôi ưu tiên tách văn bản pháp luật theo các tiêu đề tự nhiên như Chương và Điều. Mỗi chunk được giữ kèm tiêu đề Chương và Điều tương ứng để thông tin pháp lý không bị mất ngữ cảnh. Nếu nội dung của một Điều dài hơn 1.200 ký tự, strategy sử dụng RecursiveChunker để tiếp tục chia theo đoạn văn, dòng, câu và từ. Tiêu đề của Điều được lặp lại trong các chunk con để mỗi chunk vẫn có thể được hiểu độc lập.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Văn bản pháp luật Việt Nam có cấu trúc rõ ràng theo Chương và Điều, trong đó câu trả lời thường gắn với một Điều cụ thể. Strategy này khai thác trực tiếp cấu trúc đó, giúp hạn chế việc một chunk chứa nội dung từ nhiều Điều khác nhau. Việc giữ lại tiêu đề Điều cũng giúp kết quả retrieval dễ kiểm tra và giải thích hơn.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

## So sánh: Strategy của tôi vs Baseline

Baseline phù hợp nhất để so sánh là **RecursiveChunker(chunk_size=1200)** vì strategy này cũng cố gắng giữ các ranh giới tự nhiên của văn bản, nhưng không nhận biết riêng cấu trúc **Chương/Điều**.

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality |
|---|---|---:|---:|---|
| Luật Phòng cháy và chữa cháy | RecursiveChunker baseline | 39 | 1112.4 | Chunk lớn, có thể chứa nhiều Điều hoặc thiếu tiêu đề liên quan |
| Luật Phòng cháy và chữa cháy | LawRecursiveChunker | 81 | 548.2 | Giữ ngữ cảnh Điều tốt hơn, phù hợp truy vấn pháp luật cụ thể |
| Luật Bảo vệ sức khỏe nhân dân | RecursiveChunker baseline | 26 | 1072.7 | Ít chunk nhưng nội dung tương đối rộng |
| Luật Bảo vệ sức khỏe nhân dân | LawRecursiveChunker | 68 | 418.5 | Chunk tập trung hơn vào từng Điều |
| Luật Biên giới quốc gia | RecursiveChunker baseline | 19 | 1043.2 | Có nguy cơ gộp nhiều quy định gần nhau |
| Luật Biên giới quốc gia | LawRecursiveChunker | 51 | 397.5 | Tìm kiếm chính xác hơn theo Điều và nội dung pháp lý |

## So sánh với thành viên khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|---|---|---:|---|---|
| Tôi – Linh | LawRecursiveChunker | Chưa có kết quả chuẩn hóa | Tách theo Chương/Điều, giữ tiêu đề pháp lý trong mỗi chunk | Tạo nhiều chunk; chưa chạy đầy đủ benchmark chung |
| Hùng Lê | FixedSizeChunker + metadata filter | 10/10 | Đạt 5/5 truy vấn Top-3 nhờ metadata filtering | Fixed-size có thể cắt ngang Điều, phụ thuộc chất lượng metadata |
| Duy | MarkdownSectionChunker | 2/10 theo mock ranking | Bám sát cấu trúc Markdown và Điều luật, phù hợp domain | Custom logic phức tạp; mock embedding xếp hạng chưa tốt |

## Strategy nào tốt nhất cho domain này? Tại sao?

Theo kết quả benchmark hiện tại, strategy của **Hùng Lê** cho kết quả tốt nhất với **5/5 truy vấn** nhờ kết hợp chunk cố định và metadata filtering. Tuy nhiên, xét về mức độ phù hợp lâu dài với văn bản pháp luật, strategy tách theo **Chương/Điều** của tôi hoặc **MarkdownSectionChunker** của Duy có tiềm năng tốt hơn vì giữ được cấu trúc và ngữ cảnh pháp lý. Giải pháp tối ưu là kết hợp **section-aware chunking** với **metadata filtering**.

## 4. My Approach — Cá nhân (10 điểm)


Cách tiếp cận chính của tôi là xây dựng quy trình RAG theo từng bước rõ ràng: chia văn bản thành các chunk giữ được ngữ cảnh, tạo và lưu embedding kèm metadata, sau đó truy xuất các chunk liên quan nhất để cung cấp context cho LLM. Với văn bản pháp luật, tôi ưu tiên tách theo Chương và Điều, đồng thời sử dụng recursive chunking cho nội dung quá dài. Cách làm này giúp kết quả tìm kiếm tập trung, dễ kiểm chứng và hạn chế câu trả lời không dựa trên dữ liệu.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi sử dụng regex (?<=[.!?])(?:[ \t]+|\n+) để phát hiện ranh giới câu dựa trên dấu chấm, chấm than và dấu hỏi. Sau khi loại bỏ khoảng trắng và các câu rỗng, các câu được nhóm theo max_sentences_per_chunk để tạo thành những chunk dễ đọc và không cắt giữa câu.

**`RecursiveChunker.chunk` / `_split`** Tôi chia văn bản đệ quy theo thứ tự ưu tiên gồm đoạn văn, dòng, câu, từ và cuối cùng là ký tự. Các phần được ghép nếu chưa vượt quá chunk_size; phần quá dài tiếp tục được chia bằng separator tiếp theo. Base case là khi đoạn đã đủ nhỏ hoặc không còn separator, lúc đó nội dung được chia trực tiếp theo số ký tự.
### EmbeddingStore

**`add_documents` + `search`** — approach:
> add_documents tạo embedding cho nội dung của từng Document, sau đó lưu embedding cùng ID, nội dung và metadata vào in-memory store và ChromaDB nếu khả dụng. Khi tìm kiếm, query được embedding rồi so sánh với các document bằng dot product; kết quả được sắp xếp theo score giảm dần và trả về top_k chunk liên quan nhất.

**`search_with_filter` + `delete_document`** — approach:
> search_with_filter lọc trước các chunk có metadata khớp với điều kiện, sau đó mới thực hiện similarity search để giảm nhiễu. delete_document tìm và xóa toàn bộ chunk có cùng doc_id khỏi in-memory store và ChromaDB, đồng thời trả về trạng thái cho biết có dữ liệu được xóa hay không.

### KnowledgeBaseAgent

**`answer`** — approach:
> answer truy xuất các chunk liên quan nhất từ EmbeddingStore rồi nối chúng thành phần context trong prompt. Prompt yêu cầu LLM chỉ sử dụng context được cung cấp để trả lời và nói không biết nếu không có đủ thông tin, giúp hạn chế câu trả lời không có căn cứ.

### Test Results

```
# Paste output of: pytest tests/ -v
```

**Số tests pass:** 42 / 42
---

## Similarity Predictions

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|---:|---|---|---|---:|---|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Ngày 04 tháng 10 hằng năm là ngày toàn dân phòng cháy và chữa cháy. | High | 0.2352 | Đúng |
| 2 | Người bệnh có thể được cấp cứu tại cơ sở nào? | Người bệnh được cấp cứu tại bất kỳ cơ sở khám chữa bệnh nào. | High | -0.0150 | Sai |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp? | Hệ thống quân hàm sĩ quan gồm ba cấp và mười hai bậc. | High | -0.2786 | Sai |
| 4 | Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm? | Hôm nay tôi nấu phở bò cho bữa tối. | Low | 0.0320 | Đúng |
| 5 | Ai quyết định tặng huân chương và huy chương? | Chủ tịch nước quyết định tặng huân chương và huy chương. | High | -0.1031 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*Kết quả bất ngờ nhất là cặp 3 có nội dung liên quan trực tiếp nhưng nhận similarity âm -0.2786. Điều này xảy ra vì _mock_embed tạo vector xác định từ chuỗi ký tự nhưng không thực sự hiểu ngữ nghĩa tiếng Việt. Vì vậy, mock embedding phù hợp để kiểm thử pipeline nhưng không đáng tin cậy khi đánh giá chất lượng retrieval thực tế.

---

## 6. Results — Cá nhân

Tôi sử dụng `LawRecursiveChunker(chunk_size=1200)` và model embedding `all-MiniLM-L6-v2`, tạo **530 chunks** từ **9 văn bản pháp luật**.

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer |
|---:|---|---|
| 1 | Ngày toàn dân phòng cháy và chữa cháy là ngày nào? | Ngày 04 tháng 10 hằng năm |
| 2 | Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu? | Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí |
| 3 | Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc? | Ba cấp, mười hai bậc |
| 4 | Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm? | Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới |
| 5 | Ai quyết định tặng huân chương và huy chương? | Chủ tịch nước |

### Kết quả của tôi

| # | Top-1 Retrieved Chunk | Score | Relevant? | Agent Answer |
|---:|---|---:|---|---|
| 1 | Luật PCCC, Điều 11: Ngày toàn dân PCCC | 0.8052 | Có | Ngày 04 tháng 10 hằng năm |
| 2 | Điều 41: Bảo vệ sức khỏe người cao tuổi và người tàn tật | 0.7064 | Không, nhưng chunk đúng ở Top-2 | Có thể trả lời từ Điều 23 trong context |
| 3 | Luật Biên giới quốc gia, Điều 7 | 0.6274 | Không, nhưng chunk đúng ở Top-3 | Có thể trả lời: ba cấp, mười hai bậc |
| 4 | Luật PCCC, Điều 13: Các hành vi bị nghiêm cấm | 0.7664 | Không | Không đủ context để trả lời đúng |
| 5 | Chương về đầu tư cho hoạt động PCCC | 0.7991 | Không | Không đủ context để trả lời đúng |

### Đánh giá

**Số queries trả về chunk relevant trong Top-3:** **3 / 5**

Kết quả cho thấy model embedding thực tế cải thiện đáng kể so với `_mock_embed`, từ **0/5** lên **3/5**. Strategy tìm chính xác các Điều luật cho ba truy vấn đầu, nhưng thất bại ở truy vấn 4 và 5 do các văn bản khác chứa nhiều thuật ngữ tương tự như “nghiêm cấm”, “huân chương” và “huy chương”. Có thể cải thiện bằng cách kết hợp **article-aware chunking** với **metadata filtering** theo nguồn hoặc chủ đề.
---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được từ kết quả của Hùng rằng metadata filtering có thể cải thiện retrieval đáng kể, đặc biệt khi các văn bản pháp luật sử dụng nhiều thuật ngữ giống nhau. Kết hợp metadata với chunking theo cấu trúc sẽ hiệu quả hơn việc chỉ tối ưu cách chia chunk.
**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Qua phần demo, tôi nhận thấy cần đánh giá đồng thời Top-k recall và chất lượng câu trả lời cuối cùng. Việc tìm thấy chunk liên quan chưa đảm bảo agent trả lời chính xác nếu chunk thiếu ngữ cảnh hoặc prompt chưa đủ chặt chẽ.
**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ bổ sung metadata như law_title, chapter, article và topic, sau đó áp dụng metadata filtering trước khi tìm kiếm vector. Tôi cũng sẽ sử dụng embedding hỗ trợ tiếng Việt tốt hơn và kết hợp reranking để giảm các kết quả có từ khóa tương tự nhưng sai Điều luật.

---

## Tự đánh giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|---|---|---:|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** |  | **87 / 100** |
