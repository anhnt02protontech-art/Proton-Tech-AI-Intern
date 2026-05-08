"""
Buoc khoi tao cho du an AI Email Summarizer.
- Quan ly API key bang python-dotenv.
- Nhap noi dung email nhieu dong.
- Goi model qua OpenRouter de tom tat email.
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError

try:
    from rich.console import Console
    from rich.json import JSON
except ImportError:
    Console = None
    JSON = None

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "tencent/hy3-preview:free"
ALLOWED_PRIORITIES = {"High", "Medium", "Low"}
SYSTEM_PROMPT = """
Role:
Ban la chuyen gia phan tich du lieu va tro ly dieu hanh.

Task:
Tom tat email va trich xuat thong tin quan trong.

Output Format:
Luon tra ve JSON hop le voi dung 4 key sau:
- summary: string
- action_items: list[string]
- priority: mot trong ba gia tri High, Medium, Low
- people_mentioned: list[string]

Constraint:
Khong them loi dan, khong them markdown, chi tra ve JSON thuan tuy.
Ngon ngu phan hoi la tieng Viet.
""".strip()
console = Console() if Console else None


def default_output() -> dict[str, Any]:
    """
    Tra ve cau truc ket qua mac dinh.
    """
    return {
        "summary": "",
        "action_items": [],
        "priority": "Medium",
        "people_mentioned": [],
    }


def load_api_key(env_var_name: str = "OPENROUTER_API_KEY") -> str:
    """
    Doc API key tu file .env.

    Args:
        env_var_name: Ten bien moi truong chua API key.

    Returns:
        Chuoi API key.

    Raises:
        ValueError: Khi khong tim thay API key trong .env.
    """
    # Nap bien moi truong tu file .env o thu muc du an.
    load_dotenv()

    api_key = os.getenv(env_var_name)
    if not api_key:
        raise ValueError(
            f"Khong tim thay '{env_var_name}' trong file .env. "
            "Hay kiem tra lai cau hinh."
        )
    return api_key


def create_openai_client(api_key: str) -> OpenAI:
    """
    Tao OpenAI client de goi OpenRouter API.
    """
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def get_email_input(end_keyword: str = "END") -> str | None:
    """
    Nhan noi dung email nhieu dong tu ban phim.

    Co 2 cach ket thuc:
    - Nhap tu khoa ket thuc (mac dinh la END) tren mot dong rieng.
    - Nhan Ctrl+Z roi Enter (Windows) hoac Ctrl+D (macOS/Linux).
    """
    print("Dan noi dung email (nhieu dong).")
    print(
        f"Nhap '{end_keyword}' de ket thuc, "
        "hoac dung Ctrl+Z/Ctrl+D."
    )
    print("Neu ta muon thoat chuong trinh, hay nhap 'exit' o dong dau tien.")

    email_lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            # EOF cho phep ket thuc nhanh khi paste noi dung dai.
            break

        # Neu 'exit' duoc nhap o dong dau tien, ta thoat chuong trinh.
        if not email_lines and line.strip().lower() == "exit":
            return None

        if line.strip().upper() == end_keyword.upper():
            break

        email_lines.append(line)

    return "\n".join(email_lines).strip()


def summarize_email(email_content: str, client: OpenAI) -> str | None:
    """
    Goi model LLM de tom tat email.

    - SYSTEM_PROMPT duoc gui voi role 'system'.
    - email_content duoc gui voi role 'user'.
    - Tra ve chuoi van ban model tra lai.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Email can xu ly:\n{email_content}"},
            ],
        )
        return response.choices[0].message.content or ""
    except RateLimitError:
        print("Loi: Ta dang gui qua nhieu yeu cau. Vui long thu lai sau it phut.")
        return None
    except APIConnectionError:
        print("Loi: Khong ket noi duoc den OpenRouter API. Ta hay kiem tra mang.")
        return None
    except APIError as error:
        print(f"Loi API tu nha cung cap model: {error}")
        return None


def parse_llm_response(raw_response: str) -> dict:
    """
    Lam sach va parse ket qua tra ve tu LLM thanh dictionary.
    """
    cleaned_response = raw_response.strip()

    # Neu model tra ve markdown code fence, ta loai bo de parse JSON.
    if cleaned_response.startswith("```"):
        response_lines = cleaned_response.splitlines()
        if response_lines:
            first_line = response_lines[0].strip().lower()
            if first_line in {"```json", "```"}:
                response_lines = response_lines[1:]
        if response_lines and response_lines[-1].strip() == "```":
            response_lines = response_lines[:-1]
        cleaned_response = "\n".join(response_lines).strip()

    try:
        parsed_data = json.loads(cleaned_response)
        if not isinstance(parsed_data, dict):
            raise ValueError("Noi dung JSON khong phai object.")
        return parsed_data
    except ValueError as error:
        print(f"Loi parse JSON tu LLM: {error}")
        return default_output()


def validate_output(data: dict[str, Any]) -> dict[str, Any]:
    """
    Kiem tra va chuan hoa du lieu sau khi parse JSON tu LLM.
    """
    validated_data = dict(data) if isinstance(data, dict) else {}

    required_defaults = default_output()

    for key, default_value in required_defaults.items():
        if key not in validated_data:
            validated_data[key] = default_value

    if validated_data["priority"] not in ALLOWED_PRIORITIES:
        validated_data["priority"] = "Medium"

    if not isinstance(validated_data["action_items"], list):
        validated_data["action_items"] = []

    if not isinstance(validated_data["people_mentioned"], list):
        validated_data["people_mentioned"] = []

    if not isinstance(validated_data["summary"], str):
        validated_data["summary"] = ""

    return validated_data


def process_email_pipeline(email_content: str, client: OpenAI) -> dict[str, Any]:
    """
    Luong xu ly theo functional style:
    1) Goi API lay ket qua tho.
    2) Parse chuoi JSON.
    3) Validate cau truc va gia tri.
    4) Tra ve ket qua cuoi cung.
    """
    raw_response = summarize_email(email_content=email_content, client=client)
    if raw_response is None:
        return default_output()

    parsed_output = parse_llm_response(raw_response=raw_response)
    return validate_output(data=parsed_output)


def print_result_json(result: dict[str, Any]) -> None:
    """
    In ket qua JSON de ta de doc tren CLI.
    """
    if console and JSON:
        console.print(JSON.from_data(result))
        return
    print(json.dumps(result, ensure_ascii=False, indent=4))


def process_with_feedback(email_content: str, client: OpenAI) -> dict[str, Any]:
    """
    Chay pipeline va hien thi trang thai de ta biet dang cho API.
    """
    if console:
        with console.status("Ta dang xu ly..."):
            return process_email_pipeline(email_content=email_content, client=client)

    print("Ta dang xu ly...")
    return process_email_pipeline(email_content=email_content, client=client)


def main() -> None:
    """
    Luong chay chinh:
    1) Doc API key va khoi tao client.
    2) Nhan noi dung email tu nguoi dung.
    3) Chay pipeline xu ly va in ket qua cuoi cung.
    """
    api_key = load_api_key()
    client = create_openai_client(api_key=api_key)

    print("=== AI Email Summarizer CLI ===")
    while True:
        email_content = get_email_input()
        if email_content is None:
            print("Ta da thoat chuong trinh.")
            break

        if not email_content:
            print("Khong co noi dung email de tom tat. Ta thu lai email khac.\n")
            continue

        final_result = process_with_feedback(email_content=email_content, client=client)

        print("\n--- Ket qua cuoi cung ---")
        print_result_json(final_result)
        print()


if __name__ == "__main__":
    main()
