import csv
import contextlib
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from scripts.arxiv_autofill import (
    discover_public_map_arxiv_candidates,
    read_curated_arxiv_links,
)
from scripts.curated_schema import (
    CURATED_ARXIV_LINK_COLUMNS,
    PAPER_EXCLUSION_COLUMNS,
    REVIEW_DECISION_COLUMNS,
)
from scripts.review_decisions import read_review_decisions
from scripts.serve_admin import make_handler


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def public_record():
    return {
        "id": "paper:one",
        "title": "Exact Synthetic Image Detection",
        "year": 2025,
        "publication_year": 2025,
        "doi": "10.1000/example",
        "openalex_url": "https://openalex.org/W1",
        "arxiv_id": "",
        "in_scope": True,
        "task": "detection",
        "entry_type": "method",
        "institution": "Example University",
        "latitude": 43.0,
        "longitude": 11.0,
        "resolution_confidence": "high",
        "needs_review": False,
    }


class ArxivEnrichmentDiscoveryTests(unittest.TestCase):
    def test_discovery_returns_evidence_without_writing_curated_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "map.json"
            links_path = root / "paper_arxiv_links.csv"
            exclusions_path = root / "paper_exclusions.csv"
            map_path.write_text(json.dumps([public_record()]), encoding="utf-8")
            write_csv(links_path, CURATED_ARXIV_LINK_COLUMNS)
            write_csv(exclusions_path, PAPER_EXCLUSION_COLUMNS)
            before = links_path.read_bytes()

            result = discover_public_map_arxiv_candidates(
                map_path=map_path,
                links_path=links_path,
                exclusions_path=exclusions_path,
                lookup=lambda _title: [{
                    "title": "Exact Synthetic Image Detection",
                    "arxiv_id": "2501.01234v2",
                }],
            )

            self.assertFalse(result["writes_performed"])
            self.assertEqual(links_path.read_bytes(), before)
            candidate = result["candidate_papers"][0]["candidates"][0]
            self.assertEqual(candidate["arxiv_id"], "2501.01234")
            self.assertEqual(candidate["confidence"], "high")
            self.assertIn("title match", candidate["evidence"])
            self.assertIn("arXiv Atom API", candidate["source"])


class ArxivEnrichmentActionTests(unittest.TestCase):
    @contextlib.contextmanager
    def server(self, directory):
        root = Path(directory)
        links_path = root / "paper_arxiv_links.csv"
        decisions_path = root / "review_decisions.csv"
        write_csv(links_path, CURATED_ARXIV_LINK_COLUMNS)
        write_csv(decisions_path, REVIEW_DECISION_COLUMNS)
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler(
                "test-token",
                curated_arxiv_links_path=links_path,
                review_decisions_path=decisions_path,
            ),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", links_path, decisions_path
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def post(self, base_url, payload):
        request = urllib.request.Request(
            base_url + "/api/admin/papers/arxiv-enrichment/action",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"X-Admin-Token": "test-token", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.loads(response.read())

    def test_accept_requires_confirmation_and_ignore_does_not_write_link(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.server(directory) as (base_url, links_path, decisions_path):
                paper = {
                    "title": "Paper One",
                    "year": "2025",
                    "doi": "10.1000/one",
                    "openalex_url": "https://openalex.org/W1",
                    "arxiv_id": "2501.01234",
                    "action": "accept",
                }
                before = links_path.read_bytes()
                with self.assertRaises(urllib.error.HTTPError) as unconfirmed:
                    self.post(base_url, paper)
                self.assertEqual(unconfirmed.exception.code, 400)
                self.assertEqual(links_path.read_bytes(), before)

                self.post(base_url, {**paper, "confirmed": True})
                self.assertEqual(
                    read_curated_arxiv_links(links_path)[0]["arxiv_id"],
                    "2501.01234",
                )
                linked_bytes = links_path.read_bytes()
                self.post(base_url, {
                    **paper,
                    "title": "Paper Two",
                    "doi": "10.1000/two",
                    "openalex_url": "https://openalex.org/W2",
                    "action": "ignore",
                    "confirmed": True,
                })
                self.assertEqual(links_path.read_bytes(), linked_bytes)
                self.assertEqual(
                    read_review_decisions(decisions_path)[0]["action"],
                    "ignore_arxiv_candidate",
                )


if __name__ == "__main__":
    unittest.main()
