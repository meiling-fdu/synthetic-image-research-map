#!/usr/bin/env python3
"""Regenerate the public pair canonically, preserving unrelated review queues.

All previous public records must survive exactly; only the approved batch may
be added. The canonical coverage report is refreshed after proving its CSV in
data/manual is unchanged. No affiliation, institution, or geocoding workflow is
needed for this bibliography-only import.
"""
from contextlib import redirect_stdout
import gzip
import io
import json
from pathlib import Path
import tempfile

try:
    from . import export_public_preview as exporter
    from . import audit_key_paper_coverage as coverage
    from .integrate_literature51_2026_10_16 import ROOT, OUT, read, save, sha
    from .public_export_metadata import atomic_write_json_files
except ImportError:
    import export_public_preview as exporter
    import audit_key_paper_coverage as coverage
    from integrate_literature51_2026_10_16 import ROOT, OUT, read, save, sha
    from public_export_metadata import atomic_write_json_files

NAMES = ('public_preview_map_data.json','public_preview_papers.json')


def regenerate():
    out=ROOT/OUT
    plan=read(out/'plan.json')
    expected_ids={p['paper_id'] for p in plan['additions']['papers.csv']}
    before_hashes={name:sha(ROOT/'web/data'/name) for name in NAMES}
    with tempfile.TemporaryDirectory(prefix='literature51-export-') as name:
        stage=Path(name)
        for filename in NAMES:
            (stage/filename).write_bytes((ROOT/'web/data'/filename).read_bytes())
        review=stage/'institution_location_review.csv'
        review.write_bytes((ROOT/'data/curated/institution_location_review.csv').read_bytes())
        output=io.StringIO()
        with redirect_stdout(output):
            status=exporter.main(['--preserve-existing','--output',str(stage/NAMES[0]),
                '--paper-output',str(stage/NAMES[1]),'--location-review',str(review)])
        if status:
            raise RuntimeError(output.getvalue())
        maps,papers=(read(stage/n) for n in NAMES)
        old_maps=read_compressed(out/(NAMES[0]+'.before.gz'))
        old_papers=read_compressed(out/(NAMES[1]+'.before.gz'))
        assert maps['records']==old_maps['records'],'Existing map relationships drifted'
        current={exporter.identity_key(p):p for p in papers['records']}
        for p in old_papers['records']:
            assert current[exporter.identity_key(p)]==p,'Existing public paper changed: '+p['title']
        old_ids={exporter.identity_key(p) for p in old_papers['records']}
        added=[p for p in papers['records'] if exporter.identity_key(p) not in old_ids]
        assert {p.get('paper_id') for p in added}==expected_ids
        assert all(not p['has_map_location'] for p in added)
        atomic_write_json_files({ROOT/'web/data'/NAMES[0]:maps,ROOT/'web/data'/NAMES[1]:papers})
    artifacts,summary,errors=coverage.expected_artifacts()
    assert not errors,errors
    assert (ROOT/coverage.OUT_PATH).read_bytes()==artifacts[coverage.OUT_PATH].encode(), 'Manual CSV must stay unchanged'
    (ROOT/coverage.MARKDOWN_PATH).write_text(artifacts[coverage.MARKDOWN_PATH],encoding='utf-8')
    after_hashes={name:sha(ROOT/'web/data'/name) for name in NAMES}
    result={'canonical_exporter':'scripts/export_public_preview.py --preserve-existing',
            'before_sha256':before_hashes,'after_sha256':after_hashes,
            'byte_stable':before_hashes==after_hashes,'existing_papers_unchanged':len(old_papers['records']),
            'existing_map_relationships_unchanged':len(old_maps['records']),
            'approved_papers_added':len(added),'manual_files_written':0,
            'unrelated_location_queue_written':False,'coverage':summary}
    save(out/'regeneration.json',result)
    print(json.dumps(result,indent=2))
    return result


def read_compressed(path):
    return json.loads(gzip.decompress(path.read_bytes()))


if __name__=='__main__':
    regenerate()
