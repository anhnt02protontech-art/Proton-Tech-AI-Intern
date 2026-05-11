# Hướng dẫn bài tập Ngày 6 - Chatbot Basics

## Mục tiêu

- Hiểu cách quản lý conversation memory cho chatbot.
- Xây dựng `Chatbot` có khả năng lưu lịch sử hội thoại.
- Áp dụng sliding window để giữ 20 message gần nhất.
- Cài đặt tóm tắt context khi vượt ngưỡng bộ nhớ/token.
- Đếm token và cảnh báo khi gần limit.
- Chat qua terminal và giữ ngữ cảnh nhiều lượt.

## Nội dung cần hoàn thành

1. `chatbot.py`
   - `Chatbot` lưu lịch sử hội thoại.
   - `Chatbot` thực hiện sliding window: giữ 20 messages gần nhất.
   - `Chatbot` tóm tắt hội thoại cũ khi vượt token limit.
   - `Chatbot` đếm token và cảnh báo khi gần limit.
   - Cho phép chat trực tiếp trong terminal.

2. `README.md`
   - Giải thích chức năng, cách chạy và cấu trúc file.

3. `report_results.md`
   - Ghi lại kết quả thực hành và quan sát.

## Hướng dẫn thực hành

### Bước 1: Khởi tạo history manager

- Xây dựng phương thức lưu lịch sử bằng danh sách message.
- Mỗi message có role (`user` hoặc `assistant`) và nội dung.
- Kiểm tra bằng cách thêm vài message và in ra history.

### Bước 2: Sliding window

- Sau mỗi lần thêm message, chỉ giữ 20 message gần nhất.
- Cắt tỉa message cũ khi số lượng vượt quá.

### Bước 3: Summarization

- Khi tổng token vượt ngưỡng, tạo tóm tắt cho phần hội thoại cũ.
- Lưu tóm tắt đó thay cho các message cũ đã bị cắt.
- Giữ lại bản tóm tắt cùng với 20 message mới nhất.

### Bước 4: Token counting và warning

- Xây hàm đếm token giả định dựa trên tách từ.
- Nếu tổng token gần tới giới hạn (>= 90%), hiển thị cảnh báo.

### Bước 5: Chat terminal

- Triển khai hàm `main()` để chạy vòng lặp chat.
- Người dùng nhập câu hỏi, chatbot trả lời.
- Chatbot giữ context giữa các lượt.
- Nếu có API key, kết nối tới OpenRouter để lấy phản hồi model.

## Ghi chú

- `Chatbot` tại đây dùng đếm token như một phép xấp xỉ.
- Code có thể gọi OpenRouter model nếu cấu hình biến môi trường `OPENROUTER_API_KEY`.
- Nếu không có API key hoặc `openai` chưa cài, chatbot sẽ trả lời bằng fallback nội bộ.
- Ghi rõ kết quả và quan sát trong `report_results.md`.
