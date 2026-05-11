"""
Chatbot Basics - Week 2 Day 1

File này định nghĩa lớp Chatbot có:
- Lưu trữ conversation history.
- Sliding window giữ 20 messages gần nhất.
- Context summarization khi vượt ngưỡng token.
- Token counting và warning.
- Chat qua terminal.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:  # type: ignore
    find_dotenv = None  # type: ignore
    load_dotenv = None  # type: ignore

try:
    from openai import OpenAI
except ImportError:  # type: ignore
    OpenAI = None  # type: ignore

if load_dotenv is not None and find_dotenv is not None:
    load_dotenv(find_dotenv())


@dataclass
class Message:
    role: str
    text: str


@dataclass
class Chatbot:
    max_messages: int = 20
    token_limit: int = 1000
    warning_threshold: float = 0.9
    model_name: str = "inclusionai/ring-2.6-1t:free"
    history: List[Message] = field(default_factory=list)
    summary: str = ""
    client: Optional[Any] = None

    def __post_init__(self) -> None:
        self._load_api_client()

    def _load_api_client(self) -> None:
        """Load OpenRouter client from environment configuration."""
        if OpenAI is None:
            print("[INFO] openai package không cài đặt. API model sẽ bị vô hiệu hóa.")
            return

        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            print("[INFO] OPENROUTER_API_KEY không tìm thấy. Model sẽ dùng chế độ fallback.")
            return

        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key)

    def add_message(self, role: str, text: str) -> None:
        """Add a new message to history and manage memory."""
        self.history.append(Message(role=role, text=text.strip()))
        self._apply_sliding_window()
        self._check_token_limits()

    def _apply_sliding_window(self) -> None:
        """Keep only the latest max_messages in history and preserve older context in summary."""
        if len(self.history) <= self.max_messages:
            return

        old_messages = self.history[:-self.max_messages]
        if old_messages:
            summary_texts = [f'{msg.role}: {msg.text}' for msg in old_messages]
            new_summary = self._create_summary_text(" | ".join(summary_texts))
            self.summary = self._merge_summaries(self.summary, new_summary)

        self.history = self.history[-self.max_messages :]

    def _check_token_limits(self) -> None:
        """Tự động tóm tắt hoặc cắt tỉa khi token count vượt ngưỡng."""
        total_tokens = self.current_token_count()
        if total_tokens > self.token_limit:
            self._summarize_old_history()
            self._apply_sliding_window()

            # Nếu vẫn vượt hạn sau khi tạo summary, cắt bớt thêm lịch sử cũ.
            if self.current_token_count() > self.token_limit:
                self._prune_to_limit()

        self._print_warning_if_needed()

    def _summarize_old_history(self) -> None:
        """Create a short summary from older history when token limit is exceeded."""
        if self.summary:
            return

        if len(self.history) <= self.max_messages:
            return

        old_messages = self.history[:-self.max_messages]
        if not old_messages:
            return

        summary_texts = [f'{msg.role}: {msg.text}' for msg in old_messages]
        summary_text = " | ".join(summary_texts)
        self.summary = self._create_summary_text(summary_text)

        # Giữ lại chỉ phần message mới nhất; summary được lưu riêng.
        self.history = self.history[-self.max_messages :]

    def _create_summary_text(self, text: str) -> str:
        """Generate a condensed summary from the provided text."""
        # Tóm tắt bằng cách giữ các câu chủ đạo và cắt ngắn.
        sentences = re.split(r"(?<=[.!?])\s+", text)
        if len(sentences) <= 3:
            return text

        short_summary = " ".join(sentences[:3])
        if len(short_summary) > 300:
            short_summary = short_summary[:300].rstrip()
        return f"[Tóm tắt hội thoại trước đây] {short_summary}"

    def _merge_summaries(self, existing: str, new: str) -> str:
        """Combine an existing summary with newly truncated history."""
        if not existing:
            return new
        if not new:
            return existing
        merged = f"{existing} | {new}"
        if len(merged) > 1000:
            return merged[:1000].rstrip()
        return merged

    def _prune_to_limit(self) -> None:
        """Remove older messages until token count fits within token_limit."""
        while self.history and self.current_token_count() > self.token_limit:
            self.history.pop(0)

    def current_token_count(self) -> int:
        """Count tokens for summary and current history."""
        count = self._mock_token_count(self.summary)
        for msg in self.history:
            count += self._mock_token_count(msg.text)
        return count

    def _mock_token_count(self, text: str) -> int:
        """Estimate token count using whitespace and punctuation-based splitting."""
        if not text:
            return 0

        tokens = re.findall(r"\w+|[^	\w\s]", text)
        return len(tokens)

    def _print_warning_if_needed(self) -> None:
        """Warn when token usage is close to the limit."""
        current_tokens = self.current_token_count()
        if current_tokens >= self.token_limit:
            print("[WARNING] Token limit exceeded. History đã bị rút gọn hoặc tóm tắt.")
        elif current_tokens >= int(self.token_limit * self.warning_threshold):
            print(f"[WARNING] Token usage cao: {current_tokens}/{self.token_limit} tokens.")

    def _build_model_messages(self) -> List[Dict[str, str]]:
        """Build message payload for the chat completion model."""
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": "Bạn là một trợ lý chatbot thông minh. Sử dụng ngữ cảnh hội thoại để trả lời rõ ràng và ngắn gọn. Hãy nhớ và tham chiếu đến các câu hỏi trước đó nếu cần.",
            }
        ]
        if self.summary:
            messages.append(
                {
                    "role": "system",
                    "content": f"Tóm tắt hội thoại trước đây: {self.summary}",
                }
            )

        for msg in self.history:
            messages.append({"role": msg.role, "content": msg.text})

        return messages

    def _call_model(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Call the OpenRouter model and return the assistant response."""
        if self.client is None:
            return None

        try:
            raw_response = self.client.chat.completions.with_raw_response.create(
                model=self.model_name,
                messages=messages,
            )
            response = raw_response.parse()
            return response.choices[0].message.content.strip()
        except Exception as exc:
            print("[ERROR] Request model failed:", exc)
            return None

    def get_context(self) -> str:
        """Build the context string used để mô phỏng cách chatbot nhớ lại."""
        parts = []
        if self.summary:
            parts.append(self.summary)
        for msg in self.history:
            parts.append(f"{msg.role}: {msg.text}")
        return "\n".join(parts)

    def get_history(self) -> List[Dict[str, str]]:
        """Return conversation history as a list of role/text dictionaries."""
        return [{"role": msg.role, "text": msg.text} for msg in self.history]

    def _is_meta_question(self, user_text: str) -> bool:
        """Detect user questions about conversation metadata."""
        normalized = user_text.lower()
        return any(
            phrase in normalized
            for phrase in [
                "first question",
                "first user question",
                "what was the first question",
                "what is first question",
                "first thing i asked",
            ]
        )

    def _get_user_questions(self) -> List[str]:
        """Return all user questions found in history and summary."""
        user_questions = [msg.text for msg in self.history if msg.role == "user"]
        if self.summary:
            additional = re.findall(r"user:\s*(.+?)(?:\s*\|\s*assistant:|$)", self.summary, flags=re.IGNORECASE)
            user_questions = [q.strip() for q in additional if q.strip()] + user_questions
        return user_questions

    def _get_first_user_question(self, current_user_text: str) -> Optional[str]:
        """Return the earliest user question before the current meta query."""
        user_questions = self._get_user_questions()
        # Exclude the current user_text if it's a meta question to avoid self-reference
        if user_questions and user_questions[-1] == current_user_text and self._is_meta_question(current_user_text):
            user_questions = user_questions[:-1]
        if len(user_questions) <= 0:
            return None
        return user_questions[0]

    def _handle_meta_question(self, user_text: str) -> Optional[str]:
        """Handle special follow-up questions using local history."""
        if not self._is_meta_question(user_text):
            return None

        first_question = self._get_first_user_question(user_text)
        if first_question:
            return f"Your first question was: \"{first_question}\"."

        return "Tôi chưa có đủ câu hỏi trước đó để xác định câu hỏi đầu tiên."

    def generate_reply(self, user_text: str) -> str:
        """Generate a reply based on the current context and latest user message."""
        self.add_message(role="user", text=user_text)

        meta_reply = self._handle_meta_question(user_text)
        if meta_reply is not None:
            reply = meta_reply
        else:
            model_messages = self._build_model_messages()
            reply = self._call_model(model_messages)
            if reply is None:
                # Fallback nếu không có API key hoặc API gặp lỗi.
                if "nhớ" in user_text.lower():
                    reply = "Tôi vẫn còn nhớ phần lớn cuộc hội thoại và sẽ cố gắng giữ ngữ cảnh cho bạn."
                elif "tóm tắt" in user_text.lower() or "summary" in user_text.lower():
                    reply = "Tôi có thể giữ ý chính của các lượt trước bằng cách tóm tắt nội dung cũ."
                else:
                    reply = f"Tôi đã nhận được tin nhắn của bạn: \"{user_text}\"."

        self.add_message(role="assistant", text=reply)
        return reply

    def terminal_chat(self) -> None:
        """Start a terminal-based conversation loop."""
        print("Chatbot đang chạy. Gõ 'exit' hoặc 'quit' để thoát.")
        print("Nhập câu hỏi và nhấn Enter để tiếp tục.")

        while True:
            user_text = input("Bạn: ").strip()
            if not user_text or user_text.lower() in {"exit", "quit"}:
                print("Kết thúc trò chuyện. Cảm ơn bạn!")
                break

            reply = self.generate_reply(user_text)
            print(f"Bot: {reply}")
            print(f"[Token hiện tại: {self.current_token_count()}/{self.token_limit}]\n")


def main() -> None:
    chatbot = Chatbot()
    chatbot.terminal_chat()


if __name__ == "__main__":
    main()
