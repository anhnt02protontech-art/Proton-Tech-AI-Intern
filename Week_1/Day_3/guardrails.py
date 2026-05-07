import json
import os
from typing import Any

try:
    from openai import OpenAI
except ModuleNotFoundError as exc:
    raise SystemExit("Thieu thu vien openai. Cai bang: pip install openai") from exc

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
except ModuleNotFoundError:
    # Van chay duoc neu bien moi truong da duoc set tu he thong.
    pass

from pydantic import BaseModel, ValidationError, field_validator

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Thieu OPENROUTER_API_KEY trong file .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "tencent/hy3-preview:free"
FORBIDDEN_WORDS = ["lua dao", "doc hai", "xau xa", "hack"]


class AIOutputSchema(BaseModel):
    cong_ty: str
    cong_nghe: str
    tom_tat_ngan: str

    @field_validator("tom_tat_ngan")
    @classmethod
    def check_length(cls, value: str) -> str:
        # Guardrail 2: do dai tom tat bat buoc trong khoang 10-100 ky tu.
        if len(value) < 10:
            raise ValueError("Tom tat qua ngan, can chi tiet hon.")
        if len(value) > 100:
            raise ValueError("Tom tat qua dai, can suc tich hon.")
        return value


def extract_json_object(raw_text: str) -> dict[str, Any]:
    """
    Guardrail 1: validate JSON output.
    Ho tro 2 truong hop:
    1) Model tra ve JSON thuan.
    2) Model tra ve JSON trong markdown code block.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model khong tra ve JSON hop le: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("JSON phai la object (khong phai list/string/number).")
    return parsed


def safety_filter(text: str) -> bool:
    # Guardrail 3: loc noi dung nhay cam.
    lowered = text.lower()
    for word in FORBIDDEN_WORDS:
        if word in lowered:
            return False
    return True


def check_all_text_fields_for_safety(data: AIOutputSchema) -> bool:
    return all(
        safety_filter(value) for value in [data.cong_ty, data.cong_nghe, data.tom_tat_ngan]
    )


def call_ai_with_guardrails(user_input: str) -> dict[str, Any]:
    prompt = f"""
Trich xuat thong tin tu van ban sau va tra ve dung 1 JSON object.
Yeu cau schema:
{{
  "cong_ty": "<ten cong ty>",
  "cong_nghe": "<cong nghe chinh>",
  "tom_tat_ngan": "<tom tat loi ich trong 1 cau, 10-100 ky tu>"
}}

Van ban: {user_input}
JSON:
""".strip()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        raw_content = response.choices[0].message.content
        if raw_content is None:
            return {"status": "error", "message": "Model tra ve content=None."}

        json_data = extract_json_object(raw_content)
        validated_data = AIOutputSchema(**json_data)

        if not check_all_text_fields_for_safety(validated_data):
            return {"status": "error", "message": "Noi dung vi pham chinh sach an toan."}

        return {"status": "success", "data": validated_data.model_dump()}

    except ValidationError as exc:
        return {"status": "error", "message": f"Loi schema/do dai: {exc.json()}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    print("=== TEST 1: INPUT CHUAN ===")
    print(call_ai_with_guardrails("Google ra mat Gemini giup lap trinh nhanh hon."))

    print("\n=== TEST 2: INPUT CO RUI RO DO DAI ===")
    print(call_ai_with_guardrails("Apple ra mat M3."))

    print("\n=== TEST 3: INPUT CO TU NHAY CAM ===")
    print(call_ai_with_guardrails("Cong ty X ra mat phan mem hack tai khoan."))
