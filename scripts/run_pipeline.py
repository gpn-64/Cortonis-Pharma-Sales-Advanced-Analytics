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


def main() -> None:
    transactions = pd.read_csv(INPUT, parse_dates=["Date"])
    OUTPUT.mkdir(parents=True, exist_ok=True)

    rfm = build_rfm(transactions, "2020-12-01")
    segmented, _, _ = fit_segments(rfm, n_clusters=4)
    profile_segments(segmented).to_csv(OUTPUT / "customer_segment_profiles.csv", index=False)
    segmented.to_csv(OUTPUT / "customer_segments.csv", index=False)
    choose_k(rfm).to_csv(OUTPUT / "customer_k_selection.csv", index=False)

    city = build_city_table(transactions)
    classified, _, _ = classify_territories(city)
    classified.to_csv(OUTPUT / "territories_by_city.csv", index=False)
    aggregate_regions(classified).to_csv(OUTPUT / "territories_by_region.csv", index=False)
    top_opportunities(classified).to_csv(OUTPUT / "territory_opportunities.csv", index=False)

    history = monthly_sales(transactions, country="Germany")
    train = history[history["ds"] < "2020-01-01"]
    test = history[history["ds"] >= "2020-01-01"]
    backtest = compare_backtest(train, test)
    history.to_csv(OUTPUT / "monthly_sales_history.csv", index=False)
    backtest.to_csv(OUTPUT / "sales_forecast_backtest.csv", index=False)
    mape_summary(backtest).to_csv(OUTPUT / "sales_forecast_metrics.csv", index=False)
    prophet_forecast(history, periods=12).to_csv(OUTPUT / "sales_forecast_prophet.csv", index=False)

    print(f"Generated exports in {OUTPUT}")


if __name__ == "__main__":
    main()
