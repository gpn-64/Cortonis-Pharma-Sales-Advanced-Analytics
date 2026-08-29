# Layout de dashboard — Cortonis Pharma Advanced Analytics

## Contexte

Ce repo (`Cortonis-Pharma-Sales-Advanced-Analytics`) est la suite du dashboard Power BI existant (`Cortonis-Pharma-Sales-Dashboard`, Project 1), qui couvre le reporting classique (quoi, par canal, par produit, par période). Ici, trois modules Python répondent à des questions que le reporting ne peut pas trancher seul :

1. **Segmentation clients** (RFM + K-Means, 4 segments)
2. **Sous-performance territoriale** (potentiel démographique vs. ventes réelles, 4 quadrants)
3. **Prévision des ventes** par classe thérapeutique (Prophet — résultat négatif assumé)

D'après le README, ces outputs sont pensés pour être **injectés dans le Power BI existant** (colonnes Segment/Quadrant/Forecast rattachées à la table de transactions), pas pour un dashboard séparé. Le layout proposé ci-dessous suit donc cette logique : 3 nouvelles pages qui s'ajoutent au dashboard Project 1, plus une page de garde. Chaque page a un objectif narratif clair, pas juste une liste de graphiques — avec les nuances déjà identifiées dans le README (biais Pologne/Allemagne, R²=0.02, forecast qui ne bat pas la moyenne) explicitement mises en scène plutôt que cachées.

Filtres globaux communs à toutes les pages : `Country`, `Channel`/`SubChannel`, `Product Class`, plage de dates.

---

## Page 0 — Vue d'ensemble & note de méthode

**Histoire :** avant les KPIs, poser le cadre : 254k lignes, Allemagne + Pologne, 2017-2020, et surtout le biais structurel (Allemagne = 4 ans pleins, Pologne = 2018 seulement). Cette page sert de "disclaimer actif" que les pages suivantes référencent, pas une page qu'on ignore.

- **Bandeau KPI** : CA total, nb clients actifs, nb villes couvertes, CA par pays
- **Card texte/annotation** : encadré "Pologne = 1 an, Allemagne = 4 ans — lire les comparatifs pays avec prudence" (repris visuellement sur les pages 2 et 3 par un tag sur les visuels concernés)
- **Courbe CA mensuel** (ligne, par pays en couleur) — montre visuellement l'asymétrie de fenêtre temporelle plutôt que de l'expliquer seulement en texte
- **Treemap ou barres** CA par Channel / SubChannel / Product Class (vue reporting de rappel, reprise du Project 1)

---

## Page 1 — Segmentation clients (RFM + K-Means)

**Histoire :** qui sont nos clients et lesquels méritent un traitement différencié — avec la nuance que "Dormant" ne veut pas dire "mauvais client", ça veut souvent dire "vu sur une fenêtre plus courte (Pologne)".

- **4 cards KPI** en tête, une par segment (Key Accounts, Core Active, Dormant-High Potential, Dormant-Low Value) : nb clients, % clients, % CA — repris du tableau README
- **Scatter plot** Frequency (log) × Monetary (log), couleur = Segment, taille = point — le visuel "carte d'identité" des 4 clusters
- **Barres empilées 100%** : répartition Segment × Country — rend visible que Dormant ≈ Pologne mécaniquement
- **Barres comparatives** : Monthly Revenue Rate par segment (la métrique qui neutralise le biais de fenêtre) à côté du CA total par segment (la métrique brute) — juxtaposition volontaire pour montrer que le classement change
- **Table/drill-through** client : Segment, Recency, Frequency, Monetary, Monthly Rate, Country — pour l'équipe commerciale
- **Annotation** sur le scatter : pourquoi k=4 (silhouette 0.43, k=2 trop grossier bien que plus "propre" à 0.87)

---

## Page 2 — Territoires : potentiel vs. performance

**Histoire :** où sont les opportunités géographiques réelles — et où la donnée ne permet pas de conclure (R²=0.02, prudence sur Berlin/Hambourg/Brême à faible échantillon).

- **Carte choroplèthe** (GeoJSON régions DE/PL, `RegionCanonical`) : CA mensuel ou Residual par région
- **Scatter log-log** Population × Monthly Sales, avec la droite de régression, couleur = Quadrant (Underserved / Strong Market / Efficient Niche / Low Priority) — le graphique central de la page, avec R²=0.02 affiché explicitement en annotation (pas caché)
- **4 cards Quadrant** : nb villes, CA agrégé par quadrant
- **Table "Top opportunités"** (Quadrant = Sous-exploité) triée par Residual : City, Country, Region, Population, MonthlySales, Channel — avec Varsovie en tête, mise en avant comme call-out narratif ("plus grande ville du dataset, l'une des plus sous-performantes relativement à sa taille")
- **Alerte/annotation** sur les villes à faible échantillon (Berlin, Hambourg, Brême : 1-2 clients vs. population en millions) — badge "échantillon faible" directement sur la carte/scatter, pas en footnote
- **Cross-check** : les villes allemandes sous-performantes (Düsseldorf, Leipzig, Essen) croisées avec le Segment de la Page 1 → ce sont des Core Active, donc opportunité de cross-sell et non de prospection — un petit visuel de correspondance (table ou icônes) qui relie les deux pages

---

## Page 3 — Prévision des ventes (résultat honnête)

**Histoire :** cette page ne vend pas un forecast qui marche — elle montre pourquoi Prophet perd contre la simple moyenne historique, et ce qu'on utilise à la place pour le target-setting. Allemagne uniquement (Pologne = 12 mois, insuffisant).

- **Bandeau texte en haut de page** (pas en bas) : "La prévision Prophet ne bat pas la moyenne historique sur ce dataset — voir le backtest ci-dessous" — assumé dès l'entrée, cohérence avec le README
- **Courbe** CA mensuel réel par classe thérapeutique + bande d'intervalle Prophet (yhat_lower/yhat_upper) superposée — visuel qui montre visuellement l'absence de saisonnalité/tendance exploitable
- **Barres groupées MAPE** par classe thérapeutique × méthode (Prophet / naive m-12 / moyenne historique) — le graphique clé : montre que la moyenne historique gagne sur les 6 classes
- **Cards** : moyenne historique ± écart-type par classe (la métrique recommandée pour le target-setting, mise en avant visuellement plus que le forecast Prophet lui-même)
- **Note méthodo repliable** : backtest 2017-19→2020 et 2017-18→2019, ACF proche de zéro, auto-ARIMA qui converge vers (0,0,0) sur 5 classes/6

---

## Cohérence transverse

- Un même code couleur Segment (Page 1) et Quadrant (Page 2) réutilisé partout où ils apparaissent en croisement, pour que l'œil relie les pages sans relire les légendes.
- Le tag "échantillon/fenêtre limité(e)" (Pologne, ou villes à 1-2 clients) est un badge visuel standard réutilisé sur Page 0, 1, 2 — pas juste du texte one-off par page.
- Chaque page a un seul message central mis en évidence visuellement (le scatter Page 1, le scatter log-log Page 2, les barres MAPE Page 3) — les autres visuels sont support, pas au même niveau hiérarchique.

## Prochaine étape

Ce document est une proposition de contenu/layout, pas une implémentation Power BI. Étapes suivantes possibles :
- construire un prototype (maquette) pour visualiser l'agencement avant de le reporter dans Power BI ;
- ajuster les champs exacts par visuel une fois les tables `results/generated/` régénérées par `scripts/run_pipeline.py`.
