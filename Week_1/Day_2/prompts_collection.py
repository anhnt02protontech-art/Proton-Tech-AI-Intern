import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load biến môi trường và khởi tạo Client
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

class StructuredPromptLibrary:
    """Bộ 10 Structured Prompts theo cấu trúc RICC"""
    
    # --- TÓM TẮT ---
    SUMMARIZE_NEWS = "[ROLE]: Editor. [INSTRUCTION]: Tóm tắt thành 3 ý JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    SUMMARIZE_MEETING = "[ROLE]: PM. [INSTRUCTION]: Trích xuất Action Items JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    
    # --- PHÂN LOẠI ---
    CLASSIFY_INTENT = "[ROLE]: CS Analyst. [INSTRUCTION]: Phân loại ý định JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    CLASSIFY_SENTIMENT = "[ROLE]: Sentiment AI. [INSTRUCTION]: Phân tích cảm xúc JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    
    # --- TRÍCH XUẤT ---
    EXTRACT_INVOICE = "[ROLE]: Accountant. [INSTRUCTION]: Trích xuất info hóa đơn JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    EXTRACT_BIO = "[ROLE]: HR. [INSTRUCTION]: Trích xuất profile JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    
    # --- DỊCH THUẬT ---
    TRANSLATE_TECH = "[ROLE]: Tech Translator. [INSTRUCTION]: Dịch kỹ thuật JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    TRANSLATE_BUSINESS = "[ROLE]: Business Translator. [INSTRUCTION]: Dịch formal JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    
    # --- SÁNG TẠO ---
    GENERATE_AD = "[ROLE]: Copywriter. [INSTRUCTION]: Tạo quảng cáo JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."
    GENERATE_EMAIL = "[ROLE]: Email Expert. [INSTRUCTION]: Soạn email phản hồi JSON. [CONTEXT]: {text} [CONSTRAINT]: JSON format only."

# --- HÀM THỰC THI GỌI OPENROUTER ---

def call_openrouter_ai(prompt_template, raw_input):
    """Lắp prompt và gọi model qua OpenRouter"""
    try:
        # Format prompt
        full_prompt = prompt_template.format(text=raw_input)
        
        # Gọi API với raw response (để lấy status code nếu cần)
        raw_response = client.chat.completions.with_raw_response.create(
            model="tencent/hy3-preview:free",
            messages=[
                {"role": "user", "content": full_prompt}
            ],
        )
        
        # Lấy nội dung text từ response
        completion = raw_response.parse()
        content = completion.choices[0].message.content
        
        # Làm sạch JSON (xóa code blocks ```json ... ```)
        clean_json_str = re.sub(r'^```json|```$', '', content.strip(), flags=re.MULTILINE)
        
        return json.loads(clean_json_str)
    
    except Exception as e:
        return {"error": str(e)}

# --- 10 FUNCTIONS TƯƠNG ỨNG ---

def summarize_news(text): return call_openrouter_ai(StructuredPromptLibrary.SUMMARIZE_NEWS, text)
def summarize_meeting(text): return call_openrouter_ai(StructuredPromptLibrary.SUMMARIZE_MEETING, text)
def classify_intent(text): return call_openrouter_ai(StructuredPromptLibrary.CLASSIFY_INTENT, text)
def classify_sentiment(text): return call_openrouter_ai(StructuredPromptLibrary.CLASSIFY_SENTIMENT, text)
def extract_invoice(text): return call_openrouter_ai(StructuredPromptLibrary.EXTRACT_INVOICE, text)
def extract_bio(text): return call_openrouter_ai(StructuredPromptLibrary.EXTRACT_BIO, text)
def translate_tech(text): return call_openrouter_ai(StructuredPromptLibrary.TRANSLATE_TECH, text)
def translate_business(text): return call_openrouter_ai(StructuredPromptLibrary.TRANSLATE_BUSINESS, text)
def generate_ad(text): return call_openrouter_ai(StructuredPromptLibrary.GENERATE_AD, text)
def generate_email(text): return call_openrouter_ai(StructuredPromptLibrary.GENERATE_EMAIL, text)

# --- TEST ---
if __name__ == "__main__":
    test_text = "Tôi muốn mua một chiếc laptop gaming tầm giá 30 triệu."
    print("AI Response:", classify_intent(test_text))