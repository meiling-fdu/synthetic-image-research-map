import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.venue_audit import VenueAudit, enrich_aliases, review_queue, source_fingerprint
from scripts.venue_audit import confirmation_fingerprint
from scripts.venues import read_venue_aliases, canonical_venue_registry, canonicalize_records, create_canonical_venue, VenueRegistryError, VENUE_ALIAS_COLUMNS
from scripts.publication_types import normalize_book_record
from scripts.curated_export import _curated_paper_record
from tests import test_paper_metadata_editing as metadata_tests
from tests.test_paper_metadata_editing import chi_venue_fields

ROOT = Path(__file__).resolve().parents[1]


def test_unresolved_venue_keeps_saved_reason_and_verified_preprint_state():
    source = dict(title="Example preprint", doi="10.48550/arXiv.2608.00001",
                  publication_type="preprint", venue="arXiv", venue_name="arXiv",
                  venue_id="venue:arxiv", venue_type="preprint", venue_acronym="",
                  venue_track="", raw_venue="arXiv", curation_status="needs_review")
    reason = "Expected conference acceptance is unverified; retain the preprint."
    decision = dict(review_queue="publication_venues", action="unresolved",
                    review_note=reason + " [venue-state:" + confirmation_fingerprint(source) + "]")
    audit = VenueAudit([alias("arXiv", "venue:arxiv", "preprint", "")],
                       evidence=[], decisions=[decision])
    row, finding = audit.paper(source)
    assert finding["reason"] == reason
    assert row["venue_id"] == "venue:arxiv"
    assert row["publication_type"] == "preprint"
    assert row["curation_status"] == "needs_review"


def alias(name="Test Journal", identifier="venue:test", kind="journal", acronym="TJ"):
    return dict(alias=name, venue_name=name, venue_id=identifier, venue_type=kind,
                venue_acronym=acronym, venue_track="", review_status="confirmed", notes="Reviewed")


