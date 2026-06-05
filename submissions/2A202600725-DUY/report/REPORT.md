# Bao Cao Lab 7: Embedding & Vector Store

**Ho ten:** Duy
**MSSV:** 2A202600725
**Nhom:** [Ten nhom]
**Ngay:** 05/06/2026

---

## 1. Warm-up (5 diem)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghia la gi?**  
High cosine similarity nghia la hai vector embedding tro cung huong, nen hai doan text co kha nang cung noi ve mot chu de, cung y dinh, hoac co nghia gan nhau. Diem cang gan 1 thi muc do tuong dong ve ngu nghia cang cao.

**Vi du HIGH similarity:**
- Sentence A: Python is a high-level programming language.
- Sentence B: Python is widely used for software development.
- Tai sao tuong dong: ca hai cau deu noi ve Python va viec lap trinh/phat trien phan mem.

**Vi du LOW similarity:**
- Sentence A: Vector stores index embeddings for similarity search.
- Sentence B: The cafe opens at seven in the morning.
- Tai sao khac: mot cau noi ve vector store trong AI, cau con lai noi ve gio mo cua quan ca phe.

**Tai sao cosine similarity duoc uu tien hon Euclidean distance cho text embeddings?**  
Cosine similarity tap trung vao huong cua vector, nen phu hop khi ta quan tam den nghia cua text hon la do lon tuyet doi cua vector. Voi embeddings, hai cau co the co vector dai/ngan khac nhau nhung van cung huong ve mat ngu nghia.

### Chunking Math (Ex 1.2)

**Document 10,000 ky tu, chunk_size=500, overlap=50. Bao nhieu chunks?**

Cong thuc:

```text
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / (500 - 50))
           = ceil(9950 / 450)
           = ceil(22.11)
           = 23 chunks
```

**Neu overlap tang len 100, chunk count thay doi the nao? Tai sao muon overlap nhieu hon?**

```text
num_chunks = ceil((10000 - 100) / (500 - 100))
           = ceil(9900 / 400)
           = ceil(24.75)
           = 25 chunks
```

Overlap tang lam so chunk tang tu 23 len 25 vi moi buoc truot ngan hon. Overlap nhieu hon giup giu ngu canh o bien chunk, tranh viec mot y quan trong bi cat doi giua hai chunk.

---

## 2. Document Selection - Nhom (10 diem)

### Domain & Ly Do Chon

**Domain:** [Nhom bo sung]

**Tai sao nhom chon domain nay?**  
[Nhom bo sung 2-3 cau ve ly do chon domain.]

### Data Inventory

| # | Ten tai lieu | Nguon | So ky tu | Metadata da gan |
|---|--------------|-------|----------|-----------------|
| 1 | [Nhom bo sung] | | | |
| 2 | [Nhom bo sung] | | | |
| 3 | [Nhom bo sung] | | | |
| 4 | [Nhom bo sung] | | | |
| 5 | [Nhom bo sung] | | | |

### Metadata Schema

| Truong metadata | Kieu | Vi du gia tri | Tai sao huu ich cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | [ten_file.md] | Biet chunk den tu file nao de trace lai evidence. |
| language | string | en, vi | Huu ich khi query tieng Viet hoac tieng Anh can filter rieng. |
| doc_type | string | report, playbook, notes | Giam nhieu khi cau hoi chi phu hop voi mot loai tai lieu. |

---

## 3. Chunking Strategy - Ca nhan chon, nhom so sanh (15 diem)

### Baseline Analysis

Chay `ChunkingStrategyComparator().compare()` voi `chunk_size=500` tren 3 tai lieu:

| Tai lieu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| chunking_experiment_report.md | FixedSizeChunker (`fixed_size`) | 5 | 437.4 | Trung binh, co the cat ngang cau |
| chunking_experiment_report.md | SentenceChunker (`by_sentences`) | 5 | 395.6 | Tot, doc de hon |
| chunking_experiment_report.md | RecursiveChunker (`recursive`) | 5 | 395.8 | Tot nhat, giu cau truc section/paragraph |
| customer_support_playbook.txt | FixedSizeChunker (`fixed_size`) | 4 | 460.5 | Trung binh |
| customer_support_playbook.txt | SentenceChunker (`by_sentences`) | 4 | 421.0 | Tot voi noi dung FAQ/playbook |
| customer_support_playbook.txt | RecursiveChunker (`recursive`) | 5 | 336.8 | Tot, chunk ngan va co ngu canh |
| python_intro.txt | FixedSizeChunker (`fixed_size`) | 5 | 428.8 | Trung binh |
| python_intro.txt | SentenceChunker (`by_sentences`) | 5 | 387.0 | Tot |
| python_intro.txt | RecursiveChunker (`recursive`) | 5 | 387.2 | Tot |

### Strategy Cua Toi

**Loai:** RecursiveChunker voi `chunk_size=700`.

