# Debug Journal - Lab4

## 1) NameError: `pd` is not defined
- Symptom:
  - `NameError: name 'pd' is not defined` khi khai bao type hint `pd.DataFrame`.
- Root cause:
  - Thieu dong `import pandas as pd` trong file Python.
- AI fix:
  - Them `import pandas as pd` o dau file.
  - Chay lai `py_compile` de xac nhan het loi.

## 2) KeyError: `'Prices'`
- Symptom:
  - `KeyError: 'Prices'` khi xu ly DataFrame.
- Root cause:
  - CSV co cot `Price`, nhung code tham chieu nham `Prices`.
- AI fix:
  - Doi tat ca `working_df["Prices"]` thanh `working_df["Price"]`.
  - Kiem tra lai dieu kien loc va cong thuc tinh doanh thu.

## 3) Unicode output error tren Windows terminal
- Symptom:
  - Loi encode `charmap` khi in du lieu co ky tu tieng Viet.
- Root cause:
  - Encoding cua stdout trong terminal khong phu hop voi Unicode.
- AI fix:
  - Them:
    - `if hasattr(sys.stdout, "reconfigure"):`
    - `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
  - Chay lai script, output hien thi on dinh.

## 4) Thieu thu vien runtime/test
- Symptom:
  - `ModuleNotFoundError: No module named 'pandas'`
  - `No module named pytest` / khong dung duoc `--cov`
- Root cause:
  - Moi truong `.venv` chua cai du dependencies.
- AI fix:
  - Cai dat:
    - `pip install -r requirements.txt`
    - `pip install pytest pytest-cov coverage`
  - Chay lai test thanh cong.

## 5) Coverage report "No data to report"
- Symptom:
  - `CoverageWarning: No data was collected`.
- Root cause:
  - Dung sai target trong `--cov` (dua duong dan file thay vi module name).
- AI fix:
  - Chay test tu thu muc `lab4` va dung `--cov=lab4`.
  - Tao duoc report terminal + HTML (`htmlcov`).

## 6) Unit test co lap I/O (khong dung file that)
- Symptom:
  - Can test ham doc CSV ma khong tao file that.
- Root cause:
  - Ham doc file ban dau goi truc tiep theo path, chua toi uu cho mock.
- AI fix:
  - Chinh ham `read_and_preview_csv` dung `open(...)` + `pd.read_csv(file_obj)`.
  - Viet test voi `unittest.mock.mock_open` + `patch("builtins.open", ...)`.
  - Bo test da chay duoc ma khong phu thuoc filesystem.

## 7) Rule validation cho `calculate_revenue`
- Symptom:
  - Can xu ly du lieu loi (None, NaN, bool, string, list, dict, so am).
- Root cause:
  - Ham ban dau chi nhan va nhan truc tiep, chua co guard rails.
- AI fix:
  - Them validation:
    - `None/NaN` -> `ValueError`
    - sai kieu (`str`, `bool`, `list`, `dict`) -> `TypeError`
    - gia tri am -> `ValueError`
  - Bo sung test `@pytest.mark.parametrize` cho edge cases + invalid data.
