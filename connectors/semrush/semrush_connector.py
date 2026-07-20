#!/usr/bin/env python3
"""Semrush connector: pulls per-domain SEO metrics into a CSV report.

Reads a list of hostnames (one per line) and, for each, fetches:
  - Authority Score and Referring Domains (Backlinks Overview)
  - Organic Keywords and Organic Traffic (Domain Overview)

Requires a SEMRUSH_API_KEY environment variable.

Not covered by Semrush's core Analytics API (and left blank in the output):
  - AI Visibility, Cited Pages, Mentions — these belong to Semrush's
    separate AI/AEO (answer-engine-optimization) product, not the
    Domain/Backlinks Analytics toolkits this script calls.
  - True "Monthly Traffic" (total site visits) — that lives under the
    Traffic Analytics toolkit, which requires a separate Semrush plan/API
    entitlement. "Organic Traffic" (estimated organic-search traffic) is
    used as the closest available substitute.

Usage:
    SEMRUSH_API_KEY=xxxx python3 semrush_connector.py \
        --domains ../../data/semrush/domains.txt \
        --out ../../reports/semrush_domain_report.csv
"""
import argparse
import csv
import os
import sys
import time
import urllib.parse
import urllib.request

API_URL = "https://api.semrush.com/"

DOMAIN_RANK_COLUMNS = ["Dn", "Rk", "Or", "Ot", "Oc"]  # domain, rank, organic keywords, organic traffic, organic cost
BACKLINKS_COLUMNS = ["ascore", "total", "domains_num"]  # authority score, total backlinks, referring domains


def api_request(params: dict) -> str:
    url = API_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_semicolon_report(raw: str) -> dict:
    lines = [l for l in raw.strip().splitlines() if l.strip()]
    if len(lines) < 2 or lines[0].startswith("ERROR"):
        return {}
    header = lines[0].split(";")
    values = lines[1].split(";")
    return dict(zip(header, values))


def fetch_domain_overview(domain: str, api_key: str, database: str = "us") -> dict:
    params = {
        "type": "domain_rank",
        "key": api_key,
        "domain": domain,
        "database": database,
        "export_columns": ",".join(DOMAIN_RANK_COLUMNS),
    }
    return parse_semicolon_report(api_request(params))


def fetch_backlinks_overview(domain: str, api_key: str) -> dict:
    params = {
        "type": "backlinks_overview",
        "key": api_key,
        "target": domain,
        "target_type": "domain",
        "export_columns": ",".join(BACKLINKS_COLUMNS),
    }
    return parse_semicolon_report(api_request(params))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domains", required=True, help="Path to a text file of hostnames, one per line")
    parser.add_argument("--out", required=True, help="Path to write the output CSV")
    parser.add_argument("--database", default="us", help="Semrush regional database (default: us)")
    parser.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between API calls")
    args = parser.parse_args()

    api_key = os.environ.get("SEMRUSH_API_KEY")
    if not api_key:
        sys.exit("SEMRUSH_API_KEY environment variable is required")

    with open(args.domains) as f:
        domains = [line.strip() for line in f if line.strip()]

    rows = []
    for domain in domains:
        overview = fetch_domain_overview(domain, api_key, args.database)
        time.sleep(args.sleep)
        backlinks = fetch_backlinks_overview(domain, api_key)
        time.sleep(args.sleep)

        rows.append([
            domain,
            "N/A",  # AI Visibility — not available via this API
            "N/A",  # Cited Pages — not available via this API
            "N/A",  # Mentions — not available via this API
            backlinks.get("ascore", ""),
            overview.get("Ot", ""),  # Organic Traffic, used as Monthly Traffic proxy
            overview.get("Or", ""),  # Organic Keywords
            backlinks.get("domains_num", ""),
        ])
        print(f"fetched {domain}", file=sys.stderr)

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Domain", "AI Visibility", "Cited Pages", "Mentions",
            "Authority Score", "Monthly Traffic (Organic, est.)",
            "Organic Keywords", "Referring Domains",
        ])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
