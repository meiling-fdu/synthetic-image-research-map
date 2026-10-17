"""Targeted release, review-state, compact-cache and preservation regressions."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import integrate_literature51_2026_10_16 as batch
from scripts import reassess_literature51_2026_10_16 as followup
from scripts.verify_literature51_main_integration import baseline_bytes
from scripts.collect_literature51_sources import cache_sources, optional_retrieval_bodies


class Literature51FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event=followup.receipt()
        cls.review=batch.read(batch.ROOT/followup.OUT/'review.json')
        cls.original=batch.read(batch.ROOT/batch.OUT/'plan.json')
        cls.papers=batch.rows(batch.ROOT/'data/curated/papers.csv')
        cls.tax=batch.rows(batch.ROOT/'data/curated/paper_taxonomy.csv')

    def test_exhaustive_successor_without_restarting_the_batch(self):
        self.assertEqual(self.original['counts'],{'import':38,'held':13})
        self.assertEqual(self.event['counts'],{'import':39,'held':12})
        self.assertEqual(set(self.review['released']),{'B03'})
        self.assertEqual(len(self.review['held']),12)
        self.assertEqual(len({r['candidate_id'] for r in self.original['audit']}),51)
        self.assertEqual(self.review['summary']['unexplained'],0)

    def test_b03_version_order_and_preprint_status(self):
        matches=[p for p in self.papers if p['arxiv_id']=='2511.20722']
        self.assertEqual(len(matches),1)
        p=matches[0]
        self.assertEqual(p['authors'].split('; '),['Minh Thong Doi','Vincent Itier','Jan Butora','Jérémie Boulanger','Patrick Bas'])
        self.assertEqual(p['publication_type'],'preprint')
        self.assertEqual(p['year'],'2025')
        self.assertEqual(p['venue_track'],'')
        self.assertEqual(p['tasks'],'localization')
        self.assertEqual(p['image_scopes'],'generative_editing')
        self.assertFalse(p['doi'])
        self.assertIn('Learning from the Best',p['metadata_source'])
        self.assertIn('no formal proceedings',p['metadata_source'])
        self.assertEqual(batch.read(batch.ROOT/'data/raw/literature51_2026_10_16/followup/hal_v2.json')['response']['docs'][0]['authFullName_s'],p['authors'].split('; '))

    def test_immutable_holds_and_append_only_resolution(self):
        decisions=batch.rows(batch.ROOT/'data/curated/review_decisions.csv')
        original=next(r for r in self.original['audit'] if r['candidate_id']=='B03')
        old=next(r for r in decisions if r['decision_id']==original['new_review_decision_id'])
        self.assertEqual(old['action'],'unresolved')
        new=next(r for r in decisions if r['decision_id']==self.event['additions']['review_decisions.csv'][0]['decision_id'])
        self.assertEqual(new['action'],'add_paper')
        self.assertIn(old['decision_id'],new['review_note'])
        for cid in ('B01','E07','E01','E15'):
            self.assertEqual(self.review['held'][cid]['decision'],'held')
        self.assertEqual(self.review['held']['E18']['proposed_tasks'],'detection')
        self.assertEqual(self.review['held']['E18']['ordered_authors'],['Martin Dahlgren','Abu Naser Masud'])

    def test_only_e17_taxonomy_review_is_finalized(self):
        before={p['paper_id']:p for p in self.original['additions']['paper_taxonomy.csv']}
        current={p['paper_id']:p for p in self.tax}
        pending=[p for p in before.values() if p['taxonomy_status']=='needs_review']
        self.assertEqual(len(pending),15)
        self.assertEqual(sum(current[p['paper_id']]['taxonomy_status']=='needs_review' for p in pending),14)
        for p in before.values():
            q=current[p['paper_id']]
            for dim in ('tasks','image_scopes','research_types'):
                self.assertEqual(q[dim],p[dim])
            if p['paper_id']=='curated:fa41c2810887fb216f5d':
                self.assertEqual(q['taxonomy_status'],'reviewed')
                self.assertEqual(q['tasks_evidence_tier'],'primary_abstract')
            else:
                self.assertEqual(q,p)
        self.assertEqual(current['curated:a116171fee8869392bc0']['image_scopes_status'],'needs_review')

    def test_original_38_papers_and_all_map_objects_preserved(self):
        by_id={p['paper_id']:p for p in self.papers}
        for p in self.original['additions']['papers.csv']:
            self.assertEqual(by_id[p['paper_id']],p)
        old_maps=json.loads(baseline_bytes(batch.ROOT,'web/data/public_preview_map_data.json'))
        maps=batch.read(batch.ROOT/'web/data/public_preview_map_data.json')
        self.assertEqual(maps['records'],old_maps['records'])
        public=batch.read(batch.ROOT/'web/data/public_preview_papers.json')['records']
        b03=next(p for p in public if p.get('paper_id')==self.event['paper_id'])
        self.assertFalse(b03['has_map_location'])
        self.assertTrue(all(a['affiliation_status']=='unresolved' for a in b03['authors']))
        self.assertEqual(len(public),674)
        self.assertEqual(sum(p['publication_type'] in ('conference','journal','book') for p in public),557)

    def test_only_approved_review_fields_drift_in_public_predecessor(self):
        old=json.loads(baseline_bytes(batch.ROOT,'web/data/public_preview_papers.json'))['records']
        current={batch.title_key(p['title']):p for p in batch.read(batch.ROOT/'web/data/public_preview_papers.json')['records']}
        changes=[]
        for p in old:
            q=current[batch.title_key(p['title'])]
            if p!=q:
                changes.append(p['paper_id'])
                self.assertEqual({k for k in p.keys()|q.keys() if p.get(k)!=q.get(k)}, {'taxonomy_status','taxonomy_review'})
                self.assertEqual(q['taxonomy_status'],'reviewed')
        self.assertEqual(changes,[])
        reviewed=next(p for p in current.values() if p.get('paper_id')=='curated:fa41c2810887fb216f5d')
        self.assertEqual(reviewed['taxonomy_status'],'reviewed')

    def test_compact_cache_keeps_all_primary_evidence(self):
        sources=cache_sources()
        optional=optional_retrieval_bodies()
        self.assertEqual(len(optional),34)
        self.assertTrue(all(s.get('raw_path') not in optional for s in sources if s['kind']=='crossref'))
        expected,_=batch.extract_metadata()
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            for rel in (batch.RAW/'source_manifest.json',batch.RAW/'candidates.json',followup.OUT/'cache_policy.json'):
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(batch.ROOT/rel,target)
            for s in sources:
                if s.get('raw_path') and s['raw_path'] not in optional:
                    target=root/s['raw_path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(batch.ROOT/s['raw_path'],target)
            actual,_=batch.extract_metadata(root)
            self.assertEqual(actual,expected)
            self.assertEqual(len(list((root/batch.RAW/'sources').glob('*.json'))),0)
            required=next(s for s in sources if s['kind']=='crossref')
            (root/required['raw_path']).unlink()
            with self.assertRaises(FileNotFoundError):
                batch.extract_metadata(root)

    def test_present_optional_bodies_still_reject_hash_drift(self):
        source=next(s for s in cache_sources() if s.get('raw_path') in optional_retrieval_bodies())
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);path=root/source['raw_path'];path.parent.mkdir(parents=True)
            path.write_bytes(gzip.compress(b'changed response'))
            with self.assertRaises(ValueError):
                batch.source_body(root,source)

    def test_successor_check_and_repeat_apply_are_read_only(self):
        paths=[batch.ROOT/'data/curated'/n for n in self.event['additions']]
        before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(followup.check()['counts'],{'import':39,'held':12})
        followup.apply()
        self.assertEqual(before,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})


if __name__=='__main__':
    unittest.main()
