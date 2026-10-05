"""Regressions for reviewed identities, scope decisions and source preservation."""
import copy
import hashlib
import json
import unittest
from unittest.mock import patch
from collections import Counter

from scripts import migrate_systematic_gap_2026_10_03 as migration
from scripts import audit_gap_2026_10_02 as audit
from scripts.paper_taxonomy import normalize_tasks, normalize_image_scopes, normalize_research_types
from scripts.corpus_quality_history import predecessor_root


class ApprovedGapMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This suite verifies the completed 17-paper migration at its historical
        # boundary; current Batch A invariants have a separate regression suite.
        root = cls.enterClassContext(predecessor_root())
        cls.enterClassContext(patch.object(migration, 'ROOT', root))
        cls.plan = migration.read(migration.OUT / 'plan.json')
        cls.receipt = migration.read(migration.OUT / 'insertion.json')
        cls.baseline = migration.read(migration.OUT / 'baseline.json')
        cls.public = migration.read(migration.ROOT / 'web/data/public_preview_papers.json')['records']
        cls.by_id = {p['paper_id']: p for p in cls.public if p.get('paper_id')}
        cls.proposals = {p['candidate_id']: p for p in cls.plan['papers']}
        cls.decisions = {d['candidate_id']: d for d in migration.read(migration.OUT / 'maintainer_decisions.json')}

    def paper(self, cid):
        return self.by_id[self.proposals[cid]['paper_id']]

    def test_every_approved_identity_occurs_once(self):
        self.assertEqual(set(self.receipt['paper_ids']), {p['paper_id'] for p in self.plan['papers']})
        counts = Counter(p.get('paper_id') for p in self.public)
        for ident in self.receipt['paper_ids']:
            self.assertEqual(counts[ident], 1, ident)

    def test_global_doi_arxiv_and_normalized_title_uniqueness(self):
        for key, clean in [('doi', audit.doi), ('arxiv_id', audit.arxiv), ('title', audit.normalize)]:
            counts = Counter(clean(p.get(key, '')) for p in self.public if clean(p.get(key, '')))
            self.assertEqual({k: n for k, n in counts.items() if n > 1}, {}, key)

    def test_all_seven_deduplication_checks_are_preserved(self):
        for row in migration.read(migration.OUT / 'live_deduplication.json'):
            self.assertEqual(set(row['checks']['exact_public']), {'doi', 'arxiv_id', 'title', 'paper_id'})
            self.assertIn('acronym_matches', row['checks'])
            self.assertIn('title_similarity_top3', row['checks'])
            self.assertIn('author_year_matches', row['checks'])
            self.assertIn('curated_manual_matches', row['checks'])
            self.assertEqual(row['outcome'], 'ADD_NEW')
            self.assertFalse(any(row['checks']['exact_public'].values()))

    def test_dna_is_not_the_existing_attribution_work(self):
        detection = self.paper('gap-847aa30be0f5')
        attribution = self.by_id['curated:0b6c1b00c1b39838db42']
        self.assertNotEqual(detection['paper_id'], attribution['paper_id'])
        self.assertEqual(detection['arxiv_id'], '2601.22515')
        self.assertEqual(detection['tasks'], ['detection'])
        self.assertIn('source_attribution', attribution['tasks'])

    def test_ra_det_does_not_reuse_rejected_drct_suggestion(self):
        paper = self.paper('gap-923484c8a9ee')
        self.assertEqual(paper['arxiv_id'], '2603.01544')
        self.assertTrue(paper['paper_id'].startswith('curated:'))
        self.assertEqual(paper['authors'][0]['name'], 'Xinchang Wang')
        self.assertFalse(any('drct' in str(paper.get(k, '')).lower() for k in ('paper_id', 'formal_url', 'title')))

    def test_generative_editing_is_in_scope_with_forensic_tasks(self):
        for cid, tasks in [('gap-ae64f73095cc', {'localization'}),
                           ('gap-3d4856c630d6', {'detection', 'source_attribution'})]:
            paper = self.paper(cid)
            self.assertTrue(paper['in_scope'])
            self.assertEqual(set(paper['tasks']), tasks)
            self.assertEqual(paper['image_scopes'], ['generative_editing'])

    def test_adaparse_passive_source_attribution(self):
        paper = self.paper('gap-d5c62e3fe662')
        self.assertEqual(paper['tasks'], ['source_attribution'])
        self.assertEqual(audit.doi(paper['doi']), '10.1109/tifs.2026.3671095')
        tax = next(r for r in migration.rows('paper_taxonomy.csv') if r['paper_id'] == paper['paper_id'])
        self.assertIn('Passive inference', tax['tasks_evidence_excerpt'])
        self.assertIn('no active fingerprint embedding', tax['tasks_evidence_excerpt'])

    def test_challenge_reports_remain_preprints(self):
        for cid in ('gap-244d54f4c08b', 'gap-6f54ea382cde'):
            paper = self.paper(cid)
            self.assertEqual(paper['publication_type'], 'preprint')
            self.assertEqual(paper['venue_id'], 'venue:arxiv')
            self.assertFalse(paper['formal_url'])
            self.assertEqual(paper['research_types'], ['method'])

    def test_prpo_and_medical_taxonomy(self):
        prpo = self.paper('gap-97036bf7d3f3')
        self.assertEqual(set(prpo['research_types']), {'method', 'dataset'})
        self.assertIn('fully_generated', prpo['image_scopes'])
        medical = self.paper('gap-661e383aa4c7')
        self.assertTrue(medical['in_scope'])
        self.assertEqual(set(medical['research_types']), {'benchmark', 'analysis_study'})
        self.assertEqual(medical['tasks'], ['detection'])

    def test_canonical_taxonomy_only(self):
        for paper in self.plan['papers']:
            actual = self.by_id[paper['paper_id']]
            for dim, normalizer in [('tasks', normalize_tasks), ('image_scopes', normalize_image_scopes), ('research_types', normalize_research_types)]:
                self.assertEqual(actual[dim], normalizer(paper[dim].split(';')))

    def test_author_order_and_every_reviewed_affiliation_survive_export(self):
        registry = {r['institution_id']: r for r in migration.rows('institutions.csv')}
        mappings = migration.rows('author_institution_mappings.csv')
        for p in self.plan['papers']:
            actual = self.by_id[p['paper_id']]
            self.assertEqual([a['name'] for a in actual['authors']], p['authors'].split('; '))
            expected = [m for m in self.plan['additions']['author_institution_mappings.csv'] if m['paper_id'] == p['paper_id']]
            public_affs = {a['institution_id']: set(a['authors']) for a in actual['author_institution_affiliations']}
            for m in expected:
                self.assertEqual(registry[m['institution_id']]['institution_status'], 'active')
                self.assertIn(m, mappings)
                self.assertEqual(public_affs[m['institution_id']], set(m['institution_authors'].split('; ')))

    def test_missing_medical_affiliations_stay_unresolved(self):
        paper = self.paper('gap-661e383aa4c7')
        self.assertNotIn('Kitty K. Wong', [a['name'] for a in paper['authors']])
        self.assertEqual(len(paper['authors']), 10)
        self.assertFalse(paper['has_map_location'])
        for author in paper['authors']:
            self.assertEqual(author['affiliation_status'], 'unresolved')
            self.assertEqual(author['affiliation_review']['status'], 'unresolved')

    def test_non_adds_absent_and_temporary_holds_not_excluded(self):
        public_titles = {audit.normalize(p['title']) for p in self.public}
        exclusions = {audit.normalize(p['title']) for p in migration.rows('paper_exclusions.csv') if p['is_active'] == 'true'}
        for decision in self.decisions.values():
            if decision['decision'] == 'APPROVE_ADD':
                continue
            title = audit.normalize(decision['title'])
            self.assertNotIn(title, public_titles)
            if decision['decision'] == 'EXCLUDE_OUT_OF_SCOPE':
                self.assertIn(title, exclusions)
            else:
                self.assertNotIn(title, exclusions)
        empirical = self.decisions['gap-d59604897b0c']
        self.assertEqual(empirical['decision'], 'AMBIGUOUS_IDENTITY')
        self.assertTrue(any('2511.02791' in url for url in empirical['source_urls']))
        self.assertTrue(any('6032054' in url for url in empirical['source_urls']))

    def test_metadata_updates_preserve_identity_and_arxiv_links(self):
        expected = [u for u in self.plan['updates'] if u['file'] == 'papers.csv']
        self.assertEqual(set(self.receipt['metadata_update_ids']), {u['identity'] for u in expected})
        for change in expected:
            paper = self.by_id[change['identity']]
            self.assertEqual(paper['publication_type'], change['after']['publication_type'])
            self.assertEqual(paper['year'], int(change['after']['year']))
            self.assertEqual(paper['arxiv_id'], change['before']['arxiv_id'])
            expected_url = ('https://doi.org/' + change['after']['doi']
                            if change['after']['doi'] else change['after']['paper_url'])
            self.assertEqual(paper['formal_url'], expected_url)
            if 'DGS-Net:' in paper['title']:
                self.assertEqual([a['name'] for a in paper['authors']], change['after']['authors'].split('; '))

    def test_frozen_neurips_is_byte_identical(self):
        for path, expected in self.baseline['frozen_sha256'].items():
            self.assertEqual(hashlib.sha256((migration.ROOT / path).read_bytes()).hexdigest(), expected, path)
        frozen = self.baseline['frozen_mirror_public']
        self.assertEqual(self.by_id[frozen['paper_id']], frozen)

    def test_discovery_history_is_unchanged_beneath_decision_layer(self):
        original = migration.read(migration.OUT / 'discovery_snapshot.json')
        now = copy.deepcopy(migration.read(migration.AUDIT / 'candidates.json'))
        for c in now['works']:
            c.pop('maintainer_decision', None)
            c.pop('migration_outcome', None)
        self.assertEqual(now, original)

    def test_current_changes_are_exactly_the_approved_delta(self):
        result = migration.validation_payload()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['unexpected_curated_files'], [])
        self.assertEqual(result['unrelated_public_changes'], {})

    def test_csv_update_preserves_unrelated_rows_and_line_endings(self):
        before = b'id,text\na,unchanged\r\nb,"old, quoted"\nc,untouched\r\n'
        update = {'key': 'id', 'identity': 'b', 'before': {'id': 'b', 'text': 'old, quoted'},
                  'after': {'id': 'b', 'text': 'new'}}
        result = migration.csv_delta_bytes(before, [{'id': 'd', 'text': 'added'}], [update])
        self.assertEqual(result, b'id,text\na,unchanged\r\nb,new\nc,untouched\r\nd,added\n')


if __name__ == '__main__':
    unittest.main()
