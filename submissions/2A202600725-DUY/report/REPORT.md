# Bao Cao Lab 7: Embedding & Vector Store

**Ho ten:** Duy
**MSSV:** 2A202600725
**Nhom:** Data Foundations - Education Law Docs
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

**Domain:** Van ban giao duc, thong tu BGDĐT va tai lieu nen tang retrieval/RAG.

**Tai sao nhom chon domain nay?**  
Nhom chon domain nay vi tai lieu co cau truc ro rang theo thong tu, chuong, dieu va heading Markdown. Day la bo du lieu phu hop de so sanh chunking strategy: neu chunk cat sai, retrieval se mat ngu canh dieu khoan; neu metadata tot, search co the thu hep dung nguon tai lieu.

### Data Inventory

| # | Ten tai lieu | Nguon | So ky tu | Metadata da gan |
|---|--------------|-------|----------|-----------------|
| 1 | 2026_266_35_2026_TT-BGDDT.md | data/ | 306761 | source, doc_type, language |
| 2 | 36_2026_TT-BGDDT_703627.md | data/ | 24105 | source, doc_type, language |
| 3 | vector_store_notes.md | data/ | 2123 | source, doc_type, language |
| 4 | rag_system_design.md | data/ | 2391 | source, doc_type, language |
| 5 | chunking_experiment_report.md | data/ | 1987 | source, doc_type, language |

### Metadata Schema

| Truong metadata | Kieu | Vi du gia tri | Tai sao huu ich cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | 36_2026_TT-BGDDT_703627.md | Biet chunk den tu file nao de trace lai evidence va loc dung thong tu. |
| language | string | vi, en | Huu ich khi query tieng Viet hoac tieng Anh can filter rieng. |
| doc_type | string | legal, notes, report | Giam nhieu khi cau hoi chi phu hop voi van ban phap quy hoac note ky thuat. |

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

**Loai:** Custom strategy - `MarkdownSectionChunker(chunk_size=900)`.

**Mo ta cach hoat dong:**  
Strategy rieng cua toi tach tai lieu theo cau truc Markdown va van ban phap quy: heading `#`, `##`, cac moc `Chuong`, `Dieu`. Neu mot section van dai hon `chunk_size`, strategy fallback sang fixed-size split noi bo de khong vuot gioi han. Cach nay khac voi fixed/sentence/recursive mac dinh vi no uu tien giu tron ven mot muc dieu khoan hoac mot section tai lieu.

**Tai sao toi chon strategy nay cho domain nhom?**  
Bo tai lieu nhom co Markdown va tai lieu phap quy/thong tu, trong do thong tin quan trong thuong nam trong heading, chuong, dieu. `MarkdownSectionChunker` phu hop vi no giu duoc ngu canh cua tung muc, tranh viec query retrieve mot nua dieu khoan ma thieu tieu de hoac dieu kien ap dung.

### So Sanh: Strategy cua toi vs Baseline

| Tai lieu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| chunking_experiment_report.md | best baseline: recursive 500 | 5 | 395.8 | Coherent, giu section tot |
| chunking_experiment_report.md | cua toi: MarkdownSectionChunker 900 | 3 | 660.7 | Giu section Markdown ro hon |
| vector_store_notes.md | cua toi: MarkdownSectionChunker 900 | 3 | 706.0 | Giu heading va noi dung lien quan trong cung chunk |
| 36_2026_TT-BGDDT_703627.md | cua toi: MarkdownSectionChunker 900 | 27 | 891.1 | Giu cac khoi dieu/chuyen muc, phu hop van ban dai |
| 2026_266_35_2026_TT-BGDDT.md | cua toi: MarkdownSectionChunker 900 | 341 | 889.5 | Chia van ban rat dai thanh chunk gan gioi han nhung van bam cau truc |

### So Sanh Voi Thanh Vien Khac

| Thanh vien | Strategy | Retrieval Score (/10) | Diem manh | Diem yeu |
|-----------|----------|----------------------|-----------|----------|
| Toi | MarkdownSectionChunker, chunk_size=900 | [Cap nhat sau khi chay query nhom] | Giu heading/chuong/dieu, phu hop Markdown va van ban phap quy | Neu section qua dai van phai fallback cat nho |
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

**`MarkdownSectionChunker.chunk` - custom strategy:**  
Toi them strategy rieng de split theo heading Markdown va cac moc phap quy nhu `Chuong`, `Dieu`. Strategy nay gom cac section lien tiep neu tong do dai con duoi `chunk_size`; neu section qua dai thi fallback bang fixed-size split noi bo. Muc tieu la giu tieu de va noi dung dieu khoan trong cung chunk de retrieval de trace hon.

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

