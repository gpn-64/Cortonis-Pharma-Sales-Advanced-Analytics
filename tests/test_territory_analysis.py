import pandas as pd

from src.territory_analysis import build_city_table, classify_territories


def test_city_monthly_sales_and_quadrant_are_calculated() -> None:
    transactions = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2020-01-01", "2020-02-01"]),
            "City": ["A", "A"], "Country": ["Germany", "Germany"],
            "Region": ["Bayern", "Bayern"], "Population": [1000, 1000],
            "Sales": [100, 300], "Channel": ["Hospital", "Hospital"],
        }
    )
    city = build_city_table(transactions)
    classified, _, _ = classify_territories(pd.concat([city, city.assign(City="B", Population=2000)]))

    assert city.loc[0, "MonthlySales"] == 200
    assert len(classified) == 2
    assert classified["Quadrant"].notna().all()
