"""Exact remote preservation and negative merge-boundary checks."""
import csv
import io
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import verify_literature51_main_integration as successor

from tests.literature51_published_endpoint import published_literature_endpoint

ROOT = published_literature_endpoint()


def test_remote_plus_reviewed_delta_is_exact():
    result = successor.check(ROOT)
    assert result['counts'] == {'import': 39, 'held': 12}
    assert result['corpus'] == {
        'curated': 535, 'public': 674, 'formal': 557, 'mapped': 613,
        'unmapped': 61, 'relationship_rows': 1410, 'taxonomy_pending': 14,
        'review_decisions': 81,
    }
    assert result['remote_public_objects_unchanged'] == 635
    assert result['remote_map_objects_unchanged'] == 1410


def test_remote_existing_row_cannot_be_replaced_by_the_old_literature_baseline():
    path = 'data/curated/papers.csv'
    actual = successor.baseline_bytes(ROOT, path)
    rows = successor.csv_rows(actual)
    corrected = next(r for r in rows if r['paper_id'] == 'curated:34fdf09ae334914a2723')
    assert corrected['tasks'] == 'source_attribution'
    corrected['tasks'] = 'detection;source_attribution'
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    real = successor.baseline_bytes
    with patch.object(successor, 'baseline_bytes', side_effect=lambda root, relative: stream.getvalue().encode() if relative == path else real(root, relative)):
        with pytest.raises(AssertionError):
            successor.check(ROOT)


def test_missing_new_record_cannot_be_accepted_as_a_deduplication():
    real = successor.expected_csv
    with patch.object(successor, 'expected_csv', side_effect=lambda root, name: successor.baseline_bytes(root, 'data/curated/' + name) if name == 'papers.csv' else real(root, name)):
        with pytest.raises(AssertionError):
            successor.check(ROOT)


def test_exact_taxonomy_contributions_of_the_39_imports():
    from collections import Counter
    import json
    from tests.baseline_expectations import LITERATURE51_TAXONOMY_ADDITIONS
    folder = ROOT/'data/processed/literature51_2026_10_16'
    plan = json.loads((folder/'plan.json').read_text())
    followup = json.loads((folder/'followup/receipt.json').read_text())
    imported = plan['additions']['papers.csv'] + followup['additions']['papers.csv']
    assert len(imported) == 39
    totals = Counter(label for p in imported for key in ('tasks','research_types') for label in p[key].split(';') if label)
    assert totals == LITERATURE51_TAXONOMY_ADDITIONS
