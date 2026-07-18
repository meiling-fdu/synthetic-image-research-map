import csv
import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts.curated_institutions import stable_institution_id
from scripts.curated_mappings import (
    CuratedMappingError,
    create_mapping,
    load_location_reviews,
    load_mappings,
    save_location_reviews,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_REVIEW_QUEUE_COLUMNS,
)
from scripts.serve_admin import AdminDataError, make_handler, queue_location_review


ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row(columns, **values):
    return {column: values.get(column, "") for column in columns}


class MappingInstitutionRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.mappings = root / "mappings.csv"
        self.reviews = root / "reviews.csv"
        self.institutions = root / "institutions.csv"
        self.aliases = root / "aliases.csv"
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS)
        write_csv(self.reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS)
        write_csv(self.institutions, INSTITUTION_COLUMNS)
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS)
        self.paper = {
            "paper_id": "curated:fixture",
            "title": "Progressive Open Space Expansion for Synthetic Images",
            "year": "2026",
        }
        self.draft = {
            "institution": "Zhejiang Lab",
            "institution_authors": "Sheng Tang",
            "raw_affiliation": (
                "Research Institute of Intelligent Computing, Zhejiang Lab, "
                "Hangzhou, China"
            ),
            "evidence_source": "Publisher PDF",
            "evidence_url": "https://example.test/paper.pdf",
            "affiliation_note": "Authors list Zhejiang Lab.",
            "mapping_status": "needs_review",
            "review_note": "Optional confirmation note.",
        }

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create(self, draft=None, paper=None):
        return create_mapping(
            paper or self.paper,
            draft or self.draft,
            map_records=[],
            mappings_path=self.mappings,
            location_review_path=self.reviews,
            institutions_path=self.institutions,
            institution_aliases_path=self.aliases,
        )

    def seed_institutions(self, *entities):
        write_csv(self.institutions, INSTITUTION_COLUMNS, entities)

    def test_mapping_review_writer_rejects_blank_canonical_id(self):
        review = row(
            INSTITUTION_LOCATION_REVIEW_COLUMNS,
            institution="Unregistered Lab",
            related_paper_id=self.paper["paper_id"],
        )

        with self.assertRaisesRegex(
            CuratedMappingError, "require a canonical institution_id"
        ):
            save_location_reviews([review], self.reviews)

    def test_existing_valid_id_is_reused_without_duplicate_entity(self):
        entity = row(
            INSTITUTION_COLUMNS,
            institution_id="institution:zhejiang",
            canonical_name="Zhejiang Lab",
            institution_type="laboratory",
            institution_status="active",
            public_display="Zhejiang Lab",
        )
        self.seed_institutions(entity)
        result = self.create({**self.draft, "institution_id": "institution:zhejiang"})
        self.assertEqual(result["institution_resolution"], "existing")
        self.assertEqual(result["mapping"]["institution_id"], "institution:zhejiang")
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), 1)

    def test_stale_id_resolves_by_normalized_canonical_name(self):
        self.seed_institutions(row(
            INSTITUTION_COLUMNS,
            institution_id="institution:zhejiang",
            canonical_name="Zhejiang Lab",
            institution_type="laboratory",
            institution_status="active",
        ))
        result = self.create({
            **self.draft,
            "institution": " zhejiang-lab ",
            "institution_id": "institution:stale-preview-id",
        })
        self.assertEqual(result["mapping"]["institution_id"], "institution:zhejiang")
        self.assertEqual(result["mapping"]["institution"], "Zhejiang Lab")

    def test_new_name_creates_provisional_mapping_and_needs_coordinates_review(self):
        result = self.create()
        identifier = stable_institution_id("Zhejiang Lab")
        self.assertEqual(result["institution_resolution"], "provisional")
        self.assertEqual(result["mapping"]["institution_id"], identifier)
        self.assertEqual(result["location_review"], "created")
        mapping = load_mappings(self.mappings)[0]
        self.assertEqual(mapping["institution_authors"], self.draft["institution_authors"])
        self.assertEqual(mapping["raw_affiliation"], self.draft["raw_affiliation"])
        self.assertEqual(mapping["evidence_url"], self.draft["evidence_url"])
        self.assertEqual(mapping["mapping_status"], "needs_review")
        self.assertEqual(mapping["review_note"], self.draft["review_note"])
        review = load_location_reviews(self.reviews)[0]
        self.assertEqual(review["institution_id"], identifier)
        self.assertEqual(review["review_status"], "needs_coordinates")
        self.assertEqual(review["coordinate_status"], "missing")
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            institution = next(csv.DictReader(handle))
        self.assertEqual(institution["institution_type"], "research_unit")

    def test_repeated_new_name_does_not_duplicate_institution(self):
        self.create()
        self.create(paper={**self.paper, "paper_id": "curated:fixture-2", "title": "Second paper"})
        with self.institutions.open(encoding="utf-8", newline="") as handle:
            institutions = list(csv.DictReader(handle))
        self.assertEqual(len(institutions), 1)
        self.assertEqual(len(load_mappings(self.mappings)), 2)

    def test_ambiguous_normalized_alias_blocks_with_candidates(self):
        self.seed_institutions(
            row(INSTITUTION_COLUMNS, institution_id="institution:one", canonical_name="Zhejiang Research Lab", institution_status="active"),
            row(INSTITUTION_COLUMNS, institution_id="institution:two", canonical_name="Zhejiang AI Lab", institution_status="active"),
        )
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [
            row(INSTITUTION_ALIAS_COLUMNS, alias_id="alias:one", alias_name="Zhejiang Lab", institution_id="institution:one", review_status="confirmed"),
            row(INSTITUTION_ALIAS_COLUMNS, alias_id="alias:two", alias_name="Zhejiang Lab", institution_id="institution:two", review_status="confirmed"),
        ])
        with self.assertRaisesRegex(CuratedMappingError, "ambiguous.*institution:one.*institution:two"):
            self.create({**self.draft, "institution_id": "institution:stale"})
        self.assertEqual(load_mappings(self.mappings), [])

    def test_write_failure_rolls_back_all_three_curated_files(self):
        before = {path: path.read_bytes() for path in (self.institutions, self.mappings, self.reviews)}
        with patch("scripts.curated_mappings.save_mappings", side_effect=OSError("fixture failure")):
            with self.assertRaisesRegex(OSError, "fixture failure"):
                self.create()
        self.assertEqual(
            {path: path.read_bytes() for path in before},
            before,
        )

    def test_frontend_candidate_source_and_payload_are_canonical_consistent(self):
        html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        javascript = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn('list="mapping-institution-options"', html)
        self.assertIn('id="mapping-institution-id" type="hidden"', html)
        self.assertIn("state.institutions", javascript)
        self.assertIn('institution_id: elements["mapping-institution-id"].value', javascript)
        self.assertIn("provisional institution added", (ROOT / "scripts/serve_admin.py").read_text(encoding="utf-8"))

    def test_review_action_resolves_stale_id_and_never_writes_missing_id(self):
        canonical_id = "institution:zhejiang"
        self.seed_institutions(row(
            INSTITUTION_COLUMNS,
            institution_id=canonical_id,
            canonical_name="Zhejiang Lab",
            institution_status="active",
        ))
        saved = queue_location_review(
            {
                **self.paper,
                **self.draft,
                "institution_id": "institution:stale-preview-id",
            },
            path=self.reviews,
            institutions_path=self.institutions,
            aliases_path=self.aliases,
        )
        self.assertEqual(saved["institution_id"], canonical_id)
        self.assertEqual(saved["canonical_institution_name"], "Zhejiang Lab")

    def test_review_action_rejects_unregistered_institution_without_writing(self):
        with self.assertRaisesRegex(AdminDataError, "canonical registry"):
            queue_location_review(
                {**self.paper, **self.draft},
                path=self.reviews,
                institutions_path=self.institutions,
                aliases_path=self.aliases,
            )
        self.assertEqual(load_location_reviews(self.reviews), [])

    def test_real_regression_alias_review_row_receives_active_canonical_id(self):
        canonical_id = "institution:ict-cas"
        self.seed_institutions(row(
            INSTITUTION_COLUMNS,
            institution_id=canonical_id,
            canonical_name=(
                "Institute of Computing Technology, Chinese Academy of Sciences"
            ),
            institution_status="active",
        ))
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [
            row(
                INSTITUTION_ALIAS_COLUMNS,
                alias_id="alias:ict",
                alias_name="Institute of Computing Technology",
                institution_id=canonical_id,
                canonical_institution_name=(
                    "Institute of Computing Technology, Chinese Academy of Sciences"
                ),
                review_status="confirmed",
            ),
        ])
        saved = queue_location_review(
            {
                **self.paper,
                **self.draft,
                "institution": "Institute of Computing Technology",
                "raw_affiliation": (
                    "Institute of Computing Technology, Chinese Academy of "
                    "Sciences, Beijing, China"
                ),
                "institution_id": "",
            },
            path=self.reviews,
            institutions_path=self.institutions,
            aliases_path=self.aliases,
        )
        self.assertEqual(saved["institution_id"], canonical_id)
        self.assertEqual(
            saved["canonical_institution_name"],
            "Institute of Computing Technology, Chinese Academy of Sciences",
        )
        self.assertEqual(
            saved["raw_affiliation"],
            "Institute of Computing Technology, Chinese Academy of Sciences, "
            "Beijing, China",
        )


