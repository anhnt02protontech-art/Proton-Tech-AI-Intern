import json
import os
import re
from textwrap import dedent

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# 1) Load biến môi trường và khởi tạo OpenRouter client
load_dotenv(find_dotenv())
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


class StructuredPromptLibrary:
    """Bộ 10 Structured Prompts theo cấu trúc RICC (Role, Instruction, Context, Constraint)."""

    # --- TÓM TẮT ---
    SUMMARIZE_NEWS = dedent(
        """
        [ROLE]
        Bạn là biên tập viên tin tức giàu kinh nghiệm.

        [INSTRUCTION]
        Tóm tắt nội dung thành 3 ý chính, nêu thực thể quan trọng và đặt 1 tiêu đề ngắn.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm.

        [OUTPUT_SCHEMA]
        {
          "headline": "string",
          "summary_3_points": ["string", "string", "string"],
          "key_entities": ["string"]
        }
        """
    ).strip()

    SUMMARIZE_MEETING = dedent(
        """
        [ROLE]
        Bạn là project manager chuyên ghi biên bản họp.

        [INSTRUCTION]
        Tóm tắt cuộc họp theo: mục tiêu, quyết định, việc cần làm.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Chỉ trả về JSON hợp lệ, không markdown, không suy diễn thông tin thiếu.

        [OUTPUT_SCHEMA]
        {
          "meeting_goal": "string",
          "decisions": ["string"],
          "action_items": [
            {
              "task": "string",
              "owner": "string",
              "deadline": "string|null"
            }
          ]
        }
        """
    ).strip()

    # --- PHÂN LOẠI ---
    CLASSIFY_INTENT = dedent(
        """
        [ROLE]
        Bạn là chuyên viên phân tích intent cho chăm sóc khách hàng.

        [INSTRUCTION]
        Phân loại ý định chính của người dùng từ đoạn văn bản.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Chỉ dùng nhãn: "purchase", "support", "complaint", "refund", "other".
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "primary_intent": "purchase|support|complaint|refund|other",
          "confidence": 0.0,
          "reason": "string"
        }
        """
    ).strip()

    CLASSIFY_SENTIMENT = dedent(
        """
        [ROLE]
        Bạn là hệ thống phân tích cảm xúc tiếng Việt.

        [INSTRUCTION]
        Xác định cảm xúc tổng thể của văn bản và cường độ cảm xúc.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Chỉ dùng nhãn: "positive", "neutral", "negative".
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "sentiment": "positive|neutral|negative",
          "sentiment_score": 0.0,
          "evidence": ["string"]
        }
        """
    ).strip()

    # --- TRÍCH XUẤT ---
    EXTRACT_INVOICE = dedent(
        """
        [ROLE]
        Bạn là kế toán viên xử lý hóa đơn.

        [INSTRUCTION]
        Trích xuất các trường quan trọng từ hóa đơn.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Nếu thiếu thông tin thì trả về null.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "vendor_name": "string|null",
          "invoice_number": "string|null",
          "invoice_date": "string|null",
          "total_amount": "number|null",
          "currency": "string|null"
        }
        """
    ).strip()

    EXTRACT_BIO = dedent(
        """
        [ROLE]
        Bạn là HR analyst chuẩn hóa hồ sơ ứng viên.

        [INSTRUCTION]
        Trích xuất thông tin chính từ đoạn mô tả tiểu sử/giới thiệu cá nhân.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Không tự bịa dữ liệu.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "full_name": "string|null",
          "current_title": "string|null",
          "years_of_experience": "number|null",
          "skills": ["string"],
          "location": "string|null"
        }
        """
    ).strip()

    # --- DỊCH THUẬT ---
    TRANSLATE_TECH = dedent(
        """
        [ROLE]
        Bạn là biên dịch viên kỹ thuật Anh-Việt.

        [INSTRUCTION]
        Dịch văn bản kỹ thuật sang tiếng Việt, giữ nguyên thuật ngữ chuyên ngành quan trọng.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Không thêm thông tin ngoài văn bản gốc.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "source_language": "string",
          "target_language": "vi",
          "translated_text": "string",
          "glossary": [{"source_term": "string", "target_term": "string"}]
        }
        """
    ).strip()

    TRANSLATE_BUSINESS = dedent(
        """
        [ROLE]
        Bạn là biên dịch viên thương mại, giọng văn trang trọng.

        [INSTRUCTION]
        Dịch văn bản kinh doanh sang tiếng Việt theo phong cách lịch sự và rõ ràng.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Giữ đúng nghĩa, không rút gọn thông tin quan trọng.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "source_language": "string",
          "target_language": "vi",
          "translated_text": "string",
          "tone": "formal"
        }
        """
    ).strip()

    # --- TẠO NỘI DUNG ---
    GENERATE_AD = dedent(
        """
        [ROLE]
        Bạn là copywriter quảng cáo số.

        [INSTRUCTION]
        Tạo nội dung quảng cáo cho sản phẩm/dịch vụ từ ngữ cảnh đầu vào.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Viết rõ lợi ích, CTA mạnh, không dùng từ ngữ gây hiểu lầm.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "headline_options": ["string", "string", "string"],
          "ad_body": "string",
          "cta": "string"
        }
        """
    ).strip()

    GENERATE_EMAIL = dedent(
        """
        [ROLE]
        Bạn là chuyên gia soạn email doanh nghiệp.

        [INSTRUCTION]
        Soạn email phản hồi chuyên nghiệp dựa trên ngữ cảnh đầu vào.

        [CONTEXT]
        {text}

        [CONSTRAINT]
        Ngắn gọn, lịch sự, rõ hành động tiếp theo.
        Chỉ trả về JSON hợp lệ.

        [OUTPUT_SCHEMA]
        {
          "subject": "string",
          "email_body": "string",
          "next_step": "string"
        }
        """
    ).strip()


