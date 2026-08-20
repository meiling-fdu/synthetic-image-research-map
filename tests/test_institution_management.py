import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.curated_institutions import (
    CuratedInstitutionError,
    add_institution_alias,
    effective_location,
    ignore_institution,
    institution_impact,
    merge_institutions,
    set_parent_institution,
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
    INSTITUTION_LOCATION_AUDIT_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
    INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS,
)
from scripts.export_public_preview import exclude_nonpublic_institutions, public_institution_aliases
from scripts.serve_admin import institution_hierarchy_details
from scripts.validate_curated_database import validate_institution_entities


CERTH = "Centre for Research and Technology Hellas (CERTH)"
AMAZON = "Amazon"
ROOT = Path(__file__).resolve().parents[1]


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
        self.location_audits = self.root / "location_audits.csv"
        self.hierarchy = self.root / "hierarchy.csv"
        self.review_queue = self.root / "review_queue.csv"
        self.search_relationships = self.root / "search_relationships.csv"
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            blank(INSTITUTION_COLUMNS, institution_id=self.certh_id, canonical_name=CERTH, institution_type="institute", institution_status="active", public_display="self"),
            blank(INSTITUTION_COLUMNS, institution_id=self.amazon_id, canonical_name=AMAZON, institution_type="company", institution_status="active", public_display="self"),
        ])
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_COLUMNS,
                location_id="location:amazon",
                institution_id=self.amazon_id,
                institution=AMAZON,
                normalized_institution="amazon",
                city="Seattle",
                country="United States",
                country_code="US",
                lat="47",
                lon="-122",
                coordinate_status="known",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                created_by="test",
            ),
        ])
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            blank(AUTHOR_INSTITUTION_MAPPING_COLUMNS, mapping_id="mapping:certh", paper_id="paper:1", title="AI-Generated Image Detection: Challenges and Recent Advances", institution=CERTH, institution_id=self.certh_id, institution_authors="Symeon Papadopoulos; Vasileios Mezaris", raw_affiliation="Information Technologies Institute, Centre for Research and Technology Hellas (CERTH)", mapping_status="active"),
        ])
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [])
        write_csv(self.audits, INSTITUTION_AUDIT_COLUMNS, [])
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [])
        write_csv(self.location_audits, INSTITUTION_LOCATION_AUDIT_COLUMNS, [])
        write_csv(self.hierarchy, INSTITUTION_HIERARCHY_COLUMNS, [])
        write_csv(self.review_queue, INSTITUTION_REVIEW_QUEUE_COLUMNS, [])
        write_csv(
            self.search_relationships,
            INSTITUTION_SEARCH_RELATIONSHIP_COLUMNS,
            [],
        )

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

    def test_institution_impact_counts_actual_public_markers_when_available(self):
        mappings = [
            blank(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                mapping_id="mapping:one",
                paper_id="openalex:W1",
                institution_id=self.certh_id,
                institution=CERTH,
                institution_authors="Ada Author",
                mapping_status="active",
            ),
            blank(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                mapping_id="mapping:two",
                paper_id="openalex:W2",
                institution_id=self.certh_id,
                institution=CERTH,
                institution_authors="Grace Author",
                mapping_status="active",
            ),
        ]
        public_markers = [{
            "paper_id": "openalex:W1",
            "institution_id": self.certh_id,
            "institution": CERTH,
        }]

        impact = institution_impact(self.certh_id, mappings, public_markers)

        self.assertEqual(impact["papers"], 2)
        self.assertEqual(impact["author_mappings"], 2)
        self.assertEqual(impact["markers"], 1)

    def test_editing_amazon_coordinates_does_not_modify_certh_mapping(self):
        before = self.mappings.read_bytes()
        update_institution_location(
            self.amazon_id,
            {
                "institution_id": self.amazon_id,
                "city": "Beijing",
                "country_code": "US",
                "lat": "39.9",
                "lon": "116.4",
                "coordinate_status": "known",
            },
            institutions_path=self.institutions,
            locations_path=self.locations,
        )
        self.assertEqual(self.mappings.read_bytes(), before)
        with self.assertRaisesRegex(CuratedInstitutionError, "exactly match"):
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
        with self.assertRaisesRegex(CuratedInstitutionError, "identify exactly one"):
            update_institution_location(
                "institution:missing", {"institution_id": "institution:missing"},
                institutions_path=self.institutions, locations_path=self.locations,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "exactly match"):
            update_institution_location(
                self.amazon_id,
                {"institution_id": self.amazon_id, "loaded_institution_id": self.certh_id},
                institutions_path=self.institutions, locations_path=self.locations,
            )
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                institution=AMAZON,
                canonical_institution_name=AMAZON,
                institution_id=self.amazon_id,
                related_paper_id="paper:1",
                title="Fixture paper",
                year="2026",
                review_status="pending_review",
                location_status="missing",
                coordinate_status="missing",
            ),
        ])
        updated = update_institution_location(
            self.amazon_id,
            {
                "institution_id": self.amazon_id,
                "loaded_institution_id": self.amazon_id,
                "city": "Seattle", "region": "Washington",
                "country": "United States", "country_code": "US",
                "lat": "47.6", "lon": "-122.3",
                "coordinate_status": "known",
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

    def test_location_only_contract_persists_evidence_and_preserves_mappings(self):
        mappings_before = self.mappings.read_bytes()
        identity_audit_before = self.audits.read_bytes()
        result = update_institution_location(
            self.amazon_id,
            {
                "city": "Vancouver", "region": "British Columbia",
                "country": "Canada", "country_code": "CA",
                "lat": "49.2606", "lon": "-123.2460",
                "coordinate_status": "known",
                "created_by": "test-reviewer",
            },
            institutions_path=self.institutions,
            locations_path=self.locations,
            location_audit_path=self.location_audits,
        )
        self.assertEqual(result["institution_id"], self.amazon_id)
        self.assertEqual(self.mappings.read_bytes(), mappings_before)
        self.assertEqual(self.audits.read_bytes(), identity_audit_before)
        with self.location_audits.open(encoding="utf-8", newline="") as handle:
            evidence = next(csv.DictReader(handle))
        self.assertEqual(evidence["action"], "location_replaced")
        self.assertEqual(evidence["institution_id"], self.amazon_id)
        self.assertEqual(evidence["previous_lat"], "47")
        self.assertEqual(evidence["confirmed_lat"], "49.2606")
        self.assertEqual(evidence["created_by"], "test-reviewer")

    def test_explicit_new_location_preserves_existing_location_and_identity(self):
        institutions_before = self.institutions.read_bytes()
        mappings_before = self.mappings.read_bytes()
        result = update_institution_location(
            self.amazon_id,
            {
                "create_new_location": True,
                "city": "Vancouver", "region": "British Columbia",
                "country": "Canada", "country_code": "CA",
                "lat": "49.2606", "lon": "-123.2460",
                "coordinate_status": "known",
            },
            institutions_path=self.institutions,
            locations_path=self.locations,
        )
        with self.locations.open(encoding="utf-8", newline="") as handle:
            saved = list(csv.DictReader(handle))
        self.assertEqual(len(saved), 2)
        self.assertEqual({row["city"] for row in saved}, {"Seattle", "Vancouver"})
        self.assertEqual(result["institution_id"], self.amazon_id)
        self.assertEqual(self.institutions.read_bytes(), institutions_before)
        self.assertEqual(self.mappings.read_bytes(), mappings_before)

    def test_merge_preserves_multiple_source_locations_with_unique_ids(self):
        with self.locations.open(encoding="utf-8", newline="") as handle:
            existing = next(csv.DictReader(handle))
        second = dict(existing)
        second.update({
            "location_id": "location:amazon-vancouver", "city": "Vancouver",
            "region": "British Columbia", "country": "Canada", "country_code": "CA",
            "lat": "49.2606", "lon": "-123.2460",
        })
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [existing, second])
        merge_institutions(
            self.amazon_id, self.certh_id,
            confirmation=f"REPLACE {AMAZON} WITH {CERTH} GLOBALLY",
            review_note="Fixture merge.", institutions_path=self.institutions,
            mappings_path=self.mappings, aliases_path=self.aliases,
            locations_path=self.locations, location_reviews_path=self.location_reviews,
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )
        with self.locations.open(encoding="utf-8", newline="") as handle:
            saved = list(csv.DictReader(handle))
        self.assertEqual(len(saved), 2)
        self.assertEqual({row["institution_id"] for row in saved}, {self.certh_id})
        self.assertEqual(len({row["location_id"] for row in saved}), 2)

    def test_location_path_id_is_authoritative_and_identity_fields_are_rejected(self):
        before = self.locations.read_bytes()
        with self.assertRaisesRegex(CuratedInstitutionError, "exactly match"):
            update_institution_location(
                self.amazon_id,
                {"institution_id": self.certh_id},
                institutions_path=self.institutions,
                locations_path=self.locations,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "unsupported field"):
            update_institution_location(
                self.amazon_id,
                {"canonical_name": CERTH},
                institutions_path=self.institutions,
                locations_path=self.locations,
            )
        self.assertEqual(self.locations.read_bytes(), before)

    def test_same_name_northeastern_locations_cannot_be_cross_applied(self):
        china_id = "institution:0008285766dcabc7"
        us_id = "institution:ff1a1bc95dbe91a8"
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            blank(
                INSTITUTION_COLUMNS, institution_id=china_id,
                canonical_name="Northeastern University",
                institution_type="university", institution_status="active",
            ),
            blank(
                INSTITUTION_COLUMNS, institution_id=us_id,
                canonical_name="Northeastern University",
                institution_type="university", institution_status="active",
            ),
        ])
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_COLUMNS, location_id="location:china",
                institution_id=china_id, institution="Northeastern University",
                normalized_institution="northeastern university",
                city="Shenyang", country="China", country_code="CN",
                lat="41.7634632", lon="123.4117577",
                coordinate_status="known", created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z", created_by="test",
            ),
            blank(
                INSTITUTION_LOCATION_COLUMNS, location_id="location:us",
                institution_id=us_id, institution="Northeastern University",
                normalized_institution="northeastern university",
                city="Boston", country="United States", country_code="US",
                lat="42.3398", lon="-71.0892",
                coordinate_status="known", created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z", created_by="test",
            ),
        ])
        update_institution_location(
            us_id,
            {
                "city": "Boston", "country": "United States",
                "country_code": "US", "lat": "42.35", "lon": "-71.08",
                "coordinate_status": "known",
            },
            institutions_path=self.institutions,
            locations_path=self.locations,
        )
        with self.locations.open(encoding="utf-8", newline="") as handle:
            by_id = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(by_id[china_id]["city"], "Shenyang")
        self.assertEqual(by_id[china_id]["lat"], "41.7634632")
        self.assertEqual(by_id[us_id]["lat"], "42.35")

    def test_merged_ubc_id_cannot_receive_a_location_confirmation(self):
        with self.assertRaisesRegex(CuratedInstitutionError, "active canonical"):
            update_institution_location(
                "institution:05b67f44dd9f6846",
                {},
                institutions_path=ROOT / "data/curated/institutions.csv",
                locations_path=self.locations,
            )

    def test_direct_location_save_without_review_evidence_creates_no_review_row(self):
        update_institution_location(
            self.certh_id,
            {
                "institution_id": self.certh_id,
                "loaded_institution_id": self.certh_id,
                "city": "Thessaloniki",
                "country": "Greece",
                "country_code": "GR",
                "lat": "40.566",
                "lon": "22.997",
                "coordinate_status": "known",
            },
            institutions_path=self.institutions,
            locations_path=self.locations,
            location_reviews_path=self.location_reviews,
        )
        with self.location_reviews.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), [])

    def test_failed_location_review_write_rolls_back_location_file(self):
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                institution=AMAZON,
                canonical_institution_name=AMAZON,
                institution_id=self.amazon_id,
                related_paper_id="paper:1",
                title="Fixture paper",
                year="2026",
            ),
        ])
        before = {
            path: path.read_bytes()
            for path in (self.locations, self.location_reviews)
        }
        real_write = __import__(
            "scripts.curated_institutions", fromlist=["_write"]
        )._write

        def fail_review(path, columns, rows):
            if path == self.location_reviews:
                raise OSError("fixture review write failure")
            return real_write(path, columns, rows)

        with patch("scripts.curated_institutions._write", side_effect=fail_review):
            with self.assertRaisesRegex(OSError, "fixture review write failure"):
                update_institution_location(
                    self.amazon_id,
                    {
                        "institution_id": self.amazon_id,
                        "city": "Changed city",
                        "country_code": "US",
                        "lat": "47",
                        "lon": "-122",
                        "coordinate_status": "known",
                    },
                    institutions_path=self.institutions,
                    locations_path=self.locations,
                    location_reviews_path=self.location_reviews,
                )
        self.assertEqual(
            {path: path.read_bytes() for path in before},
            before,
        )

    def test_invalid_parent_is_rejected_without_modifying_registry(self):
        before = self.institutions.read_bytes()
        with self.assertRaisesRegex(CuratedInstitutionError, "identify exactly one"):
            set_parent_institution(
                self.certh_id,
                "institution:stale-parent",
                institutions_path=self.institutions,
            )
        self.assertEqual(self.institutions.read_bytes(), before)

    def test_parent_assignment_rejects_self_cycles_and_inactive_ids(self):
        rows = [
            blank(INSTITUTION_COLUMNS, institution_id="institution:parent", canonical_name="Parent", institution_status="active"),
            blank(INSTITUTION_COLUMNS, institution_id="institution:child", canonical_name="Child", institution_status="active", parent_institution_id="institution:parent"),
            blank(INSTITUTION_COLUMNS, institution_id="institution:merged", canonical_name="Merged", institution_status="merged"),
        ]
        write_csv(self.institutions, INSTITUTION_COLUMNS, rows)
        before = self.institutions.read_bytes()
        with self.assertRaisesRegex(CuratedInstitutionError, "own parent"):
            set_parent_institution(
                "institution:parent", "institution:parent",
                institutions_path=self.institutions, hierarchy_path=self.hierarchy,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "cycle"):
            set_parent_institution(
                "institution:parent", "institution:child",
                institutions_path=self.institutions, hierarchy_path=self.hierarchy,
            )
        with self.assertRaisesRegex(CuratedInstitutionError, "active canonical"):
            set_parent_institution(
                "institution:child", "institution:merged",
                institutions_path=self.institutions, hierarchy_path=self.hierarchy,
            )
        self.assertEqual(self.institutions.read_bytes(), before)

    def test_parent_assignment_synchronizes_registry_hierarchy_and_admin_details(self):
        child_id = "institution:iti"
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows.append(blank(
            INSTITUTION_COLUMNS,
            institution_id=child_id,
            canonical_name="Information Technologies Institute (ITI)",
            institution_status="active",
        ))
        write_csv(self.institutions, INSTITUTION_COLUMNS, rows)
        set_parent_institution(
            child_id, self.certh_id,
            institutions_path=self.institutions, hierarchy_path=self.hierarchy,
        )
        with self.hierarchy.open(encoding="utf-8", newline="") as handle:
            relationship = next(csv.DictReader(handle))
        self.assertEqual(relationship["parent_institution_id"], self.certh_id)
        self.assertEqual(relationship["child_institution_id"], child_id)
        self.assertEqual(relationship["review_status"], "confirmed")
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            entities = list(csv.DictReader(handle))
        parent_details = institution_hierarchy_details(entities, self.certh_id)
        child_details = institution_hierarchy_details(entities, child_id)
        self.assertEqual(
            [row["canonical_name"] for row in parent_details["descendants"]],
            ["Information Technologies Institute (ITI)"],
        )
        self.assertEqual(child_details["parent"]["canonical_name"], CERTH)

    def test_merging_child_preserves_parent_linkage_in_both_stores(self):
        child_id = "institution:old-iti"
        target_id = "institution:new-iti"
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows.extend([
            blank(INSTITUTION_COLUMNS, institution_id=child_id, canonical_name="Old ITI", institution_status="active", parent_institution_id=self.certh_id),
            blank(INSTITUTION_COLUMNS, institution_id=target_id, canonical_name="Information Technologies Institute", institution_status="active"),
        ])
        write_csv(self.institutions, INSTITUTION_COLUMNS, rows)
        write_csv(self.hierarchy, INSTITUTION_HIERARCHY_COLUMNS, [
            blank(INSTITUTION_HIERARCHY_COLUMNS, parent_institution_id=self.certh_id, child_institution_id=child_id, relationship_type="affiliated_institute", review_status="confirmed"),
        ])
        merge_institutions(
            child_id, target_id,
            confirmation="REPLACE Old ITI WITH Information Technologies Institute GLOBALLY",
            review_note="Fixture merge.",
            institutions_path=self.institutions, mappings_path=self.mappings,
            aliases_path=self.aliases, locations_path=self.locations,
            location_reviews_path=self.location_reviews,
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            entities = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(entities[target_id]["parent_institution_id"], self.certh_id)
        with self.hierarchy.open(encoding="utf-8", newline="") as handle:
            relationship = next(csv.DictReader(handle))
        self.assertEqual(relationship["child_institution_id"], target_id)

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
                aliases_path=self.aliases, location_audit_path=self.location_audits,
                search_relationships_path=self.search_relationships,
                audit_path=self.audits,
            )
        with self.mappings.open(encoding="utf-8", newline="") as handle:
            mapping = next(csv.DictReader(handle))
        self.assertEqual(mapping["institution_id"], self.certh_id)

    def test_merge_requires_location_resolution_and_keeps_selected_target_location(self):
        guangzhou_id = "institution:hkust-guangzhou"
        unit_id = "institution:research-unit"
        parent_id = "institution:parent"
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            institutions = list(csv.DictReader(handle))
        institutions.extend([
            blank(
                INSTITUTION_COLUMNS,
                institution_id=guangzhou_id,
                canonical_name="The Hong Kong University of Science and Technology (Guangzhou)",
                institution_status="active",
                parent_institution_id=self.amazon_id,
            ),
            blank(INSTITUTION_COLUMNS, institution_id=unit_id, canonical_name="Research Unit", institution_status="active"),
            blank(INSTITUTION_COLUMNS, institution_id=parent_id, canonical_name="Parent", institution_status="active"),
        ])
        write_csv(self.institutions, INSTITUTION_COLUMNS, institutions)
        with self.locations.open(encoding="utf-8", newline="") as handle:
            target_location = next(csv.DictReader(handle))
        source_location = blank(
            INSTITUTION_LOCATION_COLUMNS,
            location_id="location:certh",
            institution_id=self.certh_id,
            institution=CERTH,
            normalized_institution="centre for research and technology hellas certh",
            city="Thessaloniki",
            country="Greece",
            country_code="GR",
            lat="40.6401",
            lon="22.9444",
            coordinate_status="known",
        )
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [target_location, source_location])
        with self.mappings.open(encoding="utf-8", newline="") as handle:
            source_mapping = next(csv.DictReader(handle))
        source_mapping["location_id"] = source_location["location_id"]
        guangzhou_mapping = blank(
            AUTHOR_INSTITUTION_MAPPING_COLUMNS,
            mapping_id="mapping:guangzhou",
            paper_id="paper:guangzhou",
            institution="The Hong Kong University of Science and Technology (Guangzhou)",
            institution_id=guangzhou_id,
            mapping_status="active",
        )
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [source_mapping, guangzhou_mapping])
        write_csv(self.location_reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [
            blank(
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                institution=CERTH,
                canonical_institution_name=CERTH,
                institution_id=self.certh_id,
                related_paper_id="paper:1",
            ),
        ])
        write_csv(self.location_audits, INSTITUTION_LOCATION_AUDIT_COLUMNS, [
            blank(INSTITUTION_LOCATION_AUDIT_COLUMNS, audit_id="location-audit:1", institution_id=self.certh_id),
        ])
        write_csv(self.hierarchy, INSTITUTION_HIERARCHY_COLUMNS, [
            blank(INSTITUTION_HIERARCHY_COLUMNS, parent_institution_id=self.certh_id, child_institution_id=unit_id, relationship_type="unit"),
            blank(INSTITUTION_HIERARCHY_COLUMNS, parent_institution_id=parent_id, child_institution_id=self.certh_id, relationship_type="member"),
        ])
        write_csv(self.review_queue, INSTITUTION_REVIEW_QUEUE_COLUMNS, [
            blank(INSTITUTION_REVIEW_QUEUE_COLUMNS, current_institution=CERTH, current_institution_id=self.certh_id),
            blank(INSTITUTION_REVIEW_QUEUE_COLUMNS, suggested_canonical_institution=CERTH, suggested_institution_id=self.certh_id),
        ])
        tracked_paths = (
            self.institutions, self.locations, self.mappings, self.aliases,
            self.location_reviews, self.location_audits, self.hierarchy,
            self.search_relationships, self.review_queue, self.audits,
        )
        before = {path: path.read_bytes() for path in tracked_paths}

        with self.assertRaisesRegex(CuratedInstitutionError, "explicitly"):
            merge_institutions(
                self.certh_id, self.amazon_id,
                confirmation=f"REPLACE {CERTH} WITH {AMAZON} GLOBALLY",
                review_note="Confirmed duplicate.",
                institutions_path=self.institutions, mappings_path=self.mappings,
                aliases_path=self.aliases, locations_path=self.locations,
                location_reviews_path=self.location_reviews,
                location_audit_path=self.location_audits,
                hierarchy_path=self.hierarchy,
                search_relationships_path=self.search_relationships,
                review_queue_path=self.review_queue,
                audit_path=self.audits,
            )
        self.assertEqual(
            {path: path.read_bytes() for path in tracked_paths},
            before,
        )

        merge_institutions(
            self.certh_id, self.amazon_id,
            confirmation=f"REPLACE {CERTH} WITH {AMAZON} GLOBALLY",
            review_note="Confirmed duplicate.", location_resolution="keep_target",
            institutions_path=self.institutions, mappings_path=self.mappings,
            aliases_path=self.aliases, locations_path=self.locations,
            location_reviews_path=self.location_reviews,
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )

        with self.locations.open(encoding="utf-8", newline="") as handle:
            locations = list(csv.DictReader(handle))
        self.assertEqual(locations, [target_location])
        with self.mappings.open(encoding="utf-8", newline="") as handle:
            mappings = {row["mapping_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(mappings["mapping:certh"]["institution_id"], self.amazon_id)
        self.assertEqual(mappings["mapping:certh"]["institution"], AMAZON)
        self.assertEqual(mappings["mapping:certh"]["location_id"], "location:amazon")
        self.assertEqual(mappings["mapping:guangzhou"], guangzhou_mapping)
        with self.aliases.open(encoding="utf-8", newline="") as handle:
            aliases = list(csv.DictReader(handle))
        self.assertTrue(any(row["alias_name"] == CERTH and row["institution_id"] == self.amazon_id for row in aliases))
        with self.location_reviews.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["institution_id"], self.amazon_id)
        with self.location_audits.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["institution_id"], self.amazon_id)
        with self.hierarchy.open(encoding="utf-8", newline="") as handle:
            hierarchy = list(csv.DictReader(handle))
        self.assertFalse(any(self.certh_id in (row["parent_institution_id"], row["child_institution_id"]) for row in hierarchy))
        with self.review_queue.open(encoding="utf-8", newline="") as handle:
            reviews = list(csv.DictReader(handle))
        self.assertFalse(any(self.certh_id in (row["current_institution_id"], row["suggested_institution_id"]) for row in reviews))
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            saved_institutions = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(saved_institutions[self.certh_id]["institution_status"], "merged")
        self.assertEqual(saved_institutions[self.amazon_id]["institution_status"], "active")
        self.assertEqual(saved_institutions[guangzhou_id], institutions[2])

    def test_merge_can_explicitly_use_source_location(self):
        with self.locations.open(encoding="utf-8", newline="") as handle:
            target_location = next(csv.DictReader(handle))
        source_location = dict(target_location)
        source_location.update({
            "location_id": "location:certh", "institution_id": self.certh_id,
            "institution": CERTH, "city": "Thessaloniki", "country": "Greece",
            "country_code": "GR", "lat": "40.6401", "lon": "22.9444",
        })
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [target_location, source_location])

        result = merge_institutions(
            self.certh_id, self.amazon_id,
            confirmation=f"REPLACE {CERTH} WITH {AMAZON} GLOBALLY",
            review_note="Confirmed duplicate.", location_resolution="use_source",
            institutions_path=self.institutions, mappings_path=self.mappings,
            aliases_path=self.aliases, locations_path=self.locations,
            location_reviews_path=self.location_reviews,
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )

        with self.locations.open(encoding="utf-8", newline="") as handle:
            kept = next(csv.DictReader(handle))
        self.assertEqual(kept["institution_id"], self.amazon_id)
        self.assertEqual(kept["institution"], AMAZON)
        self.assertEqual(kept["city"], "Thessaloniki")
        self.assertEqual(result["location_resolution"], "use_source")

    def test_merge_atomically_rebinds_dependent_institution_references(self):
        shared_alias = "Centre for Research and Technology Hellas"
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [
            blank(
                INSTITUTION_ALIAS_COLUMNS,
                alias_id="alias:certh",
                alias_name=shared_alias,
                institution_id=self.certh_id,
                canonical_institution_name=CERTH,
                alias_source="manual-review",
                review_status="confirmed",
                notes="Confirmed from the publisher PDF.",
            ),
            blank(
                INSTITUTION_ALIAS_COLUMNS,
                alias_id="alias:certh",
                alias_name=shared_alias,
                institution_id=self.amazon_id,
                canonical_institution_name=AMAZON,
                alias_source="legacy-migration",
                review_status="confirmed",
                notes="Retained from the legacy canonical record.",
            ),
        ])
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
                review_status="pending_review",
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
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
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
        with self.aliases.open(encoding="utf-8", newline="") as handle:
            aliases = [
                row for row in csv.DictReader(handle)
                if row["alias_name"] == shared_alias
            ]
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["institution_id"], self.amazon_id)
        self.assertEqual(
            aliases[0]["alias_source"],
            "manual-review | legacy-migration",
        )
        self.assertIn("Confirmed from the publisher PDF.", aliases[0]["notes"])
        self.assertIn("Retained from the legacy canonical record.", aliases[0]["notes"])

    def test_merge_same_display_name_does_not_create_self_alias(self):
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            institutions = list(csv.DictReader(handle))
        institutions[0]["canonical_name"] = AMAZON
        write_csv(self.institutions, INSTITUTION_COLUMNS, institutions)

        merge_institutions(
            self.certh_id,
            self.amazon_id,
            confirmation=f"REPLACE {AMAZON} WITH {AMAZON} GLOBALLY",
            review_note="Merged a legacy duplicate ID with the same display name.",
            institutions_path=self.institutions,
            mappings_path=self.mappings,
            aliases_path=self.aliases,
            locations_path=self.locations,
            location_reviews_path=self.location_reviews,
            location_audit_path=self.location_audits,
            hierarchy_path=self.hierarchy,
            search_relationships_path=self.search_relationships,
            review_queue_path=self.review_queue,
            audit_path=self.audits,
        )

        with self.aliases.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), [])

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

    def test_validator_rejects_active_mapping_to_merged_institution(self):
        old_id = "institution:old"
        new_id = "institution:new"
        issues = []
        validate_institution_entities(
            [
                blank(
                    INSTITUTION_COLUMNS,
                    institution_id=old_id,
                    canonical_name="Old University",
                    institution_status="merged",
                ),
                blank(
                    INSTITUTION_COLUMNS,
                    institution_id=new_id,
                    canonical_name="The New University",
                    institution_status="active",
                ),
            ],
            [blank(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                institution_id=old_id,
                mapping_status="active",
            )],
            [],
            [],
            [],
            [blank(
                INSTITUTION_AUDIT_COLUMNS,
                action="merge",
                institution_id=new_id,
                previous_institution_id=old_id,
            )],
            issues,
        )
        self.assertTrue(any(
            "active mapping targets a non-active institution" in issue.message
            for issue in issues
        ))


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
