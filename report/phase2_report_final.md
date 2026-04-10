# Báo Cáo Giai Đoạn 2 - Đánh Giá & So Sánh Chiến Lược Retrieval

**Nhóm 5 Người:** Minh, Nghĩa, Vinh, Đạt, Trung  
**Ngày:** 10/04/2026

---

## 1. Tổng Quan Điển Biến
Nhóm đã tiến hành thử nghiệm 5 chiến lược (strategies) chunking khác nhau trên cùng bộ tài liệu "Laws of the Game 2025/26" nhằm đánh giá hiệu quả trích xuất văn bản (retrieval) qua 5 câu hỏi (benchmark queries).

### Cấu Hình Các Chiến Lược

| Thành viên | Chiến Lược | Cấu hình Chunk (Size/Overlap) | Mức độ Metadata |
|------------|------------|-------------------------------|-----------------|
| N/A | True Baseline | Không Chunk (1 Chunk >205k chars) | Không có |
| Minh | Baseline | FixedSize (256/32) | Cơ bản |
| Nghĩa | Sentence | Dựa trên Câu (3 câu/chunk) | Cơ bản |
| Vinh | Large Context| Recursive (512/64) | Vừa phải |
| Đạt | Balanced | Recursive (256/32) | Vừa phải |
| Trung | Hybrid Smart | FixedSize (384/48) | Phong phú |

---

## 2. Kết Quả Điểm Số & Đánh Giá Chiến Lược

| Thành viên | Chiến Lược | Chunk Count | Retrieval Score | Điểm Mạnh | Điểm Yếu |
|------------|------------|-------------|-----------------|-----------|----------|
| Trung | **Hybrid Smart** | **611** | **8.5/10** | Metadata mạnh, đánh tag thông minh (law_number, tính mới, độ quan trọng). | Cần hard-code logic trích xuất lúc ban đầu. |
| Vinh | Large Context | 640 | 8.0/10 | Bắt giữ và duy trì ngữ cảnh lớn rất tốt. | Dễ gây nhiễu và làm loãng Vector Similarity. |
| Đạt | Balanced 256 | 1123 | 7.2/10 | Cân bằng ngữ cảnh và sự chi tiết bề mặt. | Overhead cao do đệ quy, chưa đủ metadata sâu. |
| Minh | Baseline 256 | 916 | 7.0/10 | Triển khai nhanh, đơn giản, làm tiêu chuẩn tốt. | Chunk bị cắt dọc mù quáng (làm mất câu). |
| Nghĩa | Sentence 3 | 271 | 6.0/10 | Thuật toán mạch lạc, logic hợp văn tự sự. | Tài liệu luật quá phức tạp khiến nghĩa gãy vụn. |
| N/A | No Chunking | 1 | 0.0/10 | Không bị cắt chữ. | Lỗi Token Limit, kết quả hoàn toàn fail (Sim ~0.38). |

🏆 **Chiến lược tối ưu nhất:** `Hybrid Smart` của Trung. Phương pháp này bù đắp những điểm mù Semantic của Embedder bằng khả năng phân luồng thẻ Tags metadata (Keywords, section) và phân loại độ ưu tiên (Importance Score).

---
## 3. Các Nhận Định Quan Trọng (Key Findings)

1. **Tính Bắt Buộc Của Chunking:** Thử nghiệm "No-Chunking" thất bại hoàn toàn. Với tài liệu >205k ký tự, điểm similarity trung bình chỉ đạt **~0.38**. Lý do là mô hình bị giới hạn Max Sequence Length, dẫn đến cắt cụt (truncate) thông tin và gây loãng ngữ nghĩa (Semantic Dilution).
2. **Metadata Quyết Định Khác Biệt:** Metadata thông minh quan trọng hơn bản thân thuật toán cắt. Chiến lược "Hybrid Smart" đã tăng độ chính xác lên đến 15-20% so với phương pháp chunk theo khoảng cách thông thường.
3. **Kích Thước (Size) Rất Quan Trọng:** 
   - 256 chars (Minh/Đạt): Quá nhỏ, ngữ cảnh bị cụt.
   - 512 chars (Vinh): Quá rộng, làm loãng độ chính xác.
   - **384 chars (Trung): Tối ưu nhất**, vừa vặn để đóng gói trọn vẹn 1 quy tắc (Rule) trên văn bản mẫu của miền dữ liệu này.
4. **Chia Text Theo Câu (Sentence) Không Hợp Luật Pháp:** Câu trong luật có nhiều mệnh đề con nối tiếp. Chia theo dấu câu (Nghĩa) làm mất liên kết giải nghĩa, biến nó thành cách làm kém hiệu quả nhất (Avg 65%).

---

## 4. Bài Học & Đề Xuất Tương Lai

**Bài Học Tích Lũy:**
- **Metadata là linh hồn của RAG**: Khả năng phân loại (Importance Score) và dán nhãn (Tagging) quan trọng hơn nhiều so với việc chỉ thay đổi thuật toán cắt gọt.
- **Kích thước "Sweet Spot"**: Với văn bản pháp lý, 384 chars là kích thước tối ưu để đóng gói trọn vẹn ngữ cảnh mà không gây nhiễu cho LLM.
- **Cần kiểm tra Baseline**: Việc test "No-Chunking" giúp nhóm hiểu sâu về giới hạn vật lý (Sequence Length) của các mô hình nhúng.

**Đề Xuất Dự Án Cấp Hệ Thống:**
1. Triển khai mô hình **Hybrid Smart (Trung Strategy)** làm tiêu chuẩn cho Production.
2. Kết hợp chặt chẽ **Semantic Search + Metadata Filter** để đạt hiệu suất phản hồi tối ưu (> 90%).
3. Tự động hóa quá trình gán nhãn Metadata bằng các mô hình NLP nhỏ (Entity Extraction) thay vì Regex thủ công để mở rộng quy mô dữ liệu.
