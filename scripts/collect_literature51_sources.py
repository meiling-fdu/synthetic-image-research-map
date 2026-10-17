#!/usr/bin/env python3
"""Inspect/retrieve only the fixed references in the literature51 source manifest.

The default is a cache/hash audit without network access. --fetch-missing
retrieves missing captures; existing responses (including failed attempts) are
never overwritten. No credentials, geocoding, or discovery searches are used.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/literature51_2026_10_16'


def cache_sources(root=ROOT):
    """Read the consolidated manifest; redundant per-URL JSON is not required."""
    return json.loads((root / RAW.relative_to(ROOT) / 'source_manifest.json').read_text())


def optional_retrieval_bodies(root=ROOT):
    """Only reviewed non-evidence challenge/redirect bodies may stay local.

    The URL, response hash and failure classification remain in the committed
    manifests. Required bibliographic/technical captures may never be omitted.
    Existing optional bodies are still hash-checked when present.
    """
    path = root / 'data/processed/literature51_2026_10_16/followup/cache_policy.json'
    if not path.exists():
        return set()
    policy = json.loads(path.read_text())
    manifest = root / RAW.relative_to(ROOT) / 'source_manifest.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != policy['manifest_sha256']:
        raise ValueError('Source manifest differs from the cache-policy review')
    sources = {s.get('raw_path'): s for s in cache_sources(root) if s.get('raw_path')}
    optional = set()
    for item in policy['optional_bodies']:
        source = sources[item['path']]
        if source['sha256'] != item['response_sha256'] or item['reason'] not in {
            'bot_challenge', 'publisher_redirect', 'access_challenge'
        }:
            raise ValueError('Invalid non-evidence cache disposition')
        optional.add(item['path'])
    return optional


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-missing', action='store_true')
    args = parser.parse_args()
    manifest = cache_sources()
    optional = optional_retrieval_bodies()
    summary = {'references':len(manifest),'cached_responses':0,'documented_failures':0,
               'optional_non_evidence_omitted':0,'missing':[]}
    for source in manifest:
        if not source.get('raw_path'):
            summary['documented_failures'] += 1
            continue
        path = ROOT/source['raw_path']
        if path.exists():
            body = gzip.decompress(path.read_bytes())
            if hashlib.sha256(body).hexdigest() != source['sha256']:
                raise ValueError('Cache hash mismatch: '+str(path))
            summary['cached_responses'] += 1
            continue
        if source['raw_path'] in optional:
            summary['optional_non_evidence_omitted'] += 1
            continue
        if args.fetch_missing:
            request = urllib.request.Request(source['url'], headers={'User-Agent':'SyntheticImageResearchMap literature51 public-metadata verification'})
            with urllib.request.urlopen(request,timeout=35) as response:
                body = response.read()
            # Current network content must never impersonate the historical capture.
            if hashlib.sha256(body).hexdigest() != source['sha256']:
                raise ValueError('Source changed since the audited capture: '+source['url'])
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(gzip.compress(body,mtime=0))
        else:
            summary['missing'].append(str(path.relative_to(ROOT)))
    print(json.dumps(summary,indent=2))
    return bool(summary['missing'])


if __name__ == '__main__':
    raise SystemExit(main())
