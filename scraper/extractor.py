import json
import re
from openai import OpenAI

PROMPT = """Extrahiere aus folgendem Text alle CDR-Deal-Informationen.
Gib ein JSON-Objekt zurück mit den Feldern:
kaeufer, verkaeufer, cdr_typ, menge_tco2, menge_pro_jahr_tco2,
preis_per_ton, gesamtwert, lieferzeitraum, standort,
projektstart, deal_datum, zusammenfassung, zementrelevant (true/false).
Wenn ein Feld nicht im Text vorkommt, setze null.
Wenn der Text keinen CDR-Deal beschreibt, gib {{"kein_deal": true}} zurück.
Antworte NUR mit dem JSON-Objekt, ohne weitere Erklärungen.
Text: {text}"""

MODEL = "meta/llama-3.1-70b-instruct"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def extract_deal(text: str, api_key: str) -> dict | None:
    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(text=text[:8000])}],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    data = _parse_json(raw)
    if data is None or not isinstance(data, dict) or data.get("kein_deal"):
        return None
    return data


def _parse_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None
