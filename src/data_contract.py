"""Validation rules for the canonical transaction table."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


REQUIRED_TRANSACTION_COLUMNS = frozenset(
    {
        "Date",
        "Sales",
        "Customer Name",
        "Country",
        "Channel",
        "SubChannel",
        "Product Class",
    }
)

MONTH_NUMBERS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def validate_transactions(
    transactions: pd.DataFrame,
    required_columns: Iterable[str] = REQUIRED_TRANSACTION_COLUMNS,
) -> None:
    """Raise ``ValueError`` when a canonical transaction table is invalid."""

    required = set(required_columns)
    missing = sorted(required.difference(transactions.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if transactions.empty:
        raise ValueError("Transaction table is empty")

    dates = pd.to_datetime(transactions["Date"], errors="coerce")
    if dates.isna().any():
        raise ValueError("Date contains invalid or missing values")

    sales = pd.to_numeric(transactions["Sales"], errors="coerce")
    if sales.isna().any():
        raise ValueError("Sales contains invalid or missing values")
    for column in ("Customer Name", "Country", "Channel", "SubChannel", "Product Class"):
        if transactions[column].isna().any():
            raise ValueError(f"{column} contains missing values")


def normalize_transactions(path: str, sheet_name: str = "Data") -> pd.DataFrame:
    """Load the raw CSV or Excel data and return the canonical table."""

    if path.lower().endswith((".xlsx", ".xls")):
        transactions = pd.read_excel(path, sheet_name=sheet_name)
    else:
        transactions = pd.read_csv(path, encoding="cp1252")
    transactions = transactions.rename(columns={"Sub-channel": "SubChannel"})

    if "SubChannel" not in transactions.columns:
        raise ValueError("Source must contain the 'Sub-channel' column")

    transactions["Date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(transactions["Year"], errors="coerce"),
            "month": transactions["Month"].map(MONTH_NUMBERS),
            "day": 1,
        },
        errors="coerce",
    )
    transactions["Sales"] = pd.to_numeric(transactions["Sales"], errors="coerce")
    transactions["Population"] = pd.to_numeric(
        transactions["Population"].astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    )

    if path.lower().endswith((".xlsx", ".xls")):
        transactions = enrich_excel_reference_tables(path, transactions)

    for column in ("City", "Region"):
        transactions[column] = transactions[column].replace("?", pd.NA)

    validate_transactions(transactions)
    return transactions


def enrich_excel_reference_tables(path: str, transactions: pd.DataFrame) -> pd.DataFrame:
    """Fill missing population and region values from Excel helper sheets."""

    result = transactions.copy()
    demo = pd.read_excel(path, sheet_name="Demo", usecols=["City 1", "Population"])
    demo = demo.rename(columns={"City 1": "City"}).dropna(subset=["City"])
    demo = demo.drop_duplicates("City").set_index("City")
    population_by_city = demo["Population"]
    result["Population"] = result["Population"].fillna(result["City"].map(population_by_city))

    mapping = pd.read_excel(path, sheet_name="Sheet3", usecols=["Country", "City", "Bundesland"])
    mapping = mapping.dropna(subset=["Country", "City", "Bundesland"])
    mapping = mapping.drop_duplicates(["Country", "City"])
    result = result.merge(
        mapping.rename(columns={"Bundesland": "RegionFromReference"}),
        on=["Country", "City"],
        how="left",
    )
    result["Region"] = result["RegionFromReference"].fillna(result["Region"])
    return result.drop(columns="RegionFromReference")