class PublicationVenueAuditTests(unittest.TestCase):
    def test_export_preserves_source_venue_when_canonical_identity_is_unverified(self):
        from scripts.export_public_preview import preserve_existing_venue_provenance
        previous = [dict(id="one", raw_venue="Original proceedings title")]
        current = [dict(id="one", publication_type="journal", venue_review_required=True)]
        preserve_existing_venue_provenance(current, previous)
        self.assertEqual(current[0]["raw_venue"], previous[0]["raw_venue"])
        current[0]["raw_venue"] = "New manually verified provenance"
        preserve_existing_venue_provenance(current, previous)
        self.assertEqual(current[0]["raw_venue"], "New manually verified provenance")

    def test_missing_journal_abbreviation_keeps_safe_normalization_and_live_review(self):
        audit = VenueAudit([alias(acronym="")], evidence=[], decisions=[])
        source = dict(title="Example", publication_type="conference", venue="TEST JOURNAL")
        row, finding = audit.paper(source)
        self.assertEqual((row["publication_type"], row["venue_name"], row["venue_id"]),
                         ("journal", "Test Journal", "venue:test"))
        self.assertIn("abbreviation has not been verified", finding["reason"])
        self.assertEqual(finding["current_type"], "conference")
        self.assertEqual(audit.run([row])[1]["summary"]["automatically_corrected"], 0)
        self.assertTrue(audit.effective(source)["venue_review_required"])
        self.assertEqual(audit.effective(source)["venue_id"], "venue:test")
        confirmed = VenueAudit([alias(acronym="")], evidence=[dict(name="Test Journal",
            type="journal", acronym="", short_name_is_full=True)], decisions=[])
        self.assertIsNone(confirmed.paper(source)[1])

    def test_new_abbreviation_must_not_collide_with_existing_alias(self):
        aliases = [alias("ACM Multimedia", "venue:acm", "conference", "ACM MM"),
                   dict(alias("ACM Multimedia", "venue:acm", "conference", "ACM MM"), alias="MM"),
                   alias("IEEE MultiMedia", "venue:ieee", "journal", "")]
        evidence = [dict(name="IEEE MultiMedia", type="journal", acronym="MM", source="https://example.test/publisher")]
        enriched = enrich_aliases(aliases, evidence)
        audit = VenueAudit(enriched, evidence=evidence, decisions=[])
        self.assertFalse(audit.duplicates)
        _, finding = audit.paper(dict(title="Example", venue="IEEE MultiMedia", publication_type="journal"))
        self.assertEqual(finding["proposed_abbreviation"], "MM")
        self.assertIn("conflicts with another registry", finding["reason"])

    def test_full_dataset_scope_idempotence_and_unrelated_metadata_preservation(self):
        baseline = json.loads((ROOT / "data/processed/venue_audit_baseline.json").read_text())
        audit = VenueAudit(read_venue_aliases(), decisions=[])
        result, report = audit.run(baseline)
        self.assertEqual(report["summary"]["total_papers_audited"], 551)
        self.assertEqual(sum(p.get("is_currently_published", False) and p.get("publication_type") in
                             {"conference", "journal", "preprint", "book"} for p in baseline), 546)
        allowed = {"year", "publication_year", "publication_type", "venue", "venue_id", "venue_name", "venue_acronym",
                   "venue_type", "venue_track", "venue_label", "venue_aliases", "raw_venue", "ambiguity_status"}
        for source, normalized in zip(baseline, result):
            self.assertEqual({k: v for k, v in source.items() if k not in allowed},
                             {k: v for k, v in normalized.items() if k not in allowed})
        self.assertEqual(audit.run(result)[1]["summary"]["automatically_corrected"], 0)
    def test_new_registry_entries_separate_year_and_track_and_reject_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.csv"
            path.write_text(",".join(VENUE_ALIAS_COLUMNS) + "\n")
            venue = create_canonical_venue(dict(venue_name="27th Example Conference 2025 Workshops",
                venue_type="conference", venue_acronym="EX", venue_track="Workshop",
                raw_alias="EX 2025 Workshops", review_note="Checked event website"), path)
            self.assertEqual(venue["venue_name"], "Example Conference")
            self.assertNotIn("2025", venue["venue_id"])
            self.assertNotIn("Workshop", venue["venue_id"])
            with self.assertRaisesRegex(VenueRegistryError, "duplicates"):
                create_canonical_venue(dict(venue_name="Example Conference 2026", venue_type="conference",
                    venue_acronym="EX", raw_alias="EX 2026", review_note="Same series"), path)

    def test_dashboard_exposes_venue_card_and_actionable_columns(self):
        source = (ROOT / "web/admin.js").read_text()
        dashboard = source.split("function renderDashboard()", 1)[1].split("function ", 1)[0]
        self.assertIn("publication_venues:", dashboard)
        for value in ("publication-venues", "proposed_venue_id", "current_track", "evidence_url", "openCurationPaper"):
            self.assertIn(value, source)
    def test_screenshot_journal_and_abbreviation_without_source_mutation(self):
        path = ROOT / "data/curated/venue_aliases.csv"
        before = path.read_bytes()
        name = "Journal of King Saud University – Computer and Information Sciences"
        row = dict(title="Screenshot", venue=name, publication_type="conference", year=2025,
                   metadata_source="manual", raw_venue="Original publisher provenance")
        result, finding = VenueAudit(read_venue_aliases()).paper(row)
        self.assertIsNone(finding)
        self.assertEqual(result["publication_type"], "journal")
        self.assertEqual(result["venue_acronym"], "JKSUCI")
        self.assertEqual(result["venue_track"], "")
        self.assertEqual(result["raw_venue"], row["raw_venue"])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(row["publication_type"], "conference")

    def test_exact_variants_names_ids_and_acronyms_are_idempotent(self):
        rows = [dict(title="One", venue="TEST JOURNAL", publication_type="conference")]
        audit = VenueAudit([alias()], evidence=[])
        output, report = audit.run(rows)
        self.assertEqual(report["summary"]["automatically_corrected"], 1)
        self.assertEqual(output[0]["venue_id"], "venue:test")
        self.assertEqual(output[0]["venue_acronym"], "TJ")
        self.assertEqual(audit.run(output)[1]["summary"]["automatically_corrected"], 0)

    def test_manual_name_acronym_and_explicit_type_conflicts_are_preserved(self):
        audit = VenueAudit([alias()], evidence=[])
        for override in [dict(venue="My reviewed venue"), dict(venue_acronym="MANUAL"),
                         dict(publication_type="preprint", publication_type_override=True)]:
            row = dict(paper_id="curated:one", venue="Test Journal", venue_id="venue:test",
                       publication_type="journal", abstract="Keep", review_status="pending", **{})
            row.update(override)
            result, finding = audit.paper(row)
            self.assertEqual(result, row)
            self.assertTrue(finding["manual_review"])

    def test_preprint_with_formal_venue_is_not_guessed(self):
        result, finding = VenueAudit([alias()], evidence=[]).paper(
            dict(title="Uncertain version", publication_type="preprint", venue="Test Journal"))
        self.assertEqual(result["publication_type"], "preprint")
        self.assertIn("Preprint has a formal", finding["reason"])

    def test_eccv_chapter_and_lncs_ccis_resolve_using_paper_evidence(self):
        for container in ["Lecture Notes in Computer Science, vol. 15643", "CCIS", "Computer Vision – ECCV 2024 Workshops"]:
            row = dict(title="Are CLIP Features All You Need for Universal Synthetic Image Origin Attribution?",
                       doi="10.1007/978-3-031-92648-8_22", publication_type="book", venue=container,
                       year=2025, raw_venue=container, research_types=["method"])
            result, finding = VenueAudit(read_venue_aliases()).paper(row)
            self.assertIsNone(finding)
            self.assertEqual((result["publication_type"], result["venue_id"], result["year"], result["venue_track"]),
                             ("conference", "venue:eccv", 2024, "Workshop"))
            self.assertEqual(result["raw_venue"], container)
            self.assertEqual(normalize_book_record(row)["publication_type"], "conference")

    def test_edition_and_track_variants_use_one_canonical_record(self):
        aliases = enrich_aliases([
            alias("Test Conference 2025", "venue:test:main", "conference", "TC"),
            alias("Test Conference 2024 Workshops", "venue:test:workshops", "conference", "TC"),
        ], evidence=[])
        registry = canonical_venue_registry(aliases)
        self.assertEqual(list(registry), ["venue:test"])
        self.assertEqual(registry["venue:test"]["venue_name"], "Test Conference")
        audit = VenueAudit(read_venue_aliases())
        for venue, identifier, year, track in [
            ("CVPR 2025", "venue:cvpr", 2025, "Main"),
            ("ICCV 2023 Workshops", "venue:iccv", 2023, "Workshop"),
            ("ECCV 2024 Workshops", "venue:eccv", 2024, "Workshop"),
            ("ACM Multimedia 2025", "venue:acm-mm", 2025, "Main"),
        ]:
            row, finding = audit.paper(dict(title="Example", venue=venue, publication_type="conference"))
            self.assertIsNone(finding, venue)
            self.assertEqual((row["venue_id"], row["year"], row["venue_track"]), (identifier, year, track))

    def test_ambiguous_proceedings_stay_in_live_queue_and_curation_is_untouched(self):
        paper = dict(title="Unknown chapter", venue="CCIS volume 100", publication_type="conference",
                     curation_status="needs_review", review_status="pending", display_id="one")
        audit = VenueAudit([], evidence=[])
        row, finding = audit.paper(paper)
        self.assertEqual(row, paper)
        self.assertTrue(finding)
        queue = review_queue([paper], [])
        self.assertEqual(queue["count"], len(queue["records"]))
        corrected = dict(paper, venue="Test Journal", publication_type="journal")
        self.assertEqual(review_queue([corrected], [alias()])["count"], 0)
        self.assertEqual(corrected["curation_status"], "needs_review")
        self.assertNotEqual(source_fingerprint(paper), source_fingerprint(corrected))

    def test_registry_enrichment_preserves_valid_curated_abbreviation(self):
        evidence = [dict(name="Test Journal", type="journal", acronym="Test J.", source="https://example.org")]
        result = enrich_aliases([alias()], evidence)
        self.assertEqual(canonical_venue_registry(result)["venue:test"]["venue_acronym"], "TJ")

    def test_generic_event_metadata_does_not_erase_manual_workshop_track(self):
        audit = VenueAudit([alias("Test Conference", kind="conference", acronym="TC")], evidence=[])
        audit.paper_evidence = {"10.1/test": dict(name="Test Conference", type="conference", track="Main")}
        row, finding = audit.paper(dict(title="Example", doi="10.1/test", publication_type="conference",
            paper_id="curated:example", venue="Test Conference", venue_track="Workshop"))
        self.assertIsNone(finding)
        self.assertEqual(row["venue_track"], "Workshop")

    def test_api_export_card_share_journal_type(self):
        row = dict(title="Screenshot", publication_type="conference",
                   venue="Journal of King Saud University - Computer and Information Sciences", year=2025)
        exported = _curated_paper_record(row, "source_attribution")
        output = canonicalize_records([row])[0]
        for field in ("publication_type", "venue_id", "venue_name", "venue_acronym", "venue_track"):
            self.assertEqual(output[field], exported[field])
        node = str(Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
        script = "const h=require('./web/paper_details_helpers.js'); const p=" + json.dumps(output) + "; console.log(h.publicationMetadata(p,p.venue_label,p.year).typeLabel)"
        result = subprocess.run([node, "-e", script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Journal")


class VenueSaveLifecycleTests(unittest.TestCase):
    def test_uncertain_book_container_remains_visible_in_editor_and_dashboard(self):
        helper = metadata_tests.PaperMetadataEditingTests()
        with tempfile.TemporaryDirectory() as directory:
            with helper.metadata_server(directory, [], original_overrides={
                    "publication_type": "book", "venue": "Unknown proceedings", "doi": ""}) as (base, original, path, links, identifier):
                queue = helper.metadata_request(base, "/api/dashboard")["data"]["action_queues"]["publication_venues"]
                self.assertEqual(queue["count"], 1)
                self.assertEqual(queue["records"][0]["current_venue"], "Unknown proceedings")
                editor = helper.metadata_request(base, "/api/paper/metadata?id=" + identifier)["data"]["effective_record"]
                self.assertTrue(editor["venue_review_required"])
                self.assertIn("not verified", editor["venue_review_reason"])

    def test_explicit_review_confirmation_persists_and_reopens_on_venue_change(self):
        helper = metadata_tests.PaperMetadataEditingTests()
        with tempfile.TemporaryDirectory() as directory:
            with helper.metadata_server(directory, [], original_overrides={
                    **chi_venue_fields(), "doi": "10.1145/3770916"}) as (base, original, path, links, identifier):
                self.assertEqual(helper.metadata_request(base, "/api/dashboard")["data"]["action_queues"]["publication_venues"]["count"], 1)
                helper.metadata_request(base, "/api/paper/metadata/update", {
                    "id": identifier, "venue_review_confirmed": True,
                    "venue_review_note": "Checked source; retain selected venue despite conflicting deposited metadata."})
                self.assertEqual(helper.metadata_request(base, "/api/dashboard")["data"]["action_queues"]["publication_venues"]["count"], 0)
                self.assertFalse(helper.metadata_request(base, "/api/paper/metadata?id=" + identifier)["data"]["effective_record"]["venue_review_required"])
                with (Path(directory) / "review_decisions.csv").open() as handle:
                    decisions = list(csv.DictReader(handle))
                with path.open() as handle:
                    saved = list(csv.DictReader(handle))[0]
                self.assertIn(confirmation_fingerprint(saved), decisions[0]["review_note"])
                audit = VenueAudit(read_venue_aliases(), decisions=decisions)
                self.assertIsNone(audit.paper(saved)[1])
                self.assertIsNotNone(audit.paper(dict(saved, raw_venue="New source metadata"))[1])

    def test_http_save_removes_resolved_review_and_updates_dashboard_immediately(self):
        helper = metadata_tests.PaperMetadataEditingTests()
        with tempfile.TemporaryDirectory() as directory:
            with helper.metadata_server(directory, [], original_overrides={
                    "publication_type": "conference", "venue": "Unknown proceedings"}) as (base, original, path, links, identifier):
                def get_snapshot():
                    return helper.metadata_request(base, "/api/dashboard")["data"]
                before = get_snapshot()
                queue = before["action_queues"]["publication_venues"]
                metric = next(m for m in before["action_required"] if m["queue"] == "publication_venues")
                self.assertEqual(metric["value"], len(queue["records"]))
                self.assertEqual(queue["count"], 1)
                helper.metadata_request(base, "/api/paper/metadata/update", {
                    "id": identifier, **chi_venue_fields(), "venue_selection_confirmed": True})
                after = get_snapshot()
                self.assertEqual(after["action_queues"]["publication_venues"]["count"], 0)
                self.assertEqual(next(m for m in after["action_required"] if m["queue"] == "publication_venues")["value"], 0)
                detail = helper.metadata_request(base, "/api/review/publication-venues")["data"]
                self.assertEqual(detail["records"], [])
