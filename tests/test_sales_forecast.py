import pandas as pd

from src.sales_forecast import historical_mean_forecast, monthly_sales, seasonal_naive_forecast


def test_monthly_sales_and_baselines() -> None:
    transactions = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2019-01-01", "2020-01-01", "2020-02-01"]),
            "Country": ["Germany"] * 3,
            "Product Class": ["Analgesics"] * 3,
            "Sales": [100, 200, 300],
        }
    )
    history = monthly_sales(transactions)
    train = history.iloc[:1]
    test = history.iloc[1:]

    assert len(history) == 3
    assert historical_mean_forecast(train, test).loc[1, "yhat_mean"] == 100
    assert seasonal_naive_forecast(train, test).loc[1, "yhat_naive"] == 100
