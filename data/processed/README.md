# Données préparées

Les tables normalisées et enrichies générées par les notebooks ou scripts sont produites ici.

Les fichiers sont régénérables et ne doivent pas être traités comme la source de vérité.

La source principale est la feuille `Data` du classeur Excel original. La préparation est générée avec :

```powershell
python scripts/prepare_data.py "data/raw/Pharm Data.xlsx" "data/processed/transactions_normalized.csv"
```

Le CSV reste disponible comme source de comparaison et est encodé en `cp1252`.
Le classeur Excel répare plusieurs noms de villes et régions. Les feuilles `Demo`
et `Sheet3` sont utilisées comme tables de référence pour compléter les
populations et régions manquantes lorsqu'une correspondance `City` ou
`Country + City` est disponible. Les ventes négatives et doublons sont conservés
et documentés plutôt que corrigés silencieusement.
