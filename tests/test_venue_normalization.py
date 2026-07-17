import csv
import tempfile
import unittest
from pathlib import Path

from scripts.migrate_venues import migrate_rows
from scripts.curated_papers import CuratedPaperError, apply_canonical_venue_selection
from scripts.report_public_preview import build_report
from scripts.venues import (
    VENUE_ALIAS_COLUMNS,
    VENUE_TYPE_ORDER,
    VenueRegistryError,
    canonical_venue_options,
    create_canonical_venue,
    display_venue,
    read_venue_aliases,
    resolve_venue,
    venue_type_rank,
)


class VenueNormalizationTests(unittest.TestCase):
    def resolve(self, raw, publication_type="conference"):
        return resolve_venue(raw, publication_type=publication_type, aliases=read_venue_aliases())

    def test_year_proceedings_ordinal_and_acronym_normalize(self):
        venue = self.resolve("2026 Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")
        self.assertEqual(venue.venue_id, "venue:cvpr:main")
        self.assertEqual(venue.venue_name, "IEEE/CVF Conference on Computer Vision and Pattern Recognition")
        self.assertEqual(venue.venue_acronym, "CVPR")
        self.assertEqual(venue.raw_venue, "2026 Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")

    def test_tracks_are_distinct(self):
        main = self.resolve("2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")
        workshops = self.resolve("2026 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops")
        findings = self.resolve("2026 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Findings")
        self.assertEqual({main.venue_track, workshops.venue_track, findings.venue_track}, {"main", "workshops", "findings"})
        self.assertEqual(len({main.venue_id, workshops.venue_id, findings.venue_id}), 3)
        self.assertEqual(workshops.venue_type, "conference")

    def test_wacv_workshop_is_separate(self):
        main = self.resolve("2025 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)")
        workshop = self.resolve("2026 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) Workshop")
        self.assertEqual(main.venue_id, "venue:wacv:main")
        self.assertEqual(workshop.venue_id, "venue:wacv:workshops")

    def test_icml_edition_and_neurips_volume(self):
        self.assertEqual(self.resolve("Proceedings of the 42nd International Conference on Machine Learning").venue_id, "venue:icml:main")
        self.assertEqual(self.resolve("Advances in Neural Information Processing Systems 37").venue_id, "venue:neurips:main")

    def test_ih_mmsec_year_and_proceedings(self):
        first = self.resolve("2026 ACM Workshop on Information Hiding and Multimedia Security (IH&MMSec)")
        second = self.resolve("Proceedings of the 2026 ACM Workshop on Information Hiding and Multimedia Security (IH&MMSec)")
        self.assertEqual(first.venue_id, "venue:ih-mmsec:main")
        self.assertEqual(second.venue_id, first.venue_id)
        self.assertEqual(first.venue_type, "conference")
        self.assertEqual(first.venue_track, "workshops")

    def test_journal_is_stable_and_article_reuses_journal_label(self):
        venue = self.resolve("Pattern Recognition", publication_type="article")
        self.assertEqual(venue.venue_name, "Pattern Recognition")
        self.assertEqual(venue.venue_type, "journal")
        self.assertEqual(venue.venue_track, "main")

    def test_display_format(self):
        venue = self.resolve("2026 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops")
        self.assertEqual(display_venue(venue.as_record()), "IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) · Workshops")
        self.assertEqual(
            display_venue(self.resolve("CHI Conference on Human Factors in Computing Systems").as_record()),
            "CHI Conference on Human Factors in Computing Systems (CHI)",
        )
        self.assertEqual(
            display_venue(self.resolve("Pattern Recognition", publication_type="journal").as_record()),
            "Pattern Recognition (PR)",
        )

    def test_conflicting_alias_is_ambiguous_and_not_merged(self):
        base = {
            "alias": "Example Venue", "venue_name": "Example Venue", "venue_acronym": "",
            "venue_type": "conference", "venue_track": "main", "review_status": "confirmed", "notes": "",
        }
        venue = resolve_venue("Example Venue", publication_type="conference", aliases=[
            {**base, "venue_id": "venue:one:main"},
            {**base, "venue_id": "venue:two:main"},
        ])
        self.assertEqual(venue.ambiguity_status, "ambiguous")
        self.assertNotIn(venue.venue_id, {"venue:one:main", "venue:two:main"})

    def test_migration_is_idempotent_and_deduplicates_identity_counts(self):
        rows = [
            {"paper_id": "one", "title": "One", "year": "2024", "venue": "2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)", "publication_type": "conference"},
            {"paper_id": "two", "title": "Two", "year": "2025", "venue": "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)", "publication_type": "conference"},
        ]
        migrated, report = migrate_rows(rows)
        second, second_report = migrate_rows(migrated)
        self.assertEqual(report["canonical_venue_count"], 1)
        self.assertEqual(report["largest_duplicate_groups_merged"][0]["paper_count"], 2)
        self.assertEqual(second_report["records_changed"], 0)
        self.assertEqual(migrated, second)

    def test_workshop_migration_is_idempotent_and_preserves_track_identity(self):
        rows = [{
            "paper_id": "workshop-paper",
            "title": "Workshop paper",
            "year": "2024",
            "venue": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "venue_id": "venue:cvpr:workshops",
            "venue_name": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "venue_acronym": "CVPR",
            "venue_type": "workshop",
            "venue_track": "workshops",
            "raw_venue": "2024 CVPR Workshops",
            "publication_type": "conference",
        }]
        migrated, report = migrate_rows(rows)
        second, second_report = migrate_rows(migrated)
        self.assertEqual(migrated[0]["venue_id"], "venue:cvpr:workshops")
        self.assertEqual(migrated[0]["venue_type"], "conference")
        self.assertEqual(migrated[0]["venue_track"], "workshops")
        self.assertEqual(report["workshop_records_migrated"], 1)
        self.assertEqual(second_report["workshop_records_migrated"], 0)
        self.assertEqual(second_report["records_changed"], 0)
        self.assertEqual(migrated, second)

    def test_admin_options_are_canonical_counted_and_searchable(self):
        aliases = read_venue_aliases()
        papers = [
            {"paper_id": "one", "venue_id": "venue:cvpr:workshops", "raw_venue": "2024 CVPR Workshops"},
            {"paper_id": "two", "venue_id": "venue:cvpr:workshops", "raw_venue": "CVPRW"},
        ]
        options = canonical_venue_options(aliases, papers)
        workshops = next(option for option in options if option["venue_id"] == "venue:cvpr:workshops")
        self.assertEqual(workshops["paper_count"], 2)
        self.assertEqual(workshops["venue_track"], "workshops")
        searchable = workshops["search_text"].casefold()
        for term in ("computer vision", "cvpr", "workshop", "2024 cvpr workshops", "cvprw"):
            self.assertIn(term, searchable)
        self.assertEqual(options, sorted(options, key=lambda option: (
            option["venue_name"].casefold(),
            option["venue_acronym"].casefold(),
            option["venue_track"].casefold(),
            option["venue_id"],
        )))
        self.assertEqual(VENUE_TYPE_ORDER, ("conference", "journal", "preprint", "book"))

    def test_audited_journal_acronyms_display_resolve_and_do_not_collide(self):
        expected = {
            "IEEE Transactions on Pattern Analysis and Machine Intelligence": "TPAMI",
            "IEEE Transactions on Information Forensics and Security": "TIFS",
            "IEEE Transactions on Multimedia": "TMM",
            "IEEE Signal Processing Letters": "SPL",
            "Pattern Recognition": "PR",
            "Pattern Recognition Letters": "PRL",
            "ACM Transactions on Multimedia Computing, Communications, and Applications": "TOMM",
        }
        for name, acronym in expected.items():
            with self.subTest(acronym=acronym):
                venue = self.resolve(name, publication_type="journal")
                self.assertEqual(venue.venue_acronym, acronym)
                self.assertEqual(self.resolve(acronym, "journal").venue_id, venue.venue_id)
                self.assertIn(f"({acronym})", display_venue(venue.as_record()))

        collision_rows = [
            {
                "alias": "First Journal", "venue_id": "venue:first:main",
                "venue_name": "First Journal", "venue_acronym": "DUP",
                "venue_type": "journal", "venue_track": "main",
                "review_status": "confirmed", "notes": "",
            },
            {
                "alias": "Second Journal", "venue_id": "venue:second:main",
                "venue_name": "Second Journal", "venue_acronym": "DUP",
                "venue_type": "journal", "venue_track": "main",
                "review_status": "confirmed", "notes": "",
            },
        ]
        with self.assertRaisesRegex(VenueRegistryError, "acronym.*collides"):
            canonical_venue_options(collision_rows)

    def test_acronym_collision_is_rejected_before_registry_write(self):
        existing = {
            "alias": "First Journal", "venue_id": "venue:first:main",
            "venue_name": "First Journal", "venue_acronym": "DUP",
            "venue_type": "journal", "venue_track": "main",
            "review_status": "confirmed", "notes": "",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "venue_aliases.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=VENUE_ALIAS_COLUMNS)
                writer.writeheader()
                writer.writerow(existing)
            before = path.read_bytes()
            with self.assertRaisesRegex(VenueRegistryError, "acronym collides"):
                create_canonical_venue({
                    "venue_name": "Second Journal",
                    "venue_acronym": "DUP",
                    "venue_type": "journal",
                    "venue_track": "main",
                    "raw_alias": "Second Journal",
                    "confirmed_similar": True,
                }, path)
            self.assertEqual(path.read_bytes(), before)

    def test_top_venues_report_uses_shared_type_then_count_order(self):
        records = [
            {
                "id": "conference", "title": "Conference paper", "year": 2024,
                "venue_label": "Conference · Alpha", "venue_name": "Alpha",
                "venue_type": "conference", "institution": "One",
            },
            *[
                {
                    "id": f"journal-{index}", "title": f"Journal {index}", "year": 2024,
                    "venue_label": "Journal · Popular", "venue_name": "Popular",
                    "venue_type": "journal", "institution": "Two",
                }
                for index in range(3)
            ],
            {
                "id": "preprint", "title": "Preprint paper", "year": 2024,
                "venue_label": "Preprint · arXiv", "venue_name": "arXiv",
                "venue_type": "preprint", "institution": "Three",
            },
        ]
        report = build_report(Path("preview.json"), {}, records)
        top_venues = report.split("## Top Venues", 1)[1].split("## Top Countries", 1)[0]
        self.assertLess(top_venues.index("Conference · Alpha"), top_venues.index("Journal · Popular"))
        self.assertLess(top_venues.index("Journal · Popular"), top_venues.index("Preprint · arXiv"))

    def test_structured_selection_syncs_type_and_preserves_raw_provenance(self):
        selection = {
            "venue_id": "venue:cvpr:workshops",
            "venue_name": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "venue_acronym": "CVPR",
            "venue_type": "conference",
            "venue_track": "workshops",
            "publication_type": "conference",
        }
        result = apply_canonical_venue_selection(
            selection,
            existing={"raw_venue": "2024 IEEE/CVF CVPR Workshops", "venue": "Old display"},
        )
        self.assertEqual(result["publication_type"], "conference")
        self.assertEqual(result["raw_venue"], "2024 IEEE/CVF CVPR Workshops")
        self.assertEqual(result["venue_id"], "venue:cvpr:workshops")
        replaced = apply_canonical_venue_selection(
            {**selection, "raw_venue": "Reviewed replacement", "replace_raw_venue": True},
            existing={"raw_venue": "Historical source"},
        )
        self.assertEqual(replaced["raw_venue"], "Reviewed replacement")

    def test_structured_selection_requires_consistent_complete_metadata(self):
        with self.assertRaisesRegex(CuratedPaperError, "venue_acronym must match"):
            apply_canonical_venue_selection({
                "venue_id": "venue:chi:main",
                "venue_name": "CHI Conference on Human Factors in Computing Systems",
                "venue_type": "conference",
                "venue_track": "main",
                "publication_type": "conference",
            })

    def test_publication_type_conflict_requires_explicit_override(self):
        selection = {
            "venue_id": "venue:chi:main",
            "venue_name": "CHI Conference on Human Factors in Computing Systems",
            "venue_acronym": "CHI",
            "venue_type": "conference",
            "venue_track": "main",
            "publication_type": "journal",
        }
        with self.assertRaisesRegex(CuratedPaperError, "explicit override"):
            apply_canonical_venue_selection(selection)
        overridden = apply_canonical_venue_selection(
            {**selection, "publication_type_override": True}
        )
        self.assertEqual(overridden["publication_type"], "journal")


if __name__ == "__main__":
    unittest.main()
