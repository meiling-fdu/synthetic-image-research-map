import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_locations import location_review_payload
from scripts.curated_schema import (
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    PAPER_EXCLUSION_COLUMNS,
)


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row(columns, **values):
    return {column: values.get(column, "") for column in columns}


class InstitutionReviewCompleteDatasetTests(unittest.TestCase):
    def test_payload_retains_pending_and_every_resolved_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            institutions = root / "institutions.csv"
            reviews = root / "reviews.csv"
            locations = root / "locations.csv"
            aliases = root / "aliases.csv"
            institution_rows = []
            review_rows = []
            statuses = ["pending_review", "ambiguous", "confirmed", "ignore", "excluded"]
            for index, status in enumerate(statuses):
                identifier = f"institution:{index}"
                name = f"Example Institution {index}"
                institution_rows.append(row(
                    INSTITUTION_COLUMNS, institution_id=identifier,
                    canonical_name=name, abbreviation=f"EI{index}",
                    institution_type="other", institution_status="active",
                ))
                review_rows.append(row(
                    INSTITUTION_LOCATION_REVIEW_COLUMNS,
                    institution=name, institution_id=identifier,
                    related_paper_id=f"paper:{index}", title=f"Paper {index}",
                    year="2026", review_status=status,
                    location_status="known" if status == "confirmed" else "missing",
                    coordinate_status="known" if status == "confirmed" else "missing",
                ))
            institution_rows.append(row(
                INSTITUTION_COLUMNS, institution_id="institution:ignored",
                canonical_name="Ignored Registry Institution",
                institution_type="other", institution_status="ignored",
            ))
            review_rows.append(row(
                INSTITUTION_LOCATION_REVIEW_COLUMNS,
                institution="Ignored Registry Institution",
                institution_id="institution:ignored", related_paper_id="paper:ignored",
                title="Ignored paper", year="2026", review_status="pending_review",
            ))
            write_csv(institutions, INSTITUTION_COLUMNS, institution_rows)
            write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, review_rows)
            write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [row(
                INSTITUTION_LOCATION_COLUMNS, location_id="location:2",
                institution_id="institution:2", institution="Example Institution 2",
                normalized_institution="example institution 2", city="City",
                country="Italy", country_code="IT", lat="1", lon="2",
                coordinate_status="known",
            )])
            write_csv(aliases, INSTITUTION_ALIAS_COLUMNS, [])

            payload = location_review_payload(
                review_path=reviews, locations_path=locations,
                aliases_path=aliases, institutions_path=institutions,
            )

            self.assertEqual(len(payload["records"]), 6)
            effective = [record["review_status"] for record in payload["records"]]
            for status in ("pending_review", "ambiguous", "confirmed", "ignore", "excluded"):
                self.assertIn(status, effective)
            self.assertEqual(effective.count("ignore"), 2)
            self.assertEqual(payload["summary"]["confirmed"], 1)
            self.assertEqual(payload["summary"]["ignore"], 2)
            self.assertEqual(
                payload["summary"]["pending_review"],
                sum(row["review_status"] == "pending_review" for row in payload["records"]),
            )
            confirmed = next(record for record in payload["records"] if record["review_status"] == "confirmed")
            self.assertEqual(confirmed["confirmed_location"]["location_id"], "location:2")
            self.assertEqual(confirmed["candidate_suggestions"], [])

    def test_actionable_coordinate_summary_uses_effective_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            institutions = root / "institutions.csv"
            reviews = root / "reviews.csv"
            locations = root / "locations.csv"
            aliases = root / "aliases.csv"
            write_csv(institutions, INSTITUTION_COLUMNS, [
                row(INSTITUTION_COLUMNS, institution_id="institution:located", canonical_name="Located", institution_status="active"),
                row(INSTITUTION_COLUMNS, institution_id="institution:excluded", canonical_name="Excluded", institution_status="active"),
            ])
            write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [
                row(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="Located", institution_id="institution:located", related_paper_id="paper:active", review_status="pending_review"),
                row(INSTITUTION_LOCATION_REVIEW_COLUMNS, institution="Excluded", institution_id="institution:excluded", related_paper_id="paper:excluded", review_status="pending_review"),
            ])
            write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [
                row(INSTITUTION_LOCATION_COLUMNS, location_id="location:located", institution_id="institution:located", institution="Located", lat="1", lon="2", coordinate_status="known"),
            ])
            write_csv(aliases, INSTITUTION_ALIAS_COLUMNS, [])
            exclusions = [row(PAPER_EXCLUSION_COLUMNS, paper_id="paper:excluded", is_active="true")]
            payload = location_review_payload(
                review_path=reviews, locations_path=locations,
                aliases_path=aliases, institutions_path=institutions,
                exclusions=exclusions,
            )
            self.assertEqual(payload["summary"]["needs_coordinates"], 0)
            excluded = next(item for item in payload["records"] if item["institution"] == "Excluded")
            self.assertEqual(excluded["review_status"], "excluded")
            self.assertTrue(payload["records"][0]["has_usable_confirmed_location"])

    def test_missing_review_row_is_derived_from_active_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            institutions = root / "institutions.csv"
            reviews = root / "reviews.csv"
            locations = root / "locations.csv"
            aliases = root / "aliases.csv"
            write_csv(institutions, INSTITUTION_COLUMNS, [row(
                INSTITUTION_COLUMNS, institution_id="institution:missing",
                canonical_name="Missing Institute", institution_status="active",
            )])
            write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [])
            write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [])
            write_csv(aliases, INSTITUTION_ALIAS_COLUMNS, [])
            payload = location_review_payload(
                review_path=reviews, locations_path=locations,
                aliases_path=aliases, institutions_path=institutions,
                mappings=[{
                    "mapping_id": "mapping:one", "paper_id": "paper:one",
                    "title": "Paper", "year": "2026",
                    "institution": "Missing Institute",
                    "institution_id": "institution:missing",
                    "mapping_status": "active",
                }],
            )
            self.assertEqual(payload["summary"]["needs_coordinates"], 1)
            self.assertEqual(payload["total_unresolved"], 1)
            self.assertEqual(payload["records"][0]["derived_from_active_mapping"], "true")

    def test_derived_rows_exclude_inactive_entities_and_disappear_when_located(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            institutions = root / "institutions.csv"
            reviews = root / "reviews.csv"
            locations = root / "locations.csv"
            aliases = root / "aliases.csv"
            write_csv(institutions, INSTITUTION_COLUMNS, [
                row(
                    INSTITUTION_COLUMNS,
                    institution_id="institution:located",
                    canonical_name="Located Institute",
                    institution_status="active",
                ),
                row(
                    INSTITUTION_COLUMNS,
                    institution_id="institution:inactive",
                    canonical_name="Inactive Institute",
                    institution_status="ignored",
                ),
            ])
            write_csv(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [])
            write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [row(
                INSTITUTION_LOCATION_COLUMNS,
                location_id="location:located",
                institution_id="institution:located",
                institution="Located Institute",
                lat="1", lon="2", coordinate_status="known",
            )])
            write_csv(aliases, INSTITUTION_ALIAS_COLUMNS, [])
            mappings = [
                {
                    "mapping_id": "mapping:located", "paper_id": "paper:active",
                    "institution": "Located Institute",
                    "institution_id": "institution:located", "mapping_status": "active",
                },
                {
                    "mapping_id": "mapping:inactive", "paper_id": "paper:active",
                    "institution": "Inactive Institute",
                    "institution_id": "institution:inactive", "mapping_status": "active",
                },
                {
                    "mapping_id": "mapping:excluded", "paper_id": "paper:excluded",
                    "institution": "Located Institute",
                    "institution_id": "institution:located", "mapping_status": "active",
                },
            ]
            payload = location_review_payload(
                review_path=reviews, locations_path=locations,
                aliases_path=aliases, institutions_path=institutions,
                mappings=mappings,
                exclusions=[row(
                    PAPER_EXCLUSION_COLUMNS,
                    paper_id="paper:excluded", is_active="true",
                )],
            )
            self.assertEqual(payload["records"], [])
            self.assertEqual(payload["summary"]["needs_coordinates"], 0)
            self.assertEqual(payload["total_unresolved"], 0)


if __name__ == "__main__":
    unittest.main()
