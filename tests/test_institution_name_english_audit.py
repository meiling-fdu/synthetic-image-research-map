import csv
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.audit_institution_names import (
    REPORT_COLUMNS,
    build_report,
    contains_non_latin_script,
)
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS,
)


ROOT = Path(__file__).resolve().parents[1]


def row(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_csv(path, columns, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class InstitutionNameEnglishAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.institutions = self.root / "institutions.csv"
        self.aliases = self.root / "aliases.csv"
        self.mappings = self.root / "mappings.csv"
        self.locations = self.root / "locations.csv"
        self.report = self.root / "report.csv"
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            row(
                INSTITUTION_COLUMNS,
                institution_id="institution:2e62680df0fed751",
                canonical_name="Huawei Noah’s Ark Lab",
                institution_type="company",
                institution_status="active",
                updated_at="2026-01-01T00:00:00Z",
            ),
            row(
                INSTITUTION_COLUMNS,
                institution_id="institution:neu-cn",
                canonical_name="Northeastern University",
                institution_status="active",
            ),
            row(
                INSTITUTION_COLUMNS,
                institution_id="institution:neu-us",
                canonical_name="Northeastern University",
                institution_status="active",
            ),
            row(
                INSTITUTION_COLUMNS,
                institution_id="institution:zh",
                canonical_name="东北大学",
                institution_status="active",
            ),
        ])
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [
            row(
                INSTITUTION_ALIAS_COLUMNS,
                alias_id="alias:huawei",
                alias_name="Huawei Noah's Ark Lab",
                institution_id="institution:2e62680df0fed751",
                canonical_institution_name="Huawei Noah’s Ark Lab",
                review_status="confirmed",
            ),
            row(
                INSTITUTION_ALIAS_COLUMNS,
                alias_id="alias:zh",
                alias_name="Northeastern University, China",
                institution_id="institution:zh",
                canonical_institution_name="东北大学",
                review_status="confirmed",
            ),
        ])
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            row(
                AUTHOR_INSTITUTION_MAPPING_COLUMNS,
                mapping_id="mapping:huawei",
                paper_id="paper:1",
                institution="Huawei Noah’s Ark Lab",
                institution_id="institution:2e62680df0fed751",
                institution_authors="Ada Author",
                mapping_status="active",
            )
        ])
        write_csv(self.locations, INSTITUTION_LOCATION_COLUMNS, [
            row(
                INSTITUTION_LOCATION_COLUMNS,
                institution_id="institution:neu-cn",
                institution="Northeastern University",
                city="Shenyang",
                country="China",
            ),
            row(
                INSTITUTION_LOCATION_COLUMNS,
                institution_id="institution:neu-us",
                institution="Northeastern University",
                city="Boston",
                country="United States",
            ),
        ])

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, *args):
        return subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/audit_institution_names.py"),
                *args,
                "--institutions",
                str(self.institutions),
                "--aliases",
                str(self.aliases),
                "--mappings",
                str(self.mappings),
                "--locations",
                str(self.locations),
                "--output",
                str(self.report),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_non_latin_canonical_name_is_review_candidate(self):
        rows = build_report(read_csv(self.institutions), read_csv(self.aliases), read_csv(self.locations), read_csv(self.mappings))
        candidate = next(row for row in rows if row["institution_id"] == "institution:zh")
        self.assertTrue(contains_non_latin_script(candidate["old_canonical_name"]))
        self.assertEqual(candidate["review_required"], "true")
        self.assertEqual(candidate["confidence"], "review")

    def test_apply_high_confidence_preserves_ids_and_updates_display_name(self):
        self.run_script("--apply-high-confidence")
        institutions = read_csv(self.institutions)
        aliases = read_csv(self.aliases)
        mappings = read_csv(self.mappings)
        huawei = next(row for row in institutions if row["institution_id"] == "institution:2e62680df0fed751")
        self.assertEqual(huawei["canonical_name"], "Huawei Noah's Ark Lab")
        self.assertTrue(any(
            row["institution_id"] == "institution:2e62680df0fed751"
            and row["alias_name"] == "Huawei Noah’s Ark Lab"
            for row in aliases
        ))
        self.assertEqual(mappings[0]["mapping_id"], "mapping:huawei")
        self.assertEqual(mappings[0]["institution_id"], "institution:2e62680df0fed751")
        self.assertEqual(mappings[0]["institution"], "Huawei Noah's Ark Lab")

    def test_check_writes_deterministic_report_without_applying(self):
        self.run_script("--check")
        first = self.report.read_text(encoding="utf-8")
        self.run_script("--check")
        self.assertEqual(self.report.read_text(encoding="utf-8"), first)
        report_rows = read_csv(self.report)
        self.assertEqual(tuple(report_rows[0].keys()), REPORT_COLUMNS)
        institutions = read_csv(self.institutions)
        huawei = next(row for row in institutions if row["institution_id"] == "institution:2e62680df0fed751")
        self.assertEqual(huawei["canonical_name"], "Huawei Noah’s Ark Lab")

    def test_duplicate_english_names_remain_separate_by_id(self):
        self.run_script("--check")
        rows = read_csv(self.report)
        neu_rows = [row for row in rows if row["old_canonical_name"] == "Northeastern University"]
        self.assertEqual({row["institution_id"] for row in neu_rows}, {"institution:neu-cn", "institution:neu-us"})
        self.assertTrue(all("Duplicate canonical name" in row["notes"] for row in neu_rows))

