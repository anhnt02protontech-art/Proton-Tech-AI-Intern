from pathlib import Path
import argparse
from numbers import Real

import pandas as pd


def read_and_preview_csv(file_path: str) -> pd.DataFrame | None:
    """Reads a CSV file and prints the first five rows.

    Args:
        file_path: Path to the CSV file.

    Returns:
        The loaded DataFrame if reading succeeds; otherwise, None.
    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as csv_file:
            df = pd.read_csv(csv_file)
        print("5 dong dau tien cua du lieu:")
        print(df.head(5))
        return df
    except FileNotFoundError:
        print(f"Khong tim thay file: {file_path}")
        return None
    except Exception as error:
        print(f"Co loi xay ra khi doc file CSV: {error}")
        return None


def _format_number_like_csv(value: float) -> str:
    """Formats a numeric value with thousand separators like in data.csv.

    Args:
        value: Numeric value to format.

    Returns:
        A string representation with comma-separated thousands.
    """
    return f"{value:,.0f}"


def _print_table(title: str, table: pd.DataFrame) -> None:
    """Prints a DataFrame as a simple console table with a title.

    Args:
        title: Table title printed above the data.
        table: DataFrame content to display.
    """
    print(f"\n{title}")
    print("-" * len(title))
    print(table.to_string(index=False))


def calculate_revenue(price: float, quantity: float) -> float:
    """Calculates revenue from price and quantity.

    Args:
        price: Unit price.
        quantity: Sold quantity.

    Returns:
        Revenue value computed as price * quantity.
    """
    if price is None or quantity is None:
        raise ValueError("price and quantity must not be None")

    if isinstance(price, bool) or isinstance(quantity, bool):
        raise TypeError("price and quantity must be numeric values")

    if not isinstance(price, Real) or not isinstance(quantity, Real):
        raise TypeError("price and quantity must be numeric values")

    if pd.isna(price) or pd.isna(quantity):
        raise ValueError("price and quantity must not be NaN")

    if price < 0 or quantity < 0:
        raise ValueError("price and quantity must be non-negative")

    return float(price * quantity)


def process_sales_data(df: pd.DataFrame) -> None:
    """Processes sales data for filtering and revenue statistics.

    Steps:
        - Validates required columns.
        - Converts price and quantity to numeric types.
        - Filters products where price is greater than 5,000,000.
        - Computes total revenue grouped by category.
        - Prints formatted tables to the console.

    Args:
        df: Input DataFrame with Product, Price, Quantity, and Category columns.
    """
    required_columns = {"Product", "Price", "Quantity", "Category"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        print(f"Thieu cot bat buoc: {', '.join(sorted(missing_columns))}")
        return

    working_df = df.copy()
    working_df["Price"] = (
        working_df["Price"].astype(str).str.replace(",", "", regex=False).astype(float)
    )
    working_df["Quantity"] = pd.to_numeric(working_df["Quantity"], errors="coerce")
    working_df = working_df.dropna(subset=["Price", "Quantity"])

    filtered_df = working_df.loc[
        working_df["Price"] > 5_000_000, ["Product", "Price", "Quantity", "Category"]
    ].copy()
    filtered_df["Price"] = filtered_df["Price"].map(_format_number_like_csv)

    working_df["Revenue"] = working_df.apply(
        lambda row: calculate_revenue(row["Price"], row["Quantity"]), axis=1
    )
    revenue_by_category = (
        working_df.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    revenue_by_category["Revenue"] = revenue_by_category["Revenue"].map(
        _format_number_like_csv
    )

    _print_table("San pham co Price > 5,000,000", filtered_df)
    _print_table("Tong doanh thu theo Category", revenue_by_category)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read sales CSV, filter products, and summarize revenue by category."
    )
    parser.add_argument(
        "--file",
        dest="file_path",
        default=str(Path(__file__).with_name("data.csv")),
        help="Path to CSV file. Default: data.csv in the same folder as lab4.py",
    )
    args = parser.parse_args()

    csv_path = Path(args.file_path)
    data = read_and_preview_csv(str(csv_path))
    if data is not None:
        process_sales_data(data)
