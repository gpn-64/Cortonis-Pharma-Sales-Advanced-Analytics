import pandas as pd
import pytest

from src.data_contract import normalize_transactions, validate_transactions


def valid_transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2020-01-01"],
            "Sales": [100.0],
            "Customer Name": ["Example Customer"],
            "Country": ["Germany"],
            "City": ["Berlin"],
            "Channel": ["Hospital"],
            "SubChannel": ["Government"],
            "Product Class": ["Analgesics"],
        }
    )


def test_valid_transactions_pass_validation() -> None:
    validate_transactions(valid_transactions())


def test_missing_column_is_rejected() -> None:
    transactions = valid_transactions().drop(columns="Sales")

    with pytest.raises(ValueError, match="Sales"):
        validate_transactions(transactions)


def test_negative_sales_are_rejected() -> None:
    transactions = valid_transactions()
    transactions.loc[0, "Sales"] = -1

    validate_transactions(transactions)


def test_raw_csv_is_normalized_to_canonical_columns(tmp_path) -> None:
    source = tmp_path / "transactions.csv"
    pd.DataFrame(
        {
            "Date": ["ignored"],
            "Year": [2018],
            "Month": ["January"],
            "Sales": [-10],
            "Customer Name": ["Example Customer"],
            "Country": ["Poland"],
            "City": ["?"],
            "Channel": ["Pharmacy"],
            "Sub-channel": ["Retail"],
            "Product Class": ["Analgesics"],
            "Population": ["12,345"],
            "Region": ["?"],
        }
    ).to_csv(source, index=False, encoding="cp1252")

    transactions = normalize_transactions(str(source))

    assert transactions.loc[0, "Date"] == pd.Timestamp("2018-01-01")
    assert transactions.loc[0, "SubChannel"] == "Retail"
    assert transactions.loc[0, "Population"] == 12345
    assert pd.isna(transactions.loc[0, "City"])
