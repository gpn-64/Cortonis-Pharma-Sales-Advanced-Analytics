# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository aligned with the [BI-Repository-Template](https://github.com/gpn-64/BI-Repository-Template): `LICENSE` (MIT), `CHANGELOG.md`, `.gitattributes`, `docs/data-dictionary.md`, `docs/methodology.md`, `reports/screenshots/`, and per-folder `README.md` stubs.
- `dashboard/` scaffold (`powerbi/` PBIP + `assets/`) ready to receive the Power BI project.
- Status and license badges in `README.md`.

### Changed
- `scripts/run_pipeline.py` writes the Power BI exports as UTF-8 with BOM (`utf-8-sig`) so Power BI Desktop auto-detects the encoding and keeps `ü` / `ł` / `ó` in city and region names.

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- 

## [1.0.0] - 2026-08-24

### Added
- Module 1 — customer segmentation (RFM + K-Means), `src/customer_segmentation.py`, notebook `01_customer_segmentation.ipynb`.
- Module 2 — territory underperformance analysis (log-log regression, quadrants), `src/territory_analysis.py`, notebook `02_territory_underperformance.ipynb`.
- Module 3 — sales forecast by therapeutic class (Prophet + baselines, backtested), `src/sales_forecast.py`, notebook `03_sales_forecast.ipynb`.
- Canonical data contract and loader (`src/data_contract.py`), region mapping (`src/region_mapping.py`).
- Reproducible pipeline: `scripts/prepare_data.py`, `scripts/run_pipeline.py`, CSV exports in `results/generated/` for Power BI.
- Data-contract and analytical validation tests under `tests/`.
