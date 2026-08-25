"""Prepare the raw transaction file for the analytical notebooks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_contract import normalize_transactions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to the raw CSV or Excel file")
    parser.add_argument("destination", type=Path, help="Path for the normalized CSV")
    arguments = parser.parse_args()

    transactions = normalize_transactions(str(arguments.source))
    arguments.destination.parent.mkdir(parents=True, exist_ok=True)
    transactions.to_csv(arguments.destination, index=False, encoding="utf-8")
    print(f"Wrote {len(transactions):,} rows to {arguments.destination}")


if __name__ == "__main__":
    main()
