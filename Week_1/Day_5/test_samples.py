"""
Script chay mau de kiem thu AI Email Summarizer voi nhieu loai email.
"""

from __future__ import annotations

import json

from ai_email_summarizer import (
    create_openai_client,
    default_output,
    load_api_key,
    print_result_json,
    process_email_pipeline,
    summarize_email,
)

EMAIL_SAMPLES = [
    {
        "label": "Email cong viec cuc dai",
        "content": """
Subject: Ke hoach trien khai Q3 va cac dau muc can chot gap

Chao team,
Sau buoi hop sang nay, ta can chot ke hoach trien khai cho 3 du an: Orion, Nimbus va Atlas.
Anh Nam se phu trach tong hop backlog cho Orion truoc ngay 18/05.
Chi Linh can gui ban draft KPI moi cho khoi Sales va CS truoc 20/05.
Ban Huy va ban Trang phoi hop voi doi Data de xac nhan schema tracking event truoc 17:00 ngay 16/05.

Danh sach deadline quan trong:
1) 15/05: Chot budget marketing thang 6 (owner: Minh, cc: Lan, Duy).
2) 16/05: Chot pham vi MVP cho Atlas (owner: Hieu, support: Quynh).
3) 18/05: Hoan tat tai lieu onboarding noi bo cho du an Nimbus (owner: Phuong, review: Nam).
4) 21/05: Demo noi bo cho ban dieu hanh (owner: Linh, presenter: Khoa).

Rui ro hien tai:
- Thieu 2 backend dev cho module billing.
- Data quality o funnel checkout chua on dinh.
- Tai lieu phap ly cho hop dong doi tac XYZ chua duoc legal xac nhan.

Nho moi nguoi cap nhat tien do moi ngay luc 5:30 PM tren dashboard, va ping truc tiep cho toi neu co blocker.

Cam on,
Tuan
""".strip(),
    },
    {
        "label": "Email rac (Spam)",
        "content": """
CHUC MUNG!!! Ban da trung 1 iPhone 20 Pro Max va voucher du lich tri gia 100,000,000 VND!!!
Nhan ngay uu dai doc quyen trong 24h, click vao link: http://free-reward-now.example
Khuyen mai dac biet, giam 99% toi nay, co hoi cuoi cung, dung bo lo!!!
""".strip(),
    },
    {
        "label": "Email ngan/than mat",
        "content": "Chao ban, toi chi muon hoi hom nay ban co ranh cafe khong?",
    },
    {
        "label": "Email loi",
        "content": "asdjklqwe 123123 ### ??? zzz@@@ $$$ \\\\ //// ....",
    },
]


def run_sample_tests() -> None:
    """
    Chay bo mau email theo cung luong xu ly cua ung dung chinh de ta review.
    """
    api_key = load_api_key()
    client = create_openai_client(api_key=api_key)

    print("=== Bat dau chay bo mau email ===\n")
    for index, sample in enumerate(EMAIL_SAMPLES, start=1):
        print(f"[Mau {index}] {sample['label']}")
        raw_result = summarize_email(email_content=sample["content"], client=client)

        if raw_result is None:
            print("Raw response:")
            print("(Khong nhan duoc phan hoi tu API)")
        else:
            print("Raw response:")
            print(raw_result)

        final_result = (
            process_email_pipeline(email_content=sample["content"], client=client)
            if raw_result is not None
            else default_output()
        )
        print("\nValidated JSON:")
        if print_result_json:
            print_result_json(final_result)
        else:
            print(json.dumps(final_result, ensure_ascii=False, indent=4))
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    run_sample_tests()
