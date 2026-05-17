from scraper.notion_writer import write_deal, _build_properties


def test_build_properties_creates_title():
    props = _build_properties({"kaeufer": "Heidelberg Materials", "verkaeufer": "CarbonCure"})
    assert props["Deal-Name"]["title"][0]["text"]["content"] == "Heidelberg Materials ← CarbonCure"


def test_build_properties_handles_missing_buyer():
    props = _build_properties({"kaeufer": None, "verkaeufer": "CarbonCure"})
    assert props["Deal-Name"]["title"][0]["text"]["content"] == "? ← CarbonCure"


def test_build_properties_skips_null_number_fields():
    props = _build_properties({"kaeufer": "A", "verkaeufer": "B", "menge_tco2": None, "preis_per_ton": 200})
    assert "Menge gesamt (tCO2)" not in props
    assert props["Preis ($/t)"]["number"] == 200


def test_build_properties_sets_liefermenge_pro_jahr():
    props = _build_properties({"kaeufer": "A", "verkaeufer": "B", "menge_pro_jahr_tco2": 2000})
    assert props["Liefermenge pro Jahr (tCO2)"]["number"] == 2000


def test_build_properties_sets_checkbox():
    props = _build_properties({"kaeufer": "A", "verkaeufer": "B", "zementrelevant": True})
    assert props["Zementrelevanz"]["checkbox"] is True


def test_build_properties_sets_select_cdr_typ():
    props = _build_properties({"kaeufer": "A", "verkaeufer": "B", "cdr_typ": "Biochar"})
    assert props["CDR-Typ"]["select"]["name"] == "Biochar"


def test_build_properties_sets_url():
    props = _build_properties({"kaeufer": "A", "verkaeufer": "B", "quelle": "https://example.com/article"})
    assert props["Quelle"]["url"] == "https://example.com/article"


def test_write_deal_calls_notion_api(mocker):
    mock_client = mocker.MagicMock()
    mocker.patch("scraper.notion_writer.Client", return_value=mock_client)

    deal = {
        "kaeufer": "Heidelberg Materials",
        "verkaeufer": "CarbonCure",
        "cdr_typ": "Mineralisierung",
        "menge_tco2": 10000,
        "menge_pro_jahr_tco2": 2000,
        "preis_per_ton": 200,
        "gesamtwert": 2000000,
        "lieferzeitraum": "2025-2030",
        "standort": "Norwegen",
        "projektstart": "2024-01-01",
        "deal_datum": "2024-03-15",
        "quelle": "https://example.com",
        "zusammenfassung": "Ein CDR-Deal.",
        "zementrelevant": True,
    }

    write_deal(deal, "db-id-123", "notion-token-xyz")

    mock_client.pages.create.assert_called_once()
    call_kwargs = mock_client.pages.create.call_args[1]
    assert call_kwargs["parent"] == {"database_id": "db-id-123"}
