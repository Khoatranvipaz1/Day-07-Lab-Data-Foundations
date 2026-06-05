# Retrieval Benchmark Results

Domain: Vietnamese law documents converted from `docs/0000.parquet`.

Evaluation: a query is counted as a Top-3 hit when at least one retrieved chunk comes from the expected document.

Chosen personal strategy: `sentence_chunker_1200`.

Design rationale: sentence-based chunks preserve sentence boundaries, which fits legal documents where answers are often stated as complete clauses or articles.

## Strategy Run

Chunks indexed: 285

### Query 1

**Query:** Ngày toàn dân phòng cháy và chữa cháy là ngày nào?

**Gold answer:** Ngày 04 tháng 10 hằng năm.

**Expected document:** `law-2001-luat-phong-chay-va-chua-chay.md`

**Top-3 hit:** no

| Rank | Retrieved document | Chunk | Score | Preview |
|---|---|---:|---:|---|
| 1 | `law-2003-luat-thi-dua-khen-thuong.md` | 14 | 0.3671 | "Huân chương Sao vàng" để tặng cho tập thể đạt các tiêu chuẩn sau: a) Lập được thành tích xuất sắc liên tục từ 10 năm tr... |
| 2 | `law-2003-luat-thi-dua-khen-thuong.md` | 29 | 0.2927 | Danh hiệu vinh dự nhà nước để tặng hoặc truy tặng cho cá nhân, tặng cho tập thể có những đóng góp đặc biệt xuất sắc vào ... |
| 3 | `law-2004-luat-an-ninh-quoc-gia.md` | 16 | 0.2873 | Các nhiệm vụ cụ thể của cơ quan chuyên trách bảo vệ an ninh quốc gia: a) Tổ chức thu thập thông tin, phân tích, đánh giá... |

### Query 2

**Query:** Khi cấp cứu, người bệnh có thể được cấp cứu ở đâu?

**Gold answer:** Tại bất kỳ cơ sở khám chữa bệnh nào; cơ sở phải tiếp nhận và xử trí.

**Expected document:** `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md`

**Top-3 hit:** no

| Rank | Retrieved document | Chunk | Score | Preview |
|---|---|---:|---:|---|
| 1 | `law-2003-luat-thi-dua-khen-thuong.md` | 11 | 0.3208 | Danh hiệu "Tập thể lao động tiên tiến" được xét tặng cho tập thể đạt các tiêu chuẩn sau: a) Hoàn thành tốt nhiệm vụ và k... |
| 2 | `law-1993-luat-thue-su-dung-dat-nong-nghiep.md` | 10 | 0.2765 | Ưu tiên truyền thông, vận động, giáo dục về các nội dung sau đây: a) Khuyến khích kết hôn, sinh con để duy trì mức sinh ... |
| 3 | `law-2000-luat-kinh-doanh-bao-hiem.md` | 10 | 0.2765 | Ưu tiên truyền thông, vận động, giáo dục về các nội dung sau đây: a) Khuyến khích kết hôn, sinh con để duy trì mức sinh ... |

### Query 3

**Query:** Hệ thống cấp bậc quân hàm sĩ quan gồm bao nhiêu cấp và bậc?

**Gold answer:** Ba cấp, mười hai bậc.

**Expected document:** `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md`

**Top-3 hit:** yes

| Rank | Retrieved document | Chunk | Score | Preview |
|---|---|---:|---:|---|
| 1 | `law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam.md` | 0 | 0.2830 | # Luật Sĩ quan Quân đội nhân dân Việt Nam - id: law-1999-luat-si-quan-quan-doi-nhan-dan-viet-nam - type: law - source_fi... |
| 2 | `law-2001-luat-di-san-van-hoa.md` | 0 | 0.2662 | # Luật Di sản văn hóa - id: law-2001-luat-di-san-van-hoa - type: law - source_file: law-2001-luat-di-san-van-hoa.md - co... |
| 3 | `law-2003-luat-thi-dua-khen-thuong.md` | 11 | 0.2661 | Danh hiệu "Tập thể lao động tiên tiến" được xét tặng cho tập thể đạt các tiêu chuẩn sau: a) Hoàn thành tốt nhiệm vụ và k... |

### Query 4

**Query:** Những hành vi nào liên quan đến mốc quốc giới bị nghiêm cấm?

**Gold answer:** Xê dịch, phá hoại mốc hoặc làm sai lệch đường biên giới.

**Expected document:** `law-2003-luat-bien-gioi-quoc-gia.md`

**Top-3 hit:** no

| Rank | Retrieved document | Chunk | Score | Preview |
|---|---|---:|---:|---|
| 1 | `law-2004-luat-an-ninh-quoc-gia.md` | 19 | 0.3350 | Cán bộ chuyên trách bảo vệ an ninh quốc gia trong khi thực hiện nhiệm vụ được quyền: a) Thực hiện các quyền quy định tại... |
| 2 | `law-2003-luat-thi-dua-khen-thuong.md` | 5 | 0.3184 | Tổ chức các hoạt động thiết thực nhằm động viên, khích lệ mọi người tự giác, hăng hái thi đua lao động, sản xuất, học tậ... |
| 3 | `law-2003-luat-thi-dua-khen-thuong.md` | 51 | 0.2967 | Cơ quan, tổ chức, cá nhân có thẩm quyền có trách nhiệm giải quyết khiếu nại, tố cáo về thi đua, khen thưởng theo quy địn... |

### Query 5

**Query:** Ai quyết định tặng huân chương và huy chương?

**Gold answer:** Chủ tịch nước.

**Expected document:** `law-2003-luat-thi-dua-khen-thuong.md`

**Top-3 hit:** no

| Rank | Retrieved document | Chunk | Score | Preview |
|---|---|---:|---:|---|
| 1 | `law-1989-luat-bao-ve-suc-khoe-nhan-dan.md` | 6 | 0.3691 | 2- Nghiêm cấm các tổ chức Nhà nước, tập thể, tư nhân và mọi công dân làm ô nhiễm các nguồn nước dùng trong sinh hoạt của... |
| 2 | `law-1993-luat-thue-su-dung-dat-nong-nghiep.md` | 20 | 0.3653 | Viện trợ, tài trợ, hỗ trợ của tổ chức, cá nhân trong nước và nước ngoài theo quy định của pháp luật. 5. Các nguồn kinh p... |
| 3 | `law-2000-luat-kinh-doanh-bao-hiem.md` | 20 | 0.3653 | Viện trợ, tài trợ, hỗ trợ của tổ chức, cá nhân trong nước và nước ngoài theo quy định của pháp luật. 5. Các nguồn kinh p... |

## Summary

| Strategy | Top-3 recall | Chunks indexed |
|---|---:|---:|
| sentence_chunker_1200 | 1/5 | 285 |

Result: `sentence_chunker_1200` retrieved the expected document in the top 3 for 1/5 benchmark queries.

Note: this benchmark uses the mock embedder, so it validates the retrieval pipeline but does not fully measure semantic quality. A real Vietnamese-capable embedding model should improve retrieval quality.
