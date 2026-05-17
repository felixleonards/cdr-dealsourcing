# CDR Deal Sourcing Tool

Automatically sources CDR deals relevant to the cement industry and writes them to a Notion database. Runs daily via GitHub Actions at 07:00 UTC. Total cost: $0.

## Setup

### 1. Create the Notion Database

1. In Notion, create a new full-page database
2. Add these properties with exact names and types:

| Property | Type | Options |
|---|---|---|
| Deal-Name | Title | — |
| Käufer | Text | — |
| Verkäufer / Projekt | Text | — |
| CDR-Typ | Select | Biochar, DAC, BECCS, Mineralisierung, Sonstige |
| Menge gesamt (tCO2) | Number | — |
| Liefermenge pro Jahr (tCO2) | Number | — |
| Preis ($/t) | Number | — |
| Gesamtwert ($) | Number | — |
| Lieferzeitraum | Text | — |
| Projektstandort | Text | — |
| Projektstart / Baustart | Date | — |
| Deal-Datum | Date | — |
| Status | Select | Announced, Signed, Delivered |
| Quelle | URL | — |
| Zusammenfassung | Text | — |
| Zementrelevanz | Checkbox | — |

3. Copy the database ID from the URL: `notion.so/<DATABASE_ID>?v=...`
4. Go to [notion.so/my-integrations](https://notion.so/my-integrations) → New integration → copy the token (starts with `secret_`)
5. Open your database → ··· → Connections → connect your integration

### 2. Get NVIDIA NIM API Key

1. Log in at [build.nvidia.com](https://build.nvidia.com)
2. Profile → API Keys → Generate Key

### 3. Add GitHub Secrets

In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret

Add these three secrets:
- `NVIDIA_API_KEY` — your NVIDIA NIM key
- `NOTION_API_KEY` — your Notion integration token
- `NOTION_DATABASE_ID` — your Notion database ID

### 4. Push to GitHub and Enable Actions

Before pushing, make sure `seen_urls.json` exists in the repo root with content `[]`:
```bash
echo '[]' > seen_urls.json
git add seen_urls.json
git commit -m "chore: initialize seen_urls"
```

```bash
git remote add origin https://github.com/YOUR_USERNAME/cdr-dealsourcing.git
git branch -M main
git push -u origin main
```

The scraper runs daily. Trigger manually: GitHub → Actions → CDR Deal Scraper → Run workflow.

## Running Locally

```bash
export NVIDIA_API_KEY=your-key
export NOTION_API_KEY=secret_your-token
export NOTION_DATABASE_ID=your-db-id
python -m scraper.main
```

## Running Tests

```bash
pytest -v
```
