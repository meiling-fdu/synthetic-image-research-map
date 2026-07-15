import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import (
    CuratedInstitutionError,
    add_institution_alias,
    effective_location,
    ignore_institution,
    merge_institutions,
    stable_institution_id,
    update_institution_location,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_AUDIT_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_HIERARCHY_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
)
from scripts.export_public_preview import exclude_nonpublic_institutions, public_institution_aliases
from scripts.validate_curated_database import validate_institution_entities


CERTH = "Centre for Research and Technology Hellas (CERTH)"
AMAZON = "Amazon"


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def blank(columns, **values):
    return {column: values.get(column, "") for column in columns}


class InstitutionManagementTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.certh_id = stable_institution_id(CERTH)
        self.amazon_id = stable_institution_id(AMAZON)
        self.institutions = self.root / "institutions.csv"
        self.locations = self.root / "locations.csv"
        self.mappings = self.root / "mappings.csv"
        self.aliases = self.root / "aliases.csv"
        self.audits = self.root / "audit.csv"
        self.location_reviews = self.root / "location_reviews.csv"
        self.hierarchy = self.root / "hierarchy.csv"
        self.review_queue = self.root / "review_queue.csv"
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            blank(INSTITUTION_COLUMNS, institution_id=self.certh_id, canonical_name=CERTH, institution_type="institute", institution_status="active", public_display="self"),
            blank(INSTITUTION_COLUMNS, institution_id=self.amazon_id, canonical_name=AMAZON, institution_type="company", institution_status="active", public_display="self"),
        ])
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            blank(INSTITUTION_LOCATION_COLUMNS, location_id="location:amazon", institution_id=self.amazon_id, institution=AMAZON, normalized_institution="amazon", city="Seattle", country="United States", country_code="US", lat="47", lon="-122", coordinate_status="known"),
        ])
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            blank(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:certh", paper_id="paper:1", title="AI-Generated Image Detection: Challenges and Recent Advances", institution=CERTH, institution_id=self.certh_id, institution_authors="Symeon Papadopoulos; Vasileios Mezaris", raw_affiliation="Information Technologies Institute, Centre for Research and Technology Hellas (CERTH)", mapping_status="active"),
        ])
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [])
        write_csv(self.audits, INSTITUTION_AUDIT_COLUMNS, [])
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [])
        write_csv(self.hierarchy, INSTITUTION_HIERARCHY_COLUMNS, [])
        write_csv(self.review_queue, INSTITUTION_REVIEW_QUEUE_COLUMNS, [])

    def tearDown(self):
        self.temporary.cleanup()

    def test_certh_affiliation_cannot_resolve_to_amazon(self):
        with self.assertRaisesRegex(CuratedInstitutionError, "alias already resolves|alias must differ|another"):
            add_institution_alias(
                self.amazon_id, CERTH,
                institutions_path=self.institutions,
                aliases_path=self.aliases,
            )
        # A canonical institution name is protected even before an alias exists.
        with self.aliases.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), [])

    def test_editing_amazon_coordinates_does_not_modify_certh_mapping(self):
        before = self.mappings.read_bytes()
        update_institution_location(
            self.amazon_id,
            {"institution_id": self.amazon_id, "city": "Beijing", "lat": "39.9", "lon": "116.4"},
            institutions_path=self.institutions,
            locations_path=self.locations,
        )
        self.assertEqual(self.mappings.read_bytes(), before)
        with self.assertRaisesRegex(CuratedInstitutionError, "cannot change institution_id"):
            update_institution_location(
                self.amazon_id,
                {"institution_id": self.certh_id, "lat": "1", "lon": "2"},
                institutions_path=self.institutions,
                locations_path=self.locations,
            )

    def test_location_save_requires_bound_known_id_and_updates_matching_review_only(self):
        before = {
            "institutions": self.institutions.read_bytes(),
            "aliases": self.aliases.read_bytes(),
            "mappings": self.mappings.read_bytes(),
            "hierarchy": self.hierarchy.read_bytes(),
        }
        with self.assertRaisesRegex(CuratedInstitutionError, "institution_id is required"):
            update_institution_location(
                self.amazon_id, {"institution_id": "", "city": "Seattle"},
                institutions_path=self.institutions, locations_path=self.locations,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "identify exactly one"):
            update_institution_location(
                "institution:missing", {"institution_id": "institution:missing"},
                institutions_path=self.institutions, locations_path=self.locations,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "differs from the institution loaded"):
            update_institution_location(
                self.amazon_id,
                {"institution_id": self.amazon_id, "loaded_institution_id": self.certh_id},
                institutions_path=self.institutions, locations_path=self.locations,
            )
        updated = update_institution_location(
            self.amazon_id,
            {
                "institution_id": self.amazon_id,
                "loaded_institution_id": self.amazon_id,
                "city": "Seattle", "region": "Washington",
                "country": "United States", "country_code": "US",
                "lat": "47.6", "lon": "-122.3", "review_note": "Confirmed manually.",
            },
            institutions_path=self.institutions, locations_path=self.locations,
            location_reviews_path=self.location_reviews,
        )
        self.assertEqual(updated["institution_id"], self.amazon_id)
        with self.location_reviews.open(encoding="utf-8", newline="") as handle:
            review = next(csv.DictReader(handle))
        self.assertEqual(review["institution_id"], self.amazon_id)
        self.assertEqual(review["review_status"], "confirmed")
        for name, content in before.items():
            self.assertEqual(getattr(self, name).read_bytes(), content)

    def test_ignoring_institution_removes_it_from_public_export(self):
        ignore_institution(
            self.certh_id, confirmation=True, review_note="Not public",
            institutions_path=self.institutions, mappings_path=self.mappings,
            audit_path=self.audits,
        )
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            entities = list(csv.DictReader(handle))
        papers, maps, removed = exclude_nonpublic_institutions(
            [{"affiliations": [{"index": 1, "institution_id": self.certh_id}], "author_institution_affiliations": [{"index": 1, "institution_id": self.certh_id}]}],
            [{"institution_id": self.certh_id}], entities,
        )
        self.assertEqual(maps, [])
        self.assertEqual(papers[0]["affiliations"], [])
        self.assertEqual(removed, 1)

    def test_parent_location_inheritance(self):
        institutions = [
            {"institution_id": self.certh_id, "parent_institution_id": ""},
            {"institution_id": "institution:iti", "parent_institution_id": self.certh_id},
        ]
        location = effective_location("institution:iti", institutions, [{"institution_id": self.certh_id, "city": "Thessaloniki"}])
        self.assertEqual(location["city"], "Thessaloniki")
        self.assertEqual(location["inherited_from_institution_id"], self.certh_id)

    def test_alias_resolution_uses_stable_canonical_id(self):
        alias = add_institution_alias(
            self.certh_id, "Information Technologies Institute",
            institutions_path=self.institutions, aliases_path=self.aliases,
        )
        exported = public_institution_aliases([alias])
        self.assertEqual(exported[0]["canonical_institution_id"], self.certh_id)

    def test_institution_merge_requires_exact_confirmation_and_audits(self):
        with self.assertRaisesRegex(CuratedInstitutionError, "exact confirmation"):
            merge_institutions(
                self.certh_id, self.amazon_id, confirmation=True, review_note="Wrong",
                institutions_path=self.institutions, mappings_path=self.mappings,
                aliases_path=self.aliases, audit_path=self.audits,
            )
        with self.mappings.open(encoding="utf-8", newline="") as handle:
            mapping = next(csv.DictReader(handle))
        self.assertEqual(mapping["institution_id"], self.certh_id)

    def test_merge_atomically_rebinds_dependent_institution_references(self):
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                institution=CERTH,
                canonical_institution_name=CERTH,
                institution_id=self.certh_id,
                related_paper_id="paper:1",
                title="AI-Generated Image Detection: Challenges and Recent Advances",
                year="2026",
                institution_authors="Symeon Papadopoulos; Vasileios Mezaris",
                raw_affiliation="Information Technologies Institute, CERTH",
                review_status="needs_coordinates",
                location_status="missing",
                coordinate_status="missing",
            ),
        ])
        write_csv(self.hierarchy, INSTITUTION_HIERARCHY_COLUMNS, [
            blank(
                INSTITUTION_HIERARCHY_COLUMNS,
                parent_institution_id=self.certh_id,
                child_institution_id="institution:unit",
                relationship_type="research_unit",
                review_status="confirmed",
            ),
        ])
        write_csv(self.review_queue, INSTITUTION_REVIEW_QUEUE_COLUMNS, [
            blank(
                INSTITUTION_REVIEW_QUEUE_COLUMNS,
                current_institution=CERTH,
                current_institution_id=self.certh_id,
            ),
        ])

        merge_institutions(
            self.certh_id,
            self.amazon_id,
            confirmation=f"REPLACE {CERTH} WITH {AMAZON} GLOBALLY",
            review_note="Confirmed stale canonical entity.",
            institutions_path=self.institutions,
            mappings_path=self.mappings,
            aliases_path=self.aliases,
            locations_path=self.locations,
            location_reviews_path=self.location_reviews,
            hierarchy_path=self.hierarchy,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )

        with self.mappings.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["institution_id"], self.amazon_id)
        with self.location_reviews.open(encoding="utf-8", newline="") as handle:
            review = next(csv.DictReader(handle))
        self.assertEqual(review["institution_id"], self.amazon_id)
        self.assertEqual(review["canonical_institution_name"], AMAZON)
        with self.hierarchy.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["parent_institution_id"], self.amazon_id)
        with self.review_queue.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["current_institution_id"], self.amazon_id)
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            entities = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(entities[self.certh_id]["institution_status"], "merged")
        self.assertIn(self.amazon_id, entities)

    def test_validator_rejects_true_mapping_and_location_review_orphans(self):
        institutions = [
            blank(
                INSTITUTION_COLUMNS,
                institution_id=self.certh_id,
                canonical_name=CERTH,
                institution_type="institute",
                institution_status="active",
            )
        ]
        orphan_id = "institution:missing"
        issues = []
        validate_institution_entities(
            institutions,
            [blank(AUTHOR_INSTITUTION_MAPPING_COLUMNS, institution_id=orphan_id)],
            [],
            [blank(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution_id=orphan_id)],
            [],
            [],
            issues,
        )
        self.assertEqual(
            [issue.filename for issue in issues if "unknown institution_id" in issue.message],
            ["author_institution_mappings.csv", "institution_location_review.csv"],
        )


class CerthRepositoryRegressionTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_certh_repair_is_not_exported_as_amazon(self):
        with (self.root / "data/curated/institution_aliases.csv").open(encoding="utf-8", newline="") as handle:
            aliases = list(csv.DictReader(handle))
        self.assertFalse(any(
            row["alias_name"] == CERTH and row["canonical_institution_name"] == AMAZON
            for row in aliases
        ))
        payload = json.loads((self.root / "web/data/public_preview_map_data.json").read_text())
        records = [
            row for row in payload["records"]
            if row.get("title") == "AI-Generated Image Detection: Challenges and Recent Advances"
        ]
        self.assertFalse(any(
            row.get("institution") == AMAZON
            and "Symeon Papadopoulos" in (row.get("institution_authors") or [])
            for row in records
        ))


if __name__ == "__main__":
    unittest.main()
