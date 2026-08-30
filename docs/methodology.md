# Méthodologie

## Sources de données

| Source | Propriétaire | Fiabilité |
|---|---|---|
| Foresight — *Pharmaceutical Manufacturing Company's Wholesale-Retail Data* | Jeu de données public de practice (portfolio) | Suffisante pour un exercice ; couverture temporelle inégale entre pays |

- Fichier : `data/raw/Pharm Data.xlsx`, feuille `Data`. Feuilles `Demo` (populations) et `Sheet3` (mapping `Country + City → Region`) utilisées comme références.
- **Limite structurante :** l'Allemagne couvre 2017–2020 (4 ans), la Pologne seulement 2018. Ce déséquilibre affecte les trois modules et est signalé à chaque endroit où il compte.

## Pipeline

Ce projet est une **couche analytique Python** ; il n'y a pas de couche SQL (`sql/` du template
sans objet) — le code Power Query M vit dans le modèle sémantique (TMDL) sous
`dashboard/powerbi/`. Le rapport historique reste hébergé dans le
[Projet 1](https://github.com/gpn64/Cortonis-Pharma-Sales-Dashboard) ; `dashboard/powerbi/`
accueille la version PBIP qui consomme en plus les sorties de cette couche.

1. **Extraction / normalisation** (`src/data_contract.py`) : lecture de la feuille `Data`, renommage `Sub-channel → SubChannel`, construction de `Date`, conversion numérique de `Sales` et `Population`, enrichissement population/région via les feuilles de référence, validation du contrat.
   ```powershell
   .\.venv\Scripts\python.exe scripts/prepare_data.py "data/raw/Pharm Data.xlsx" "data/processed/transactions_normalized.csv"
   ```
2. **Transformation / analyse** (`src/`, notebooks `notebooks/`) : un module par question métier.
3. **Vues finales** : tables plates exportées en CSV dans `results/generated/`.
   ```powershell
   .\.venv\Scripts\python.exe scripts/run_pipeline.py
   ```
4. **Chargement dashboard** : les CSV sont importés dans le rapport Power BI du Projet 1. Aucun commit/push n'est effectué par les scripts.

## Définitions des KPI

| KPI | Formule | Source |
|---|---|---|
| Recency | Mois entre la dernière commande et la fin de la fenêtre d'observation | Module 1 |
| Frequency | Nombre de lignes de transaction du client | Module 1 |
| Monetary | Somme de `Sales` du client | Module 1 |
| MonthlyRevenueRate | `Monetary / ActiveMonths` | Modules 1 & 2 |
| Residual (territoire) | `ln(MonthlySales) − prédiction` d'une régression OLS `ln(Population) → ln(MonthlySales)` | Module 2 |
| MAPE | `mean(|réel − prédit| / |réel|)` sur la fenêtre de backtest | Module 3 |

## Méthodes par module

- **Module 1 — Segmentation :** table RFM au niveau client, `log1p` sur F et M, standardisation, K-Means. `k=4` retenu au silhouette (k=2 plus net à 0,87 mais sépare seulement actif/dormant). Labels assignés *après* clustering (les numéros de cluster ne sont pas stables). Contrôle : re-clustering Allemagne seule → même découpe à deux niveaux.
- **Module 2 — Territoires :** territoire = ville. Performance = ventes mensuelles. Potentiel = population (seul proxy disponible). Régression log-log, résidu + médiane de population → 4 quadrants. Mapping manuel des régions vers 16 Bundesländer / 16 voïvodies (`src/region_mapping.py`, 99,86 % des lignes).
- **Module 3 — Prévision :** ventes mensuelles par classe thérapeutique, Allemagne seule. Backtest (train 2017–2019, test 2020) de Prophet contre deux baselines (saisonnier naïf m-12, moyenne historique). Second backtest (train 2017–2018, test 2019) pour contrôle.

## Hypothèses et limites

- Fenêtres d'observation inégales DE/PL : les segments « dormants » du Module 1 correspondent surtout au segment Pologne, pas à un churn documenté.
- La population explique peu la performance territoriale (R² ≈ 0,02) : les quadrants du Module 2 sont un point de départ de priorisation, à valider avec l'équipe terrain, pas une preuve de sous-couverture.
- Environ 1 client par ville dans ce jeu de données : le Module 2 ne sépare pas « mauvaise couverture » de « ce client achète peu ».
- Module 3 est un **résultat négatif assumé** : aucune tendance ni saisonnalité exploitable à ce niveau d'agrégation ; la moyenne historique ± écart-type sert de référence pour la fixation d'objectifs. Prophet reste exploratoire.
- Villes-États (Berlin, Hambourg, Brême) : 1–2 clients pour des populations en millions → ratios par habitant non comparables.
- Les workbooks Excel à la racine du repo sont des références historiques, pas des sorties de production.

## Historique des changements

| Date | Changement | Auteur |
|---|---|---|
| 2026-08-24 | Création initiale (3 modules, pipeline reproductible) | GPien |
| 2026-08-29 | Mise aux normes du template BI (docs, LICENSE, CHANGELOG, .gitattributes) | GPien |
