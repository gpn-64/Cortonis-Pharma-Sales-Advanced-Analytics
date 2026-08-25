"""Notebook-style script for customer RFM segmentation.

Run from the project root with the workspace virtual environment:
    python notebooks/01_customer_segmentation.py
"""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.customer_segmentation import build_rfm, choose_k, fit_segments, profile_segments


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_normalized.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "generated"


def main() -> None:
    transactions = pd.read_csv(INPUT_PATH, parse_dates=["Date"])
    rfm = build_rfm(transactions, analysis_date="2020-12-01")
    k_scores = choose_k(rfm)
    segmented, _, _ = fit_segments(rfm, n_clusters=4)
    profile = profile_segments(segmented)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    segmented.to_csv(OUTPUT_DIR / "customer_segments.csv", index=False)
    profile.to_csv(OUTPUT_DIR / "customer_segment_profiles.csv", index=False)
    k_scores.to_csv(OUTPUT_DIR / "customer_k_selection.csv", index=False)

    print(f"Customers: {len(segmented):,}")
    print(profile[["Segment", "n", "SharePctRevenue"]].to_string(index=False))


if __name__ == "__main__":
    main()
