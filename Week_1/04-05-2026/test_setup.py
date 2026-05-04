import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load biến môi trường
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 2. Khởi tạo client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def test_status_code():
    try:
        # Gọi API với raw response để lấy status code
        raw_response = client.chat.completions.with_raw_response.create(
            model="tencent/hy3-preview:free",
            messages=[
                {"role": "user", "content": "Hello"}
            ],
        )

        # In status code
        print("Status code:", raw_response.status_code)

        # Nếu muốn xem nội dung trả về
        response = raw_response.parse()
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print("Request failed!")
        print(e)

if __name__ == "__main__":
    test_status_code()