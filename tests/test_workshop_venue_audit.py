"""Workshop field roles, source preservation and shared effective-state regressions."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.venue_tracks import normalize_venue_track, VENUE_TRACKS
from scripts.venues import read_venue_aliases, resolve_venue, canonical_venue_registry
from scripts.venue_evidence import stable_event
from scripts.venue_audit import VenueAudit, review_queue, source_with_curation
from tests import test_paper_metadata_editing as metadata_tests

ROOT = Path(__file__).resolve().parents[1]
STANDALONE = {"WIFS", "IH&MMSec", "MAD", "WDC", "CCWC"}


class WorkshopVenueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aliases = read_venue_aliases()
        cls.audit = VenueAudit(cls.aliases)
        cls.registry = canonical_venue_registry(cls.aliases)

    def test_controlled_singular_tracks_and_unknowns(self):
        for original, expected in {"workshops": "Workshop", "Workshops": "Workshop",
                "workshop": "Workshop", "main": "Main", "tutorials": "Tutorial",
                "demos": "Demo", "challenges": "Challenge", "short_papers": "Short Paper",
                "posters": "Poster", "doctoral_consortium": "Doctoral Consortium"}.items():
            self.assertEqual(normalize_venue_track(original), expected)
        for value in VENUE_TRACKS:
            self.assertEqual(normalize_venue_track(value), value)
        self.assertEqual(normalize_venue_track("Unknown experimental track"), "Unknown experimental track")

    def test_official_workshop_aliases_resolve_to_verified_parents(self):
        for source, acronym in {"SPW": "IEEE S&P", "EuroS&PW": "EuroS&P", "ICDMW": "ICDM",
                               "CVPRW": "CVPR", "ICCVW": "ICCV", "WACVW": "WACV"}.items():
            result = resolve_venue(source, publication_type="conference", aliases=self.aliases)
            self.assertEqual(result.venue_acronym, acronym, source)
            self.assertEqual(result.venue_track, "Workshop", source)
            self.assertEqual(result.raw_venue, source)
            self.assertIn(source, result.venue_aliases)
            self.assertEqual(self.registry[result.venue_id]["venue_track"], "")

    def test_plural_proceedings_remain_verbatim(self):
        for title in ("ECCV 2024 Workshops", "CVPR Workshops", "2020 IEEE Security and Privacy Workshops (SPW)"):
            paper = dict(title="Example", publication_type="conference", venue=title, raw_venue=title, venue_track="Workshops")
            result, finding = self.audit.paper(paper)
            self.assertIsNone(finding)
            self.assertEqual(result["raw_venue"], title)
            self.assertEqual(result["venue_track"], "Workshop")

    def test_standalone_identities_and_no_name_only_track_inference(self):
        for acronym in STANDALONE:
            venue = next(v for v in self.registry.values() if v["venue_acronym"] == acronym)
            for name in (venue["venue_name"], acronym):
                result = resolve_venue(name, publication_type="conference", aliases=self.aliases)
                self.assertEqual(result.venue_id, venue["venue_id"])
                self.assertEqual(result.venue_track, "Main")
        name = "Independent Imaging Workshop"
        self.assertEqual(stable_event(name)[0], name)
        result = resolve_venue(name, publication_type="conference", aliases=[])
        self.assertEqual(result.venue_name, name)
        self.assertEqual(result.venue_track, "Main")
        self.assertEqual(result.ambiguity_status, "unmapped")
        parent = dict(alias="Independent Imaging", venue_id="venue:independent-imaging", venue_name="Independent Imaging",
                      venue_acronym="II", venue_type="conference", venue_track="", review_status="confirmed", notes="")
        self.assertEqual(resolve_venue(name, publication_type="conference", aliases=[parent]).ambiguity_status, "unmapped")

    def test_standalone_existing_workshop_is_reviewed_not_guessed(self):
        for acronym in STANDALONE:
            venue = next(v for v in self.registry.values() if v["venue_acronym"] == acronym)
            paper = dict(venue, title="Example", publication_type="conference", venue=venue["venue_name"], venue_track="workshops")
            result = self.audit.effective(paper)
            self.assertEqual(result["venue_id"], venue["venue_id"])
            self.assertEqual(result["venue_track"], "Workshop")
            self.assertTrue(result["venue_review_required"])
            queue = review_queue([paper], self.aliases)
            self.assertEqual(queue["count"], len(queue["records"]))
            self.assertEqual(queue["records"][0]["current_track"], "Workshop")
            self.assertIn("standalone scholarly workshop", queue["records"][0]["reason"])
            for track in ("Main", "Tutorial", "Short Paper"):
                updated, finding = self.audit.paper(dict(paper, venue_track=track))
                self.assertIsNone(finding)
                self.assertEqual(updated["venue_track"], track)

    def test_blank_manual_track_does_not_erase_existing_assignment(self):
        result = source_with_curation(dict(publication_type="conference", venue_track="workshops", curated_record={"venue_track": ""}))
        self.assertEqual(normalize_venue_track(result["venue_track"]), "Workshop")
        result = source_with_curation(dict(publication_type="conference", venue_track="workshops", curated_record={"venue_track": "Main"}))
        self.assertEqual(result["venue_track"], "Main")

    def test_standalone_review_save_updates_api_editor_and_dashboard(self):
        helper = metadata_tests.PaperMetadataEditingTests()
        venue = dict(self.registry["venue:wifs"])
        with tempfile.TemporaryDirectory() as directory:
            with helper.metadata_server(directory, [], original_overrides={
                    **{k: venue[k] for k in ("venue_id", "venue_name", "venue_acronym", "venue_type")},
                    "venue": venue["venue_name"], "publication_type": "conference", "venue_track": "workshops", "doi": ""}) as (base, original, path, links, identifier):
                def snapshot():
                    return helper.metadata_request(base, "/api/dashboard")["data"]
                before = snapshot()
                queue = before["action_queues"]["publication_venues"]
                self.assertEqual(queue["count"], 1)
                self.assertEqual(queue["records"][0]["current_track"], "Workshop")
                detail = helper.metadata_request(base, "/api/paper/metadata?id=" + identifier)["data"]["effective_record"]
                self.assertEqual(detail["venue_track"], "Workshop")
                helper.metadata_request(base, "/api/paper/metadata/update", {"id": identifier, "venue_track": "Main"})
                after = snapshot()
                self.assertEqual(after["action_queues"]["publication_venues"]["records"], [])
                self.assertEqual(next(m["value"] for m in after["action_required"] if m["queue"] == "publication_venues"), 0)
                with path.open() as handle:
                    saved = next(csv.DictReader(handle))
                self.assertEqual(saved["venue_id"], "venue:wifs")
                self.assertEqual(saved["venue_track"], "Main")

    def test_rebuild_preserves_observed_tracks_but_manual_main_wins(self):
        paper = dict(title="Tiny Autoencoders Are Effective Few-Shot Generative Model Detectors",
                     doi="10.1109/wifs61860.2024.10810686", publication_type="conference",
                     venue="IEEE International Workshop on Information Forensics and Security", venue_track="Main")
        rebuilt = self.audit.effective(paper)
        self.assertEqual(rebuilt["venue_track"], "Workshop")
        self.assertTrue(rebuilt["venue_review_required"])
        explicit = self.audit.effective(dict(paper, paper_id="curated:example", metadata_source="manual"))
        self.assertEqual(explicit["venue_track"], "Main")
        self.assertFalse(explicit["venue_review_required"])

    def test_conflicting_mad_proceedings_preserves_prior_selection_for_review(self):
        paper = dict(title="Cross-Forgery Analysis of Vision Transformers and CNNs for Deepfake Image Detection",
                     doi="10.1145/3512732.3533582", publication_type="conference",
                     venue="Proceedings of the 1st International Workshop on Multimedia AI against Disinformation")
        result = self.audit.effective(paper)
        self.assertEqual(result["venue_id"], "venue:icmr")
        self.assertEqual(result["venue_track"], "Workshop")
        self.assertTrue(result["venue_review_required"])
        finding = self.audit.paper(paper)[1]
        self.assertEqual(finding["proposed_abbreviation"], "MAD")
        self.assertEqual(finding["proposed_track"], "Main")


class WorkshopArtifactTests(unittest.TestCase):
    def test_full_dataset_before_after_and_source_preservation(self):
        from scripts.audit_workshop_venues import source_hashes
        baseline = json.loads((ROOT / "data/processed/workshop_venue_baseline.json").read_text())
        records = json.loads((ROOT / "data/processed/venue_normalized_papers.json").read_text())["records"]
        prior = {p["title"]: p for p in baseline["papers"]}
        self.assertGreaterEqual(len(records), len(prior))
        self.assertEqual(sum(p["venue_track"] == "workshops" for p in prior.values()), 53)
        current_prior = [p for p in records if p["title"] in prior]
        self.assertEqual(sum(prior[p["title"]]["venue_track"] == "workshops" and p["venue_track"] == "Workshop" for p in current_prior), 53)
        self.assertFalse(any(p["venue_track"] in {"Workshops", "workshops"} for p in records))
        self.assertTrue(all(p["venue_track"] in {*VENUE_TRACKS, ""} for p in records))
        # The historical snapshot protects immutable raw evidence. Curated and
        # manual files legitimately evolve in later repository-wide audits,
        # and new raw evidence may be added without altering snapshot inputs.
        current_hashes = source_hashes()
        historical_raw_hashes = {
            path: digest
            for path, digest in baseline["source_hashes"].items()
            if path.startswith("data/raw/")
        }
        self.assertEqual(
            {path: current_hashes.get(path) for path in historical_raw_hashes},
            historical_raw_hashes,
        )
        self.assertTrue(all(p["raw_venue"] == prior[p["title"]]["raw_venue"] for p in current_prior))

    def test_processed_admin_dashboard_public_and_marker_state_agree(self):
        from scripts.serve_admin import load_admin_data
        from scripts.export_public_preview import identity_key, paper_identity_keys
        records = json.loads((ROOT / "data/processed/venue_normalized_papers.json").read_text())["records"]
        admin, _ = load_admin_data()
        by_id = {p["display_id"]: p for p in admin}
        by_key = {identity_key(p): p for p in admin}
        fields = ("venue_id", "venue_name", "venue_acronym", "venue_type", "venue_track", "publication_type")
        for record in records:
            for field in fields:
                self.assertEqual(record.get(field, ""), by_id[record["display_id"]].get(field, ""), (record["title"], field))
        queue = review_queue(admin, read_venue_aliases())
        self.assertEqual(queue["count"], len(queue["records"]))
        self.assertEqual({p["display_id"] for p in admin if p.get("venue_review_required")}, {p["display_id"] for p in queue["records"]})
        public = json.loads((ROOT / "web/data/public_preview_papers.json").read_text())
        markers = json.loads((ROOT / "web/data/public_preview_map_data.json").read_text())
        if isinstance(public, dict): public = public["records"]
        if isinstance(markers, dict): markers = markers["records"]
        for paper in public:
            for field in fields:
                self.assertEqual(paper.get(field, ""), by_key[identity_key(paper)].get(field, ""), (paper["title"], field))
        public_by_key = {key: p for p in public for key in paper_identity_keys(p)}
        for marker in markers:
            paper = next(public_by_key[key] for key in paper_identity_keys(marker) if key in public_by_key)
            for field in fields:
                self.assertEqual(marker.get(field, ""), paper.get(field, ""), (marker["title"], field))


if __name__ == "__main__":
    unittest.main()
