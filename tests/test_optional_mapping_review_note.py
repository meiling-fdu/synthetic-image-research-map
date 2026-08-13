import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_mappings import (
    CuratedMappingError,
    canonical_institution_authors,
    create_mapping,
    exclude_mapping,
    load_mappings,
    replace_all_mappings,
    update_mapping,
)
from scripts.curated_locations import location_review_report
from scripts.curated_institutions import stable_institution_id
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)
from scripts.validate_curated_database import validate_mapping_evidence


def write_empty_csv(path, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=columns).writeheader()


class SimplifiedMappingSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.mappings_path = directory / "mappings.csv"
        self.locations_path = directory / "locations.csv"
        self.confirmed_locations_path = directory / "confirmed_locations.csv"
        self.institutions_path = directory / "institutions.csv"
        self.aliases_path = directory / "aliases.csv"
        self.audits_path = directory / "audits.csv"
        write_empty_csv(self.mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_empty_csv(self.locations_path, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        institution_id = stable_institution_id("Example University")
        with self.confirmed_locations_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=INSTITUTION_LOCATION_COLUMNS)
            writer.writeheader()
            for location_id, city, lat, lon in (
                ("location:shanghai", "Shanghai", "31.2304", "121.4737"),
                ("location:beijing", "Beijing", "39.9042", "116.4074"),
                ("location:old", "Old City", "10", "20"),
                ("location:new", "New City", "11", "21"),
            ):
                writer.writerow({
                    **{column: "" for column in INSTITUTION_LOCATION_COLUMNS},
                    "location_id": location_id,
                    "institution_id": institution_id,
                    "institution": "Example University",
                    "city": city,
                    "country": "Example Country",
                    "lat": lat,
                    "lon": lon,
                    "coordinate_status": "known",
                })
        write_empty_csv(self.institutions_path, INSTITUTION_COLUMNS)
        write_empty_csv(self.aliases_path, INSTITUTION_ALIAS_COLUMNS)
        write_empty_csv(self.audits_path, INSTITUTION_AUDIT_COLUMNS)
        self.paper = {
            "paper_id": "curated:test",
            "title": "Test paper",
            "year": "2026",
        }
        self.draft = {
            "institution": "Example University",
            "institution_authors": "Researcher One",
            "raw_affiliation": "Department of Vision, Example University",
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create(self, draft):
        institution = draft.get("institution")
        if institution:
            with self.institutions_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            institution_id = stable_institution_id(institution)
            if not any(row["institution_id"] == institution_id for row in rows):
                rows.append({
                    **{column: "" for column in INSTITUTION_COLUMNS},
                    "institution_id": institution_id,
                    "canonical_name": institution,
                    "institution_type": "university",
                    "institution_status": "active",
                    "public_display": "self",
                })
                with self.institutions_path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=INSTITUTION_COLUMNS)
                    writer.writeheader()
                    writer.writerows(rows)
        return create_mapping(
            self.paper,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_aliases_path=self.aliases_path,
            institution_locations_path=self.confirmed_locations_path,
        )["mapping"]

    def update(self, mapping_id, draft):
        return update_mapping(
            self.paper,
            mapping_id,
            draft,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_aliases_path=self.aliases_path,
            institution_locations_path=self.confirmed_locations_path,
            institution_audit_path=self.audits_path,
        )["mapping"]

    def test_create_and_update_drop_obsolete_payload_fields(self):
        obsolete = {
            "evidence_source": "Publisher PDF",
            "evidence_url": "https://example.test/paper.pdf",
            "affiliation_note": "Legacy duplicate note",
            "review_note": "Legacy mapping note",
        }
        mapping = self.create({**self.draft, **obsolete})
        self.assertTrue(set(mapping).isdisjoint(obsolete))
        updated = self.update(mapping["mapping_id"], {**self.draft, **obsolete})
        self.assertEqual(updated["mapping_id"], mapping["mapping_id"])
        self.assertTrue(set(load_mappings(self.mappings_path)[0]).isdisjoint(obsolete))

    def test_legacy_csv_header_is_loaded_and_migrated_without_losing_rows(self):
        obsolete = ["evidence_source", "evidence_url", "affiliation_note", "review_note"]
        legacy_columns = list(AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        insertion = legacy_columns.index("mapping_status")
        legacy_columns[insertion:insertion] = obsolete
        legacy = {
            **{column: "" for column in legacy_columns},
            "mapping_id": "mapping:legacy",
            "paper_id": self.paper["paper_id"],
            "title": self.paper["title"],
            "year": self.paper["year"],
            "institution": "Example University",
            "institution_id": stable_institution_id("Example University"),
            "institution_authors": "Researcher One",
            "raw_affiliation": self.draft["raw_affiliation"],
            "mapping_status": "active",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "evidence_source": "legacy source",
            "evidence_url": "https://example.test/legacy",
            "affiliation_note": "legacy affiliation note",
            "review_note": "legacy review note",
        }
        with self.mappings_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=legacy_columns)
            writer.writeheader()
            writer.writerow(legacy)

        loaded = load_mappings(self.mappings_path)
        self.assertEqual([row["mapping_id"] for row in loaded], ["mapping:legacy"])
        from scripts.curated_mappings import save_mappings
        save_mappings(loaded, self.mappings_path)
        with self.mappings_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        self.assertEqual(tuple(reader.fieldnames), AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        self.assertEqual([row["mapping_id"] for row in rows], ["mapping:legacy"])

    def test_alias_only_edit_keeps_canonical_identity_without_change_audit(self):
        canonical = "Polytechnic University of Hauts-de-France"
        alias = "University Polytechnique Hauts-de-France"
        mapping = self.create({
            **self.draft,
            "institution": canonical,
            "provenance_source": "manually_confirmed",
        })
        with self.aliases_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=INSTITUTION_ALIAS_COLUMNS)
            writer.writeheader()
            writer.writerow({
                **{column: "" for column in INSTITUTION_ALIAS_COLUMNS},
                "alias_id": "alias:university-polytechnique",
                "alias_name": alias,
                "institution_id": mapping["institution_id"],
                "canonical_institution_name": canonical,
                "alias_source": "publisher-affiliation",
                "review_status": "confirmed",
            })

        updated = self.update(mapping["mapping_id"], {
            **self.draft,
            "institution": alias,
            "institution_id": "alias:university-polytechnique",
            "provenance_source": "manually_confirmed",
        })

        self.assertEqual(updated["mapping_id"], mapping["mapping_id"])
        self.assertEqual(updated["institution_id"], mapping["institution_id"])
        self.assertEqual(updated["institution"], canonical)
        with self.audits_path.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), [])

    def test_location_only_mapping_change_writes_exact_transition_evidence(self):
        mapping = self.create({
            **self.draft,
            "location_id": "location:shanghai",
            "provenance_source": "manually_confirmed",
        })
        self.update(mapping["mapping_id"], {
            **self.draft,
            "location_id": "location:beijing",
            "provenance_source": "manually_confirmed",
        })
        with self.audits_path.open(encoding="utf-8", newline="") as handle:
            audits = list(csv.DictReader(handle))
        self.assertEqual(len(audits), 1)
        audit = audits[0]
        self.assertEqual(audit["paper_id"], "curated:test")
        self.assertEqual(audit["previous_mapping_id"], mapping["mapping_id"])
        self.assertEqual(audit["mapping_id"], mapping["mapping_id"])
        self.assertEqual(audit["previous_location_id"], "location:shanghai")
        self.assertEqual(audit["location_id"], "location:beijing")
        self.assertEqual(audit["previous_authors"], "Researcher One")
        self.assertEqual(audit["new_authors"], "Researcher One")

    def test_explicit_mapping_exclusion_writes_exact_removal_evidence(self):
        mapping = self.create({
            **self.draft, "provenance_source": "manually_confirmed"
        })
        exclude_mapping(
            self.paper, mapping["mapping_id"], "Reviewed true removal.",
            mappings_path=self.mappings_path,
            institution_audit_path=self.audits_path,
        )
        with self.audits_path.open(encoding="utf-8", newline="") as handle:
            audit = next(csv.DictReader(handle))
        self.assertEqual(audit["action"], "mapping_removed")
        self.assertEqual(audit["paper_id"], "curated:test")
        self.assertEqual(audit["previous_mapping_id"], mapping["mapping_id"])
        self.assertEqual(audit["previous_institution_id"], mapping["institution_id"])
        self.assertEqual(audit["previous_authors"], "Researcher One")
        self.assertEqual(audit["review_note"], "Reviewed true removal.")

    def test_mapping_update_preserves_current_location_evidence_and_derives_need(self):
        mapping = self.create(self.draft)
        with self.locations_path.open(encoding="utf-8", newline="") as handle:
            review = next(csv.DictReader(handle))
        review.update({
            "evidence_source": "Dedicated location source",
            "evidence_url": "https://example.test/location",
        })
        with self.locations_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=INSTITUTION_LOCATION_REVIEW_COLUMNS)
            writer.writeheader()
            writer.writerow(review)

        self.update(mapping["mapping_id"], self.draft)

        with self.locations_path.open(encoding="utf-8", newline="") as handle:
            saved = next(csv.DictReader(handle))
        self.assertEqual(saved["evidence_source"], "Dedicated location source")
        self.assertEqual(saved["evidence_url"], "https://example.test/location")
        self.assertNotIn("review_note", saved)
        self.assertEqual(location_review_report([saved], [])["needs_coordinates"], 1)
        with self.confirmed_locations_path.open(
            encoding="utf-8", newline=""
        ) as handle:
            confirmed = list(csv.DictReader(handle))
        self.assertEqual(
            location_review_report([saved], confirmed)["needs_coordinates"], 0
        )

    def test_mapping_authors_are_serialized_with_semicolon_delimiters(self):
        value = "Researcher One, Researcher Two, Researcher Three"
        mapping = self.create({**self.draft, "institution_authors": value})
        self.assertEqual(
            mapping["institution_authors"],
            "Researcher One; Researcher Two; Researcher Three",
        )
        self.assertEqual(
            canonical_institution_authors("Family, Given"), "Family, Given"
        )

    def test_replace_all_writes_author_scoped_replacement_evidence(self):
        mapping = self.create({
            **self.draft,
            "location_id": "location:old",
            "institution_authors": "Researcher One; Researcher Two",
            "provenance_source": "manually_confirmed",
        })
        result = replace_all_mappings(
            self.paper,
            [{
                **self.draft,
                "institution_id": mapping["institution_id"],
                "location_id": "location:new",
                "institution_authors": "Researcher One; Researcher Two",
                "provenance_source": "manually_confirmed",
            }],
            "Reviewed location replacement.",
            confirm_replace_all=True,
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_aliases_path=self.aliases_path,
            institution_locations_path=self.confirmed_locations_path,
            institution_audit_path=self.audits_path,
        )
        with self.audits_path.open(encoding="utf-8", newline="") as handle:
            audits = list(csv.DictReader(handle))
        self.assertEqual(len(audits), 2)
        self.assertEqual(
            {row["previous_authors"] for row in audits},
            {"Researcher One", "Researcher Two"},
        )
        self.assertTrue(all(
            row["previous_mapping_id"] == mapping["mapping_id"]
            and row["mapping_id"] == result["mappings"][0]["mapping_id"]
            and row["previous_location_id"] == "location:old"
            and row["location_id"] == "location:new"
            for row in audits
        ))
        self.assertTrue(all(
            row["review_note"] == "Reviewed location replacement."
            for row in audits
        ))

    def test_other_required_fields_remain_required(self):
        for field in ("institution", "institution_authors"):
            with self.subTest(field=field), self.assertRaises(CuratedMappingError):
                self.create({**self.draft, field: ""})

    def test_create_registers_unknown_institution_before_writing_mapping(self):
        result = create_mapping(
            self.paper,
            {**self.draft, "institution": "Unregistered University"},
            map_records=[],
            mappings_path=self.mappings_path,
            location_review_path=self.locations_path,
            institutions_path=self.institutions_path,
            institution_aliases_path=self.aliases_path,
        )
        self.assertEqual(result["institution_resolution"], "provisional")
        self.assertEqual(result["mapping"]["institution_id"], stable_institution_id("Unregistered University"))

    def test_active_mapping_with_raw_affiliation_passes_database_validation(self):
        issues = []

        validate_mapping_evidence(
            [{**self.draft, "mapping_status": "active"}],
            issues,
        )

        self.assertEqual(issues, [])

    def test_active_mapping_without_raw_affiliation_uses_paper_level_provenance(self):
        issues = []

        validate_mapping_evidence(
            [
                {
                    **self.draft,
                    "mapping_status": "active",
                    "raw_affiliation": "",
                }
            ],
            issues,
        )

        self.assertEqual(issues, [])

    def test_frontend_uses_compact_mapping_fields_and_no_obsolete_payload_keys(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "web" / "admin.html").read_text()
        javascript = (root / "web" / "admin.js").read_text()
        for field in ("evidence-source", "evidence-url", "affiliation-note", "review-note"):
            self.assertNotIn(f"mapping-{field}", html)
            self.assertNotIn(f"mapping-{field}", javascript)
        mapping_draft = javascript.split("function mappingDraft()", 1)[1].split(
            "async function submitMapping", 1
        )[0]
        for key in ("evidence_source", "evidence_url", "affiliation_note", "review_note"):
            self.assertNotIn(key, mapping_draft)
        self.assertIn('id="mapping-institution" type="text" list="mapping-institution-options" required', html)
        self.assertIn('id="mapping-location-id" disabled', html)
        self.assertIn(
            'id="mapping-authors" type="text" placeholder="Separate authors with semicolons" required',
            html,
        )
        self.assertIn('id="mapping-raw-affiliation" rows="2"', html)


if __name__ == "__main__":
    unittest.main()
