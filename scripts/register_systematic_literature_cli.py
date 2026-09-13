#!/usr/bin/env python3
"""Record saved CLI retrieval provenance; HTTP status is not exposed by this CLI."""
import hashlib
import json
from datetime import datetime, timezone
from collect_systematic_literature import ROOT, RAW, PROCESSED

SAVED = [('hf_papers_supplement_2026_09_12.json', 'AI generated image localization attribution', 30, 3),
         ('hf_detection_validation_pass7.json', 'AI generated image detection', 40, 7)]


def register():
    records = []
    for filename, query, bound, discovery_pass in SAVED:
        path = RAW / filename
        if not path.exists():
            continue
        data = path.read_bytes()
        json.loads(data)
        records.append({'channel': 'A', 'kind': 'hf_search', 'seed': 'Hugging Face bounded paper search',
                        'url': 'https://huggingface.co/papers', 'query': query, 'retrieval_bound': bound,
                        'command': f'hf papers search {query!r} --limit {bound} --format json',
                        'status': 'CLI_SUCCESS', 'http_status': None, 'cli_exit_code': 0,
                        'retrieved_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                        'raw_path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(),
                        'enumeration_level': 'BOUNDED_SEARCH', 'discovery_pass': discovery_pass})
    (PROCESSED / 'hf_sources.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    register()
