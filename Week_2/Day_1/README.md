# Week 2 - Day 1: Chatbot Basics

## Tổng quan

Bài tập này xây dựng một chatbot cơ bản có memory. Chatbot sẽ:

- Lưu lịch sử hội thoại.
- Áp dụng sliding window để giữ 20 messages gần nhất.
- Tóm tắt hội thoại cũ khi vượt ngưỡng token.
- Đếm token và cảnh báo khi gần giới hạn.
- Cho phép trò chuyện qua terminal.

## File trong thư mục

- `chatbot.py`: cài đặt `Chatbot` và vòng lặp chat terminal.
- `instructions.md`: hướng dẫn làm bài và nội dung thực hành.
- `report_results.md`: lưu kết quả thu được và bài học.

## Cách chạy

1. Mở terminal tại `Week_2/Day_1`.
2. Tạo file `.env` hoặc thiết lập biến môi trường `OPENROUTER_API_KEY` với API key của bạn.
3. Cài đặt dependencies nếu cần:

```bash
pip install python-dotenv openai
```

4. Chạy lệnh:

```bash
python chatbot.py
```

5. Nhập câu hỏi để trò chuyện.
6. Gõ `exit`, `quit`, hoặc nhấn Enter vào dòng trống để thoát.

## Chú ý

- `chatbot.py` dùng OpenRouter model nếu biến môi trường `OPENROUTER_API_KEY` tồn tại.
- Nếu không có API key hoặc `openai` chưa cài, chatbot sẽ dùng câu trả lời fallback nội bộ.
- `chatbot.py` vẫn sử dụng bộ đếm token ước lượng cho mục đích demo.
- Khi lịch sử quá dài, chatbot tự động tóm tắt và cắt bớt nội dung cũ.
- Cảnh báo token sẽ hiển thị khi bộ đếm vượt 90% giới hạn.
