# Phase 2 — Hướng Dẫn Chi Tiết So Sánh Retrieval Strategy
## Nhóm 5 Người: Minh, Nghĩa, Vinh, Đạt, Trung

---

## 🎯 Mục Tiêu Phase 2

Mỗi bạn sẽ **thử strategy khác nhau** trên cùng bộ tài liệu (Laws of the Game 2025/26), chạy **5 benchmark queries**, rồi **so sánh kết quả** để học từ nhau có strategy nào tốt nhất.

---

## 📋 Phân Công Role (Mỗi Người 1 Strategy)

| Thành Viên | Strategy | Chunker Class | chunk_size | overlap | Metadata Focus | Nhiệm Vụ |
|-----------|----------|---------------|-----------|---------|-----------------|----------|
| **Minh** | Baseline | `FixedSizeChunker` | 256 | 32 | source, law_number | Tạo comparison baseline |
| **Nghĩa** | Sentence-based | `SentenceChunker` | 3-4 sentences | N/A | source, section, topic | Optimize readability |
| **Vinh** | Recursive + Large | `RecursiveChunker` | 512 | 64 | source, law_number, is_new_rule | Context preservation |
| **Đạt** | Recursive + Small | `RecursiveChunker` | 256 | 32 | source, section, difficulty | Fine-grained chunks |
| **Trung** | Hybrid + Smart | `FixedSizeChunker` + custom filter | 384 | 48 | source, law_number, section, importance | Multi-factor optimization |

---

## ⏳ Timeline & Deadline

| Giai Đoạn | Thời Gian | Ai Làm | Deadline |
|-----------|----------|-------|----------|
| **Setup & Understand** | Hôm nay | Tất cả (30 phút) | 30 min |
| **Implement Code** | Hôm nay | Từng người riêng (1-2h) | Before day end |
| **Run Benchmark** | Hôm nay | Từng người riêng (30 min) | Before day end |
| **Collect Results** | Hôm nay | **Minh** compile (30 min) | 6 PM |
| **Group Analysis** | Ngày mai | Tất cả (1-2h) | Morning meeting |
| **Prepare Demo** | Ngày mai | **Đạt** lead + others (1h) | Afternoon |

---