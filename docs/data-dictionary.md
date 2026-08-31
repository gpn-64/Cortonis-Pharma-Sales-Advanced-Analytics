# Dictionnaire de données

Décrit chaque table produite par le pipeline et consommée par Power BI (Projet 1).
Toutes les tables sont générées dans `results/generated/` par `scripts/run_pipeline.py`.

## Source

| | |
|---|---|
| **Origine** | Foresight — *Pharmaceutical Manufacturing Company's Wholesale-Retail Data* ([lien](https://foresightbi.com.ng/practice-data/3-datasets-for-your-portfolio/)) |
| **Fichier local** | `data/raw/Pharm Data.xlsx`, feuille `Data` (feuilles `Demo` et `Sheet3` utilisées comme tables de référence) |
| **Volumétrie** | ~254 000 lignes de transaction, Allemagne + Pologne, 2017–2020 (Pologne : 2018 uniquement) |
| **Clé client** | `Customer Name` (unique par ville) — et non `Distributor` |

## Table canonique : `transactions_normalized` (`data/processed/`)

- **Grain :** une ligne par transaction source (mois × client × produit × canal).
- **Contrat :** `src/data_contract.py` (`REQUIRED_TRANSACTION_COLUMNS`).

| Colonne | Type | Description | Règle métier / calcul |
|---|---|---|---|
| `Date` | DATE | Premier jour du mois de la transaction | Construite depuis `Year` + `Month` (jour = 1) |
| `Sales` | FLOAT | Montant des ventes | Numérique ; valeurs négatives conservées et documentées |
| `Customer Name` | STRING | Nom du client (clé métier) | Non nul |
| `Country` | STRING | `Germany` / `Poland` | Non nul |
| `Channel` | STRING | Canal (`Hospital`, `Pharmacy`, …) | Non nul |
| `SubChannel` | STRING | Sous-canal | Renommé depuis `Sub-channel` |
| `Product Class` | STRING | Classe thérapeutique | Non nul |
| `City` | STRING | Ville du client | `?` → valeur manquante |
| `Region` | STRING | Région source | `?` → manquante ; complétée via `Sheet3` |
| `Population` | FLOAT | Population de la ville | Séparateurs de milliers retirés ; complétée via `Demo` |

## Table : `customer_segments` (Module 1) — 751 lignes

- **Grain :** une ligne par client (`Customer Name`).

| Colonne | Type | Description |
|---|---|---|
| `Customer Name` | STRING | Clé client |
| `Country` | STRING | Pays |
| `City` | STRING | Ville du client |
| `Channel` | STRING | Canal dominant |
| `SubChannel` | STRING | Sous-canal dominant |
| `Frequency` | INT | Nombre de lignes de transaction |
| `Monetary` | FLOAT | Ventes totales |
| `ActiveMonths` | INT | Nombre de mois actifs |
| `Recency` | INT | Mois depuis la dernière commande |
| `MonthlyOrderRate` | FLOAT | `Frequency / ActiveMonths` |
| `MonthlyRevenueRate` | FLOAT | `Monetary / ActiveMonths` (comparaison équitable DE/PL) |
| `AvgOrderValue` | FLOAT | `Monetary / Frequency` |
| `Cluster` | INT | Numéro de cluster K-Means (non stable entre exécutions) |
| `IsActive` | BOOL | Actif vs dormant (médiane de recency) |
| `Status` | STRING | `Active` / `Dormant` |
| `Segment` | STRING | `Key Accounts`, `Core Active`, `Dormant - High Potential (Win-back)`, `Dormant - Low Value` |

## Table : `customer_segment_profiles` (Module 1) — 4 lignes

- **Grain :** une ligne par segment.
- **Colonnes :** `IsActive`, `Status`, `Segment`, `n` (nb clients), `Recency`, `Frequency`, `Monetary`, `MonthlyRevenueRate`, `ActiveMonths` (moyennes), `SharePctCustomers`, `SharePctRevenue`.

## Table : `customer_k_selection` (Module 1) — 7 lignes

- **Grain :** une ligne par `k` testé (2 à 8). Colonnes : `k`, `silhouette`. Justifie le choix `k=4`.

## Table : `territories_by_city` (Module 2) — 598 lignes

- **Grain :** une ligne par ville.

| Colonne | Type | Description |
|---|---|---|
| `City` | STRING | Ville |
| `Country` | STRING | Pays |
| `RegionCanonical` | STRING | Région canonique (16 Bundesländer / 16 voïvodies) |
| `Population` | FLOAT | Population (proxy de potentiel de marché, limité) |
| `Sales` | FLOAT | Ventes totales de la ville |
| `ActiveMonths` | INT | Nombre de mois actifs |
| `Channel` | STRING | Canal dominant |
| `MonthlySales` | FLOAT | `Sales / ActiveMonths` |
| `Residual` | FLOAT | Résidu de la régression log-log population→ventes (R² ≈ 0,02) |
| `Quadrant` | STRING | `Underserved (opportunity)`, `Strong & well covered`, `Efficient niche`, `Low priority` |

## Table : `territories_by_region` (Module 2) — 32 lignes

- **Grain :** une ligne par région canonique.
- **Colonnes :** `Country`, `RegionCanonical`, `Sales`, `Population`, `MonthlySales`, `NCities`, `AvgResidual`, `SalesPerCapitaMonthly`.

## Table : `territory_opportunities` (Module 2) — 157 lignes

- **Grain :** une ligne par ville prioritaire (résidus négatifs).
- **Colonnes :** `City`, `Country`, `RegionCanonical`, `Population`, `MonthlySales`, `Residual`, `Channel`.

## Table : `monthly_sales_history` (Module 3) — 288 lignes

- **Grain :** une ligne par mois × classe thérapeutique (Allemagne uniquement). Colonnes : `ds` (mois), `Product Class`, `y` (ventes).

## Table : `sales_forecast_prophet` (Module 3) — 360 lignes

- **Grain :** une ligne par mois × classe, historique ajusté + 12 mois projetés. Colonnes : `ds`, `yhat`, `yhat_lower`, `yhat_upper` (intervalle 80 %), `Product Class`.

## Table : `sales_forecast_backtest` (Module 3) — 72 lignes

- **Grain :** une ligne par mois de test 2020 × classe (format large).
- **Colonnes :** `ds`, `Product Class`, `y` (réel), `yhat_mean`, `yhat_naive`, `yhat_prophet`, `yhat_lower`, `yhat_upper`, `ape_yhat_mean`, `ape_yhat_naive`, `ape_yhat_prophet` (erreurs absolues relatives).

## Table : `sales_forecast_metrics` (Module 3) — 6 lignes

- **Grain :** une ligne par classe. Colonnes : `Product Class`, `MAPE_mean`, `MAPE_naive`, `MAPE_prophet` (backtest 2020, en %). `MAPE_mean` est le plus bas sur les 6 classes.
