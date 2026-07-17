import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import CuratedInstitutionError, update_institution_identity
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
)
from scripts.institution_types import (
    INSTITUTION_TYPES,
    build_migration_rows,
    classify_institution_type,
    resolve_public_institution_type,
)
from scripts.migrate_institution_types import migrate
from scripts.export_public_preview import normalize_exported_institution_types


def blank(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class InstitutionTypeRuleTests(unittest.TestCase):
    def test_final_taxonomy_and_legacy_resolution(self):
        self.assertEqual(
            INSTITUTION_TYPES,
            ("university", "research_unit", "company", "other"),
        )
        self.assertEqual(resolve_public_institution_type("laboratory"), "research_unit")
        self.assertEqual(resolve_public_institution_type("department"), "research_unit")
        self.assertEqual(resolve_public_institution_type("unknown"), "other")
        self.assertEqual(resolve_public_institution_type("unexpected"), "other")

    def test_complete_case_insensitive_university_word_in_name_and_alias(self):
        self.assertEqual(
            classify_institution_type("Example UNIVERSITY Center", (), "unknown")[0],
            "university",
        )
        self.assertEqual(
            classify_institution_type("Example U", ("Example University",), "unknown")[0],
            "university",
        )
        self.assertNotEqual(
            classify_institution_type("Universitylike Labs", (), "unknown")[0],
            "university",
        )

    def test_legacy_company_corporate_lab_and_unknown_rules(self):
        self.assertEqual(classify_institution_type("Example Lab", (), "laboratory")[0], "research_unit")
        self.assertEqual(classify_institution_type("Example Department", (), "department")[0], "research_unit")
        self.assertEqual(classify_institution_type("Acme", (), "company")[0], "company")
        self.assertEqual(classify_institution_type("Acme Research Lab", (), "company")[0], "company")
        self.assertEqual(classify_institution_type("Unclassified Entity", (), "unknown")[0], "other")

    def test_merged_resolution_and_parent_child_are_independent(self):
        institutions = [
            {"institution_id": "old", "canonical_name": "Old Lab", "institution_type": "laboratory", "institution_status": "merged"},
            {"institution_id": "parent", "canonical_name": "Parent University", "institution_type": "university", "institution_status": "active"},
            {"institution_id": "child", "canonical_name": "Child Research Center", "institution_type": "research_unit", "institution_status": "active", "parent_institution_id": "parent"},
        ]
        aliases = [{"alias_name": "Old Lab", "institution_id": "child", "review_status": "confirmed"}]
        rows = {row["institution_id"]: row for row in build_migration_rows(institutions, aliases)}
        self.assertEqual(rows["old"]["proposed_type"], "research_unit")
        self.assertIn("merged_id_resolution", rows["old"]["applied_rule"])
        self.assertEqual(rows["parent"]["proposed_type"], "university")
        self.assertEqual(rows["child"]["proposed_type"], "research_unit")

    def test_public_export_uses_canonical_type_for_every_affiliation_copy(self):
        institutions = [{
            "institution_id": "research", "canonical_name": "Example Center",
            "institution_type": "research_unit", "institution_status": "active",
        }]
        papers = [{
            "affiliations": [{"institution_id": "research", "name": "Example Center", "institution_type": "unknown"}],
            "author_institution_affiliations": [{"institution_id": "research", "institution": "Example Center"}],
            "aggregated_institution_types": ["unknown"],
        }]
        maps = [{
            "institution_id": "research", "institution": "Example Center",
            "institution_type": "laboratory",
        }]
        normalize_exported_institution_types(papers, maps, institutions)
        self.assertEqual(papers[0]["aggregated_institution_types"], ["research_unit"])
        self.assertEqual(papers[0]["affiliations"][0]["institution_type"], "research_unit")
        self.assertEqual(
            papers[0]["author_institution_affiliations"][0]["institution_type"],
            "research_unit",
        )
        self.assertEqual(maps[0]["institution_type"], "research_unit")


class InstitutionTypeMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.institutions = self.root / "institutions.csv"
        self.aliases = self.root / "aliases.csv"
        self.mappings = self.root / "mappings.csv"
        self.report = self.root / "report.csv"
        write_csv(self.institutions, INSTITUTION_COLUMNS, [
            blank(INSTITUTION_COLUMNS, institution_id="u", canonical_name="Alias U", institution_type="unknown", institution_status="active"),
            blank(INSTITUTION_COLUMNS, institution_id="l", canonical_name="Research Laboratory", institution_type="laboratory", institution_status="active"),
        ])
        write_csv(self.aliases, INSTITUTION_ALIAS_COLUMNS, [
            blank(INSTITUTION_ALIAS_COLUMNS, alias_name="ALIAS UNIVERSITY", institution_id="u", review_status="confirmed"),
        ])
        write_csv(self.mappings, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [
            blank(AUTHOR_INSTITUTION_MAPPING_COLUMNS, paper_id="paper:1", institution_id="u", mapping_status="active"),
            blank(AUTHOR_INSTITUTION_MAPPING_COLUMNS, paper_id="paper:1", institution_id="u", mapping_status="active"),
        ])

    def tearDown(self):
        self.temporary.cleanup()

    def test_apply_is_idempotent_and_report_counts_unique_papers(self):
        first = migrate(self.institutions, self.aliases, self.mappings, self.report, apply=True)
        second = migrate(self.institutions, self.aliases, self.mappings, self.report, apply=False)
        self.assertEqual(first["changes"], 2)
        self.assertEqual(second["changes"], 0)
        with self.report.open(encoding="utf-8", newline="") as handle:
            report = {row["institution_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(report["u"]["affected_unique_paper_count"], "1")
        self.assertEqual(report["u"]["proposed_type"], "university")

    def test_admin_rejects_legacy_values(self):
        with self.assertRaisesRegex(CuratedInstitutionError, "unsupported institution_type"):
            update_institution_identity(
                "u", {"institution_type": "laboratory"},
                institutions_path=self.institutions,
            )
