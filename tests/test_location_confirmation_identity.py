import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_locations import (
    CuratedLocationError,
    create_or_update_confirmed_location,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
)


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class LocationConfirmationIdentityTests(unittest.TestCase):
    def fixture(self, directory):
        directory = Path(directory)
        institutions = directory / "institutions.csv"
        reviews = directory / "reviews.csv"
        locations = directory / "locations.csv"
        mappings = directory / "mappings.csv"
        canonical_id = "institution:canonical"
        stale_id = "institution:stale-review"
        other_id = "institution:other"
        write_csv(institutions, INSTITUTION_COLUMNS, [
            {
                "institution_id": canonical_id,
                "canonical_name": "Canonical Institute",
                "institution_type": "university",
                "institution_status": "active",
            },
            {
                "institution_id": stale_id,
                "canonical_name": "Long Historical Institute Name",
                "institution_type": "university",
                "institution_status": "active",
            },
            {
                "institution_id": other_id,
                "canonical_name": "Different University",
                "institution_type": "university",
                "institution_status": "active",
            },
        ])
        review = {column: "" for column in INSTITUTION_LOCATION_REVIEW_COLUMNS}
        review.update({
            "institution": "Canonical Institute",
            "canonical_institution_name": "Long Historical Institute Name",
            "institution_id": stale_id,
            "related_paper_id": "paper:one",
            "title": "Paper",
            "year": "2026",
            "review_status": "needs_coordinates",
            "location_status": "missing",
            "coordinate_status": "missing",
        })
        duplicate = dict(review)
        duplicate["institution_id"] = canonical_id
        duplicate["canonical_institution_name"] = "Canonical Institute"
        write_csv(
            reviews,
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            [review, duplicate],
        )
        write_csv(locations, INSTITUTION_LOCATION_COLUMNS, [])
        mapping = {column: "" for column in AUTHOR_INSTITUTION_MAPPING_COLUMNS}
        mapping.update({
            "mapping_id": "mapping:one",
            "paper_id": "paper:one",
            "institution": "Canonical Institute",
            "institution_id": canonical_id,
            "mapping_status": "active",
        })
        write_csv(mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [mapping])
        return institutions, reviews, locations, mappings, canonical_id, other_id

    def draft(self, queue_id, institution_id):
        return {
            "queue_id": queue_id,
            "institution_id": institution_id,
            "confirmed_city": "New Delhi",
            "confirmed_region": "Delhi",
            "confirmed_country": "India",
            "confirmed_country_code": "IN",
            "confirmed_lat": "28.546326",
            "confirmed_lon": "77.2732571",
            "coordinate_source": "OpenStreetMap Nominatim",
            "coordinate_review_note": "Confirmed in regression test.",
        }

    def test_stale_review_id_resolves_through_active_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.fixture(directory)
            institutions, reviews, locations, mappings, canonical_id, _other_id = paths
            with reviews.open(encoding="utf-8", newline="") as handle:
                queue_id = next(csv.DictReader(handle))
            from scripts.curated_locations import queue_row_id
            result = create_or_update_confirmed_location(
                queue_row_id(queue_id),
                self.draft(queue_row_id(queue_id), canonical_id),
                institutions_path=institutions,
                review_path=reviews,
                locations_path=locations,
                mappings_path=mappings,
            )
            self.assertEqual(result["location"]["institution_id"], canonical_id)
            with reviews.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(
                    {row["review_status"] for row in csv.DictReader(handle)},
                    {"confirmed"},
                )

    def test_genuine_identity_change_is_rejected_without_location_write(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.fixture(directory)
            institutions, reviews, locations, mappings, _canonical_id, other_id = paths
            from scripts.curated_locations import load_location_review_queue, queue_row_id
            queue_id = queue_row_id(load_location_review_queue(reviews)[0])
            before = locations.read_bytes()
            with self.assertRaises(CuratedLocationError) as caught:
                create_or_update_confirmed_location(
                    queue_id,
                    self.draft(queue_id, other_id),
                    institutions_path=institutions,
                    review_path=reviews,
                    locations_path=locations,
                    mappings_path=mappings,
                )
            self.assertEqual(
                caught.exception.error_code,
                "institution_identity_change_not_allowed",
            )
            self.assertEqual(locations.read_bytes(), before)
