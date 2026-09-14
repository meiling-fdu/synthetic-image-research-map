#!/usr/bin/env python3
"""Extract cached PDF text and render author-block pages for primary review."""
import json
from pypdf import PdfReader
import pypdfium2 as pdfium
from prepare_systematic_tier1 import OUT, ROOT


def inspect():
    folder = OUT / 'pdf_review'
    folder.mkdir(exist_ok=True)
    result = []
    for source in json.loads((OUT / 'sources.json').read_text()):
        if source.get('status') != 200 or not source.get('raw_path', '').endswith('.pdf'):
            continue
        path = ROOT / source['raw_path']
        key = source['candidate_id'].split(':')[1] + '-' + path.stem
        reader = PdfReader(path)
        pages = [p.extract_text(extraction_mode='layout') for p in reader.pages]
        (folder / (key + '.txt')).write_text('\n\n'.join(f'PAGE {i+1}\n{p}' for i, p in enumerate(pages)))
        doc = pdfium.PdfDocument(path)
        doc[0].render(scale=1.5).to_pil().save(folder / (key + '.png'))
        result.append({**source, 'text_path': str((folder / (key + '.txt')).relative_to(ROOT)), 'page1_image': str((folder / (key + '.png')).relative_to(ROOT)), 'pages': len(pages), 'first_page': pages[0]})
    (OUT / 'pdf_index.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Extracted/rendered {len(result)} primary PDFs.')


if __name__ == '__main__':
    inspect()
