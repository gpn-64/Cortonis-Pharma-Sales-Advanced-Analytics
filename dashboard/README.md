# dashboard

Livrable de dashboard final. Cette couche analytique alimente un rapport **Power BI** ;
le dossier `tableau/` du template n'est pas utilisé ici.

- `powerbi/` — projet Power BI au format **PBIP** (structure texte JSON/TMDL, versionnable). Voir [powerbi/README.md](powerbi/README.md).
- `assets/` — ressources runtime importées dans le rapport (fonds de page, icônes, logo).

## Relation avec le Projet 1

Le rapport historique vit dans
[Cortonis-Pharma-Sales-Dashboard](https://github.com/gpn64/Cortonis-Pharma-Sales-Dashboard).
Ce dossier accueille la version PBIP qui consomme en plus les tables générées par cette
couche analytique (`results/generated/*.csv` : segments client, quadrants territoire,
prévisions par classe thérapeutique).

## assets/

- `backgrounds/` — PNG utilisés comme fond de page Power BI. Les sources éditables (`.pptx`, `.fig`) vont dans `backgrounds/source/`.
- `icons/` — icônes custom (KPI, navigation).
- `logo/` — logo(s) du projet.
