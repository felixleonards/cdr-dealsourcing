import json
import re
from google.oauth2.service_account import Credentials
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADERS = [
    "Deal-Name", "Käufer", "Verkäufer / Projekt", "CDR-Typ",
    "Menge gesamt (tCO2)", "Liefermenge pro Jahr (tCO2)", "Preis ($/t)",
    "Gesamtwert ($)", "Lieferzeitraum", "Projektstandort",
    "Projektstart / Baustart", "Deal-Datum", "Status", "Quelle",
    "Zusammenfassung", "Zementrelevanz",
]


def _normalize_date(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else None
    if not isinstance(value, str) or not value.strip():
        return ""
    value = value.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}', value):
        return value[:10]
    try:
        from dateutil import parser as dp
        return dp.parse(value, dayfirst=False).strftime('%Y-%m-%d')
    except Exception:
        return value


def _get_sheet(credentials_json: str, sheet_id: str):
    creds = Credentials.from_service_account_info(
        json.loads(credentials_json), scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def _ensure_headers(sheet) -> None:
    if not sheet.row_values(1):
        sheet.append_row(HEADERS)


def write_deal(deal: dict, credentials_json: str, sheet_id: str) -> None:
    sheet = _get_sheet(credentials_json, sheet_id)
    _ensure_headers(sheet)
    buyer = deal.get("kaeufer") or "?"
    seller = deal.get("verkaeufer") or "?"
    row = [
        f"{buyer} ← {seller}",
        deal.get("kaeufer") or "",
        deal.get("verkaeufer") or "",
        deal.get("cdr_typ") or "",
        deal.get("menge_tco2") or "",
        deal.get("menge_pro_jahr_tco2") or "",
        deal.get("preis_per_ton") or "",
        deal.get("gesamtwert") or "",
        deal.get("lieferzeitraum") or "",
        deal.get("standort") or "",
        _normalize_date(deal.get("projektstart")),
        _normalize_date(deal.get("deal_datum")),
        "Announced",
        deal.get("quelle") or "",
        deal.get("zusammenfassung") or "",
        "Ja" if deal.get("zementrelevant") else "Nein",
    ]
    sheet.append_row(row)
