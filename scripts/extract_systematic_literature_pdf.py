#!/usr/bin/env python3
"""Reproduce the cached attribution-survey text; requires pypdf, no network."""
import io
import json
from pypdf import PdfReader
from collect_systematic_literature import PROCESSED, read_response


def extract():
    sources = [s for path in sorted(PROCESSED.glob('pass*_sources.json'))
               for s in json.loads(path.read_text()) if s['kind'] == 'survey_pdf']
    assert len(sources) == 1
    reader = PdfReader(io.BytesIO(read_response(sources[0])))
    value = '\n'.join(page.extract_text() for page in reader.pages)
    (PROCESSED / 'attribution_survey_text.txt').write_text(value)
    print(f'Extracted {len(reader.pages)} pages from the cached original PDF.')


if __name__ == '__main__':
    extract()
