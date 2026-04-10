# Kịch Bản Thuyết Trình Báo Cáo Phase 2 - Retrieval Strategy Comparison (Chi Tiết)

**Người trình bày:** Nhóm 5 (Minh, Nghĩa, Vinh, Đạt, Trung)  
**Thời lượng dự kiến:** 8 - 10 phút  
**Chủ đề:** Tại sao phải Chunking? Và Chiến lược Truy xuất (Retrieval) nào là tối ưu nhất cho RAG?  
**Tài liệu thử nghiệm:** Luật Bóng Đá (Laws of the Game 2025/26) - Dài hơn 205.000 ký tự.

---

## Phần 1: Lời ngỏ & Giới thiệu bài toán (2 phút)
**[Slide 1: Tiêu đề & Giới thiệu nhóm]**

**Người nói:**  
> "Xin chào thầy và các bạn. Hôm nay, đại diện nhóm 5 (gồm Minh, Nghĩa, Vinh, Đạt và mình là Trung), mình xin trình bày về một bài toán nền tảng nhưng mang tính chất sống còn của mọi hệ thống RAG: Đó là **Chunking và Retrieval Strategies** (Chiến lược cắt nhỏ văn bản và truy xuất dữ liệu).
> 
> Bối cảnh của tụi mình là xây dựng một hệ thống hỏi đáp dựa trên bộ "Luật Bóng Đá 2025/26". Cuốn sách luật này là một file khổng lồ với hơn 205.000 ký tự. Đây là một tài liệu kỹ thuật chứa các quy tắc chặt chẽ, móc nối với nhau, nên việc AI có "hiểu" trọn vẹn ngữ cảnh hay không phụ thuộc 100% vào cách chúng ta giúp nó "đọc" dữ liệu.
> 
> Để đưa ra cái nhìn khách quan nhất, nhóm đã thống nhất **5 benchmark queries** với các độ khó khác nhau: từ việc hỏi đơn giản (ai được nói chuyện với trọng tài) đến những tình huống "éo le" (nếu đội trưởng là thủ môn thì xử lý thế nào?). Bọn mình đã cắm 5 câu hỏi này chạy qua nhiều chiến lược Data Pipeline khác nhau. Và quả thực, kết quả làm tụi mình rất bất ngờ!"

---

## Phần 2: True Baseline "No-Chunk" - Tại sao lại phải Chunking? (1.5 phút)
**[Slide 2: Thử nghiệm không cắt văn bản - Mọi thứ sụp đổ]**

**Người nói:**
> "Nhưng trước tiên, chắc hẳn có bạn sẽ thắc mắc: *'Đang yên đang lành, văn bản liền mạch tại sao phải xé nhỏ ra (chunking) làm gì? Sao không quăng nguyên cuốn sách luật vào Embedder cho AI tìm?'*
>
> Bọn mình cũng có câu hỏi y hệt. Và mình đã làm 1 phương pháp **True Baseline (No-Chunking)**: Nghĩa là nhét toàn bộ 205.000 ký tự của cuốn sách luật vào làm 1 Chunk duy nhất và đưa qua mô hình `all-MiniLM-L6-v2`.
> 
> **Kết quả? Điểm tương đồng cực thấp (~0.38) và sai lệch hoàn toàn.** 
> 
> Bất kể mình hỏi về thủ môn, thẻ phạt hay trang phục, mô hình luôn trả về kết quả y hệt nhau, đó là danh sách Mục lục ở trang số 1. Vì sao lại thế?
> 1. **Giới hạn số token (Max Sequence Length):** Các mô hình Embedding không phải là cái túi không đáy. Model Local này thường giới hạn đọc 256 hoặc 512 token cùng lúc. Đưa 205.000 ký tự vào, nó chỉ đọc được trang đầu tiên rồi 'cắt cụp' (truncate) toàn bộ phần còn lại. Mọi nội dung bị mất trắng.
> 2. **Sự loãng ngữ nghĩa (Semantic Dilution):** Bạn hãy tưởng tượng 1 vector hướng đại diện cho 'Thẻ Phạt', 1 vector đại diện cho 'Size sân cỏ'. Khi bạn gộp nguyên cuốn sách vào, vector đại diện cho cái Chunk khổng lồ này trở thành một thứ hổ lốn, vô nghĩa. Nó chẳng giống với bất kỳ câu hỏi chi tiết nào cả.
>
> Vì vậy, Kết luận đầu tiên và quan trọng nhất của nhóm là: **Chunking là bước bắt buộc. Nếu không có nó, hệ thống RAG không thể tồn tại.**"

---

## Phần 3: 5 Chiến Lược Chia Để Trị (2.5 phút)
**[Slide 3: Bảng cấu hình 5 Strategy]**

