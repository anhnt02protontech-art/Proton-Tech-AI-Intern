import os

try:
    from openai import OpenAI
except ModuleNotFoundError as exc:
    raise SystemExit("Thieu thu vien openai. Cai bang: pip install openai") from exc

# Cau hinh moi truong
try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
except ModuleNotFoundError:
    # Van chay duoc neu bien moi truong da duoc set tu he thong.
    pass
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("Thieu OPENROUTER_API_KEY trong file .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "tencent/hy3-preview:free"
INPUT_TEXT = (
    "Microsoft vua ra mat Copilot+ PC tich hop bo xu ly NPU manh me "
    "cho cac tac vu AI dia phuong."
)

ZERO_SHOT_PROMPT = """
Trich xuat ten cong ty va cong nghe trong van ban sau.
Tra ve dung 1 JSON object voi 2 key: "cong_ty", "cong_nghe".

Van ban: "{text}"
JSON:
""".strip()

FEW_SHOT_PROMPTS = {
    "few_shot_1_co_ban": """
Ban la tro ly trich xuat du lieu.
Nhiem vu: Trich xuat "cong_ty" va "cong_nghe", tra ve JSON object.

Vi du 1:
Van ban: "Apple cong bo chip M3 cho MacBook."
JSON: {"cong_ty": "Apple", "cong_nghe": "chip M3"}

Vi du 2:
Van ban: "Google dua Gemini vao he sinh thai tim kiem."
JSON: {"cong_ty": "Google", "cong_nghe": "Gemini"}

Vi du 3:
Van ban: "Tesla nang cap FSD bang mang no-ron."
JSON: {"cong_ty": "Tesla", "cong_nghe": "FSD, mang no-ron"}

Van ban: "{text}"
JSON:
""".strip(),
    "few_shot_2_rang_buoc_format": """
Hay trich xuat thong tin va chi tra ve JSON object hop le.
Schema bat buoc:
{"cong_ty": "<string>", "cong_nghe": "<string>"}

Vi du 1:
Input: "NVIDIA day manh GPU Blackwell cho AI."
Output: {"cong_ty": "NVIDIA", "cong_nghe": "GPU Blackwell"}

Vi du 2:
Input: "OpenAI phat hanh GPT-4.1 cho lap trinh."
Output: {"cong_ty": "OpenAI", "cong_nghe": "GPT-4.1"}

Vi du 3:
Input: "Meta toi uu Llama cho ung dung tro ly ao."
Output: {"cong_ty": "Meta", "cong_nghe": "Llama"}

Input: "{text}"
Output:
""".strip(),
    "few_shot_3_phan_tich_ngan": """
Trich xuat thong tin theo mau:
1) Xac dinh cong ty.
2) Xac dinh cong nghe/nen tang duoc nhac den.
3) Tra ve JSON object voi key "cong_ty", "cong_nghe".

Mau 1:
Text: "Amazon nang cap dich vu Bedrock cho khach hang doanh nghiep."
JSON: {"cong_ty": "Amazon", "cong_nghe": "Bedrock"}

Mau 2:
Text: "Intel gioi thieu vi xu ly Lunar Lake toi uu AI tren may tinh."
JSON: {"cong_ty": "Intel", "cong_nghe": "Lunar Lake"}

Mau 3:
Text: "Adobe dua Firefly vao Photoshop de ho tro tao anh."
JSON: {"cong_ty": "Adobe", "cong_nghe": "Firefly"}

Text: "{text}"
JSON:
""".strip(),
}


def call_ai(prompt: str, temperature: float = 0.2) -> str:
    """Goi AI voi temperature thap de giam sai lech format."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if content is None:
            return "Error: Model tra ve content=None (khong co noi dung tra loi)."
        return content.strip()
    except Exception as exc:
        return f"Error: {exc}"


def fill_prompt(prompt_template: str, text: str) -> str:
    """
    Chen input text vao prompt ma khong dung str.format,
    tranh xung dot voi dau { } trong JSON examples/schema.
    """
    return prompt_template.replace("{text}", text)


def run_lab2() -> None:
    print("=" * 96)
    print("LAB 2 - SO SANH ZERO-SHOT VOI 3 FEW-SHOT PROMPTS")
    print(f"Model : {MODEL}")
    print(f"Input : {INPUT_TEXT}")
    print("=" * 96)

    print("\n[0] Zero-shot")
    zero_result = call_ai(fill_prompt(ZERO_SHOT_PROMPT, INPUT_TEXT))
    print(zero_result)

    for index, (name, prompt_template) in enumerate(FEW_SHOT_PROMPTS.items(), start=1):
        print(f"\n[{index}] {name}")
        result = call_ai(fill_prompt(prompt_template, INPUT_TEXT))
        print(result)


if __name__ == "__main__":
    run_lab2()
