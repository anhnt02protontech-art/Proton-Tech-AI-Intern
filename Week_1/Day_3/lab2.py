import json
import os
import re

try:
    from openai import OpenAI
except ModuleNotFoundError as exc:
    raise SystemExit("Thieu thu vien openai. Cai bang: pip install openai") from exc

# Cau hinh moi truong
try:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
except ModuleNotFoundError:
    pass

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Thieu OPENROUTER_API_KEY trong file .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Su dung model ban da chi dinh
MODEL = "openrouter/free"

def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # De thap de dam bao tinh on dinh khi so sanh
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Loi ket noi: {str(e)}"

# 1. Input can xu ly (Mot cau hoi kho, co tinh mia mai)
test_input = "Sản phẩm tuyệt vời, dùng xong muốn vứt luôn cái điện thoại cũ đi vì nó... quá tệ so với cái này."

# 2. Cau truc Zero-shot Prompt
zero_shot_prompt = f"""
Hãy xác định sentiment của câu sau.: "{test_input}"
Trả về kết quả định dạng JSON gồm: sentiment (Tích cực/Tiêu cực) và score (1-10).
"""

# 3. Cau truc Few-shot Prompt (Nen bat suc manh bang cach day model hieu ngu canh)
few_shot_prompt = f"""
Bạn là một chuyên gia phân tích dữ liệu khách hàng. Hãy phân tích sắc thái bình luận và trả về JSON chuẩn.

### Ví dụ 1:
Input: "Giao hàng nhanh, đóng gói cẩn thận."
Output: {{"sentiment": "Tích cực", "score": 9}}

### Ví dụ 2:
Input: "Chờ cả tuần mà hàng vẫn chưa thấy đâu, làm ăn chán thật."
Output: {{"sentiment": "Tiêu cực", "score": 2}}

### Ví dụ 3 (Nhận diện mỉa mai):
Input: "Hàng đẹp lắm, treo lên làm cảnh chứ không dùng được."
Output: {{"sentiment": "Tiêu cực", "score": 3}}

### Yêu cầu thực tế:
Input: "{test_input}"
Output:
"""

def main():
    print(test_input)
    print("--- ĐANG CHẠY THỬ NGHIỆM LAB 2 ---")
    
    print("\n[1] KẾT QUẢ ZERO-SHOT:")
    print("-" * 30)
    zs_res = get_ai_response(zero_shot_prompt)
    print(zs_res)

    print("\n[2] KẾT QUẢ FEW-SHOT:")
    print("-" * 30)
    fs_res = get_ai_response(few_shot_prompt)
    print(fs_res)

    print("\n" + "="*50)

if __name__ == "__main__":
    main()