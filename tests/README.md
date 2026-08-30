# tests

Tests de contrat de données et de validation analytique.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

| Fichier | Portée |
|---|---|
| `test_data_contract.py` | Validation du schéma canonique (colonnes requises, types, valeurs manquantes) |
| `test_data_contract_excel.py` | Chargement + enrichissement depuis le workbook Excel et ses feuilles de référence |
| `test_territory_analysis.py` | Agrégation ville, régression log-log, quadrants |
| `test_sales_forecast.py` | Ventes mensuelles, baselines, backtest, MAPE |
