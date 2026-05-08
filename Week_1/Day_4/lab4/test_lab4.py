import os
from unittest.mock import mock_open, patch

import pytest

from lab4 import calculate_revenue, read_and_preview_csv


@pytest.fixture(autouse=True)
def isolate_test_environment():
    """Sets up and restores process state to keep each test isolated."""
    original_cwd = os.getcwd()
    original_env = os.environ.copy()
    yield
    os.chdir(original_cwd)
    os.environ.clear()
    os.environ.update(original_env)


@pytest.mark.parametrize(
    ("price", "quantity", "expected"),
    [
        (100_000, 3, 300_000.0),
        (99_999.5, 2, 199_999.0),
        (10_000, 0, 0.0),
        (0, 5, 0.0),
        (0, 0, 0.0),
        (1_000_000_000_000, 1_000_000, 1_000_000_000_000_000_000.0),
    ],
)
def test_calculate_revenue_with_valid_inputs(price, quantity, expected):
    """Verifies revenue is calculated correctly for valid numeric inputs."""
    assert calculate_revenue(price, quantity) == expected


@pytest.mark.parametrize(
    ("price", "quantity"),
    [
        (-1, 2),
        (100_000, -2),
    ],
)
def test_calculate_revenue_with_negative_values_raises_value_error(price, quantity):
    """Ensures negative price or quantity is rejected with ValueError."""
    with pytest.raises(ValueError):
        calculate_revenue(price, quantity)


@pytest.mark.parametrize(
    ("price", "quantity"),
    [
        (None, 2),
        (100_000, None),
    ],
)
def test_calculate_revenue_with_none_values_raises_value_error(price, quantity):
    """Ensures None values are rejected with ValueError."""
    with pytest.raises(ValueError):
        calculate_revenue(price, quantity)


@pytest.mark.parametrize(
    ("price", "quantity", "expected_exception"),
    [
        ([], 2, TypeError),
        (100_000, [], TypeError),
        ({}, 2, TypeError),
        (100_000, {}, TypeError),
        (None, 2, ValueError),
        (100_000, None, ValueError),
        (float("nan"), 2, ValueError),
        (100_000, float("nan"), ValueError),
    ],
)
def test_calculate_revenue_with_empty_or_invalid_values(price, quantity, expected_exception):
    """Checks empty-like and invalid values raise expected exceptions."""
    with pytest.raises(expected_exception):
        calculate_revenue(price, quantity)


@pytest.mark.parametrize(
    ("price", "quantity"),
    [
        ("100000", 2),
        (100_000, "2"),
        (True, 2),
        (2, False),
        ("abc", 3),
    ],
)
def test_calculate_revenue_with_non_numeric_values_raises_type_error(price, quantity):
    """Ensures non-numeric values are rejected with TypeError."""
    with pytest.raises(TypeError):
        calculate_revenue(price, quantity)


@pytest.mark.parametrize(
    ("csv_data", "expected_rows"),
    [
        (
            "Product,Price,Quantity,Category\n"
            'Laptop Dell Inspiron,"18,500,000",3,Electronics\n'
            'Chuot Logitech M331,"350,000",10,Accessories\n',
            2,
        ),
        (
            "Product,Price,Quantity,Category\n"
            'Book Python,"180,000",15,Books\n',
            1,
        ),
    ],
)
def test_read_and_preview_csv_with_mocked_open_returns_dataframe(csv_data, expected_rows):
    """Validates CSV reading from mocked file content without disk access."""
    mocked_open = mock_open(read_data=csv_data)
    with patch("builtins.open", mocked_open):
        df = read_and_preview_csv("data.csv")

    assert df is not None
    assert len(df) == expected_rows
    assert list(df.columns) == ["Product", "Price", "Quantity", "Category"]
    mocked_open.assert_called_once_with("data.csv", mode="r", encoding="utf-8")


@pytest.mark.parametrize("file_path", ["missing.csv", "invalid/path/data.csv"])
def test_read_and_preview_csv_when_file_not_found_returns_none(file_path):
    """Ensures function returns None when mocked open raises FileNotFoundError."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        df = read_and_preview_csv(file_path)

    assert df is None


def test_read_and_preview_csv_with_invalid_csv_returns_none():
    """Ensures invalid CSV input is handled and function returns None."""
    mocked_open = mock_open(read_data='Product,Price,Quantity,Category\n"broken')
    with patch("builtins.open", mocked_open):
        df = read_and_preview_csv("bad.csv")

    assert df is None