**Người nói:**  
> "Sau khi hiểu tầm quan trọng của Chunking, tụi mình đã chia làm 5 phương pháp tiếp cận riêng biệt - mỗi người code 1 kiểu để xem ai tìm ra đáp án đúng nhất:
> 
> 1. **Baseline của Minh (FixedSize - 256 chars):** Minh dùng kiểu chặt thịt đơn giản nhất, lấy dao chặt đều từng khúc 256 ký tự (overlap 32). Rất nhanh gọn, làm cột mốc để đánh giá.
> 2. **Kiểu Nghĩa (Sentence-based - 3 câu):** Nghĩa không thích chặt mù quáng. Nghĩa chia theo dấu chấm, gom cụm 3 câu để ngữ pháp tự nhiên. Rất có lý phải không?
> 3. **Kiểu Vinh (Recursive Context Lớn - 512 chars):** Vinh lo sợ luật bóng đá dài dòng, nếu cắt quá ngắn sẽ mất sạch ý chính. Nên Vinh chơi kích cỡ bự (512 ký tự) và cắt theo cấu trúc đệ quy (xuống dòng, dấu chấm...).
> 4. **Kiểu Đạt (Recursive Cân Bằng - 256 chars):** Giống Vinh nhưng thu nhỏ kích thước lại để không ôm đồm quá nhiều thông tin thặng dư.
> 5. **Kiểu của Trung (Hybrid Smart - 384 chars + Rich Metadata):** Mình đã chọn kích cỡ ở khoảng giữa (384) không quá to, không quá nhỏ. Nhưng "vũ khí bí mật" của mình là **Siêu dữ liệu thông minh (Metadata)**. Code của mình tự bóc tách đây là Quy luật số mấy, tự nhận biết đâu là *"Luật mới cập nhật 2025/26"* và tự gán tag phân loại độ quan trọng (Importance Score)."

---

## Phần 4: Phân Tích Kết Quả - Ai là người chiến thắng? (2.5 phút)
**[Slide 4: Bảng Kết quả Thực Tế & Đánh giá]**

**Người nói:**
> "Và đây là kết quả đối đầu thực tế sau khi chạy qua 5 câu hỏi khó nhằn. Chuyện thú vị bắt đầu lộ diện:
>
> **Bất ngờ số 1: Chiến thuật chia theo câu có điểm số khiêm tốn.** Việc chia theo 3 câu của Nghĩa đạt điểm similarity trung bình khoảng 0.670. Văn phong luật pháp luôn sử dụng các câu cực kỳ dài và phức tạp (ví dụ câu liệt kê trường hợp). Việc chặt ngang đếm đúng 3 dấu chấm đã vô tình xé rách ngữ cảnh của một điều luật thành 2 nửa.
> 
> **Thực tế số 2: Đơn giản vẫn sống tốt.** Phương pháp chia tản mạn 256 ký tự của Minh (Baseline) vẫn trả ra kết quả điểm tương đồng khá tốt (0.702). Tuy nhiên ở câu hỏi ngách (ví dụ: Q2: Nếu đội trưởng đồng thời là thủ môn), phương pháp này gục ngã vì đoạn text này bị chia làm 2 chunk, AI không ghép lại được.
>
> **Lợi thế số 3: Recursive giúp ổn định.** Chiến lược 512 ký tự của Vinh giúp vượt qua mọi câu khó lấy lại ngữ cảnh (đạt score 0.695). Điểm trừ là khi nạp Context khổng lồ này cho LLM đằng sau, nó chứa cực kỳ nhiều nhiễu, nguy cơ rủi ro hallucination cao.
>
> **🏆 Nhà Vô Địch: Trung với Hybrid Smart (Score 0.70 - 0.80).** 
> Phương pháp của mình luôn tìm ra được kết quả chuẩn nhất, đặc biệt đập nát Câu hỏi số 5 (Hỏi về luật thay người bù giờ do chấn thương não). Tại sao? Thay vì tìm kiếm mù quáng, nhờ có dán nhãn thông minh (tagging 'is_new_rule_2025_26'), cơ sở dữ liệu đã tự động filter ưu tiên lọc dòng luật mới cập nhật nhất, đẩy điểm số relevance lên đến 0.799.

---

## Phần 5: Bài Học Xương Máu Từ Phase 2 (1.5 phút)
**[Slide 5: Key Findings]**

**Người nói:**
> "Qua dự án nhóm này, không phải làm cho có, mà tụi mình rút ra 4 chân lý cho việc tiền xử lý dữ liệu RAG:
>
> 1. **Chunking Size 384 là 'Sweet Spot' cho Văn bản Kỹ thuật.** 256 quá vụn vặt, 512 thì quá loãng.
> 2. **Metatada chính là linh hồn của Retrieval RAG:** Sự khác biệt giữa hệ thống đạt 75% và 90% không nằm ở thuật toán cắt xén AI thần thánh nào cả, mà nó nằm ở việc bạn bóc tách Metadata tốt đến đâu (Số hiệu, Ngày cập nhật, Chương mục). 
> 3. **Phải chọn theo đặc thù dữ liệu:** Nếu hệ thống của bạn là báo mạng, truyện cổ tích tự sự => Hãy dùng Sentence-based (kiểu của Nghĩa). Nếu là Tài liệu pháp lý/Kỹ thuật => Phải cày sâu vào cấu trúc (kiểu Trung, Vinh, Đạt).

---

## Phần 6: Lời Kết & Q&A
**[Slide 6: Lời cảm ơn & Hỏi đáp]**

**Người nói:**  
> "Để kết luận, Phase 2 chứng minh: một hệ thống RAG xịn xò thì thuật toán Vector Embedder tốt chưa đủ, mà cách bạn chia nhỏ dữ liệu và đắp thêm thẻ định danh (Metadata) mới là "chìa khóa vàng" cho độ tinh xảo của Chatbot. Nhóm đề xuất đưa **Hybrid Smart (Trung Strategy)** thành chuẩn Production cho hệ thống sắp tới.
>
> Đó cũng là toàn bộ báo cáo phân tích của nhóm tụi mình. Cảm ơn thầy và các bạn đã theo dõi. 
> Bọn mình đã Build và Run source code trực tiếp ra file JSON trên Local Embeding Model, hiện tại nếu thầy cô và các bạn có nghi vấn về kỹ thuật gán điểm 'Importance' của bọn mình hay muốn chạy trực tiếp query nào khác, nhóm xin sẵn sàng Demo live luôn ạ!"
