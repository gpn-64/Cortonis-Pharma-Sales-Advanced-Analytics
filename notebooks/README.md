# Notebooks

Les analyses reproductibles sont organisées ainsi :

1. `01_customer_segmentation.ipynb` : segmentation RFM + K-Means
2. `02_territory_underperformance.ipynb` : performance ville/région
3. `03_sales_forecast.ipynb` : backtest et prévision

Chaque notebook devra charger les données préparées, appeler les fonctions de `src/`, afficher les contrôles qualité et exporter les tables consommées par Power BI.

Pour régénérer tous les exports en une seule commande :

```powershell
.\.venv\Scripts\python.exe scripts/run_pipeline.py
```
