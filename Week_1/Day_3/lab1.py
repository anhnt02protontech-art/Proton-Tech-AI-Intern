import csv
import os
from datetime import datetime

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


def call_ai(prompt: str, temperature: float, model: str) -> str:
    """Goi AI voi gia tri temperature cu the."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"Loi: {exc}"


def save_results_csv(results: list[dict], output_path: str) -> None:
    fieldnames = ["timestamp", "model", "temperature", "run", "prompt", "output"]
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def run_lab1() -> None:
    prompt = "Hãy viết 5 định nghĩa sáng tạo, độc đáo và khác biệt về AI, mỗi định nghĩa một phong cách khác nhau."
    temperatures = [0.0, 0.3, 0.7, 1.0]
    runs_per_temperature = 2
    model = "tencent/hy3-preview:free"

    print("=" * 96)
    print("LAB 1 - THI NGHIEM TEMPERATURE")
    print(f"Prompt: {prompt}")
    print(f"Model : {model}")
    print("=" * 96)
    print(f"{'Temp':<8} | {'Run':<5} | Output")
    print("-" * 96)

    results: list[dict] = []
    timestamp = datetime.now().isoformat(timespec="seconds")

    for temperature in temperatures:
        for run in range(1, runs_per_temperature + 1):
            output = call_ai(prompt=prompt, temperature=temperature, model=model)
            one_line = output.replace("\n", " ")
            short_output = one_line[:120] + "..." if len(one_line) > 120 else one_line

            print(f"{temperature:<8} | {run:<5} | {short_output}")

            results.append(
                {
                    "timestamp": timestamp,
                    "model": model,
                    "temperature": temperature,
                    "run": run,
                    "prompt": prompt,
                    "output": output,
                }
            )
        print("-" * 96)

    output_path = os.path.join(os.path.dirname(__file__), "lab1_results.csv")
    save_results_csv(results, output_path)
    print(f"\nDa luu ket qua vao: {output_path}")


if __name__ == "__main__":
    run_lab1()
