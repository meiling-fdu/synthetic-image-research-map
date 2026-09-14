#!/usr/bin/env python3
"""Cache named Tier 1 primary sources only; no corpus or manual writes."""
import concurrent.futures
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from prepare_systematic_tier1 import OUT, RAW, ROOT


def fetch(job):
    key = hashlib.sha256(job['url'].encode()).hexdigest()[:20]
    meta = RAW / (key + '.json')
    if meta.exists():
        return {**job, **json.loads(meta.read_text())}
    result = {'url': job['url'], 'retrieved_at': datetime.now(timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(job['url'], headers={'User-Agent': 'SyntheticImageResearchMap-Tier1Curation/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read(60_000_001)
            if len(data) > 60_000_000:
                raise ValueError('Source exceeds 60 MB bound')
            path = RAW / (key + ('.pdf' if data.startswith(b'%PDF') else '.html'))
            path.write_bytes(data)
            result.update(status=response.status, final_url=response.url, raw_path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    except Exception as error:
        result.update(status='ERROR', error=str(error))
    meta.write_text(json.dumps(result, indent=2) + '\n')
    return {**job, **result}


if __name__ == '__main__':
    jobs = json.loads((OUT / 'jobs.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, jobs))
    (OUT / 'sources.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'requests': len(results), 'success': sum(r['status'] == 200 for r in results), 'failures': [r for r in results if r['status'] != 200]}, indent=2))