**Mo ta cach hoat dong:**  
Strategy nay uu tien tach theo boundary lon truoc nhu paragraph (`\n\n`), sau do moi fallback ve line, cau, khoang trang, va cuoi cung la cat cung theo ky tu. Neu mot piece van dai hon `chunk_size`, ham `_split` tiep tuc de quy voi separator nho hon. Cach nay giup chunk khong vuot qua gioi han nhung van co gang giu lai cau truc tu nhien cua tai lieu.

**Tai sao toi chon strategy nay cho domain nhom?**  
Bo tai lieu gom markdown, note ky thuat va playbook, nen paragraph/section thuong mang mot y nghia tron ven. Recursive chunking phu hop vi no khong cat may moc theo so ky tu nhu fixed-size, nhung cung on dinh hon sentence chunking khi gap cau dai.

### So Sanh: Strategy cua toi vs Baseline

| Tai lieu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| chunking_experiment_report.md | best baseline: recursive 500 | 5 | 395.8 | Coherent, giu section tot |
| chunking_experiment_report.md | cua toi: recursive 700 | 4 | xap xi 500 | It chunk hon, them ngu canh cho agent |
| customer_support_playbook.txt | best baseline: sentence | 4 | 421.0 | De doc, phu hop playbook |
| customer_support_playbook.txt | cua toi: recursive 700 | 3 | xap xi 560 | Giu du buoc xu ly va dieu kien escalation |

### So Sanh Voi Thanh Vien Khac

| Thanh vien | Strategy | Retrieval Score (/10) | Diem manh | Diem yeu |
|-----------|----------|----------------------|-----------|----------|
| Toi | RecursiveChunker, chunk_size=700 | [Cap nhat sau khi chay query nhom] | Giu context tot, phu hop mixed docs | Can semantic embedder de danh gia chat luong that |
| [Thanh vien] | [Nhom bo sung] | | | |
| [Thanh vien] | [Nhom bo sung] | | | |

**Strategy nao tot nhat cho domain nay? Tai sao?**  
[Nhom bo sung sau khi so sanh ket qua cua tung thanh vien.]

---

## 4. My Approach - Ca nhan (10 diem)

### Chunking Functions

**`SentenceChunker.chunk` - approach:**  
Toi dung regex `(?<=[.!?])\s+` de tach cau sau dau `.`, `!`, `?` va cac khoang trang/newline theo sau. Sau do strip tung cau, bo cau rong, va gom moi `max_sentences_per_chunk` cau thanh mot chunk. Edge case `text` rong tra ve `[]`, va `max_sentences_per_chunk` duoc gioi han toi thieu la 1.

**`RecursiveChunker.chunk` / `_split` - approach:**  
Ham `chunk` goi `_split` voi danh sach separators uu tien. Base case la text da ngan hon `chunk_size` thi tra ve ngay, hoac het separator thi cat cung bang `chunk_size`. Khi split theo mot separator, toi gom cac piece vao buffer cho den khi candidate vuot size, sau do flush buffer va de quy tiep neu piece con qua dai.

### EmbeddingStore

**`add_documents` + `search` - approach:**  
`EmbeddingStore` mac dinh dung in-memory list neu khong co ChromaDB. Moi document duoc embed bang `_mock_embed`, luu cung `id`, `content`, `metadata`, va `embedding`. Khi search, query cung duoc embed, sau do tinh dot product giua query embedding va tung stored embedding, roi lay top-k score cao nhat.

**`search_with_filter` + `delete_document` - approach:**  
`search_with_filter` loc metadata truoc, sau do moi tinh similarity tren tap records da loc de giam nhieu va tang precision. `delete_document` xoa tat ca record co `metadata["doc_id"]` trung voi document id dau vao; ham tra `True` neu co record bi xoa va `False` neu khong tim thay.

### KnowledgeBaseAgent

**`answer` - approach:**  
Agent goi `store.search(question, top_k)` de lay cac chunk lien quan, sau do ghep chung thanh context co danh so `[1]`, `[2]`, `[3]`. Prompt yeu cau LLM chi tra loi dua tren context duoc cung cap. Cuoi cung agent goi `llm_fn(prompt)` va tra ve chuoi answer.

### Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.3
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::* PASSED
tests/test_solution.py::TestSentenceChunker::* PASSED
tests/test_solution.py::TestRecursiveChunker::* PASSED
tests/test_solution.py::TestEmbeddingStore::* PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::* PASSED
tests/test_solution.py::TestComputeSimilarity::* PASSED
tests/test_solution.py::TestCompareChunkingStrategies::* PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::* PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::* PASSED

