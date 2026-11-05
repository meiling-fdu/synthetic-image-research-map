"""Exact B5-03 outputs and current state, independent of historical test views."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTOR = 'tests/fixtures/batch_b_b5_03_endpoint.json'
DESCRIPTOR_SHA256 = 'afb2c96bb9084a9b180d8076eb1c0ca07c56338cd16fb40b91edc40bc4226be0'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticated_descriptor(root=ROOT, read=None):
    assert (DESCRIPTOR, DESCRIPTOR_SHA256) == (
        'tests/fixtures/batch_b_b5_03_endpoint.json', 'afb2c96bb9084a9b180d8076eb1c0ca07c56338cd16fb40b91edc40bc4226be0'), 'Unreviewed B5-03 authorization metadata'
    read = read or (lambda path: (root / path).read_bytes())
    raw = read(DESCRIPTOR)
    assert sha(raw) == DESCRIPTOR_SHA256, 'Unreviewed B5-03 endpoint'
    value = json.loads(raw)
    assert value['baseline'] == '2932b9a5b58a8c84761e381668925a765ca9719e'
    assert value['source_manifest'] == '82e6592d020b69bb85341ffe7a495d5beab2b0673e3f8757ff5f0c900ec14b89'
    return value


def authorized_integration_paths(root=ROOT, read=None):
    read = read or (lambda path: (root / path).read_bytes())
    value = authenticated_descriptor(root, read)
    for group in ['producers', 'inputs', 'outputs', 'payload_sha256', 'replacements']:
        assert all(sha(read(path)) == digest for path, digest in value[group].items()), 'Changed B5-03 ' + group
    from scripts.audit_key_paper_coverage import expected_artifacts
    artifacts, _, errors = expected_artifacts(root)
    assert not errors
    assert {str(p): sha(text.encode()) for p, text in artifacts.items()} == {
        p: value['outputs'][p] for p in ['docs/key_paper_coverage_report.md', 'data/manual/key_paper_coverage_report.csv']
    }, 'Noncanonical B5-03 report generation'
    # A finite set of five original paths has independently reviewed successor
    # bytes. Every other original path keeps its immutable published hash.
    return {**value['replacements'], **value['payload_sha256']}, tuple(value['additions'])


def unique_match(index, record):
    matches = index.matches(record)
    assert len(matches) == 1, 'Ambiguous or missing canonical identity'
    return matches[0]


def verify_public_projection(root=ROOT, read=None):
    from tests import b4_04_state as live
    from tests import b5_02_historical_fixtures as history
    from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
    from scripts.paper_taxonomy_registry import public_taxonomy_fields
    from scripts.validate_corpus_quality_audit import load_context
    read = read or (lambda path: (root / path).read_bytes())
    paper_path, map_path = 'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json'
    old_p, old_m = [json.loads(history.endpoint_bytes(p, root)) for p in [paper_path, map_path]]
    new_p, new_m = [json.loads(read(p)) for p in [paper_path, map_path]]
    papers, maps = old_p['records'], old_m['records']
    index = PaperIdentityIndex(papers, PaperIdentityCache())
    assert len(papers) == 674 and len(maps) == len({r['id'] for r in maps}) == 1410
    # The canonical matcher first proves identity uniqueness. Positions are used
    # only to address the already authenticated source objects, never as identity.
    assert all(unique_match(index, row) is row for row in papers)
    context = load_context(root)
    manifest = live.manifest(root)
    approved = {}
    for record in manifest['records']:
        if record['accepted']:
            match = unique_match(index, context['papers'][record['paper_id']])
            position = index.positions[id(match)]
            assert position not in approved
            approved[position] = public_taxonomy_fields(record['binding']['expected_after_state']['taxonomy'])
    assert len(approved) == 8
    marker_positions = {r['id']: index.positions[id(unique_match(index, r))] for r in maps}
    expected_p = [{**row, **approved.get(i, {})} for i, row in enumerate(papers)]
    expected_m = [{**row, **approved.get(marker_positions[row['id']], {})} for row in maps]
    assert new_p['records'] == expected_p and new_m['records'] == expected_m, 'Unauthorized public record projection'
    for old, new in [(old_p, new_p), (old_m, new_m)]:
        expected = deepcopy(old)
        expected['records'] = new['records']
        expected['metadata']['public_preview_generated_at'] = new['metadata']['public_preview_generated_at']
        assert expected == new, 'Unrelated public metadata changed'
    assert new_p['metadata']['public_preview_generated_at'] == new_m['metadata']['public_preview_generated_at']
    missing = [i for i, row in enumerate(papers) if 'paper_id' not in row]
    assert len(missing) == 164
    assert missing == [i for i, row in enumerate(new_p['records']) if 'paper_id' not in row]
    assert context['counts'] == manifest['public_invariants']
    assert Counter(x for row in new_p['records'] for x in row['research_types']) == manifest['taxonomy_after']['research_types']
    assert Counter(x for row in new_p['records'] for x in row['tasks']) == manifest['taxonomy_after']['tasks']
    result = {'paper_records': len(papers), 'map_records': len(maps),
              'changed_papers': sum(a != b for a, b in zip(papers, new_p['records'])),
              'changed_markers': sum(a != b for a, b in zip(maps, new_m['records'])),
              'missing_optional_paper_id': len(missing)}
    assert result['changed_papers'] == 8 and result['changed_markers'] == 23
    return result
