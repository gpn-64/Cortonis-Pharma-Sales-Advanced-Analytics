# 💊 Cortonis Pharma - Advanced Analytics Layer

## About

Cortonis Pharma Advanced Analytics is a Python and Power BI portfolio project built on the same pharmaceutical sales dataset as the [Cortonis Pharma Sales Dashboard](https://github.com/gpn64/Cortonis-Pharma-Sales-Dashboard).

The dashboard answers what happened in the business. This project adds an analytical layer to answer three operational questions:

- Which customers should receive the most attention?
- Which cities may deserve a commercial review?
- Which forecasting approach is reliable enough for target-setting?

The project combines customer segmentation, territory analysis and sales forecasting. Each analysis is implemented in Python, documented in a Jupyter notebook and exported as flat tables designed for Power BI.

The goal is not to force a sophisticated model onto the data. The workflow compares alternatives, documents uncertainty and keeps simple baselines when they perform better. This is especially important here because Germany has four years of history while Poland has only one.

## Project Outcomes

- RFM + K-Means segmentation of 751 customers into four actionable groups.
- City-level performance analysis using population as a limited market-potential proxy.
- Backtested therapeutic-class forecasts, including Prophet and simple baselines.
- Reproducible CSV outputs for integration into a Power BI report.

## Context

Follow-up to [Project 1](https://github.com/gpn64/Cortonis-Pharma-Sales-Dashboard) (the Power BI dashboard), same dataset. The dashboard covers reporting - what happened, by channel, by product, by period. This part is three Python modules that dig into the questions a dashboard can describe but not really answer on its own: which customers matter and why, which territories are underperforming, and what next quarter might look like.

- Module 1: customer segmentation (RFM + K-Means)
- Module 2: territory performance vs. potential
- Module 3: sales forecast by therapeutic class

One thing came up while building Module 1 and kept showing up in every module after: Germany has 4 full years of data (2017-2020), Poland only has 2018. It affects each module differently and I've tried to flag it wherever it matters instead of burying it in a footnote.

---

## Data

Foresight's pharma wholesale/retail dataset, same file as Project 1. 254k transaction lines, Germany + Poland, 2017-2020.

I used `Customer Name` (unique per city) as the customer key rather than `Distributor`, since the same customer shows up under several distributors over time - keying on distributor would have split single customers into multiple rows for no good reason.

---

## Module 1 - Customer Segmentation (RFM + K-Means)

Standard RFM table at customer level - Recency, Frequency (order lines), Monetary (total sales) - log-transformed on F and M, standardized, then K-Means. Tried k=2 through 8 and went with k=4 based on silhouette score: k=2 was cleaner (0.87) but only split active vs. dormant, not useful enough for differentiated account management. Past k=5 the silhouette flattens out with no real gain in interpretability.

```python
X = rfm[["Recency", "Frequency", "Monetary"]].copy()
X["Frequency"] = np.log1p(X["Frequency"])
X["Monetary"] = np.log1p(X["Monetary"])
Xs = StandardScaler().fit_transform(X)

km = KMeans(n_clusters=4, n_init=20, random_state=42)
rfm["Cluster"] = km.fit_predict(Xs)
# silhouette ~0.43
```

Segments get their label after the fact (active/dormant from median recency, then ranked by monthly revenue rate within each group) instead of hardcoding a cluster number, since K-Means doesn't guarantee cluster 0 means the same thing every run.

**Poland issue:** recency and tenure turned out to be exactly constant within each country - Germany customers are always "1 month since last order, 48 months active", Poland customers are always "25 months, 12 active". There's no real variance to cluster on there, it's just the data window. So the "dormant" segments here are really "the Poland segment", not a documented churn event. I added a monthly revenue rate (sales / active months) to compare fairly across the two windows, and it turns out the dormant-but-high-value group's monthly rate is close to the core active group - they weren't necessarily worse customers, just observed over a shorter period.

I also reran the clustering on Germany only (frequency/monetary, since recency is meaningless without Poland) to check the segments weren't just an artifact of mixing both countries - got basically the same 2-tier split (263 vs 288 customers), so that part holds up.

| Segment                  | Customers | % of customers | % of revenue | Notes                                  |
| ------------------------ | --------- | -------------- | ------------ | -------------------------------------- |
| Key Accounts             | 211       | 28%            | 48%          | Highest value, weekly/bi-weekly visits |
| Core Active              | 340       | 45%            | 46%          | Monthly visits, cross-sell             |
| Dormant - High Potential | 86        | 11%            | 3%*          | Poland, worth a win-back look          |
| Dormant - Low Value      | 114       | 15%            | 3%           | Low priority, digital only             |

*revenue share is mechanically low here because of the 12-month window, not because these customers were small buyers.*

**Reference:** `Segmentation_Clients_RFM_KMeans.xlsx`

---

## Module 2 - Territory Underperformance

Territory = city here (there are 749 of them, close to 1 customer per city in this dataset). Performance = monthly sales rate again. Potential = city population, which is the only demand proxy available in this data. Fit a log-log regression of population against monthly sales, use the residual + a population median split to bucket cities into 4 quadrants (underserved / strong market / efficient niche / low priority).

```python
X = np.log(city[["Population"]])
y = np.log(city["MonthlySales"])
reg = LinearRegression().fit(X, y)
city["Residual"] = y - reg.predict(X)
# R² = 0.02
```

Worth being upfront about that R²: population barely explains anything here. Makes some sense for B2B pharma - a hospital's order volume probably depends more on the hospital than on the city it's in - but it means these quadrants are a starting point for prioritization, not proof that a city is genuinely underserved. I'd want to sanity-check a few of these with the sales team before acting on them.

Region names in the source file were a mess - mix of English/German/Polish, and mixing county-level and state-level entries in the same column. Built a manual mapping (`region_mapping.py`) to get everything to the 16 German states / 16 Polish voivodeships so it lines up with the GeoJSON boundaries for the map. Covers 99.86% of rows, one city dropped for an unresolvable region label.

Also worth flagging: Berlin, Hamburg and Bremen each have 1-2 customers in the data against populations in the millions, so their per-capita numbers aren't really comparable to regions with more customers - small sample, don't over-read it.

Biggest single opportunity in the scatter: Warsaw, largest city in the dataset and one of the weakest performers relative to its size. A handful of German cities (Düsseldorf, Leipzig, Essen) also show up here, and turn out to be Core Active customers from Module 1 rather than gaps in coverage - so more of a cross-sell opportunity than a new-account one.

**Reference:** `Territory_Underperformance_Analysis.xlsx`

---

## Module 3 - Sales Forecast (Prophet)

Monthly sales by therapeutic class, Germany only - Poland's 12 months isn't enough to fit a seasonal model on (Prophet wants at least 2-3 full years).

Before trusting the forecast I backtested it: trained on 2017-2019, tested on 2020, and compared against two dumb baselines (same month last year, plain historical average).

```python
m = Prophet(yearly_seasonality=True, seasonality_mode="multiplicative", interval_width=0.80)
m.fit(train[["ds", "y"]])
# MAPE, backtest on 2020:
#   Prophet          34-95%
#   naive (m-12)     29-77%
#   historical mean  17-43%   <- best on every class
```

The plain average beat Prophet on all 6 classes. Ran auto-ARIMA too just to double check, and on 5 of 6 classes it picked (0,0,0) - no model, basically converges to predicting the mean by itself. Checked this on a second backtest window (train 2017-18, test 2019) to make sure it wasn't just 2020 being a weird year, and got the same result. ACF is close to zero everywhere, the series is stationary, and the month-to-month pattern doesn't repeat consistently from one year to the next (correlation of monthly profile across 2017/2018/2019 is close to zero).

So: there's no real trend or seasonality to model here at this level of aggregation. My takeaway is to use historical mean +/- standard deviation for target-setting instead of the Prophet output, and if this project moved past a portfolio exercise, the next step would be finding an actual driver of demand (promotions, hospital tender cycles, something) rather than trying harder with the calendar alone.

**Reference:** `Sales_Forecast_Prophet.xlsx`

---

## Notes to self / things I'd do differently with more time

- The Poland/Germany window issue shows up in all three modules in a different shape - I caught it in Module 1 by looking at why recency looked bimodal, then had to go check for it explicitly in 2 and 3. In hindsight I'd check the data coverage by country/segment before building anything.
- Module 2's "territory" is basically 1 customer per city here, so it doesn't fully separate "bad coverage" from "this one client buys less" - would need a dataset with multiple accounts per territory to really test that distinction.
- Module 3 is a negative result and I left it that way rather than forcing a better-looking forecast. Felt more honest than tuning Prophet until the backtest looked nicer.
- Outputs are flat CSV/Excel tables meant to plug back into the Project 1 Power BI file (segment per customer, quadrant per city, forecast + CI per class/month), not a separate dashboard.

---

## Files

| File                                         | Description     |
| -------------------------------------------- | --------------- |
| `Segmentation_Clients_RFM_KMeans.xlsx`     | Module 1 output |
| `Territory_Underperformance_Analysis.xlsx` | Module 2 output |
| `Sales_Forecast_Prophet.xlsx`              | Module 3 output |

The Excel files are historical reference outputs used to understand the analyses and
the Power BI tables. They are not the production pipeline and can be replaced once
the notebooks are rebuilt.

## Repository structure

This repo follows the [BI-Repository-Template](https://github.com/gpn-64/BI-Repository-Template),
adapted for a Python analytics layer: there is **no `sql/` layer** (the Power Query M lives in
the semantic model, TMDL) and the `dashboard/tableau/` folder is unused.

```
Cortonis-Pharma-Sales-Advanced-Analytics/
├── data/
│   ├── raw/              # original source data — kept local, never modified, gitignored
│   └── processed/        # normalized/enriched tables, reproducible — gitignored
├── src/                  # reusable transformations and validation rules
├── scripts/              # prepare_data.py, run_pipeline.py
├── notebooks/            # one notebook per analytical module
├── results/generated/    # CSV outputs consumed by Power BI — gitignored
├── tests/                # data-contract and analytical validation tests
├── dashboard/
│   ├── powerbi/          # Power BI project, PBIP format (JSON/TMDL, versionable)
│   └── assets/           # backgrounds, icons, logo imported into the report
├── docs/                 # data-dictionary.md, methodology.md
├── reports/screenshots/  # captures of the final Power BI report
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Documentation

- [Data dictionary](docs/data-dictionary.md) — every generated table, its grain and columns.
- [Methodology](docs/methodology.md) — sources, pipeline, KPI definitions, assumptions and limits.
- [Changelog](CHANGELOG.md)

## Reproducible pipeline

The first prerequisite is to recover the transaction-level dataset and confirm its
schema against the canonical contract in `src/data_contract.py`.

The current local source is `data/raw/Pharm Data.xlsx`, using its `Data` sheet.
The complete pipeline can be run with:

```powershell
.\.venv\Scripts\python.exe scripts/run_pipeline.py
```

This regenerates the CSV tables in `results/generated/` for Power BI. No commit or
push is performed by the project scripts.

---

## Data Source

Foresight - Pharmaceutical Manufacturing Company's Wholesale-Retail Data: [https://foresightbi.com.ng/practice-data/3-datasets-for-your-portfolio/](https://foresightbi.com.ng/practice-data/3-datasets-for-your-portfolio/)

Part 2 of a two-part project - [Project 1](https://github.com/gpn64/Cortonis-Pharma-Sales-Dashboard) has the Power BI dashboard this builds on.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE).
