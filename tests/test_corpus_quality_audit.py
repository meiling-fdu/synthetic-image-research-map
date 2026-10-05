"""Focused failure-mode tests for the dated, read-only quality audit validator."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.validate_corpus_quality_audit import (
    batch_counts, changed_paths, load_context, load_queues, validate,
)
from scripts.corpus_quality_history import predecessor_root


class CorpusQualityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with predecessor_root() as root:
            cls.context = load_context(root)
        cls.original = load_queues()

    def setUp(self):
        self.queues = copy.deepcopy(self.original)

    def assert_invalid(self, fragment):
        errors = validate(self.queues, self.context)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_complete_audit_reconciles(self):
        self.assertEqual(validate(self.queues, self.context), [])
        self.assertEqual(batch_counts(self.queues), dict(A=20, B=159, C=41, D=1752))

    def test_omitted_unmapped_identity_is_rejected(self):
        self.queues['unmapped_papers']['records'].pop()
        self.assert_invalid('unmapped coverage')

    def test_unknown_paper_identity_is_rejected(self):
        self.queues['relationship_review']['records'][0]['paper_id'] = 'invented:paper'
        self.assert_invalid('invalid paper ID')

    def test_duplicate_review_id_is_rejected(self):
        rows = self.queues['relationship_review']['records']
        rows[1]['review_id'] = rows[0]['review_id']
        self.assert_invalid('duplicate/missing review ID')

    def test_invalid_institution_reference_is_rejected(self):
        self.queues['unmapped_papers']['records'][0]['institutions'][0]['institution_id'] = 'invented:institution'
        self.assert_invalid('invalid institution ID')

    def test_invalid_taxonomy_label_is_rejected(self):
        self.queues['taxonomy_review']['records'][0]['proposed_labels'].append('watermarking')
        self.assert_invalid('invalid labels')

    def test_invalid_status_is_rejected(self):
        self.queues['publication_metadata_review']['formal_records'][0]['status'] = 'COMPLETE_FOR_VENUE'
        self.assert_invalid('invalid publication status')

    def test_taxonomy_current_labels_must_match_registry(self):
        self.queues['taxonomy_review']['records'][0]['current_labels'] = []
        self.assert_invalid('current labels differ from registry')

    def test_duplicate_taxonomy_dimension_is_rejected(self):
        rows = self.queues['taxonomy_review']['records']
        row = copy.deepcopy(rows[0])
        row['review_id'] = 'EXTRA'
        rows.append(row)
        self.assert_invalid('duplicate taxonomy decision')

    def test_publication_upgrade_requires_identity_evidence(self):
        row = next(r for r in self.queues['publication_metadata_review']['nonformal_records']
                   if r['status'] == 'FORMAL_VERSION_FOUND')
        row['formal_version']['identity_evidence'] = ''
        self.assert_invalid('incomplete formal-version identity evidence')

    def test_recoverable_metadata_requires_an_authoritative_source(self):
        row = next(r for r in self.queues['publication_metadata_review']['formal_records']
                   if r['status'] == 'MISSING_RECOVERABLE_METADATA')
        row['authoritative_source'] = ''
        self.assert_invalid('incomplete recoverable metadata evidence')

    def test_schema_extension_is_rejected(self):
        self.queues['publication_metadata_review']['formal_records'][0]['proposed_changes']['pages'] = '1–10'
        self.assert_invalid('unsupported schema remediation')

    def test_frozen_identity_cannot_be_actionable(self):
        row = next(r for r in self.queues['publication_metadata_review']['nonformal_records']
                   if r['paper_id'] in self.context['frozen'])
        row['batch'] = 'B'
        self.assert_invalid('frozen actionable identity')

    def test_declared_counts_cannot_drift(self):
        self.queues['publication_metadata_review']['formal_status_counts']['COMPLETE_FOR_CURRENT_SCHEMA'] += 1
        self.assert_invalid('formal status counts do not reconcile')

    def test_missing_and_changed_files_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'kept').write_bytes(b'baseline')
            digest = hashlib.sha256(b'baseline').hexdigest()
            manifest = {'kept':digest, 'removed':digest}
            self.assertEqual(changed_paths(root, manifest), ['removed'])
            (root/'kept').write_bytes(b'changed')
            self.assertEqual(changed_paths(root, manifest), ['kept', 'removed'])


if __name__ == '__main__':
    unittest.main()
