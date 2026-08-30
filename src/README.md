# src

Code applicatif réutilisable importé par les scripts et les notebooks. Pas de code d'exploration ponctuelle ici — voir [notebooks/](../notebooks/).

| Module | Rôle |
|---|---|
| `data_contract.py` | Contrat de schéma canonique + loader (`normalize_transactions`, `validate_transactions`) |
| `region_mapping.py` | Mapping manuel des régions source vers les 16 Bundesländer / 16 voïvodies |
| `customer_segmentation.py` | Module 1 — RFM, choix de `k`, K-Means, profils de segments |
| `territory_analysis.py` | Module 2 — agrégation ville, régression log-log, quadrants, opportunités |
| `sales_forecast.py` | Module 3 — ventes mensuelles, baselines, Prophet, backtest, MAPE |
