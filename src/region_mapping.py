"""Small, explicit mapping from source region labels to canonical regions."""

from __future__ import annotations

import pandas as pd


REGION_REPLACEMENTS = {
    "Lower Saxony": "Niedersachsen",
    "Niedersachsen": "Niedersachsen",
    "Bavaria": "Bayern",
    "Bayern": "Bayern",
    "North Rhine-Westphalia": "Nordrhein-Westfalen",
    "Nordrhein-Westfalen": "Nordrhein-Westfalen",
    "Rhineland-Palatinate": "Rheinland-Pfalz",
    "Rheinland-Pfalz": "Rheinland-Pfalz",
    "Hesse": "Hessen",
    "Hessen": "Hessen",
    "Saxony-Anhalt": "Sachsen-Anhalt",
    "Sachsen-Anhalt": "Sachsen-Anhalt",
    "Saxony": "Sachsen",
    "Thüringen": "Thüringen",
    "Brandenburg": "Brandenburg",
    "Schleswig-Holstein": "Schleswig-Holstein",
    "Mecklenburg-Vorpommern": "Mecklenburg-Vorpommern",
    "Saarland": "Saarland",
    "Berlin": "Berlin",
    "Hamburg": "Hamburg",
    "Bremen": "Bremen",
    "Baden-Württemberg": "Baden-Württemberg",
    "Darmstadt": "Hessen",
    "Cologne": "Nordrhein-Westfalen",
    "Düsseldorf": "Nordrhein-Westfalen",
    "Münster": "Nordrhein-Westfalen",
    "Stuttgart": "Baden-Württemberg",
    "Freiburg": "Baden-Württemberg",
    "Sachsen": "Sachsen",
    "Poland": "Poland",
    "Silesian Voivodeship": "śląskie",
    "Masovian Voivodeship": "mazowieckie",
    "Lower Silesian Voivodeship": "dolnośląskie",
    "Pomeranian Voivodeship": "pomorskie",
    "Lublin Voivodeship": "lubelskie",
    "Kuyavian–Pomeranian Voivodeship": "kujawsko-pomorskie",
    "?ód? Voivodeship": "łódzkie",
    "Subcarpathian Voivodeship": "podkarpackie",
    "West Pomeranian Voivodeship": "zachodniopomorskie",
    "Warmian–Masurian Voivodeship": "warmińsko-mazurskie",
    "Lesser Poland Voivodeship": "małopolskie",
    "Podlaskie Voivodeship": "podlaskie",
    "Lubusz Voivodeship": "lubuskie",
    "Greater Poland Voivodeship": "wielkopolskie",
    "?wi?tokrzyskie Voivodeship": "świętokrzyskie",
    "Świętokrzyskie Voivodeship": "świętokrzyskie",
    "Łódź Voivodeship": "łódzkie",
    "Opole Voivodeship": "opolskie",
    "lubuskie": "lubuskie",
    "pomorskie": "pomorskie",
    "dolno?l?skie": "dolnośląskie",
    "wielkopolskie": "wielkopolskie",
    "warmi?sko-mazurskie": "warmińsko-mazurskie",
    "kujawsko-pomorskie": "kujawsko-pomorskie",
    "ma?opolskie": "małopolskie",
    "opolskie": "opolskie",
    "zachodniopomorskie": "zachodniopomorskie",
    "?l?skie": "śląskie",
    "lubelskie": "lubelskie",
    "świętokrzyskie": "świętokrzyskie",
    "łódzkie": "łódzkie",
    "śląskie": "śląskie",
    "dolnośląskie": "dolnośląskie",
    "warmińsko-mazurskie": "warmińsko-mazurskie",
    "małopolskie": "małopolskie",
}


def add_canonical_region(transactions: pd.DataFrame) -> pd.DataFrame:
    """Add canonical region labels and preserve unresolved rows as missing."""

    result = transactions.copy()
    result["RegionCanonical"] = result["Region"].map(REGION_REPLACEMENTS)
    return result
