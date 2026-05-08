# AI Email Summarizer (Day 5)

## Tong quan
Day la ung dung CLI tom tat email bang LLM (OpenRouter) voi luong xu ly:

1. Goi API LLM.
2. Parse JSON response.
3. Validate cau truc output.
4. In ket qua de review.

File chinh:

- `ai_email_summarizer.py`: CLI chinh va toan bo ham xu ly.
- `test_samples.py`: Bo test email mau de chay nhanh.

## Yeu cau moi truong

- Python 3.10+
- Cac thu vien:
  - `openai`
  - `python-dotenv`
  - `rich` (tuy chon, de in mau dep hon)

Lenh cai dat:

```bash
pip install openai python-dotenv rich
```

## Cau hinh .env

Dat file `.env` tai root project (`Proton-Tech-AI-Intern`) voi key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

Ung dung hien dang goi:

- Base URL: `https://openrouter.ai/api/v1`
- Model: `tencent/hy3-preview:free`

## Chay CLI chinh

Tu root project, chay:

```bash
python Week_1/Day_5/ai_email_summarizer.py
```

Cach dung:

1. Paste email nhieu dong.
2. Nhap `END` o dong rieng de ket thuc input.
3. Hoac dung `Ctrl+Z` (Windows) / `Ctrl+D` (macOS/Linux).
4. Nhap `exit` o dong dau tien de thoat chuong trinh.

## Chay bo mau test

```bash
python Week_1/Day_5/test_samples.py
```

Bo mau gom:

1. Email cong viec cuc dai.
2. Email spam.
3. Email ngan/than mat.
4. Email loi (noi dung vo nghia).

Script se in:

1. Raw response tu model.
2. Validated JSON sau khi parse + chuan hoa.

## Cau truc output ky vong

Output sau validate luon co 4 key:

```json
{
    "summary": "",
    "action_items": [],
    "priority": "Medium",
    "people_mentioned": []
}
```

Quy tac:

1. Thieu key se duoc bo sung tu dong.
2. `priority` chi nhan: `High`, `Medium`, `Low`; sai se ve `Medium`.
3. `action_items` va `people_mentioned` luon duoc ep ve `list`.

## Xu ly loi API

Trong `summarize_email`, da bat:

1. `RateLimitError`: gui qua nhieu request.
2. `APIConnectionError`: loi ket noi mang/API.
3. `APIError`: loi he thong tu nha cung cap model.

Neu loi, ham tra ve `None`; pipeline se fallback ve output mac dinh de chuong trinh khong bi crash.

## Su co thuong gap

1. `ModuleNotFoundError: No module named 'dotenv'`
   - Cai thu vien: `pip install python-dotenv`
2. Khong tim thay API key
   - Kiem tra `.env` co `OPENROUTER_API_KEY`.
3. API tra loi model
   - Kiem tra lai key/quota/model co con kha dung tren OpenRouter.
