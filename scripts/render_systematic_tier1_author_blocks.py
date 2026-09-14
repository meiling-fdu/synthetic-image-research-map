#!/usr/bin/env python3
"""Render primary author blocks, with page numbers, for explicit visual review."""
import json
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from prepare_systematic_tier1 import OUT, ROOT

if __name__ == '__main__':
    entries = json.loads((OUT / 'pdf_index.json').read_text())
    entries = [e for e in entries if not (e['candidate_id'] == 'audit:d7a0be175acdedc4' and 'arxiv' in e['url'])]
    tiles = []
    for e in entries:
        page = 1 if e['candidate_id'] in {'audit:08beb6425ead6689', 'audit:745a864cbd6a6efc'} else 0
        doc = pdfium.PdfDocument(ROOT / e['raw_path'])
        im = doc[page].render(scale=1.8).to_pil().convert('RGB')
        im = im.crop((0, 0, im.width, min(im.height, 570)))
        tile = Image.new('RGB', (1100, 610), 'white')
        tile.paste(im, (0, 35))
        ImageDraw.Draw(tile).text((10, 10), e['candidate_id'] + f' / PDF page {page+1}', fill='black')
        tiles.append(tile)
    for i in range(0, len(tiles), 4):
        canvas = Image.new('RGB', (2200, 1220), 'white')
        for j, tile in enumerate(tiles[i:i+4]):
            canvas.paste(tile, ((j % 2)*1100, (j // 2)*610))
        canvas.save(OUT / 'pdf_review' / f'author_blocks_{i//4+1}.png')
    for key, pages in [('08beb6425ead6689', [1]), ('d7a0be175acdedc4', [8, 9])]:
        e = next(e for e in entries if e['candidate_id'] == 'audit:' + key)
        doc = pdfium.PdfDocument(ROOT / e['raw_path'])
        for page in pages:
            doc[page].render(scale=1.7).to_pil().save(OUT / 'pdf_review' / f'{key}_affiliations_page{page+1}.png')
