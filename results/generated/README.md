# Generated Results

Tables plates consommées par Power BI, régénérées par `scripts/run_pipeline.py`.
Ne pas éditer à la main. Non versionnées (voir [.gitignore](../../.gitignore)).

**Encodage : UTF-8 avec BOM (`utf-8-sig`)** — Power BI Desktop détecte alors
automatiquement l'UTF-8 et conserve `ü`, `ł`, `ó` dans les noms de villes et
régions. Séparateur `,`, décimale `.`, dates ISO (`YYYY-MM-DD`).

## Import dans Power BI

`Obtenir les données > Texte/CSV`, pointer sur ce dossier (chemin relatif ou
paramètre Power Query). Vérifier `Origine du fichier = 65001: Unicode (UTF-8)`.

| Fichier | Grain | Rôle dashboard |
|---|---|---|
| `customer_segments.csv` | 1 ligne / client (751) | Dimension client enrichie (Segment, RFM, MonthlyRevenueRate) |
| `customer_segment_profiles.csv` | 1 ligne / segment (4) | Table de synthèse des segments |
| `customer_k_selection.csv` | 1 ligne / k testé (2–8) | Justification du choix `k=4` (silhouette) |
| `territories_by_city.csv` | 1 ligne / ville (598) | Dimension ville enrichie (Quadrant, Residual, MonthlySales) |
| `territories_by_region.csv` | 1 ligne / région (32) | Agrégats régionaux pour la carte |
| `territory_opportunities.csv` | 1 ligne / ville prioritaire (157) | Table des opportunités (résidus négatifs) |
| `monthly_sales_history.csv` | 1 ligne / mois × classe (288) | Historique mensuel Allemagne |
| `sales_forecast_prophet.csv` | 1 ligne / mois × classe (360) | Prévision Prophet + intervalle 80 % |
| `sales_forecast_backtest.csv` | 1 ligne / mois test × classe (72) | Comparaison réel / moyenne / naïf / Prophet sur 2020 |
| `sales_forecast_metrics.csv` | 1 ligne / classe (6) | MAPE par méthode — la moyenne historique gagne sur les 6 classes |

Schéma détaillé : [docs/data-dictionary.md](../../docs/data-dictionary.md).

Les trois workbooks Excel à la racine du repo sont des références historiques, hors pipeline.
