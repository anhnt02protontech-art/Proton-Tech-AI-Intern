# Test script để kiểm tra các tiêu chí của Chatbot

from chatbot import Chatbot

def test_conversation_history():
    """Kiểm tra 6.10.1: Lưu trữ conversation history"""
    bot = Chatbot(max_messages=5)  # Dùng nhỏ để test dễ
    bot.add_message('user', 'Hello')
    bot.add_message('assistant', 'Hi!')
    print("History length:", len(bot.history))
    print("History:", bot.get_history())
    # Kiểm tra: History nên có 2 messages

def test_sliding_window():
    """Kiểm tra 6.10.2: Sliding window giữ 20 messages gần nhất"""
    bot = Chatbot(max_messages=3)  # Dùng 3 để test nhanh
    for i in range(5):
        bot.add_message('user', f'Message {i}')
        bot.add_message('assistant', f'Reply {i}')
    print("History length after 5 pairs:", len(bot.history))
    print("History:", [(m.role, m.text) for m in bot.history])
    # Kiểm tra: History nên có 3 messages gần nhất (assistant: Reply 4, user: Message 4, assistant: Reply 4)

def test_context_summarization():
    """Kiểm tra 6.10.3: Context summarization khi vượt ngưỡng"""
    bot = Chatbot(max_messages=2, token_limit=20)  # Ngưỡng thấp để test
    for i in range(5):
        bot.add_message('user', f'Long message number {i} with more text to exceed token limit')
        bot.add_message('assistant', f'Short reply {i}')
    print("Summary:", bot.summary)
    print("History length:", len(bot.history))
    # Kiểm tra: Summary nên có nội dung, history giữ 2 messages gần nhất

def test_token_counting_and_warning():
    """Kiểm tra 6.10.4: Token counting và warning"""
    bot = Chatbot(token_limit=50, warning_threshold=0.8)
    bot.add_message('user', 'This is a long message that should trigger warnings when token count approaches limit.')
    print("Current token count:", bot.current_token_count())
    # Kiểm tra: Nên thấy warning nếu token > 40 (80% of 50)

def test_terminal_chat():
    """Kiểm tra 6.11: Chat qua terminal giữ ngữ cảnh"""
    # Chạy manual: python chatbot.py
    # Nhập vài câu hỏi, kiểm tra bot nhớ context (e.g., hỏi về câu trước)
    print("Run: python chatbot.py")
    print("Nhập 'What did I say before?' để kiểm tra context.")

if __name__ == "__main__":
    print("=== Test 6.10.1: Conversation History ===")
    test_conversation_history()
    print("\n=== Test 6.10.2: Sliding Window ===")
    test_sliding_window()
    print("\n=== Test 6.10.3: Context Summarization ===")
    test_context_summarization()
    print("\n=== Test 6.10.4: Token Counting and Warning ===")
    test_token_counting_and_warning()
    print("\n=== Test 6.11: Terminal Chat ===")
    test_terminal_chat()