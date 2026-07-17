import csv
import contextlib
import json
import tempfile
import threading
import unittest
import shutil
import urllib.request
import urllib.parse
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts.curated_export import integrate_curated_records
from scripts.curated_papers import (
    CuratedPaperError,
    normalize_author_names,
    update_curated_paper,
)
from scripts.curated_schema import PAPERS_COLUMNS, PAPER_EXCLUSION_COLUMNS
from scripts.arxiv_autofill import (
    apply_curated_arxiv_metadata,
    read_curated_arxiv_links,
    set_curated_arxiv_override,
)
from scripts.export_public_preview import normalize_entry_type
from scripts.paper_exclusions import (
    build_active_exclusion_index,
    record_is_excluded,
    upsert_active_exclusion,
)
from scripts.serve_admin import load_admin_data, make_handler


def curated_row(**overrides):
    row = {column: "" for column in PAPERS_COLUMNS}
    row.update(
        {
            "paper_id": "curated:survey",
            "title": "A Principled Survey",
            "year": "2026",
            "authors": "Author One; Author Two",
            "doi": "10.1000/survey",
            "paper_url": "https://doi.org/10.1000/survey",
            "publication_type": "preprint",
            "task": "source_attribution",
            "subtask": "source_identification",
            "scope_status": "in_scope",
            "source_database": "openalex",
            "metadata_source": "openalex",
            "curation_status": "corrected_by_admin",
            "review_status": "reviewed",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "entry_type": "method",
        }
    )
    row.update(overrides)
    return row


def chi_venue_fields():
    return {
        "venue": "CHI Conference on Human Factors in Computing Systems",
        "venue_id": "venue:chi:main",
        "venue_name": "CHI Conference on Human Factors in Computing Systems",
        "venue_acronym": "CHI",
        "venue_type": "conference",
        "venue_track": "main",
        "raw_venue": "Proceedings of the CHI Conference on Human Factors in Computing Systems",
        "publication_type": "conference",
    }


