# Báo cáo kết quả - Week 2 Day 1

## 1. Mục tiêu

- Thiết kế chatbot có history manager.
- Triển khai sliding window giữ 20 messages.
- Cài đặt summary context khi quá token limit.
- Đếm token và cảnh báo khi gần limit.
- Chat qua terminal và giữ được ngữ cảnh.

## 2. Kết quả thực hiện

- `chatbot.py` đã triển khai `Chatbot` với các chức năng yêu cầu.
- Chatbot lưu được lịch sử và giữ 20 message gần nhất.
- Khi bộ nhớ vượt ngưỡng, chatbot tạo tóm tắt cho phần hội thoại cũ.
- Cảnh báo token xuất hiện khi tổng token đạt >= 90% giới hạn.
- Terminal chat hoạt động, giữ ngữ cảnh giữa nhiều lượt.

## 3. Ví dụ chạy thử

```text
> Xin chào
Bot: Tôi đã nhận được tin nhắn của bạn: "Xin chào".
> Bạn có thể nhớ những gì tôi nói không?
Bot: Tôi vẫn còn nhớ cuộc hội thoại của chúng ta và sẽ cố gắng giữ ngữ cảnh.
```

## 4. Quan sát

- Sliding window giúp giảm kích thước lịch sử, giữ chỉ phần hội thoại quan trọng nhất.
- Summarization làm cho chatbot tiếp tục giữ được ý chính khi có nhiều lượt.
- Token warning hữu ích để cảnh báo khi lịch sử đã quá đầy.

## 5. Ghi chú cải tiến

- Có thể thay hàm `mock_token_count` bằng tokenizer thực tế cho chính xác hơn.
- Có thể kết nối API LLM để trả lời tự nhiên hơn.
- Có thể mở rộng `summary` thành nhiều cấp độ (summary ngắn, long-form, v.v.).
