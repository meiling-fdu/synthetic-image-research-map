import csv
import unittest
from pathlib import Path

from scripts.audit_institution_acronym_names import (
    DECISION_COLUMNS, build_audit,
)


ROOT = Path(__file__).resolve().parents[1]


class InstitutionAcronymNameAuditTests(unittest.TestCase):
    def test_repository_candidates_are_fully_resolved(self):
        with (ROOT / "data/curated/institutions.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            institutions = list(csv.DictReader(handle))
        with (ROOT / "data/manual/institution_acronym_name_decisions.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(tuple(reader.fieldnames or ()), DECISION_COLUMNS)
            decisions = list(reader)
        audit, issues = build_audit(institutions, decisions)
        self.assertEqual(issues, [])
        self.assertEqual(len(audit), 7)
        self.assertEqual(sum(row["decision"] == "expanded" for row in audit), 3)
        self.assertEqual(
            sum(row["decision"] == "intentional_brand" for row in audit), 4
        )
        self.assertTrue(all(row["validation_status"] == "resolved" for row in audit))


if __name__ == "__main__":
    unittest.main()
