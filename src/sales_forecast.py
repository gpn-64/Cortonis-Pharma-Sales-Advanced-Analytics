"""Monthly sales forecast and simple backtest baselines."""

from __future__ import annotations

import numpy as np
import pandas as pd
from prophet import Prophet


def monthly_sales(transactions: pd.DataFrame, country: str = "Germany") -> pd.DataFrame:
    """Aggregate sales to month and therapeutic class."""

    rows = transactions[transactions["Country"] == country].copy()
    rows["Date"] = pd.to_datetime(rows["Date"])
    rows["ds"] = rows["Date"].dt.to_period("M").dt.to_timestamp()
    return (
        rows.groupby(["ds", "Product Class"], as_index=False)
        .agg(Sales=("Sales", "sum"))
        .rename(columns={"Sales": "y"})
    )


def historical_mean_forecast(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Predict each class with its training-period average."""

    means = train.groupby("Product Class")["y"].mean()
    result = test[["ds", "Product Class", "y"]].copy()
    result["yhat_mean"] = result["Product Class"].map(means)
    return result


def seasonal_naive_forecast(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Predict using the value observed twelve months earlier."""

    lookup = train.set_index(["Product Class", "ds"])["y"]
    result = test[["ds", "Product Class", "y"]].copy()
    result["yhat_naive"] = [
        lookup.get((row["Product Class"], row["ds"] - pd.DateOffset(years=1)), np.nan)
        for _, row in result.iterrows()
    ]
    return result


def prophet_forecast(train: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """Fit one Prophet model per class and forecast future months."""

    forecasts = []
    for product_class, group in train.groupby("Product Class"):
        model = Prophet(yearly_seasonality=True, seasonality_mode="multiplicative", interval_width=0.80)
        model.fit(group[["ds", "y"]].sort_values("ds"))
        future = model.make_future_dataframe(periods=periods, freq="MS")
        forecast = model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        forecast["Product Class"] = product_class
        forecasts.append(forecast)
    return pd.concat(forecasts, ignore_index=True)


def prophet_predict(train: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame:
    """Predict supplied dates from a model trained only on the training data."""

    predictions = []
    for product_class, group in train.groupby("Product Class"):
        model = Prophet(yearly_seasonality=True, seasonality_mode="multiplicative", interval_width=0.80)
        model.fit(group[["ds", "y"]].sort_values("ds"))
        class_dates = dates.loc[dates["Product Class"] == product_class, ["ds"]]
        forecast = model.predict(class_dates)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        forecast["Product Class"] = product_class
        predictions.append(forecast)
    return pd.concat(predictions, ignore_index=True)


def compare_backtest(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Compare Prophet and two simple baselines with MAPE."""

    mean = historical_mean_forecast(train, test)
    naive = seasonal_naive_forecast(train, test)
    prophet = prophet_predict(train, test).rename(columns={"yhat": "yhat_prophet"})
    prophet = test[["ds", "Product Class", "y"]].merge(
        prophet[["ds", "Product Class", "yhat_prophet", "yhat_lower", "yhat_upper"]],
        on=["ds", "Product Class"],
        how="left",
    )
    result = mean.merge(naive, on=["ds", "Product Class", "y"]).merge(
        prophet, on=["ds", "Product Class", "y"]
    )
    for column in ["yhat_mean", "yhat_naive", "yhat_prophet"]:
        result[f"ape_{column}"] = (result["y"] - result[column]).abs() / result["y"].abs()
    return result


def mape_summary(backtest: pd.DataFrame) -> pd.DataFrame:
    """Summarize backtest MAPE by class."""

    return (
        backtest.groupby("Product Class", as_index=False)
        .agg(
            MAPE_mean=("ape_yhat_mean", "mean"),
            MAPE_naive=("ape_yhat_naive", "mean"),
            MAPE_prophet=("ape_yhat_prophet", "mean"),
        )
        .assign(
            MAPE_mean=lambda frame: frame["MAPE_mean"] * 100,
            MAPE_naive=lambda frame: frame["MAPE_naive"] * 100,
            MAPE_prophet=lambda frame: frame["MAPE_prophet"] * 100,
        )
    )
