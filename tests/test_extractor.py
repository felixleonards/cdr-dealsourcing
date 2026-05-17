from scraper.extractor import extract_deal

DEAL_JSON = """{
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
    "zusammenfassung": "Heidelberg Materials kauft 10.000 Tonnen CO2.",
    "zementrelevant": true
}"""

NO_DEAL_JSON = '{"kein_deal": true}'


def test_extract_deal_returns_dict_for_valid_deal(mocker):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = DEAL_JSON
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("scraper.extractor.OpenAI", return_value=mock_client)

    result = extract_deal("Some article text about a CDR deal", "test-api-key")

    assert result is not None
    assert result["kaeufer"] == "Heidelberg Materials"
    assert result["menge_tco2"] == 10000
    assert result["zementrelevant"] is True


def test_extract_deal_returns_none_for_no_deal(mocker):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = NO_DEAL_JSON
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("scraper.extractor.OpenAI", return_value=mock_client)

    result = extract_deal("Unrelated article text", "test-api-key")

    assert result is None


def test_extract_deal_handles_json_wrapped_in_text(mocker):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = f"Here is the data:\n{DEAL_JSON}\nDone."
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("scraper.extractor.OpenAI", return_value=mock_client)

    result = extract_deal("Some article text", "test-api-key")

    assert result is not None
    assert result["kaeufer"] == "Heidelberg Materials"


def test_extract_deal_returns_none_on_invalid_json(mocker):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = "This is not JSON at all."
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("scraper.extractor.OpenAI", return_value=mock_client)

    result = extract_deal("Some article text", "test-api-key")

    assert result is None
