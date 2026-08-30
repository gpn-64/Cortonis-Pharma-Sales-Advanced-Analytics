# scripts

Scripts d'automatisation exécutables directement (contrairement à [src/](../src/), bibliothèque importable).

| Script | Rôle |
|---|---|
| `prepare_data.py` | Normalise la source brute vers `data/processed/transactions_normalized.csv` |
| `run_pipeline.py` | Exécute les 3 modules et régénère tous les CSV de `results/generated/` pour Power BI |

```powershell
.\.venv\Scripts\python.exe scripts/run_pipeline.py
```

Aucun commit ni push n'est effectué par ces scripts.
