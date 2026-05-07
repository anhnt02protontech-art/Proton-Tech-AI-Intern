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
MAX_RETRIES = 3
FORBIDDEN_WORDS = ["lua dao", "doc hai", "xau xa", "hack"]


class OutputSchema(BaseModel):
    cong_ty: str
    cong_nghe: str
    tom_tat_ngan: str

    @field_validator("tom_tat_ngan")
    @classmethod
    def check_length(cls, value: str) -> str:
        if len(value) < 10:
            raise ValueError("Tom tat qua ngan (<10 ky tu).")
        if len(value) > 100:
            raise ValueError("Tom tat qua dai (>100 ky tu).")
        return value


def build_prompt(user_input: str, previous_error: str | None = None) -> str:
    retry_note = ""
    if previous_error:
        retry_note = (
            f"\nLan truoc khong dat do: {previous_error}\n"
            "Hay sua lai output va van chi tra ve JSON object."
        )

    return f"""
Trich xuat thong tin tu van ban sau va tra ve DUNG 1 JSON object.
Khong them giai thich, khong them markdown, khong them text ngoai JSON.

Schema:
{{
  "cong_ty": "<ten cong ty>",
  "cong_nghe": "<cong nghe chinh>",
  "tom_tat_ngan": "<tom tat 1 cau, 10-100 ky tu>"
}}
{retry_note}

Van ban: {user_input}
JSON:
""".strip()


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Model tra ve content=None.")
    return content.strip()


def extract_json(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON khong hop le: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("JSON phai la object.")
    return data


def safety_filter(text: str) -> bool:
    lowered = text.lower()
    return not any(word in lowered for word in FORBIDDEN_WORDS)


def validate_output(raw_text: str) -> OutputSchema:
    json_data = extract_json(raw_text)
    validated = OutputSchema(**json_data)

    all_text = [validated.cong_ty, validated.cong_nghe, validated.tom_tat_ngan]
    if not all(safety_filter(value) for value in all_text):
        raise ValueError("Noi dung vi pham bo loc an toan.")
    return validated


def run_pipeline(user_input: str, max_retries: int = MAX_RETRIES) -> dict[str, Any]:
    last_error: str | None = None

    for attempt in range(1, max_retries + 1):
        prompt = build_prompt(user_input=user_input, previous_error=last_error)
        try:
            raw_output = call_llm(prompt)
            validated = validate_output(raw_output)
            return {
                "status": "success",
                "attempt": attempt,
                "model": MODEL,
                "data": validated.model_dump(),
                "raw_output": raw_output,
            }
        except (ValidationError, ValueError, Exception) as exc:
            last_error = str(exc)

    return {
        "status": "error",
        "attempt": max_retries,
        "model": MODEL,
        "message": f"That bai sau {max_retries} lan retry. Loi cuoi: {last_error}",
    }


if __name__ == "__main__":
    sample_input = "Google ra mat Gemini giup lap trinh nhanh hon."
    result = run_pipeline(sample_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))
