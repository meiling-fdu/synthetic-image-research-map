import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import export_public_preview
from scripts.public_export_metadata import (
    TIMESTAMP_FIELD,
    add_export_timestamp,
    atomic_write_json_files,
    is_utc_timestamp,
    utc_timestamp,
)
from scripts.validate_public_preview import validate_export_metadata_pair


VENUE_ORDER = ["conference", "journal", "preprint", "book"]


def payload(kind):
    return {"metadata": {"kind": kind}, "records": [{"id": kind}]}


class PublicExportMetadataTests(unittest.TestCase):
    def test_successful_commit_writes_one_utc_iso_timestamp_to_both_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            map_path = Path(directory) / "map.json"
            paper_path = Path(directory) / "papers.json"
            map_payload = payload("map")
            paper_payload = payload("papers")
            with mock.patch.object(
                export_public_preview,
                "validate_proposed_public_outputs",
            ):
                result = export_public_preview.commit_public_outputs(
                    map_path,
                    map_payload,
                    paper_path,
                    paper_payload,
                    [],
                    timestamp="2026-07-18T12:34:56Z",
                )
            values = [
                json.loads(path.read_text())["metadata"][TIMESTAMP_FIELD]
                for path in (map_path, paper_path)
            ]
            self.assertEqual(result, "2026-07-18T12:34:56Z")
            self.assertEqual(values, [result, result])
            self.assertTrue(is_utc_timestamp(result))

    def test_dry_run_does_not_add_or_write_timestamp(self):
        map_payload = payload("map")
        paper_payload = payload("papers")
        original = (copy.deepcopy(map_payload), copy.deepcopy(paper_payload))
        with mock.patch.object(
            export_public_preview, "atomic_write_json_files"
        ) as writer:
            result = export_public_preview.commit_public_outputs(
                Path("map.json"), map_payload,
                Path("papers.json"), paper_payload,
                [], dry_run=True,
            )
        self.assertIsNone(result)
        self.assertEqual((map_payload, paper_payload), original)
        writer.assert_not_called()

    def test_validation_failure_does_not_write_timestamp_or_files(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("map.json", "papers.json")]
            for path in paths:
                path.write_text("old\n")
            before = [path.read_bytes() for path in paths]
            with mock.patch.object(
                export_public_preview,
                "validate_proposed_public_outputs",
                side_effect=export_public_preview.PreviewExportError("invalid"),
            ), self.assertRaises(export_public_preview.PreviewExportError):
                export_public_preview.commit_public_outputs(
                    paths[0], payload("map"), paths[1], payload("papers"), []
                )
            self.assertEqual([path.read_bytes() for path in paths], before)

    def test_transaction_rolls_back_first_file_if_second_replace_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("map.json", "papers.json")]
            for index, path in enumerate(paths):
                path.write_text(f"old-{index}\n")
            before = [path.read_bytes() for path in paths]
            real_replace = os.replace
            calls = 0

            def fail_second(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated second replacement failure")
                return real_replace(source, destination)

            with mock.patch(
                "scripts.public_export_metadata.os.replace",
                side_effect=fail_second,
            ), self.assertRaises(OSError):
                atomic_write_json_files({
                    paths[0]: payload("map"),
                    paths[1]: payload("papers"),
                })
            self.assertEqual([path.read_bytes() for path in paths], before)

    def test_later_successful_export_advances_timestamp(self):
        first = utc_timestamp(datetime(2026, 7, 18, 10, tzinfo=timezone.utc))
        second = utc_timestamp(datetime(2026, 7, 18, 11, tzinfo=timezone.utc))
        self.assertLess(first, second)
        map_payload = payload("map")
        paper_payload = payload("papers")
        add_export_timestamp(map_payload, paper_payload, first)
        add_export_timestamp(map_payload, paper_payload, second)
        self.assertEqual(map_payload["metadata"][TIMESTAMP_FIELD], second)
        self.assertEqual(paper_payload["metadata"][TIMESTAMP_FIELD], second)

    def test_validator_rejects_inconsistent_timestamps(self):
        map_metadata = {TIMESTAMP_FIELD: "2026-07-18T10:00:00Z"}
        paper_metadata = {TIMESTAMP_FIELD: "2026-07-18T10:00:01Z"}
        issues, paper_issues = [], []
        validate_export_metadata_pair(
            map_metadata, paper_metadata, issues, paper_issues
        )
        self.assertTrue(any("must match" in issue.message for issue in issues))
        self.assertTrue(any("must match" in issue.message for issue in paper_issues))

    def test_validator_rejects_non_utc_or_one_sided_timestamp(self):
        issues, paper_issues = [], []
        validate_export_metadata_pair(
            {TIMESTAMP_FIELD: "2026-07-18T10:00:00+02:00"},
            {},
            issues,
            paper_issues,
        )
        self.assertTrue(issues)
        self.assertTrue(paper_issues)

    def test_shrinkage_guard_precedes_timestamp_commit_in_exporter(self):
        source = Path(export_public_preview.__file__).read_text(encoding="utf-8")
        main_source = source.split("def main(", 1)[1]
        self.assertLess(
            main_source.index("shrinkage_report = analyze_shrinkage("),
            main_source.index("commit_public_outputs("),
        )


if __name__ == "__main__":
    unittest.main()
