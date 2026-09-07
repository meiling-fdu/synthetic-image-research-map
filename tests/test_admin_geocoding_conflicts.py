import json
import unittest
from pathlib import Path
from scripts.admin_geocoding import (rank_candidates, normalize_nominatim_candidate,
                                    affiliation_locality_evidence, locality_equivalent)

ROOT = Path(__file__).resolve().parents[1]


class GeocodingConflictTests(unittest.TestCase):
    def candidate(self, **kwargs):
        return dict(institution_name='Hong Kong Baptist University', city='Hong Kong',
                    region='Hong Kong', country='China', country_code='CN',
                    latitude=22.3379, longitude=114.1827, **kwargs)

    def test_hkbu_aggregate_is_blocked_even_with_generic_hong_kong_agreement(self):
        raw = json.loads((ROOT / 'data/raw/pending_institution_resolution_2026-09-06/hkbu-nominatim.json').read_text())[0]
        candidate = normalize_nominatim_candidate(raw)
        result = rank_candidates([candidate], {'names':['Hong Kong Baptist University'],
            'city':'Hong Kong','region':'Hong Kong','country_code':'CN',
            'affiliation_evidence':['TMLR Group, Hong Kong Baptist University']})[0]
        self.assertFalse(result['selectable'])
        self.assertIn('aggregate', ' '.join(result['conflicts']))
        self.assertEqual(result['provider_address'], raw['address'])
        self.assertEqual(result['provider_bounds'], raw['boundingbox'])

    def test_hkbu_kowloon_and_sha_tin_remain_distinct(self):
        candidate = self.candidate()
        candidate['region']='New Territories'
        candidate['locality_fields']={'suburb':'Sha Tin District'}
        result=rank_candidates([candidate], {'names':['Hong Kong Baptist University'],
            'city':'Hong Kong','country_code':'CN',
            'affiliation_evidence':['Hong Kong Baptist University, Kowloon Tong, Kowloon, Hong Kong']})[0]
        self.assertFalse(result['selectable'])
        self.assertIn('district conflicts', ' '.join(result['conflicts']))

    def test_valid_hk_locality_hierarchy_and_group_name(self):
        result=rank_candidates([self.candidate()], {'names':['Hong Kong Baptist University'],
            'city':'Kowloon Tong','region':'Hong Kong','country_code':'CN',
            'affiliation_evidence':['TMLR Group, Hong Kong Baptist University, Kowloon Tong, Kowloon, Hong Kong']})[0]
        self.assertTrue(result['selectable'], result['conflicts'])
        self.assertNotIn('TMLR Group', affiliation_locality_evidence(['TMLR Group, Hong Kong Baptist University']))

    def test_region_conflict_blocks_even_when_name_and_city_match(self):
        candidate=dict(institution_name='Example University',city='London',region='Scotland',
                       country='United Kingdom',country_code='GB',latitude=51.5,longitude=-0.1)
        result=rank_candidates([candidate], {'names':['Example University'],'city':'London',
                                            'region':'England','country_code':'GB'})[0]
        self.assertFalse(result['selectable'])
        self.assertIn('region differs from known evidence',result['conflicts'])

    def test_cross_city_conflicts_block_without_coordinate_context(self):
        for actual, expected, country, code in [('Sydney','Melbourne','Australia','AU'),
             ('Manchester','London','United Kingdom','GB'),('Shanghai','Beijing','China','CN')]:
            with self.subTest(city=actual):
                candidate=dict(institution_name='Same University',city=actual,region='',country=country,
                               country_code=code,latitude=30,longitude=110)
                result=rank_candidates([candidate],{'names':['Same University'],'city':expected,'country_code':code})[0]
                self.assertFalse(result['selectable'])

    def test_matching_geography_remains_eligible(self):
        candidate=dict(institution_name='Nanjing University',city='Nanjing City',region='Jiangsu',
                       country='China',country_code='CN',latitude=32.12,longitude=118.95)
        result=rank_candidates([candidate],{'names':['Nanjing University'],'city':'Nanjing',
                                           'region':'Jiangsu','country_code':'CN'})[0]
        self.assertTrue(result['selectable'],result['conflicts'])

    def test_lse_westminster_city_is_contained_in_london(self):
        raw = json.loads((ROOT / 'data/raw/pending_institution_resolution_2026-09-06/045829d79923883d.json').read_text())[0]
        candidate = normalize_nominatim_candidate(raw)
        result = rank_candidates([candidate], {
            'names': ['London School of Economics and Political Science'],
            'city': 'London', 'region': 'England', 'country_code': 'GB',
            'affiliation_evidence': ['LSE, United Kingdom'],
        })[0]
        self.assertTrue(result['selectable'], result['conflicts'])
        self.assertEqual(result['city'], 'London')
        self.assertEqual(result['provider_city'], 'City of Westminster')
        candidate['longitude'] = -2.2
        self.assertFalse(locality_equivalent('London', 'City of Westminster', candidate))

    def test_hk_hierarchy_not_applied_to_distant_point(self):
        candidate=self.candidate();candidate.update(latitude=39.9,longitude=116.4)
        self.assertFalse(locality_equivalent('Hong Kong','Kowloon Tong',candidate))

    def test_london_containment_does_not_override_material_conflicts(self):
        raw = json.loads((ROOT / 'data/raw/pending_institution_resolution_2026-09-06/045829d79923883d.json').read_text())[0]
        context = {
            'names': ['London School of Economics and Political Science'],
            'city': 'London', 'region': 'England', 'country_code': 'GB',
            'coordinates': [(51.5146063, -0.1164509)],
        }
        for changes in (
            {'provider_address': {}},
            {'country_code': 'US', 'country': 'United States'},
            {'region': 'Scotland'},
            {'longitude': -2.2},
            {'latitude': 51.55, 'longitude': -0.2},  # Another site inside the bounding box.
            {'city': 'Reading'},  # A nearby municipality is not an alias for London.
        ):
            with self.subTest(changes=changes):
                candidate = normalize_nominatim_candidate(raw)
                candidate.update(changes)
                result = rank_candidates([candidate], context)[0]
                self.assertFalse(result['selectable'], result)

    def test_same_city_different_hk_campus_is_blocked_by_known_coordinates(self):
        candidate = self.candidate()
        candidate.update(latitude=22.388, longitude=114.208)
        result = rank_candidates([candidate], {
            'names': ['Hong Kong Baptist University'], 'city': 'Hong Kong',
            'region': 'Hong Kong', 'country_code': 'CN',
            'coordinates': [(22.337924, 114.1826302)],
        })[0]
        self.assertFalse(result['selectable'])
        self.assertIn('coordinates conflict', ' '.join(result['conflicts']))

    def test_disabled_style_is_scoped(self):
        css=(ROOT/'web/admin.css').read_text()
        style=css.split('#geocode-confirm:disabled {',1)[1].split('}',1)[0]
        self.assertIn('cursor: not-allowed',style)
        self.assertIn('opacity:',style)
        html=(ROOT/'web/admin.html').read_text()
        self.assertIn('id="geocode-confirm" aria-disabled="true" type="button" disabled',html)
