"""Regenerate all Power BI exports from the normalized transaction table."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.customer_segmentation import build_rfm, choose_k, fit_segments, profile_segments
from src.sales_forecast import compare_backtest, mape_summary, monthly_sales, prophet_forecast
from src.territory_analysis import aggregate_regions, build_city_table, classify_territories, top_opportunities


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "transactions_normalized.csv"
OUTPUT = ROOT / "results" / "generated"

# utf-8-sig: the BOM lets Power BI Desktop auto-detect UTF-8 and keeps German /
# Polish characters (ü, ł, ó) intact instead of falling back to Windows-1252.
CSV_ENCODING = "utf-8-sig"


def export(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(OUTPUT / name, index=False, encoding=CSV_ENCODING)


def main() -> None:
    transactions = pd.read_csv(INPUT, parse_dates=["Date"])
    OUTPUT.mkdir(parents=True, exist_ok=True)

    rfm = build_rfm(transactions, "2020-12-01")
    segmented, _, _ = fit_segments(rfm, n_clusters=4)
    export(profile_segments(segmented), "customer_segment_profiles.csv")
    export(segmented, "customer_segments.csv")
    export(choose_k(rfm), "customer_k_selection.csv")

    city = build_city_table(transactions)
    classified, _, _ = classify_territories(city)
    export(classified, "territories_by_city.csv")
    export(aggregate_regions(classified), "territories_by_region.csv")
    export(top_opportunities(classified), "territory_opportunities.csv")

    history = monthly_sales(transactions, country="Germany")
    train = history[history["ds"] < "2020-01-01"]
    test = history[history["ds"] >= "2020-01-01"]
    backtest = compare_backtest(train, test)
    export(history, "monthly_sales_history.csv")
    export(backtest, "sales_forecast_backtest.csv")
    export(mape_summary(backtest), "sales_forecast_metrics.csv")
    export(prophet_forecast(history, periods=12), "sales_forecast_prophet.csv")

    print(f"Generated exports in {OUTPUT}")


if __name__ == "__main__":
    main()