PROMPT_MAP = {
    "summarize_news": StructuredPromptLibrary.SUMMARIZE_NEWS,
    "summarize_meeting": StructuredPromptLibrary.SUMMARIZE_MEETING,
    "classify_intent": StructuredPromptLibrary.CLASSIFY_INTENT,
    "classify_sentiment": StructuredPromptLibrary.CLASSIFY_SENTIMENT,
    "extract_invoice": StructuredPromptLibrary.EXTRACT_INVOICE,
    "extract_bio": StructuredPromptLibrary.EXTRACT_BIO,
    "translate_tech": StructuredPromptLibrary.TRANSLATE_TECH,
    "translate_business": StructuredPromptLibrary.TRANSLATE_BUSINESS,
    "generate_ad": StructuredPromptLibrary.GENERATE_AD,
    "generate_email": StructuredPromptLibrary.GENERATE_EMAIL,
}


def _extract_json_from_response(text_response: str):
    """Làm sạch code fence nếu có và parse JSON."""
    cleaned = text_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def call_openrouter_ai(prompt_template, raw_input):
    """Lắp prompt và gọi model qua OpenRouter."""
    try:
        # Dùng replace thay cho str.format để tránh lỗi với dấu { } trong JSON schema.
        full_prompt = prompt_template.replace("{text}", raw_input)

        raw_response = client.chat.completions.with_raw_response.create(
            model="tencent/hy3-preview:free",
            messages=[{"role": "user", "content": full_prompt}],
        )

        completion = raw_response.parse()
        content = completion.choices[0].message.content or "{}"
        return _extract_json_from_response(content)

    except Exception as e:
        return {"error": str(e)}


# --- 10 FUNCTIONS TƯƠNG ỨNG ---
def summarize_news(text):
    return call_openrouter_ai(StructuredPromptLibrary.SUMMARIZE_NEWS, text)


def summarize_meeting(text):
    return call_openrouter_ai(StructuredPromptLibrary.SUMMARIZE_MEETING, text)


def classify_intent(text):
    return call_openrouter_ai(StructuredPromptLibrary.CLASSIFY_INTENT, text)


def classify_sentiment(text):
    return call_openrouter_ai(StructuredPromptLibrary.CLASSIFY_SENTIMENT, text)


def extract_invoice(text):
    return call_openrouter_ai(StructuredPromptLibrary.EXTRACT_INVOICE, text)


def extract_bio(text):
    return call_openrouter_ai(StructuredPromptLibrary.EXTRACT_BIO, text)


def translate_tech(text):
    return call_openrouter_ai(StructuredPromptLibrary.TRANSLATE_TECH, text)


def translate_business(text):
    return call_openrouter_ai(StructuredPromptLibrary.TRANSLATE_BUSINESS, text)


def generate_ad(text):
    return call_openrouter_ai(StructuredPromptLibrary.GENERATE_AD, text)


def generate_email(text):
    return call_openrouter_ai(StructuredPromptLibrary.GENERATE_EMAIL, text)


# --- TEST ---
if __name__ == "__main__":
    assert len(PROMPT_MAP) == 10, "Thiếu prompt trong bộ 10."
    test_text = "Tên tôi là gì"
    print("AI Response:", classify_intent(test_text))
