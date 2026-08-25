"""City performance versus population potential."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.region_mapping import add_canonical_region


QUADRANTS = {
    (True, True): "Marche fort / bien couvert",
    (True, False): "Sous-exploite (opportunite)",
    (False, True): "Niche efficace",
    (False, False): "Priorite faible",
}


def build_city_table(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales and population to city level."""

    rows = add_canonical_region(transactions)
    rows["MonthPeriod"] = pd.to_datetime(rows["Date"]).dt.to_period("M")
    city = (
        rows.groupby(["City", "Country"], dropna=False)
        .agg(
            RegionCanonical=("RegionCanonical", "first"),
            Population=("Population", "first"),
            Sales=("Sales", "sum"),
            ActiveMonths=("MonthPeriod", "nunique"),
            Channel=("Channel", "first"),
        )
        .reset_index()
    )
    city["MonthlySales"] = city["Sales"] / city["ActiveMonths"]
    return city


def classify_territories(city: pd.DataFrame) -> tuple[pd.DataFrame, LinearRegression, float]:
    """Fit the log-log model and assign four population/performance quadrants."""

    result = city.dropna(subset=["Population", "MonthlySales", "RegionCanonical"]).copy()
    result = result[(result["Population"] > 0) & (result["MonthlySales"] > 0)]
    result["LogPopulation"] = np.log(result["Population"])
    result["LogMonthlySales"] = np.log(result["MonthlySales"])
    model = LinearRegression().fit(result[["LogPopulation"]], result["LogMonthlySales"])
    result["Residual"] = result["LogMonthlySales"] - model.predict(result[["LogPopulation"]])
    population_median = result["Population"].median()
    high_population = result["Population"] >= population_median
    result["Quadrant"] = [
        QUADRANTS[(bool(is_high), residual >= 0)]
        for is_high, residual in zip(high_population, result["Residual"])
    ]
    return result.drop(columns=["LogPopulation", "LogMonthlySales"]), model, population_median


def aggregate_regions(city: pd.DataFrame) -> pd.DataFrame:
    """Aggregate classified cities for regional reporting."""

    return (
        city.groupby(["Country", "RegionCanonical"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Population=("Population", "sum"),
            MonthlySales=("MonthlySales", "sum"),
            NCities=("City", "nunique"),
            AvgResidual=("Residual", "mean"),
        )
        .assign(SalesPerCapitaMonthly=lambda frame: frame["MonthlySales"] / frame["Population"])
    )


def top_opportunities(city: pd.DataFrame) -> pd.DataFrame:
    """Return underexploited cities ordered by the most negative residual."""

    columns = ["City", "Country", "RegionCanonical", "Population", "MonthlySales", "Residual", "Channel"]
    return city.loc[city["Quadrant"] == "Sous-exploite (opportunite)", columns].sort_values("Residual")
