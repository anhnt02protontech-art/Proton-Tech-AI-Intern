import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 1. Cấu hình môi trường
load_dotenv(find_dotenv())
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def call_ai(prompt, temp):
    """Hàm gọi AI với tham số temperature cụ thể."""
    try:
        response = client.chat.completions.create(
            model="tencent/hy3-preview:free", # Hoặc model free khác tùy chọn
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Lỗi: {str(e)}"

def run_lab1():
    # Đề bài thí nghiệm
    prompt = "Hãy viết 1 câu định nghĩa ngắn gọn về AI."
    levels = [0, 0.3, 0.7, 1.0]
    num_runs = 2 # Chạy mỗi mức 2 lần để so sánh tính ổn định

    print("="*80)
    print(f"{'Temp':<6} | {'Lần':<5} | {'Kết quả đầu ra'}")
    print("="*80)

    for temp in levels:
        for run in range(1, num_runs + 1):
            output = call_ai(prompt, temp)
            # Làm sạch output để in lên 1 dòng cho gọn
            display_text = output.replace("\n", " ")[:100] + "..." if len(output) > 100 else output
            print(f"{temp:<6} | {run:<5} | {display_text}")
        print("-" * 80) # Dấu ngăn cách giữa các mức nhiệt độ

if __name__ == "__main__":
    run_lab1()