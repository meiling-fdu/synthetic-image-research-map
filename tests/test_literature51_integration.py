"""Evidence, identity, publication, and preservation regressions for this batch."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from scripts import integrate_literature51_2026_10_16 as batch
from scripts.paper_taxonomy import taxonomy_from_record


class Literature51Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = batch.read(batch.ROOT/batch.OUT/'plan.json')
        cls.audit = {r['candidate_id']:r for r in cls.plan['audit']}
        cls.papers = {r['paper_id']:r for r in batch.rows(batch.ROOT/'data/curated/papers.csv')}
        cls.tax = {r['paper_id']:r for r in batch.rows(batch.ROOT/'data/curated/paper_taxonomy.csv')}
        cls.decisions = batch.rows(batch.ROOT/'data/curated/review_decisions.csv')

    def paper(self, cid):
        return self.papers[self.audit[cid]['paper_id']]

    def test_exact_inventory_and_exhaustive_dispositions(self):
        self.assertEqual(list(self.audit),batch.EXPECTED)
        self.assertEqual(Counter(k[0] for k in self.audit),{'A':20,'B':3,'C':3,'D':6,'E':19})
        self.assertEqual(Counter(r['decision'] for r in self.audit.values()),{'import':38,'held':13})
        self.assertEqual(len({batch.title_key(r['submitted_title']) for r in self.audit.values()}),51)

    def test_prior_holds_are_retained_and_explicitly_resolved(self):
        for cid in ('A01','A13'):
            linked = self.audit[cid]['resolves_decision_ids']
            originals = [r for r in self.decisions if r['decision_id'] in linked]
            self.assertEqual(len(originals),1)
            self.assertEqual(originals[0]['action'],'unresolved')
            self.assertIn('HOLD_EVIDENCE_INSUFFICIENT',originals[0]['review_note'])
            successor = next(r for r in self.decisions if r['decision_id']==self.audit[cid]['new_review_decision_id'])
            self.assertEqual(successor['action'],'add_paper')
            self.assertIn(linked[0],successor['review_note'])

    def test_neurips_locks_cannot_be_bypassed_as_preprints(self):
        for cid in ('B01','E07'):
            row = self.audit[cid]
            self.assertEqual(row['decision'],'held')
            self.assertFalse(row['paper_id'])
            self.assertTrue(any(m['dataset']=='neurips_locked' for m in row['identity_matches']))
        self.assertEqual(self.audit['E07']['tasks'],'source_attribution')

    def test_future_and_accepted_only_records_are_not_formal_publications(self):
        for cid in ('B03','C01','C02','C03','E01','E06','E13','E15'):
            row = self.audit[cid]
            self.assertFalse(row['publication_verified'],cid)
            self.assertFalse(row['paper_id'],cid)
        self.assertEqual(self.audit['E01']['doi'],'10.1145/3843205.3845630')
        self.assertIn('November 14, 2026',self.audit['E01']['notes'])

    def test_chapter_doi_pages_and_author_order(self):
        row = self.paper('E12')
        self.assertEqual(row['doi'],'10.1007/978-3-032-38407-2_23')
        self.assertNotEqual(row['doi'],'10.1007/978-3-032-38407-2')
        self.assertEqual(row['arxiv_id'],'2608.26648')
        self.assertEqual(row['authors'].split('; '),['Saifullah Shoaib','Akash Borigi','Rupendra Lekkala','Amaury Lendasse','Edward Ratner','Sai Sowjanya Bhamidipati','Alexander Schlager','Peggy Lindner'])
        self.assertEqual(self.audit['E12']['publication_details']['pages'],'285–297')

    def test_online_dates_and_future_issue_years_stay_distinct(self):
        self.assertEqual(self.paper('A05')['year'],'2026')
        self.assertEqual(self.audit['A05']['publication_details']['reported_online_year'],2025)
        self.assertEqual(self.paper('A17')['year'],'2027')
        self.assertEqual(self.audit['A17']['publication_details']['online_date'],'2026-09-12')
        self.assertEqual(self.audit['E16']['publication_details']['published-online']['date-parts'],[[2026,10,4]])
        self.assertEqual(self.paper('E16')['authors'],'Jingming Wang; Renwei Meng; Yunjie Si')

    def test_precise_tracks_preprint_and_task_distinctions(self):
        for cid in ('A07','E17'):
            self.assertEqual(self.paper(cid)['venue_track'],'Findings')
        for cid in ('A16','A18'):
            self.assertEqual(self.paper(cid)['venue_track'],'Workshop')
        self.assertEqual(self.paper('E19')['venue_track'],'Main')
        for cid in ('B02','D01','D02','D03','D04','D05','D06','E03'):
            self.assertEqual(self.paper(cid)['publication_type'],'preprint')
        self.assertEqual(self.paper('E03')['tasks'],'detection')
        self.assertEqual(self.paper('E05')['research_types'],'analysis_study')
        self.assertEqual(self.paper('A20')['research_types'],'survey')

    def test_frequency_training_augmentation_and_synthetic_faces_stay_in_scope(self):
        self.assertIn('detector augmentation',self.audit['A03']['scope_rationale'])
        for cid in ('A01','A19','A20','D02'):
            self.assertIn('deepfake',self.paper(cid)['image_scopes'])
            self.assertIn('fully_generated',self.paper(cid)['image_scopes'])
        self.assertEqual(self.audit['E09']['scope_decision'],'unresolved_generator_identity')
        self.assertEqual(self.audit['E18']['tasks'],'detection')

    def test_incomplete_taxonomy_is_explicitly_reviewable(self):
        for r in self.plan['additions']['paper_taxonomy.csv']:
            taxonomy_from_record(r)  # Reject vocabulary expansion.
            if r['tasks_evidence_tier']=='title':
                self.assertEqual(r['taxonomy_status'],'needs_review')
                self.assertTrue(r['tasks_review_reason'])
                self.assertTrue(self.audit[next(a['candidate_id'] for a in self.audit.values() if a['paper_id']==r['paper_id'])]['manual_review'])
        self.assertEqual(self.tax[self.paper('D06')['paper_id']]['image_scopes_status'],'needs_review')

    def test_no_author_institution_or_location_inference(self):
        pids = {r['paper_id'] for r in self.plan['additions']['papers.csv']}
        mappings = batch.rows(batch.ROOT/'data/curated/author_institution_mappings.csv')
        self.assertFalse(any(r['paper_id'] in pids for r in mappings))
        for r in self.plan['additions']['papers.csv']:
            self.assertTrue(r['authors'])
            self.assertIn('Unresolved',r['metadata_source'])

    def test_no_duplicate_title_doi_arxiv_in_the_successor(self):
        for key, normalizer in [('title',batch.title_key),('doi',batch.normalize_doi),('arxiv_id',batch.normalize_arxiv_id)]:
            counts = Counter(normalizer(r.get(key)) for r in self.papers.values() if normalizer(r.get(key)))
            self.assertFalse({k:n for k,n in counts.items() if n>1},key)

    def test_byte_preservation_provenance_and_repeat_application(self):
        self.assertTrue(batch.check()['historical_and_unrelated_files_preserved'])
        before = {name:batch.sha(batch.ROOT/'data/curated'/name) for name in self.plan['additions']}
        batch.apply()
        self.assertEqual(before,{name:batch.sha(batch.ROOT/'data/curated'/name) for name in before})
        decisions_before = gzip.decompress((batch.ROOT/batch.OUT/'review_decisions.csv.before.gz').read_bytes())
        self.assertTrue((batch.ROOT/'data/curated/review_decisions.csv').read_bytes().startswith(decisions_before))


if __name__=='__main__':
    unittest.main()