Chay 5 benchmark queries tren implementation ca nhan voi `MarkdownSectionChunker(chunk_size=900)` va mock embedding backend.

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Thong tu 36/2026/TT-BGDDT co hieu luc tu ngay nao? | Thong tu 36 co hieu luc tu ngay 07/06/2026. |
| 2 | Thong tu 35/2026/TT-BGDDT huong dan noi dung gi? | Thong tu 35 huong dan mot so noi dung ve hoat dong dau tu theo phuong thuc PPP trong linh vuc giao duc va dao tao. |
| 3 | Vector search pipeline co nhung buoc nao? | Chunk documents, embed chunks, store vector+metadata, embed query va rank by similarity. |
| 4 | RAG system giam hallucination bang cach nao? | RAG retrieve relevant context truoc, dua context vao prompt, va yeu cau model answer dua tren evidence. |
| 5 | Recursive chunking co uu diem gi trong experiment? | Recursive chunking giu context tot hon bang cach tach theo boundary lon truoc roi moi fallback separator nho hon. |

### Ket Qua Cua Toi

| # | Query | Top-1 Retrieved Chunk (tom tat) | Score | Relevant? | Agent Answer (tom tat) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thong tu 36 co hieu luc tu ngay nao? | Filter source dung 36_2026, top chunk chua phan gan Dieu 3/noi nhan | 0.1927 | Partly | Can inspect top-3 vi mock embedding chua rank dung Dieu 2 |
| 2 | Thong tu 35 huong dan noi dung gi? | Filter source dung 35_2026, top chunk trong van ban TT35 | 0.3541 | Partly | Dung source nhung top chunk chua phai doan mo dau |
| 3 | Vector search pipeline co nhung buoc nao? | vector_store_notes: mo ta vector store va workflow | -0.0010 | Yes | Co chunk dung source, answer can tom tat 4 buoc |
| 4 | RAG system giam hallucination bang cach nao? | rag_system_design: application layer inject retrieved chunks vao prompt | 0.3596 | Yes | Co context dung ve grounding va evidence |
| 5 | Recursive chunking co uu diem gi? | chunking_experiment_report: sentence/recursive comparison | 0.0343 | Partly | Co source dung, top chunk chua phai doan recursive tot nhat |

**Bao nhieu queries tra ve chunk relevant trong top-3?** 3 / 5 khi dung metadata filter theo `source`. Neu khong filter, `_mock_embed` thuong day cac chunk cua van ban dai len top-3, nen precision thap hon.

**Nhan xet:**  
Ket qua cho thay `MarkdownSectionChunker` giup chunk coherent hon voi Markdown/phap quy, nhung `_mock_embed` khong encode semantic similarity that nen ranking van nhieu nhieu. Metadata filter theo `source` rat quan trong: no thu hep search vao dung tai lieu, tang source precision tu thap len 5/5 trong benchmark nay.

---

## 7. What I Learned (5 diem - Demo)

**Dieu hay nhat toi hoc duoc tu thanh vien khac trong nhom:**  
[Bo sung sau khi nhom demo/so sanh. Du kien: moi chunking strategy co trade-off rieng; fixed-size de kiem soat kich thuoc, sentence-based de doc, recursive giu context tot hon voi tai lieu co cau truc.]

**Dieu hay nhat toi hoc duoc tu nhom khac (qua demo):**  
[Bo sung sau demo voi nhom khac.]

**Neu lam lai, toi se thay doi gi trong data strategy?**  
Toi se gan metadata chi tiet hon cho tung chunk, vi du `topic=chunking/vector_store/rag/support`, `language=en/vi`, va `doc_type=notes/playbook/report`. Toi cung se dung semantic embedder that thay vi mock embedder de benchmark retrieval quality cong bang hon.

**Failure analysis:**  
Failure ro nhat la cac query ve ngay hieu luc/noi dung thong tu: khi khong filter, top-3 thuong bi chiem boi chunk cua van ban dai `2026_266_35_2026_TT-BGDDT.md` vi mock embedding khong hieu nghia. Cach cai thien la bat buoc dung `search_with_filter(metadata_filter={"source": ...})` khi query da co so thong tu, them metadata `doc_type=legal`, `law_number`, `article`, va dung local/OpenAI embedding de ranking theo semantic tot hon.

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
