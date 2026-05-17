from notion_client import Client


def _build_properties(deal: dict) -> dict:
    buyer = deal.get("kaeufer") or "?"
    seller = deal.get("verkaeufer") or "?"
    props: dict = {
        "Deal-Name": {"title": [{"text": {"content": f"{buyer} ← {seller}"}}]},
        "Status": {"select": {"name": "Announced"}},
    }

    text_fields = {
        "kaeufer": "Käufer",
        "verkaeufer": "Verkäufer / Projekt",
        "lieferzeitraum": "Lieferzeitraum",
        "standort": "Projektstandort",
        "zusammenfassung": "Zusammenfassung",
    }
    for key, notion_field in text_fields.items():
        if deal.get(key):
            props[notion_field] = {"rich_text": [{"text": {"content": str(deal[key])}}]}

    number_fields = {
        "menge_tco2": "Menge gesamt (tCO2)",
        "menge_pro_jahr_tco2": "Liefermenge pro Jahr (tCO2)",
        "preis_per_ton": "Preis ($/t)",
        "gesamtwert": "Gesamtwert ($)",
    }
    for key, notion_field in number_fields.items():
        if deal.get(key) is not None:
            props[notion_field] = {"number": deal[key]}

    date_fields = {
        "projektstart": "Projektstart / Baustart",
        "deal_datum": "Deal-Datum",
    }
    for key, notion_field in date_fields.items():
        if deal.get(key):
            props[notion_field] = {"date": {"start": deal[key]}}

    if deal.get("cdr_typ"):
        props["CDR-Typ"] = {"select": {"name": deal["cdr_typ"]}}
    if deal.get("quelle"):
        props["Quelle"] = {"url": deal["quelle"]}
    if deal.get("zementrelevant") is not None:
        props["Zementrelevanz"] = {"checkbox": bool(deal["zementrelevant"])}

    return props


def write_deal(deal: dict, database_id: str, notion_token: str) -> None:
    client = Client(auth=notion_token)
    client.pages.create(
        parent={"database_id": database_id},
        properties=_build_properties(deal),
    )
