import pandas as pd

from src.data_contract import enrich_excel_reference_tables


def test_excel_reference_tables_fill_missing_values(tmp_path) -> None:
    source = tmp_path / "source.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame(
            {"Customer Name": ["A"], "Country": ["Germany"], "City": ["Berlin"], "Population": [None], "Region": [None]}
        ).to_excel(writer, sheet_name="Data", index=False)
        pd.DataFrame({"City 1": ["Berlin"], "Population": [1000]}).to_excel(writer, sheet_name="Demo", index=False)
        pd.DataFrame({"Country": ["Germany"], "City": ["Berlin"], "Bundesland": ["Berlin"]}).to_excel(writer, sheet_name="Sheet3", index=False)

    data = pd.read_excel(source, sheet_name="Data")
    enriched = enrich_excel_reference_tables(str(source), data)

    assert enriched.loc[0, "Population"] == 1000
    assert enriched.loc[0, "Region"] == "Berlin"