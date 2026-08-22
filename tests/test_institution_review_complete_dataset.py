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


if __name__ == "__main__":
    unittest.main()
