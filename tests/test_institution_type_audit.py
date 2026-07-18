import csv
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"


def read_csv(name):
    with (CURATED / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class InstitutionTypeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.institutions = read_csv("institutions.csv")
        cls.by_name = {row["canonical_name"]: row for row in cls.institutions}

    def test_audited_repository_counts_and_unique_ids(self):
        self.assertEqual(len(self.institutions), 344)
        self.assertEqual(len({row["institution_id"] for row in self.institutions}), 344)
        self.assertEqual(Counter(row["institution_type"] for row in self.institutions), {
            "university": 244,
            "research_unit": 57,
            "company": 39,
            "other": 4,
        })

    def test_required_universities_and_schools(self):
        for name in ("Rensselaer Polytechnic Institute", "École Polytechnique"):
            self.assertEqual(self.by_name[name]["institution_type"], "university")
        for name in (
            "Everest English Boarding Secondary School",
            "BASIS International School Nanjing",
        ):
            self.assertEqual(self.by_name[name]["institution_type"], "other")

    def test_company_and_independent_research_institute_examples(self):
        for name in ("Alibaba Group", "SenseTime", "Microsoft Research Asia"):
            self.assertEqual(self.by_name[name]["institution_type"], "company")
        self.assertEqual(
            self.by_name["Max Planck Institute for Informatics"]["institution_type"],
            "research_unit",
        )

    def test_public_outputs_share_corrected_types_and_filter_counts(self):
        payloads = []
        for filename in (
            "public_preview_papers.json", "public_preview_map_data.json",
        ):
            with (ROOT / "web/data" / filename).open(encoding="utf-8") as handle:
                payloads.append(json.load(handle))
        timestamp = payloads[0]["metadata"]["public_preview_generated_at"]
        self.assertEqual(timestamp, payloads[1]["metadata"]["public_preview_generated_at"])
        self.assertRegex(timestamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        for payload in payloads:
            by_name = {
                row["canonical_name"]: row["institution_type"]
                for row in payload["canonical_institution_search_index"].values()
            }
            self.assertEqual(by_name["Rensselaer Polytechnic Institute"], "university")
            self.assertEqual(by_name["École Polytechnique"], "university")
            self.assertEqual(by_name["Alibaba Group"], "company")
            self.assertEqual(by_name["SenseTime"], "company")
            self.assertEqual(by_name["Max Planck Institute for Informatics"], "research_unit")

        counts = Counter()
        for paper in payloads[0]["records"]:
            counts.update(set(paper.get("aggregated_institution_types") or ()))
        self.assertEqual(counts, {
            "university": 448,
            "research_unit": 109,
            "company": 49,
            "other": 61,
        })

    def test_references_still_use_stable_audited_ids(self):
        expected = {
            name: self.by_name[name]["institution_id"]
            for name in (
                "Rensselaer Polytechnic Institute", "École Polytechnique",
                "Alibaba Group", "SenseTime",
            )
        }
        self.assertEqual(len(read_csv("institution_aliases.csv")), 50)
        for filename in ("author_institution_mappings.csv", "institution_locations.csv"):
            referenced = {row.get("institution_id", "") for row in read_csv(filename)}
            for name, institution_id in expected.items():
                self.assertIn(institution_id, referenced, f"{name} missing from {filename}")
        self.assertEqual(
            self.by_name["Alibaba Group"]["parent_institution_id"],
            "institution:6faf58b52bec4e39",
        )


class InstitutionTypeFrontendContractTests(unittest.TestCase):
    def test_shared_labels_are_loaded_before_both_applications(self):
        public_html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        admin_html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        for html, application in ((public_html, "app.js"), (admin_html, "admin.js")):
            self.assertIn("institution_type_labels.js", html)
            self.assertLess(html.index("institution_type_labels.js"), html.index(application))

    def test_no_user_facing_research_unit_label_remains(self):
        labels = (ROOT / "web/institution_type_labels.js").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        admin = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn('research_unit: "Research Institute"', labels)
        self.assertNotIn("Research Unit", labels + app + admin)
        self.assertNotIn("Research unit", labels + app + admin)

    def test_admin_uses_label_resolver_but_edits_machine_value(self):
        admin = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        self.assertIn("InstitutionTypeLabels.label(institution.institution_type)", admin)
        self.assertIn("Research Institute = research_unit", admin)


if __name__ == "__main__":
    unittest.main()