============================= 42 passed in 0.13s ==============================
```

**So tests pass:** 42 / 42

---

## 5. Similarity Predictions - Ca nhan (5 diem)

Backend dung cho phan nay: `_mock_embed`, nen diem actual mang tinh deterministic smoke test hon la semantic embedding that.

| Pair | Sentence A | Sentence B | Du doan | Actual Score | Dung? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a high-level programming language. | Python is widely used for software development. | high | 0.1664 | Tuong doi dung |
| 2 | Vector stores index embeddings for similarity search. | A vector database helps retrieve semantically similar chunks. | high | -0.0786 | Sai |
| 3 | Customer support agents should confirm the order ID. | The refund process requires checking customer information. | medium/high | 0.1688 | Tuong doi dung |
| 4 | Deep learning models learn from data. | The cafe opens at seven in the morning. | low | 0.0071 | Dung |
| 5 | Vietnamese retrieval needs careful tokenization. | Weather forecasts predict rain tomorrow. | low | -0.0534 | Dung |

**Ket qua nao bat ngo nhat? Dieu nay noi gi ve cach embeddings bieu dien nghia?**  
Pair 2 bat ngo nhat vi ve mat ngu nghia hai cau deu noi ve vector store/retrieval, nhung mock embedding lai cho diem am. Dieu nay cho thay backend embedding rat quan trong: mock embedding giup test code on dinh, nhung khong thay the duoc embedding model semantic nhu `all-MiniLM-L6-v2` hay OpenAI embedding khi can danh gia retrieval chat luong that.

---

## 6. Results - Ca nhan (10 diem)

Chay 5 benchmark queries tren implementation ca nhan voi `RecursiveChunker(chunk_size=700)` va mock embedding backend.

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is chunking and why is overlap useful? | Chunking splits documents into retrievable pieces; overlap preserves context across boundaries. |
| 2 | How does a vector store search for relevant documents? | It embeds documents and query, then ranks stored vectors by similarity. |
| 3 | What are the steps in a basic RAG system? | Retrieve relevant chunks, place them into context, then generate an answer grounded in that context. |
| 4 | How should customer support handle refunds or escalations? | Follow support playbook steps such as checking policy/order context and escalating when needed. |
| 5 | What challenge appears in Vietnamese retrieval? | Vietnamese retrieval can be affected by tokenization, diacritics, and language-specific matching. |

### Ket Qua Cua Toi

| # | Query | Top-1 Retrieved Chunk (tom tat) | Score | Relevant? | Agent Answer (tom tat) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is chunking and why is overlap useful? | python_intro: noi ve project structure, khong phai chunking | 0.2597 | No | Tra loi theo question nhung context top-1 yeu |
| 2 | How does a vector store search for relevant documents? | vi_retrieval_notes: noi ve retrieval failure | 0.2152 | Partly | Co lien quan retrieval nhung khong dung gold answer |
| 3 | What are the steps in a basic RAG system? | customer_support_playbook: review failed queries | 0.1993 | No | Context khong du de tra loi kien truc RAG |
| 4 | How should customer support handle refunds or escalations? | chunking_experiment_report: noi ve recursive chunking | 0.2910 | No | Retrieval sai domain |
| 5 | What challenge appears in Vietnamese retrieval? | python_intro: noi ve Python production | 0.2459 | No | Retrieval sai tai lieu |

**Bao nhieu queries tra ve chunk relevant trong top-3?** 1 / 5

**Nhan xet:**  
Ket qua thap chu yeu do backend `_mock_embed` khong encode semantic similarity that. Phan code search, filter va delete da pass tests, nhung retrieval quality that can dung local embedder hoac OpenAI embedder de vector co y nghia hon.

---

## 7. What I Learned (5 diem - Demo)

**Dieu hay nhat toi hoc duoc tu thanh vien khac trong nhom:**  
[Bo sung sau khi nhom demo/so sanh. Du kien: moi chunking strategy co trade-off rieng; fixed-size de kiem soat kich thuoc, sentence-based de doc, recursive giu context tot hon voi tai lieu co cau truc.]

**Dieu hay nhat toi hoc duoc tu nhom khac (qua demo):**  
[Bo sung sau demo voi nhom khac.]

**Neu lam lai, toi se thay doi gi trong data strategy?**  
Toi se gan metadata chi tiet hon cho tung chunk, vi du `topic=chunking/vector_store/rag/support`, `language=en/vi`, va `doc_type=notes/playbook/report`. Toi cung se dung semantic embedder that thay vi mock embedder de benchmark retrieval quality cong bang hon.

**Failure analysis:**  
Failure ro nhat la query "How should customer support handle refunds or escalations?" nhung top-1 lai den tu `chunking_experiment_report.md`. Nguyen nhan la mock embedding khong hieu nghia va metadata chua loc theo `doc_type=playbook`. Cach cai thien la dung `search_with_filter(metadata_filter={"source": "customer_support_playbook.txt"})` hoac gan metadata `department=support`, dong thoi chay local/OpenAI embedding.

---

## Tu Danh Gia

| Tieu chi | Loai | Diem tu danh gia |
|----------|------|-------------------|
| Warm-up | Ca nhan | 5 / 5 |
| Document selection | Nhom | [Nhom bo sung] / 10 |
| Chunking strategy | Nhom | [Nhom bo sung] / 15 |
| My approach | Ca nhan | 10 / 10 |
| Similarity predictions | Ca nhan | 4 / 5 |
| Results | Ca nhan | 6 / 10 |
| Core implementation (tests) | Ca nhan | 30 / 30 |
| Demo | Nhom | [Nhom bo sung] / 5 |
| **Tong** | | **[Tinh sau khi co diem nhom] / 100** |