def write_papers(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_exclusions(path, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_EXCLUSION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class PaperMetadataEditingTests(unittest.TestCase):
    @contextlib.contextmanager
    def metadata_server(
        self, directory, export_calls, export_success=True, original_overrides=None,
    ):
        directory = Path(directory)
        curated_path = directory / "papers.csv"
        exclusions_path = directory / "paper_exclusions.csv"
        links_path = directory / "paper_arxiv_links.csv"
        public_papers = directory / "public_papers.json"
        public_map = directory / "public_map.json"
        venue_aliases = directory / "venue_aliases.csv"
        shutil.copyfile(
            Path(__file__).resolve().parents[1] / "data" / "curated" / "venue_aliases.csv",
            venue_aliases,
        )
        original = curated_row(
            arxiv_id="", paper_url="", **(original_overrides or {})
        )
        write_papers(curated_path, [original])
        write_exclusions(exclusions_path)
        public_papers.write_text("[]", encoding="utf-8")
        public_map.write_text("[]", encoding="utf-8")
        set_curated_arxiv_override(original, "2501.01234", links_path)
        with (
            patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", public_papers),
            patch("scripts.serve_admin.PUBLIC_MAP_PATH", public_map),
        ):
            _papers, admin_data = load_admin_data(
                exclusions_path=exclusions_path,
                curated_papers_path=curated_path,
            )
            display_id = next(iter(admin_data["papers_by_id"]))
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(
                    "test-token",
                    exclusions_path=exclusions_path,
                    curated_papers_path=curated_path,
                    venue_aliases_path=venue_aliases,
                    curated_arxiv_links_path=links_path,
                    metadata_export_runner=lambda name: (
                        export_calls.append(name)
                        or {"success": export_success}
                    ),
                ),
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                yield (
                    f"http://127.0.0.1:{server.server_port}",
                    original,
                    curated_path,
                    links_path,
                    display_id,
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def metadata_request(self, base_url, path, payload=None):
        request = urllib.request.Request(
            base_url + path,
            data=(json.dumps(payload).encode("utf-8") if payload is not None else None),
            method="POST" if payload is not None else "GET",
            headers={
                "X-Admin-Token": "test-token",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            return json.loads(response.read())

    def test_metadata_endpoint_reads_edits_and_clears_arxiv_override(self):
        with tempfile.TemporaryDirectory() as directory:
            exports = []
            with self.metadata_server(directory, exports) as (
                base_url,
                original,
                curated_path,
                links_path,
                display_id,
            ):
                metadata = self.metadata_request(
                    base_url,
                    f"/api/paper/metadata?id={urllib.parse.quote(display_id)}",
                )["data"]["effective_record"]
                self.assertEqual(metadata["arxiv_id"], "2501.01234")
                self.assertEqual(
                    metadata["paper_url"],
                    "https://arxiv.org/pdf/2501.01234.pdf",
                )

                edit = {
                    **original,
                    "id": display_id,
                    "arxiv_id": "2501.99999v2",
                    "arxiv_id_changed": True,
                    "paper_url": metadata["paper_url"],
                }
                updated = self.metadata_request(
                    base_url, "/api/paper/metadata/update", edit
                )["data"]["paper"]
                self.assertEqual(updated["arxiv_id"], "2501.99999")
                self.assertEqual(len(read_curated_arxiv_links(links_path)), 1)
                self.assertEqual(exports, ["export_preview"])
                with curated_path.open(encoding="utf-8", newline="") as handle:
                    saved = next(csv.DictReader(handle))
                self.assertEqual(saved["arxiv_id"], "")
                self.assertEqual(saved["authors"], original["authors"])

                cleared = {**edit, "arxiv_id": "", "arxiv_id_changed": True}
                self.metadata_request(
                    base_url, "/api/paper/metadata/update", cleared
                )
                self.assertEqual(read_curated_arxiv_links(links_path), [])
                self.assertEqual(exports, ["export_preview", "export_preview"])

    def test_unchanged_or_omitted_arxiv_field_preserves_override_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            exports = []
            with self.metadata_server(directory, exports) as (
                base_url,
                original,
                _curated_path,
                links_path,
                display_id,
            ):
                before = links_path.read_bytes()
                unchanged = {
                    **original,
                    **chi_venue_fields(),
                    "id": display_id,
                    "arxiv_id": "2501.01234",
                    "arxiv_id_changed": False,
                    "paper_url": "https://arxiv.org/pdf/2501.01234.pdf",
                }
                self.metadata_request(
                    base_url, "/api/paper/metadata/update", unchanged
                )
                self.assertEqual(links_path.read_bytes(), before)

                omitted = dict(unchanged)
                omitted.pop("arxiv_id")
                omitted.pop("arxiv_id_changed")
                self.metadata_request(
                    base_url, "/api/paper/metadata/update", omitted
                )
                self.assertEqual(links_path.read_bytes(), before)
                self.assertEqual(exports, ["export_preview", "export_preview"])

    def test_frontend_marks_arxiv_changes_explicitly(self):
        source = (
            Path(__file__).resolve().parents[1] / "web" / "admin.js"
        ).read_text()
        self.assertIn(
            'elements["metadata-arxiv-id"].dataset.originalValue', source
        )
        self.assertIn(
            "draft.arxiv_id_changed =\n    draft.arxiv_id !==", source
        )

    def test_venue_registry_api_and_structured_save_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.metadata_server(directory, []) as (
                base_url, original, curated_path, _links_path, display_id,
            ):
                venues = self.metadata_request(base_url, "/api/venues")["data"]["records"]
                chi = next(row for row in venues if row["venue_id"] == "venue:chi:main")
                self.assertEqual(
                    chi["venue_label"],
                    "CHI Conference on Human Factors in Computing Systems (CHI)",
                )
                self.assertIn("CHI", chi["search_text"])
                edit = {**original, **chi_venue_fields(), "id": display_id}
                updated = self.metadata_request(base_url, "/api/paper/metadata/update", edit)["data"]["paper"]
                self.assertEqual(updated["venue_id"], "venue:chi:main")
                self.assertEqual(updated["raw_venue"], chi_venue_fields()["raw_venue"])
                reloaded = self.metadata_request(
                    base_url, f"/api/paper/metadata?id={urllib.parse.quote(display_id)}",
                )["data"]["effective_record"]
                self.assertEqual(reloaded["venue_name"], chi["venue_name"])
                self.assertEqual(reloaded["venue_acronym"], "CHI")
                with curated_path.open(encoding="utf-8", newline="") as handle:
                    saved = next(csv.DictReader(handle))
                self.assertEqual(saved["venue_track"], "main")

    def test_legacy_venue_resolves_on_metadata_load(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.metadata_server(
                directory,
                [],
                original_overrides={
                    "venue": "Proceedings of the CHI Conference on Human Factors in Computing Systems",
                    "publication_type": "conference",
                },
            ) as (base_url, _original, _curated_path, _links_path, display_id):
                effective = self.metadata_request(
                    base_url, f"/api/paper/metadata?id={urllib.parse.quote(display_id)}",
                )["data"]["effective_record"]
                self.assertEqual(effective["venue_id"], "venue:chi:main")
                self.assertEqual(effective["venue_resolution_status"], "resolved")
                self.assertFalse(effective["venue_review_required"])

    def test_metadata_api_rejects_nonexistent_or_conflicting_venue(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.metadata_server(directory, []) as (
                base_url, original, _curated_path, _links_path, display_id,
            ):
                invalid = {**original, **chi_venue_fields(), "id": display_id, "venue_id": "venue:missing:main"}
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.metadata_request(base_url, "/api/paper/metadata/update", invalid)
                self.assertEqual(caught.exception.code, 400)
                conflicting = {**original, **chi_venue_fields(), "id": display_id, "venue_name": "Wrong name"}
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.metadata_request(base_url, "/api/paper/metadata/update", conflicting)
                self.assertEqual(caught.exception.code, 400)

    def test_canonical_venue_creation_api_prevents_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.metadata_server(directory, []) as (
                base_url, _original, _curated_path, _links_path, _display_id,
            ):
                draft = {
                    "venue_name": "International Test Venue",
                    "venue_acronym": "ITV",
                    "venue_type": "conference",
                    "venue_track": "main",
                    "raw_alias": "Proceedings of International Test Venue",
                    "review_note": "Confirmed in API regression test.",
                }
                created = self.metadata_request(base_url, "/api/venues/create", draft)["data"]["venue"]
                self.assertEqual(created["venue_acronym"], "ITV")
                venues = self.metadata_request(base_url, "/api/venues")["data"]["records"]
                self.assertTrue(any(row["venue_id"] == created["venue_id"] for row in venues))
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.metadata_request(base_url, "/api/venues/create", draft)
                self.assertEqual(caught.exception.code, 400)

    def test_similar_venue_creation_requires_explicit_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.metadata_server(directory, []) as (
                base_url, _original, _curated_path, _links_path, _display_id,
            ):
                draft = {
                    "venue_name": "CHI Conference on Human Factors in Computer Systems",
                    "venue_acronym": "CHI-X",
                    "venue_type": "conference",
                    "venue_track": "main",
                    "raw_alias": "CHI-X test alias",
                }
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.metadata_request(base_url, "/api/venues/create", draft)
                self.assertEqual(caught.exception.code, 409)
                body = json.loads(caught.exception.read())
                self.assertTrue(body["data"]["possible_matches"])
                created = self.metadata_request(
                    base_url,
                    "/api/venues/create",
                    {**draft, "confirmed_similar": True},
                )["data"]["venue"]
                self.assertEqual(created["venue_acronym"], "CHI-X")

    def test_frontend_loads_and_clears_metadata_on_paper_selection(self):
        source = (
            Path(__file__).resolve().parents[1] / "web" / "admin.js"
        ).read_text()
        select_body = source.split("async function selectPaper(id) {", 1)[1].split(
            "\nfunction clearPaperMetadata", 1
        )[0]
        editor_body = source.split("function openMetadataEditor() {", 1)[1].split(
            "\nfunction populateMetadataForm", 1
        )[0]
        self.assertIn('clearPaperMetadata("Loading metadata…")', select_body)
        self.assertIn("apiFetch(`/api/paper/metadata?id=", select_body)
        self.assertIn("populateMetadataForm();", select_body)
        self.assertNotIn("apiFetch(", editor_body)
        self.assertNotIn("populateMetadataForm();", editor_body)

    def test_frontend_rejects_stale_metadata_responses_and_stale_saves(self):
        source = (
            Path(__file__).resolve().parents[1] / "web" / "admin.js"
        ).read_text()
        self.assertIn("let paperSelectionSequence = 0;", source)
        self.assertGreaterEqual(
            source.count(
                "selectionSequence !== paperSelectionSequence || state.selectedId !=="
            ),
            3,
        )
        self.assertIn('elements["metadata-paper-id"].value = "";', source)
        self.assertIn('elements["metadata-edit-button"].disabled = true;', source)
        self.assertIn("Metadata is not loaded for the currently selected paper.", source)

    def test_frontend_renders_empty_metadata_records_explicitly(self):
        source = (
            Path(__file__).resolve().parents[1] / "web" / "admin.js"
        ).read_text()
        self.assertIn('summary.textContent = `${label}${record ? "" : " · none"}`;', source)
        self.assertIn('pre.textContent = record ? JSON.stringify(record, null, 2) : "No record.";', source)

    def test_export_failure_rolls_back_metadata_and_override_files(self):
        with tempfile.TemporaryDirectory() as directory:
            exports = []
            with self.metadata_server(
                directory, exports, export_success=False
            ) as (
                base_url,
                original,
                curated_path,
                links_path,
                display_id,
            ):
                curated_before = curated_path.read_bytes()
                links_before = links_path.read_bytes()
                edit = {
                    **original,
                    **chi_venue_fields(),
                    "id": display_id,
                    "arxiv_id": "2501.99999",
                    "arxiv_id_changed": True,
                    "paper_url": "https://arxiv.org/pdf/2501.01234.pdf",
                }
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    self.metadata_request(
                        base_url, "/api/paper/metadata/update", edit
                    )
                self.assertEqual(raised.exception.code, 500)
                self.assertEqual(curated_path.read_bytes(), curated_before)
                self.assertEqual(links_path.read_bytes(), links_before)

    def test_curated_arxiv_override_matches_public_effective_metadata(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            links = Path(temporary_directory) / "paper_arxiv_links.csv"
            base = curated_row(arxiv_id="", paper_url="")
            set_curated_arxiv_override(base, "2501.01234", links)

            admin = apply_curated_arxiv_metadata(base, links)
            public = dict(base)
            from scripts.export_candidate_map_data import apply_paper_arxiv_links
            apply_paper_arxiv_links([public], read_curated_arxiv_links(links))

            self.assertEqual(admin["arxiv_id"], "2501.01234")
            self.assertEqual(admin["arxiv_id"], public["arxiv_id"])
            self.assertEqual(
                admin["paper_url"], "https://arxiv.org/pdf/2501.01234.pdf"
            )
            self.assertEqual(admin["paper_url"], public["paper_url"])
            self.assertEqual(admin["authors"], base["authors"])

    def test_base_arxiv_and_empty_records_are_preserved_without_override(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            links = Path(temporary_directory) / "paper_arxiv_links.csv"
            base = curated_row(arxiv_id="2401.00001", paper_url="publisher")
            self.assertEqual(
                apply_curated_arxiv_metadata(base, links)["arxiv_id"],
                "2401.00001",
            )
            empty = curated_row(arxiv_id="", paper_url="")
            effective = apply_curated_arxiv_metadata(empty, links)
            self.assertEqual(effective["arxiv_id"], "")
            self.assertEqual(effective["paper_url"], "")

    def test_clearing_admin_override_reveals_unchanged_base_arxiv_id(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            links = Path(temporary_directory) / "paper_arxiv_links.csv"
            base = curated_row(arxiv_id="2401.00001")
            set_curated_arxiv_override(base, "2501.00002", links)
            self.assertEqual(
                apply_curated_arxiv_metadata(base, links)["arxiv_id"],
                "2501.00002",
            )
            set_curated_arxiv_override(base, "", links)
            self.assertEqual(read_curated_arxiv_links(links), [])
            self.assertEqual(
                apply_curated_arxiv_metadata(base, links)["arxiv_id"],
                "2401.00001",
            )

    def test_arxiv_override_edit_clear_and_deduplicate_preserve_other_rows(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            links = Path(temporary_directory) / "paper_arxiv_links.csv"
            target = curated_row(arxiv_id="")
            other = curated_row(
                paper_id="curated:other",
                title="Other paper",
                doi="10.1000/other",
                openalex_url="https://openalex.org/W-OTHER",
            )
            set_curated_arxiv_override(other, "2501.11111", links)
            set_curated_arxiv_override(target, "2501.22222", links)
            set_curated_arxiv_override(target, "2501.33333v2", links)
            rows = read_curated_arxiv_links(links)
            self.assertEqual(len(rows), 2)
            target_rows = [row for row in rows if row["doi"] == target["doi"]]
            self.assertEqual(len(target_rows), 1)
            self.assertEqual(target_rows[0]["arxiv_id"], "2501.33333")
            self.assertEqual(
                next(row for row in rows if row["doi"] == other["doi"])["arxiv_id"],
                "2501.11111",
            )
            set_curated_arxiv_override(target, "", links)
            remaining = read_curated_arxiv_links(links)
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0]["doi"], other["doi"])

    def test_override_upsert_does_not_collide_on_same_title_and_year(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            links = Path(temporary_directory) / "paper_arxiv_links.csv"
            first = curated_row(
                title="Shared title",
                year="2025",
                doi="10.1000/first",
                openalex_url="https://openalex.org/W-FIRST",
            )
            second = curated_row(
                paper_id="curated:second",
                title="Shared title",
                year="2025",
                doi="10.1000/second",
                openalex_url="https://openalex.org/W-SECOND",
            )
            set_curated_arxiv_override(first, "2501.00001", links)
            set_curated_arxiv_override(second, "2501.00002", links)
            set_curated_arxiv_override(first, "2501.00003", links)
            rows = read_curated_arxiv_links(links)
            self.assertEqual([row["doi"] for row in rows], [
                "10.1000/first", "10.1000/second"
            ])
            self.assertEqual([row["arxiv_id"] for row in rows], [
                "2501.00003", "2501.00002"
            ])
            self.assertNotIn(b"\r\n", links.read_bytes())

    def test_admin_data_loading_resolves_identity_matches_to_paper_records(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            public_papers_path = directory / "public_preview_papers.json"
            public_map_path = directory / "public_preview_map_data.json"
            curated_papers_path = directory / "papers.csv"
            exclusions_path = directory / "paper_exclusions.csv"

            shared_title = "Source Generator Attribution via Inversion"
            public_papers_path.write_text(
                json.dumps(
                    [
                        {
                            "paper_id": "openalex:W-PUBLISHED",
                            "title": shared_title,
                            "year": 2025,
                            "authors": ["Published Author"],
                            "doi": "10.1000/published",
                            "openalex_url": "https://openalex.org/W-PUBLISHED",
                        },
                        {
                            "paper_id": "openalex:W-ARXIV",
                            "title": shared_title,
                            "year": 2025,
                            "authors": [{"display_name": "Preprint Author"}],
                            "doi": "10.48550/arxiv.2401.00001",
                            "openalex_url": "https://openalex.org/W-ARXIV",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            public_map_path.write_text("[]", encoding="utf-8")
            write_papers(
                curated_papers_path,
                [
                    curated_row(
                        paper_id="openalex:W-ARXIV",
                        title=shared_title,
                        year="2025",
                        authors='[{"display_name":"Preprint Author"}]',
                        doi="10.48550/arxiv.2401.00001",
                        openalex_url="https://openalex.org/W-ARXIV",
                    )
                ],
            )
            write_exclusions(exclusions_path)

            with (
                patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", public_papers_path),
                patch("scripts.serve_admin.PUBLIC_MAP_PATH", public_map_path),
            ):
                papers, admin_data = load_admin_data(
                    exclusions_path=exclusions_path,
                    curated_papers_path=curated_papers_path,
                )

            self.assertEqual(len(papers), 2)
            self.assertTrue(all(isinstance(record, dict) for record in papers))
            papers_by_paper_id = {record["paper_id"]: record for record in papers}
            self.assertEqual(len(papers_by_paper_id), 2)
            self.assertTrue(
                papers_by_paper_id["openalex:W-ARXIV"]["is_in_curated_papers"]
            )
            self.assertFalse(
                papers_by_paper_id["openalex:W-PUBLISHED"]["is_in_curated_papers"]
            )
            self.assertEqual(len(admin_data["papers_by_id"]), 2)

    def test_author_normalization_accepts_strings_objects_and_json(self):
        cases = (
            ("Alice; Bob", ["Alice", "Bob"]),
            (["Alice", "Bob"], ["Alice", "Bob"]),
            ([{"name": "Alice"}, {"name": "Bob"}], ["Alice", "Bob"]),
            ([{"display_name": "Alice"}, {"display_name": "Bob"}], ["Alice", "Bob"]),
            ('[{"name":"Alice"},{"display_name":"Bob"}]', ["Alice", "Bob"]),
            ('{"display_name":"Alice"}', ["Alice"]),
            (None, []),
            ("", []),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(normalize_author_names(value), expected)

    def test_admin_update_serializes_object_authors_to_canonical_csv_text(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            update_curated_paper(
                original,
                {**original, "authors": [{"name": "Alice"}, {"display_name": "Bob"}]},
                preview_records=[],
                path=path,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
            self.assertEqual(saved["authors"], "Alice; Bob")
            self.assertNotIn("[object Object]", saved["authors"])

    def test_excluding_one_same_title_record_does_not_exclude_the_other(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "paper_exclusions.csv"
            write_exclusions(path)
            published = curated_row(
                paper_id="openalex:W-PUBLISHED",
                title="Source Generator Attribution via Inversion",
                doi="10.1000/published",
                openalex_url="https://openalex.org/W-PUBLISHED",
                venue="Published Venue",
            )
            preprint = curated_row(
                paper_id="openalex:W-ARXIV",
                title=published["title"],
                doi="10.48550/arxiv.2401.00001",
                openalex_url="https://openalex.org/W-ARXIV",
                venue="arXiv",
            )

            upsert_active_exclusion(preprint, "duplicate", "Duplicate preprint", path)

            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            index = build_active_exclusion_index(rows)
            self.assertEqual(len(rows), 1)
            self.assertTrue(record_is_excluded(preprint, index))
            self.assertFalse(record_is_excluded(published, index))

    def test_admin_update_persists_normalized_entry_type_to_curated_source(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            updated = update_curated_paper(
                original,
                {**original, "entry_type": "  SuRvEy  "},
                preview_records=[],
                path=path,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
            self.assertEqual(updated["entry_type"], "survey")
            self.assertEqual(saved["entry_type"], "survey")
            self.assertEqual(saved["authors"], original["authors"])
            self.assertEqual(saved["paper_url"], original["paper_url"])

    def test_admin_update_rejects_empty_or_unknown_entry_type(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "papers.csv"
            original = curated_row()
            write_papers(path, [original])

            for invalid in ("", "tutorial"):
                with self.subTest(entry_type=invalid):
                    with self.assertRaises(CuratedPaperError):
                        update_curated_paper(
                            original,
                            {**original, "entry_type": invalid},
                            preview_records=[],
                            path=path,
                        )

    def test_export_propagates_entry_type_without_changing_coverage(self):
        public_paper = {
            "paper_id": "openalex:W1",
            "title": "A Principled Survey",
            "year": 2026,
            "publication_year": 2026,
            "authors": ["Author One", "Author Two"],
            "doi": "10.1000/survey",
            "paper_url": "https://doi.org/10.1000/survey",
            "task": "source_attribution",
            "subtask": "source_identification",
            "entry_type": "method",
            "review_status": "reviewed",
        }
        public_marker = {
            **public_paper,
            "id": "marker:one",
            "institution": "Example University",
            "institution_authors": ["Author One", "Author Two"],
            "latitude": 43.3188,
            "longitude": 11.3308,
        }

        papers, markers, _reviews, _summary = integrate_curated_records(
            [public_paper],
            [public_marker],
            [curated_row(entry_type="survey")],
            [],
        )

        self.assertEqual(len(papers), 1)
        self.assertEqual(len(markers), 1)
        self.assertEqual(papers[0]["entry_type"], "survey")
        self.assertEqual(markers[0]["entry_type"], "survey")
        self.assertEqual(
            (markers[0]["latitude"], markers[0]["longitude"]),
            (43.3188, 11.3308),
        )
        self.assertEqual(
            markers[0]["institution_authors"],
            ["Author One", "Author Two"],
        )
        self.assertEqual(
            normalize_entry_type(papers[0]),
            "survey",
        )


if __name__ == "__main__":
    unittest.main()
