import csv
import tempfile
import unittest
from pathlib import Path

from scripts.curated_institutions import CuratedInstitutionError, update_institution_identity
from scripts.curated_schema import (
    ALLOWED_INSTITUTION_TYPES,
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
    INSTITUTION_COLUMNS,
)
from scripts.institution_types import (
    INSTITUTION_TYPE_LABELS,
    INSTITUTION_TYPES,
    build_migration_rows,
    classify_institution_type,
    institution_type_label,
    resolve_public_institution_type,
)
from scripts.migrate_institution_types import migrate
from scripts.export_public_preview import normalize_exported_institution_types
from scripts.validate_curated_database import validate_allowed_value
from scripts.validate_public_preview import (
    ALLOWED_INSTITUTION_TYPES as PUBLIC_ALLOWED_INSTITUTION_TYPES,
)


REPOSITORY = Path(__file__).resolve().parents[1]


def blank(columns, **values):
    return {column: values.get(column, "") for column in columns}


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class InstitutionTypeRuleTests(unittest.TestCase):
    def test_python_layers_share_one_canonical_enum(self):
        expected = frozenset({"university", "research_unit", "company", "other"})
        self.assertEqual(ALLOWED_INSTITUTION_TYPES, expected)
        self.assertEqual(PUBLIC_ALLOWED_INSTITUTION_TYPES, expected)

    def test_curated_validation_accepts_other_and_rejects_unsupported_values(self):
        for value in ("other",):
            issues = []
            validate_allowed_value(
                [{"institution_type": value}], "institutions.csv",
                "institution_type", ALLOWED_INSTITUTION_TYPES, issues,
            )
            self.assertEqual(issues, [])
        for value in (
            "research_institute", "institute", "laboratory", "school",
            "business_unit", "unexpected_value",
        ):
            issues = []
            validate_allowed_value(
                [{"institution_type": value}], "institutions.csv",
                "institution_type", ALLOWED_INSTITUTION_TYPES, issues,
            )
            self.assertEqual(len(issues), 1, value)
            self.assertIn("unsupported value", issues[0].message)

    def test_final_taxonomy_and_legacy_resolution(self):
        self.assertEqual(
            INSTITUTION_TYPES,
            ("university", "research_unit", "company", "other"),
        )
        self.assertEqual(resolve_public_institution_type("laboratory"), "research_unit")
        self.assertEqual(resolve_public_institution_type("department"), "research_unit")
        self.assertEqual(resolve_public_institution_type("unknown"), "other")
        self.assertEqual(resolve_public_institution_type("unexpected"), "other")
        self.assertEqual(INSTITUTION_TYPE_LABELS["research_unit"], "Research Institute")
        self.assertEqual(institution_type_label("research_unit"), "Research Institute")

    def test_structural_name_evidence_is_cautious(self):
        self.assertEqual(
            classify_institution_type("Example UNIVERSITY Center", (), "unknown")[0],
            "other",
        )
        self.assertEqual(
            classify_institution_type("Example University", (), "unknown")[0],
            "university",
        )
        self.assertEqual(
            classify_institution_type("Example U", ("Example University",), "unknown")[0],
            "university",
        )
        self.assertEqual(
            classify_institution_type("Example Laboratory", (), "unknown")[0],
            "research_unit",
        )
        for name in (
            "Example Institute", "University Hospital",
            "University Press", "University Laboratory", "University Medical Center",
            "Department of Example University", "School of Example University",
        ):
            resolved, rule, _ = classify_institution_type(name, (), "unknown")
            self.assertEqual(resolved, "other")
            self.assertEqual(rule, "manual_review_required")

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

    def test_public_export_preserves_other(self):
        institutions = [{
            "institution_id": "school", "canonical_name": "Example School",
            "institution_type": "other", "institution_status": "active",
        }]
        papers = [{
            "affiliations": [{"institution_id": "school", "name": "Example School"}],
            "author_institution_affiliations": [{"institution_id": "school"}],
        }]
        maps = [{"institution_id": "school", "institution": "Example School"}]
        normalize_exported_institution_types(papers, maps, institutions)
        self.assertEqual(maps[0]["institution_type"], "other")
        self.assertEqual(papers[0]["aggregated_institution_types"], ["other"])
        self.assertEqual(papers[0]["affiliations"][0]["institution_type"], "other")


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

    def test_admin_accepts_other_and_rejects_unsupported_values(self):
        updated = update_institution_identity(
            "u", {"institution_type": "other"},
            institutions_path=self.institutions,
        )
        self.assertEqual(updated["institution_type"], "other")
        for value in (
            "research_institute", "institute", "laboratory", "school",
            "business_unit", "unexpected_value",
        ):
            with self.assertRaisesRegex(
                CuratedInstitutionError, "unsupported institution_type"
            ):
                update_institution_identity(
                    "u", {"institution_type": value},
                    institutions_path=self.institutions,
                )


class SchoolInstitutionRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        curated = REPOSITORY / "data" / "curated"
        def read(name):
            with (curated / name).open(encoding="utf-8", newline="") as handle:
                return list(csv.DictReader(handle))
        cls.institutions = read("institutions.csv")
        cls.aliases = read("institution_aliases.csv")
        cls.mappings = read("author_institution_mappings.csv")
        cls.locations = read("institution_locations.csv")
        cls.location_reviews = read("institution_location_review.csv")

    def test_school_records_export_as_other(self):
        by_name = {row["canonical_name"]: row for row in self.institutions}
        for name in (
            "Everest English Boarding Secondary School",
            "BASIS International School Nanjing",
        ):
            institution = by_name[name]
            maps = [{
                "institution_id": institution["institution_id"],
                "institution": name,
            }]
            normalize_exported_institution_types([], maps, self.institutions)
            self.assertEqual(maps[0]["institution_type"], "other")

    def test_basis_spelling_migration_reuses_id_and_preserves_alias_and_references(self):
        basis_id = "institution:04c73587b47761ee"
        canonical_rows = [
            row for row in self.institutions
            if row["institution_id"] == basis_id
        ]
        self.assertEqual(len(canonical_rows), 1)
        self.assertEqual(
            canonical_rows[0]["canonical_name"],
            "BASIS International School Nanjing",
        )
        self.assertFalse(any(
            row["canonical_name"] == "Basis International School Naning"
            for row in self.institutions
        ))
        alias = next(
            row for row in self.aliases
            if row["alias_name"] == "Basis International School Naning"
        )
        self.assertEqual(alias["institution_id"], basis_id)
        self.assertEqual(alias["review_status"], "confirmed")
        self.assertTrue(any(
            row["institution_id"] == basis_id
            and row["institution"] == "BASIS International School Nanjing"
            and row["raw_affiliation"] == "Basis International School Naning"
            and row["mapping_status"] == "active"
            and row["created_at"] == "2026-07-17T23:22:28Z"
            and None not in row
            for row in self.mappings
        ))
        self.assertTrue(any(
            row["institution_id"] == basis_id
            and row["institution"] == "BASIS International School Nanjing"
            for row in self.locations
        ))
        self.assertTrue(any(
            row["institution_id"] == basis_id
            and row["institution"] == "Basis International School Naning"
            and row["canonical_institution_name"]
                == "BASIS International School Nanjing"
            for row in self.location_reviews
        ))
