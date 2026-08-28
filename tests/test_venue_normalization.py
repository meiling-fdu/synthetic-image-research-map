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
    canonicalize_record,
    canonical_venue_options,
    create_canonical_venue,
    display_venue,
    materialize_canonical_venue_metadata,
    read_venue_aliases,
    resolve_venue,
    venue_type_rank,
)


class VenueNormalizationTests(unittest.TestCase):
    def test_blank_nonconference_venues_remain_trackless(self):
        for venue_type in ("journal", "book", "preprint"):
            with self.subTest(venue_type=venue_type):
                venue = resolve_venue("", venue_type=venue_type)

                self.assertEqual(venue.venue_type, venue_type)
                self.assertEqual(venue.venue_track, "")
                self.assertEqual(venue.venue_id, "")

    def test_canonicalization_is_idempotent_without_internal_alias_field(self):
        aliases = read_venue_aliases()
        first = canonicalize_record(
            {
                "venue": "2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)",
                "publication_type": "conference",
            },
            aliases,
        )
        second = canonicalize_record(first, aliases)

        self.assertNotIn("aliases", first)
        self.assertEqual(second, first)

    def resolve(self, raw, publication_type="conference"):
        return resolve_venue(raw, publication_type=publication_type, aliases=read_venue_aliases())

    def test_unmapped_venue_does_not_alternate_between_raw_text_and_generated_id(self):
        raw = "Proceedings of the Fifteenth Unregistered Example Conference"
        first = canonicalize_record({"venue": raw, "publication_type": "conference"}, [])
        self.assertNotIn("venue_id", first)
        self.assertEqual(first["venue"], raw)
        current = first
        for _ in range(3):
            current = canonicalize_record(current, [])
            self.assertEqual(current, first)

    def test_year_proceedings_ordinal_and_acronym_normalize(self):
        venue = self.resolve("2026 Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")
        self.assertEqual(venue.venue_id, "venue:cvpr")
        self.assertEqual(venue.venue_name, "IEEE/CVF Conference on Computer Vision and Pattern Recognition")
        self.assertEqual(venue.venue_acronym, "CVPR")
        self.assertEqual(venue.raw_venue, "2026 Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")

    def test_tracks_share_canonical_identity(self):
        main = self.resolve("2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)")
        workshops = self.resolve("2026 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops")
        findings = self.resolve("2026 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Findings")
        self.assertEqual({main.venue_track, workshops.venue_track, findings.venue_track}, {"main", "workshops", "findings"})
        self.assertEqual({main.venue_id, workshops.venue_id, findings.venue_id}, {"venue:cvpr"})
        self.assertEqual(workshops.venue_type, "conference")

    def test_wacv_workshop_shares_canonical_identity(self):
        main = self.resolve("2025 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)")
        workshop = self.resolve("2026 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) Workshop")
        self.assertEqual(main.venue_id, "venue:wacv")
        self.assertEqual(workshop.venue_id, "venue:wacv")
        self.assertEqual((main.venue_track, workshop.venue_track), ("main", "workshops"))

    def test_iccv_workshops_and_icip_editions_reuse_canonical_ids(self):
        iccv_workshop = self.resolve(
            "2023 IEEE/CVF International Conference on Computer Vision Workshops (ICCVW)"
        )
        icip = self.resolve(
            "2024 IEEE International Conference on Image Processing (ICIP)"
        )
        self.assertEqual(iccv_workshop.venue_id, "venue:iccv")
        self.assertEqual(iccv_workshop.venue_acronym, "ICCV")
        self.assertEqual(iccv_workshop.venue_track, "workshops")
        self.assertEqual(
            icip.venue_id,
            "venue:ieee-international-conference-on-image-processing",
        )
        self.assertEqual(
            icip.venue_name,
            "IEEE International Conference on Image Processing",
        )
        self.assertEqual(icip.venue_track, "main")

    def test_ijcnn_variants_resolve_to_one_main_venue(self):
        variants = [
            "International Joint Conference on Neural Networks",
            "International Joint Conference on Neural Networks (IJCNN)",
            "2025 International Joint Conference on Neural Networks (IJCNN)",
            "Proceedings of the 2024 International Joint Conference on Neural Networks",
            "IJCNN - 2025 International Joint Conference on Neural Networks (IJCNN)",
            "IJCNN: International Joint Conference on Neural Networks",
        ]
        venues = [self.resolve(value) for value in variants]
        self.assertEqual({venue.venue_id for venue in venues}, {"venue:ijcnn"})
        self.assertEqual({venue.venue_name for venue in venues}, {"International Joint Conference on Neural Networks"})
        self.assertEqual({venue.venue_acronym for venue in venues}, {"IJCNN"})
        self.assertEqual({venue.venue_track for venue in venues}, {"main"})

    def test_icmr_uses_correct_acm_full_name_and_acronym(self):
        variants = [
            "International Conference on Multimedia Retrieval",
            "International Conference on Multimedia Retrieval (ICMR)",
            "ACM International Conference on Multimedia Retrieval",
            "ACM International Conference on Multimedia Retrieval (ICMR)",
            "Proceedings of the 2026 International Conference on Multimedia Retrieval (ICMR)",
            "Proceedings of the 2022 ACM International Conference on Multimedia Retrieval",
        ]
        venues = [self.resolve(value) for value in variants]
        self.assertEqual({venue.venue_id for venue in venues}, {"venue:icmr"})
        self.assertEqual({venue.venue_name for venue in venues}, {"ACM International Conference on Multimedia Retrieval"})
        self.assertEqual({venue.venue_acronym for venue in venues}, {"ICMR"})
        self.assertEqual(display_venue(venues[0].as_record()), "ACM International Conference on Multimedia Retrieval (ICMR)")

    def test_wacvw_aliases_resolve_to_wacv_workshops(self):
        variants = [
            "IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) · Workshops",
            "IEEE/CVF Winter Conference on Applications of Computer Vision (WACVW) Workshops",
            "IEEE/CVF Winter Conference on Applications of Computer Vision Workshops (WACVW)",
            "2025 IEEE/CVF Winter Conference on Applications of Computer Vision Workshops (WACVW)",
            "Proceedings of the 2025 IEEE/CVF Winter Conference on Applications of Computer Vision Workshop (WACVW)",
        ]
        venues = [self.resolve(value) for value in variants]
        self.assertEqual({venue.venue_id for venue in venues}, {"venue:wacv"})
        self.assertEqual({venue.venue_acronym for venue in venues}, {"WACV"})
        self.assertEqual({venue.venue_track for venue in venues}, {"workshops"})
        self.assertEqual(
            display_venue(venues[0].as_record()),
            "IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) · Workshops",
        )

    def test_malformed_inter_national_machine_vision_is_reviewed_alias(self):
        venue = self.resolve("17th Inter national Conference on Machine Vision")
        self.assertEqual(venue.venue_id, "venue:international-conference-on-machine-vision")
        self.assertEqual(venue.venue_name, "International Conference on Machine Vision")
        self.assertEqual(venue.raw_venue, "17th Inter national Conference on Machine Vision")

    def test_icml_edition_and_neurips_volume(self):
        self.assertEqual(self.resolve("Proceedings of the 42nd International Conference on Machine Learning").venue_id, "venue:icml")
        self.assertEqual(self.resolve("Advances in Neural Information Processing Systems 37").venue_id, "venue:neurips")

    def test_ih_mmsec_year_and_proceedings(self):
        first = self.resolve("2026 ACM Workshop on Information Hiding and Multimedia Security (IH&MMSec)")
        second = self.resolve("Proceedings of the 2026 ACM Workshop on Information Hiding and Multimedia Security (IH&MMSec)")
        self.assertEqual(first.venue_id, "venue:ih-mmsec")
        self.assertEqual(second.venue_id, first.venue_id)
        self.assertEqual(first.venue_type, "conference")
        self.assertEqual(first.venue_track, "workshops")

    def test_journal_is_stable_and_article_reuses_journal_label(self):
        venue = self.resolve("Pattern Recognition", publication_type="article")
        self.assertEqual(venue.venue_name, "Pattern Recognition")
        self.assertEqual(venue.venue_type, "journal")
        self.assertEqual(venue.venue_track, "")
        self.assertEqual(venue.venue_id, "venue:pattern-recognition")

    def test_reported_journals_are_trackless_and_tracks_are_canonical(self):
        cviu = self.resolve(
            "Computer Vision and Image Understanding",
            publication_type="journal",
        )
        sensors = self.resolve("Sensors", publication_type="journal")
        self.assertEqual(
            cviu.venue_id, "venue:computer-vision-and-image-understanding"
        )
        self.assertEqual(sensors.venue_id, "venue:sensors")
        self.assertEqual(cviu.venue_track, "")
        self.assertEqual(sensors.venue_track, "")

        siggraph = self.resolve(
            "ACM SIGGRAPH Posters", publication_type="conference"
        )
        cvpr = self.resolve(
            "IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Findings",
            publication_type="conference",
        )
        self.assertEqual(siggraph.venue_id, "venue:siggraph:posters")
        self.assertEqual(siggraph.venue_track, "posters")
        self.assertEqual(cvpr.venue_id, "venue:cvpr")

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
        self.assertIn("previous_venue_id", report["audit"][0])
        self.assertIn("proposed_canonical_venue_id", report["audit"][0])
        self.assertIn("applied_alias_or_rule", report["audit"][0])
        self.assertIn("inventory_scan", report)
        self.assertEqual(second_report["records_changed"], 0)
        self.assertEqual(migrated, second)

    def test_targeted_venue_migration_is_idempotent_and_preserves_raw_provenance(self):
        rows = [
            {
                "paper_id": "icmr",
                "title": "ICMR paper",
                "year": "2026",
                "venue": "International Conference on Multimedia Retrieval",
                "venue_id": "venue:icmr:main",
                "venue_name": "International Conference on Multimedia Retrieval",
                "venue_acronym": "ICMR",
                "venue_type": "conference",
                "venue_track": "main",
                "raw_venue": "Proceedings of the 2026 International Conference on Multimedia Retrieval (ICMR)",
                "publication_type": "conference",
            },
            {
                "paper_id": "wacvw",
                "title": "WACVW paper",
                "year": "2025",
                "venue": "IEEE/CVF Winter Conference on Applications of Computer Vision",
                "venue_id": "venue:ieee-cvf-winter-conference-on-applications-of-computer-vision:workshops",
                "venue_name": "IEEE/CVF Winter Conference on Applications of Computer Vision",
                "venue_acronym": "WACVW",
                "venue_type": "conference",
                "venue_track": "workshops",
                "raw_venue": "2025 IEEE/CVF Winter Conference on Applications of Computer Vision Workshops (WACVW)",
                "publication_type": "conference",
            },
            {
                "paper_id": "machine-vision",
                "title": "Machine vision paper",
                "year": "2024",
                "venue": "Inter national Conference on Machine Vision",
                "venue_id": "venue:inter-national-conference-on-machine-vision:main",
                "venue_name": "Inter national Conference on Machine Vision",
                "venue_acronym": "",
                "venue_type": "conference",
                "venue_track": "main",
                "raw_venue": "17th Inter national Conference on Machine Vision",
                "publication_type": "conference",
            },
        ]
        migrated, report = migrate_rows(rows)
        second, second_report = migrate_rows(migrated)
        by_paper = {row["paper_id"]: row for row in migrated}
        self.assertEqual(by_paper["icmr"]["venue_name"], "ACM International Conference on Multimedia Retrieval")
        self.assertEqual(by_paper["icmr"]["raw_venue"], "Proceedings of the 2026 International Conference on Multimedia Retrieval (ICMR)")
        self.assertEqual(by_paper["wacvw"]["venue_id"], "venue:wacv")
        self.assertEqual(by_paper["wacvw"]["venue_acronym"], "WACV")
        self.assertEqual(by_paper["machine-vision"]["venue_name"], "International Conference on Machine Vision")
        self.assertGreaterEqual(report["records_changed"], 3)
        self.assertEqual(second_report["records_changed"], 0)
        self.assertEqual(second, migrated)

    def test_workshop_migration_is_idempotent_and_preserves_track_identity(self):
        rows = [{
            "paper_id": "workshop-paper",
            "title": "Workshop paper",
            "year": "2024",
            "venue": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "venue_id": "venue:cvpr",
            "venue_name": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "venue_acronym": "CVPR",
            "venue_type": "workshop",
            "venue_track": "workshops",
            "raw_venue": "2024 CVPR Workshops",
            "publication_type": "conference",
        }]
        migrated, report = migrate_rows(rows)
        second, second_report = migrate_rows(migrated)
        self.assertEqual(migrated[0]["venue_id"], "venue:cvpr")
        self.assertEqual(migrated[0]["venue_type"], "conference")
        self.assertEqual(migrated[0]["venue_track"], "workshops")
        self.assertEqual(report["workshop_records_migrated"], 1)
        self.assertEqual(second_report["workshop_records_migrated"], 0)
        self.assertEqual(second_report["records_changed"], 0)
        self.assertEqual(migrated, second)

    def test_admin_options_are_canonical_counted_and_searchable(self):
        aliases = read_venue_aliases()
        papers = [
            {"paper_id": "one", "venue_id": "venue:cvpr", "raw_venue": "2024 CVPR Workshops"},
            {"paper_id": "two", "venue_id": "venue:cvpr", "raw_venue": "CVPRW"},
        ]
        options = canonical_venue_options(aliases, papers)
        workshops = next(option for option in options if option["venue_id"] == "venue:cvpr")
        self.assertEqual(workshops["paper_count"], 2)
        self.assertEqual(workshops["venue_track"], "")
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
                "alias": "First Journal", "venue_id": "venue:first",
                "venue_name": "First Journal", "venue_acronym": "DUP",
                "venue_type": "journal", "venue_track": "",
                "review_status": "confirmed", "notes": "",
            },
            {
                "alias": "Second Journal", "venue_id": "venue:second",
                "venue_name": "Second Journal", "venue_acronym": "DUP",
                "venue_type": "journal", "venue_track": "",
                "review_status": "confirmed", "notes": "",
            },
        ]
        with self.assertRaisesRegex(VenueRegistryError, "acronym.*collides"):
            canonical_venue_options(collision_rows)

    def test_acronym_collision_is_rejected_before_registry_write(self):
        existing = {
            "alias": "First Journal", "venue_id": "venue:first",
            "venue_name": "First Journal", "venue_acronym": "DUP",
            "venue_type": "journal", "venue_track": "",
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
                    "venue_track": "",
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
            "venue_id": "venue:cvpr",
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
        self.assertEqual(result["venue_id"], "venue:cvpr")
        replaced = apply_canonical_venue_selection(
            {**selection, "raw_venue": "Reviewed replacement", "replace_raw_venue": True},
            existing={"raw_venue": "Historical source"},
        )
        self.assertEqual(replaced["raw_venue"], "Reviewed replacement")

    def test_structured_selection_materializes_stale_same_id_metadata(self):
        result = apply_canonical_venue_selection({
            "venue_id": "venue:chi",
            "venue_name": "Old Name",
            "venue_acronym": "OLD",
            "venue_type": "workshop",
            "venue_track": "workshops",
            "publication_type": "conference",
        })
        self.assertEqual(
            result["venue_name"],
            "CHI Conference on Human Factors in Computing Systems",
        )
        self.assertEqual(result["venue_acronym"], "CHI")
        self.assertEqual(result["venue_type"], "conference")
        self.assertEqual(result["venue_track"], "workshops")

    def test_same_id_materialization_is_idempotent_and_normalizes_tracks(self):
        aliases = read_venue_aliases()
        stale = {
            "venue_id": "venue:chi",
            "venue_name": " Old Name ",
            "venue_acronym": "OLD",
            "venue_type": "workshop",
            "venue_track": " ",
            "unrelated": "preserved",
        }
        first = materialize_canonical_venue_metadata(stale, aliases)
        second = materialize_canonical_venue_metadata(first, aliases)
        self.assertEqual(second, first)
        self.assertEqual(first["venue_track"], "main")
        self.assertEqual(first["unrelated"], "preserved")
        journal = materialize_canonical_venue_metadata({
            "venue_id": "venue:ieee-transactions-on-multimedia",
            "venue_track": "main",
        }, aliases)
        self.assertEqual(journal["venue_track"], "")

    def test_same_id_materialization_rejects_dangling_id(self):
        with self.assertRaisesRegex(VenueRegistryError, "does not exist"):
            materialize_canonical_venue_metadata(
                {"venue_id": "venue:missing"}, read_venue_aliases()
            )

    def test_publication_type_conflict_requires_explicit_override(self):
        selection = {
            "venue_id": "venue:chi",
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
