import csv
import json
import unittest
from collections import defaultdict
from pathlib import Path

from scripts.curated_institutions import normalize_institution


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"
TURIN_ID = "institution:bce986d0881eaaed"
MANNHEIM_ID = "institution:a7afa880cf905469"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class AuthoritativeInstitutionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.institutions = read_csv(CURATED / "institutions.csv")
        cls.by_id = {row["institution_id"]: row for row in cls.institutions}
        cls.aliases = read_csv(CURATED / "institution_aliases.csv")
        cls.mappings = read_csv(CURATED / "author_institution_mappings.csv")

    def test_polytechnic_university_of_turin_is_canonical_and_variants_resolve(self):
        row = self.by_id[TURIN_ID]
        self.assertEqual(row["canonical_name"], "Polytechnic University of Turin")
        self.assertEqual(row["institution_type"], "university")
        names = {
            alias["alias_name"] for alias in self.aliases
            if alias["institution_id"] == TURIN_ID
        }
        self.assertTrue({
            "Polytechnic Institute of Turin",
            "Polytechnic Institute of Turin, Turin, Italy",
            "Politecnico di Torino",
            "PoliTo",
        }.issubset(names))
        self.assertEqual(self.by_id["institution:35caf31d5104b996"]["institution_status"], "merged")

    def test_mannheim_duplicate_is_consolidated_with_source_names_as_aliases(self):
        row = self.by_id[MANNHEIM_ID]
        self.assertEqual(row["canonical_name"], "Technical University of Applied Sciences Mannheim")
        self.assertEqual(row["institution_type"], "university")
        self.assertEqual(self.by_id["institution:bbbd3e4c853af6c2"]["institution_status"], "merged")
        names = {alias["alias_name"] for alias in self.aliases if alias["institution_id"] == MANNHEIM_ID}
        self.assertTrue({"Mannheim University of Applied Sciences", "Hochschule Mannheim", "Technische Hochschule Mannheim"}.issubset(names))

    def test_all_expected_duplicate_sources_are_retired(self):
        sources = {
            "institution:35caf31d5104b996", "institution:bbbd3e4c853af6c2",
            "institution:965434eee0b97685", "institution:d31a9474efa16c6c",
            "institution:42c60ebb24e9f839", "institution:6f14a665aa77ba34",
            "institution:2e732c4601154ff1", "institution:b8a4e3b25fd4a300",
            "institution:b3e3a87d3fc950c5", "institution:6faf58b52bec4e39",
            "institution:e75cc4bbe66bd6c8", "institution:29f3e76214681290",
            "institution:b771bab570cca255", "institution:49700da520d8842b",
            "institution:fe8410750f429b37", "institution:cd66beec0fcee918",
            "institution:2592e804f95fa542", "institution:f0501582969408c8",
        }
        self.assertTrue(all(self.by_id[institution_id]["institution_status"] == "merged" for institution_id in sources))

    def test_no_active_mapping_targets_a_retired_institution(self):
        active_ids = {row["institution_id"] for row in self.institutions if row["institution_status"] == "active"}
        invalid = [row["mapping_id"] for row in self.mappings if row["mapping_status"] == "active" and row["institution_id"] not in active_ids]
        self.assertEqual(invalid, [])

    def test_confirmed_aliases_do_not_resolve_ambiguously(self):
        active_ids = {row["institution_id"] for row in self.institutions if row["institution_status"] == "active"}
        targets = defaultdict(set)
        for row in self.aliases:
            if row["review_status"] == "confirmed" and row["institution_id"] in active_ids:
                targets[normalize_institution(row["alias_name"])].add(row["institution_id"])
        self.assertEqual({key: ids for key, ids in targets.items() if len(ids) > 1}, {})

    def test_suspicious_records_have_audited_types(self):
        expected = {
            "institution:64aa68d006c72586": "university",
            "institution:53765f8a62a101ca": "university",
            "institution:1f4217b90babf040": "university",
            "institution:2b6e51bec93e86c1": "company",
            "institution:3103fb7db9011c4c": "company",
            "institution:b4e88842382d76c1": "research_unit",
            "institution:e9687e710c08b33b": "research_unit",
            "institution:13bd816e4b457f40": "research_unit",
        }
        self.assertEqual({key: self.by_id[key]["institution_type"] for key in expected}, expected)

    def test_audit_ledger_covers_every_institution_active_at_migration_start(self):
        audit = read_csv(ROOT / "data/processed/institution_authoritative_audit.csv")
        summary = json.loads((ROOT / "data/processed/institution_authoritative_audit_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(len(audit), summary["audited_active_institutions"])
        self.assertEqual(len({row["institution_id"] for row in audit}), len(audit))
        self.assertEqual(summary["raw_affiliation_digest_before"], summary["raw_affiliation_digest_after"])
        self.assertEqual(summary["active_mappings_to_retired_ids"], 0)
        self.assertEqual(summary["ambiguous_alias_keys"], 0)

    def test_public_exports_use_curated_names_and_types(self):
        payload = json.loads((ROOT / "web/data/public_preview_papers.json").read_text(encoding="utf-8"))
        index = payload["canonical_institution_search_index"]
        self.assertEqual(index[TURIN_ID]["canonical_name"], "Polytechnic University of Turin")
        self.assertEqual(index[TURIN_ID]["institution_type"], "university")
        self.assertEqual(index[MANNHEIM_ID]["canonical_name"], "Technical University of Applied Sciences Mannheim")
        self.assertIn("Polytechnic Institute of Turin", index[TURIN_ID]["names"])


if __name__ == "__main__":
    unittest.main()
