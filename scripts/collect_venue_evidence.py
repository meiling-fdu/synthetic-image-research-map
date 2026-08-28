#!/usr/bin/env python3
"""Cache publisher-deposited Crossref metadata for unresolved venue/DOI records."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import urllib.parse
import urllib.request
import time
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    from .serve_admin import load_admin_data
    from .venue_audit import VenueAudit, enrich_aliases
    from .venues import read_venue_aliases
except ImportError:
    from serve_admin import load_admin_data
    from venue_audit import VenueAudit, enrich_aliases
    from venues import read_venue_aliases

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/raw/venue_audit_crossref"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doi", action="append", default=[], help="Also cache a verified published-version DOI")
    args = parser.parse_args()
    papers, _ = load_admin_data(apply_venue_audit=False)
    audit = VenueAudit(enrich_aliases(read_venue_aliases()))
    dois = {doi.lower() for doi in args.doi}
    for paper in papers:
        doi = re.sub(r"^https?://(?:dx\.)?doi.org/", "", str(paper.get("doi") or "").lower().strip())
        _, finding = audit.paper(paper)
        if doi.startswith("10.") and not doi.startswith("10.48550/") and (finding or paper.get("publication_type") == "preprint"):
            dois.add(doi)
    CACHE.mkdir(parents=True, exist_ok=True)

    def fetch(doi):
        path = CACHE / (hashlib.sha256(doi.encode()).hexdigest()[:20] + ".json")
        if path.exists():
            return "cached"
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        request = urllib.request.Request(url, headers={"User-Agent": "SyntheticImageResearchMap/venue-audit (local scholarly metadata audit)"})
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            path.write_text(json.dumps({"doi": doi, "source_url": url, "retrieved_on": datetime.now(timezone.utc).date().isoformat(), "response": payload}, ensure_ascii=False, indent=2) + "\n")
            return "fetched"
        except Exception as error:
            print(f"Unverifiable {doi}: {error}", flush=True)
            return "failed"
        finally:
            time.sleep(0.4)  # Respect Crossref's public-pool rate limits.
    from collections import Counter
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        counts = Counter(pool.map(fetch, sorted(dois)))
    print(dict(counts))
    # Preprint publication status is checked separately from venue identity.
    arxiv_ids = sorted({str(p.get("arxiv_id") or "") for p in papers
                        if p.get("publication_type") == "preprint" and p.get("arxiv_id")})
    for offset in range(0, len(arxiv_ids), 40):
        batch = arxiv_ids[offset:offset + 40]
        path = CACHE / ("arxiv-full-" + hashlib.sha256(",".join(batch).encode()).hexdigest()[:16] + ".xml")
        if path.exists():
            continue
        url = "https://export.arxiv.org/api/query?max_results=40&id_list=" + urllib.parse.quote(",".join(batch))
        try:
            with urllib.request.urlopen(url, timeout=35) as response:
                path.write_bytes(response.read())
            print(f"Cached arXiv publication status for {len(batch)} preprints", flush=True)
        except Exception as error:
            print(f"arXiv status unverifiable for {len(batch)} preprints: {error}", flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
