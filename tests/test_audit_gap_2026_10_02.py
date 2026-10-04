"""Audit integrity tests: prevent duplicate imports and scope/frozen leakage."""
import copy
import unittest
from unittest.mock import patch

from scripts import audit_gap_2026_10_02 as audit


def proposal():
    return {
        'candidate_id': 'audit-example', 'title': 'Example forensic paper',
        'authors': ['Jane Smith'], 'year': 2026, 'venue': 'Example',
        'doi': '10.1234/example', 'arxiv_id': '2601.12345',
        'official_url': 'https://example.org/paper',
        'status': 'MISSING_HIGH_CONFIDENCE', 'actionable_set': 'A',
        'manual_review': True, 'scope_reason': 'Independent generated-image task.',
        'candidate_tasks': ['detection'], 'candidate_research_types': ['method'],
        'evidence': [{'kind': 'primary', 'url': 'https://example.org/paper',
                      'capture_paths': ['example.json']}],
        'deduplication': {'exact_public': {'doi': [], 'arxiv_id': [], 'title': [], 'paper_id': []}},
    }


def payload(*works):
    counts = {}
    for c in works:
        counts[c['status']] = counts.get(c['status'], 0) + 1
    return {'works': list(works), 'frozen_encounters': [],
            'counting': {'status_counts': counts, 'unique_works_adjudicated': len(works),
                         'frozen_encounters_count': 0}}


class AuditIntegrityTests(unittest.TestCase):
    def test_normalization_and_version_ids(self):
        self.assertEqual(audit.normalize('AI–Generated &amp; Images'), audit.normalize('AI generated and images'))
        self.assertEqual(audit.doi('https://doi.org/10.1234/ABC'), '10.1234/abc')
        self.assertEqual(audit.arxiv('https://arxiv.org/abs/2601.12345v3'), '2601.12345')
        self.assertEqual(audit.author_name({'name': 'Smith, Jane'}), audit.author_name('Jane Smith'))

    def test_acronym_collision_is_not_identity(self):
        papers = [{'paper_id': 'existing', 'title': 'DNA: Dual-stage attribution',
                   'year': 2026, 'authors': [{'name': 'Jane Smith'}]}]
        with patch.object(audit, 'corpus', return_value=papers), patch.object(audit, 'identity_layers', return_value=[]):
            result = audit.compare({'title': 'DNA: Universal forensic knowledge', 'method_name': 'DNA',
                                    'authors': ['Smith, Jane'], 'year': 2026})
        self.assertFalse(any(result['exact_public'].values()))
        self.assertEqual(result['acronym_matches'][0]['paper_id'], 'existing')
        self.assertEqual(result['author_year_matches'][0]['paper_id'], 'existing')

    def test_valid_proposal_remains_unmodified(self):
        p = payload(proposal())
        before = copy.deepcopy(p)
        self.assertEqual(audit.candidate_errors(p), [])
        self.assertEqual(p, before)

    def test_rejects_identifier_and_title_duplicates(self):
        a = proposal()
        b = copy.deepcopy(a)
        b['candidate_id'] = 'another'
        b['doi'] = 'https://doi.org/10.1234/EXAMPLE'
        b['arxiv_id'] += 'v2'
        b['title'] = 'Example forensic paper!'
        errors = audit.candidate_errors(payload(a, b))
        for field in ['doi', 'arxiv_id', 'title']:
            self.assertTrue(any('Duplicate ' + field in e for e in errors))

    def test_rejects_existing_work_as_addition(self):
        c = proposal()
        c['deduplication']['exact_public']['arxiv_id'] = ['existing']
        self.assertTrue(any('matches public corpus' in e for e in audit.candidate_errors(payload(c))))

    def test_requires_primary_evidence_and_decision(self):
        c = proposal()
        c.update(status='MISSING_NEEDS_SCOPE_REVIEW', actionable_set='B')
        c['evidence'][0]['kind'] = 'search_snippet'
        errors = audit.candidate_errors(payload(c))
        self.assertTrue(any('maintainer decision' in e for e in errors))
        self.assertTrue(any('primary evidence' in e for e in errors))

    def test_rejects_frozen_addition_by_id_and_title(self):
        c = proposal()
        c['arxiv_id'] = '2602.02222v2'
        self.assertTrue(any('Frozen work reclassified' in e for e in audit.candidate_errors(payload(c))))
        c['arxiv_id'] = ''
        c['title'] = 'Beyond Real or Fake: A Dual-Channel Authenticity and Reasoning Protocol for Photographic Assessment'
        self.assertTrue(any('Frozen work reclassified' in e for e in audit.candidate_errors(payload(c))))

    def test_requires_count_reconciliation(self):
        p = payload(proposal())
        p['counting']['status_counts']['MISSING_HIGH_CONFIDENCE'] = 2
        self.assertTrue(any('reconciliation' in e for e in audit.candidate_errors(p)))


if __name__ == '__main__':
    unittest.main()
