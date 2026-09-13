#!/usr/bin/env python3
"""Bounded, cached public-source retrieval for the audit; no corpus writes."""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/systematic_literature_2026_09'
PROCESSED = ROOT / 'data/processed/systematic_literature_2026_09'


def fetch(job):
    job = {"query": parse_qs(urlsplit(job['url']).query),
           "retrieval_bound": "returned index; completeness requires parser validation",
           "enumeration_level": "BOUNDED_SEARCH", **job}
    key = hashlib.sha256(job['url'].encode()).hexdigest()[:20]
    path = RAW / (key + '.gz')
    meta_path = RAW / (key + '.json')
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get('status') == 200:
            read_response(meta)
        return {**job, **meta, 'cache_hit': True}
    result = {'url': job['url'], 'retrieved_at': datetime.now(timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(job['url'], headers={
            'User-Agent': 'SyntheticImageResearchMap-LiteratureAudit/1.0',
        })
        with urllib.request.urlopen(request, timeout=40) as response:
            data = response.read(30_000_001)
            if len(data) > 30_000_000:
                raise ValueError('Response exceeds bounded 30 MB download')
            result.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type', ''),
                          bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                          raw_path=str(path.relative_to(ROOT)))
        path.write_bytes(gzip.compress(data, mtime=0))
    except Exception as error:
        result.update(status='ERROR', http_status=getattr(error, 'code', None),
                      raw_path='', error=f'{type(error).__name__}: {error}')
    meta_path.write_text(json.dumps(result, indent=2) + '\n')
    return {**job, **result, 'cache_hit': False}


def read_response(entry):
    data = gzip.decompress((ROOT / entry['raw_path']).read_bytes())
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise ValueError('Cached response checksum mismatch: ' + entry['raw_path'])
    return data


def run(jobs, output):
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch, jobs))
    output.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'requests': len(results), 'success': sum(r['status'] == 200 for r in results),
                      'errors': [r for r in results if r['status'] != 200]}, indent=2))
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jobs', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(json.loads((ROOT / args.jobs).read_text()), ROOT / args.output)
