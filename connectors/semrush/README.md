# Semrush connector

Pulls Authority Score, Referring Domains, Organic Keywords, and Organic
Traffic for a list of domains via the Semrush Analytics API, and writes
them to a CSV report.

## Usage

```
SEMRUSH_API_KEY=xxxx python3 semrush_connector.py \
    --domains ../../data/semrush/domains.txt \
    --out ../../reports/semrush_domain_report.csv
```

## Known limitations

- **AI Visibility, Cited Pages, Mentions** are not part of Semrush's core
  Domain/Backlinks Analytics API — they belong to Semrush's separate
  AI/AEO product. These columns are written as `N/A`.
- **Monthly Traffic**: true total-visits data lives under Semrush's
  Traffic Analytics toolkit, which requires a separate plan/API
  entitlement. This connector reports **Organic Traffic** (Semrush's
  estimated organic-search traffic) as the closest available substitute.

`reports/semrush_domain_report.csv` in this repo was generated against
the current domain list using Semrush's live data (via an authenticated
Semrush MCP session, not this standalone script, since no API key was
available in this environment) — the script here reproduces the same
metrics for future runs once a `SEMRUSH_API_KEY` is configured.
