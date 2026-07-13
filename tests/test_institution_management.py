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
    INSTITUTION_LOCATION_COLUMNS,
)
from scripts.export_public_preview import exclude_nonpublic_institutions, public_institution_aliases


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
