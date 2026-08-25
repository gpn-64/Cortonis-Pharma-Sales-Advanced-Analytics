# Notebooks

The reproducible analyses are organized as follows:

1. `01_customer_segmentation.ipynb`: RFM segmentation + K-Means
2. `02_territory_underperformance.ipynb`: city and regional performance
3. `03_sales_forecast.ipynb`: backtesting and forecasting

Each notebook loads the prepared data, calls functions from `src/`, displays quality checks and exports the tables consumed by Power BI.

To regenerate all exports with one command:

```powershell
.\.venv\Scripts\python.exe scripts/run_pipeline.py
```