class MappingInstitutionRegistrationEndpointTests(unittest.TestCase):
    def test_create_endpoint_reports_provisional_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "mappings_path": root / "mappings.csv",
                "location_review_path": root / "reviews.csv",
                "institutions_path": root / "institutions.csv",
                "institution_aliases_path": root / "aliases.csv",
                "institution_locations_path": root / "locations.csv",
                "institution_review_queue_path": root / "queue.csv",
            }
            write_csv(paths["mappings_path"], AUTHOR_INSTITUTION_MAPPING_COLUMNS)
            write_csv(paths["location_review_path"], INSTITUTION_LOCATION_REVIEW_COLUMNS)
            write_csv(paths["institutions_path"], INSTITUTION_COLUMNS)
            write_csv(paths["institution_aliases_path"], INSTITUTION_ALIAS_COLUMNS)
            write_csv(paths["institution_locations_path"], INSTITUTION_LOCATION_COLUMNS)
            write_csv(paths["institution_review_queue_path"], INSTITUTION_REVIEW_QUEUE_COLUMNS)
            handler = make_handler("token", geocoder=object(), **paths)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                connection.request(
                    "POST",
                    "/api/paper/mapping/create",
                    body=json.dumps({
                        "id": "openalex:W4416604008",
                        "institution": "Zhejiang Lab",
                        "institution_id": "institution:stale-preview-id",
                        "institution_authors": "Ada Example",
                        "raw_affiliation": "Zhejiang Lab",
                        "evidence_source": "Publisher PDF",
                        "mapping_status": "active",
                    }),
                    headers={"X-Admin-Token": "token", "Content-Type": "application/json"},
                )
                response = connection.getresponse()
                payload = json.loads(response.read())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
            self.assertEqual(response.status, 201, payload)
            self.assertEqual(payload["institution_resolution"], "provisional")
            self.assertIn("Needs Coordinates", payload["message"])
            self.assertEqual(len(load_mappings(paths["mappings_path"])), 1)


if __name__ == "__main__":
    unittest.main()
