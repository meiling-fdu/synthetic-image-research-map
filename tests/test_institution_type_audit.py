import csv
import json
import subprocess
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
        self.assertEqual(len(self.institutions), 562)
        self.assertEqual(len({row["institution_id"] for row in self.institutions}), 562)
        self.assertEqual(Counter(row["institution_type"] for row in self.institutions), {
            "university": 431,
            "research_unit": 69,
            "company": 58,
            "other": 4,
        })

    def test_required_universities_and_schools(self):
        for name in ("Rensselaer Polytechnic Institute", "École Polytechnique"):
            self.assertEqual(self.by_name[name]["institution_type"], "university")
        for name in (
            "Everest English Boarding Secondary School",
            "BASIS International School Nanjing",
            "Hand and Upper Limb Clinic",
            "Indiana Hand to Shoulder Center",
        ):
            self.assertEqual(self.by_name[name]["institution_type"], "other")

    def test_confirmed_public_university_examples_are_curated(self):
        expected = {
            "University of Rajshahi": "institution:85eee734d249f6b1",
            "Korea Aerospace University": "institution:7095dc4de406754b",
            "University of Michigan–Flint": "institution:d4c5c00e6ef405e5",
            "Chaoyang University of Technology": "institution:1633fd8e927f7e3e",
            "University of Petroleum and Energy Studies": "institution:018c503420feda75",
            "Dar Al-Hekma University": "institution:ec338d817ec6cd01",
            "University of Liverpool": "institution:6897907a26009a77",
            "University of Warwick": "institution:4d3dd6848c184118",
            "Global University": "institution:f647b4b37bf4515d",
            "University of Jinan": "institution:4dc98405f4a72728",
            "Lamar University": "institution:bec45b93a867958c",
            "Anhui Business College": "institution:aa230e9d21cefa3b",
        }
        for name, institution_id in expected.items():
            self.assertEqual(self.by_name[name]["institution_id"], institution_id)
            self.assertEqual(self.by_name[name]["institution_type"], "university")
        self.assertEqual(
            self.by_name["University of Michigan–Flint"]["parent_institution_id"],
            "",
        )

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
            self.assertEqual(by_name["University of Rajshahi"], "university")
            self.assertEqual(by_name["Korea Aerospace University"], "university")
            self.assertEqual(by_name["University of Michigan–Flint"], "university")
            self.assertEqual(by_name["Anhui Business College"], "university")

        counts = Counter()
        for paper in payloads[0]["records"]:
            counts.update(set(paper.get("aggregated_institution_types") or ()))
        self.assertEqual(counts, {
            "university": 457,
            "research_unit": 96,
            "company": 70,
            "other": 39,
        })

    def test_university_filter_includes_corrected_records_and_other_excludes_them(self):
        with (ROOT / "web/data/public_preview_papers.json").open(encoding="utf-8") as handle:
            papers = json.load(handle)["records"]
        corrected = {
            "institution:85eee734d249f6b1",
            "institution:7095dc4de406754b",
            "institution:d4c5c00e6ef405e5",
            "institution:aa230e9d21cefa3b",
        }
        seen = set()
        for paper in papers:
            for affiliation in paper.get("affiliations") or []:
                if affiliation.get("institution_id") in corrected:
                    seen.add(affiliation["institution_id"])
                    self.assertEqual(affiliation["institution_type"], "university")
                    self.assertIn("university", paper["aggregated_institution_types"])
                    self.assertNotEqual(affiliation["institution_type"], "other")
        self.assertEqual(seen, corrected)

    def test_cifake_northeastern_and_branch_campus_contracts_remain_intact(self):
        by_id = {row["institution_id"]: row for row in self.institutions}
        self.assertEqual(by_id["institution:0008285766dcabc7"]["institution_type"], "university")
        self.assertEqual(by_id["institution:ff1a1bc95dbe91a8"]["institution_type"], "university")
        self.assertEqual(
            by_id["institution:d4c5c00e6ef405e5"]["canonical_name"],
            "University of Michigan–Flint",
        )
        locations = read_csv("institution_locations.csv")
        northeastern_locations = {
            row["institution_id"]: (row["city"], row["country"])
            for row in locations
            if row["institution_id"] in {
                "institution:0008285766dcabc7",
                "institution:ff1a1bc95dbe91a8",
            }
        }
        self.assertEqual(northeastern_locations["institution:0008285766dcabc7"], ("Shenyang", "China"))
        self.assertEqual(northeastern_locations["institution:ff1a1bc95dbe91a8"], ("Boston", "United States"))
        mappings = read_csv("author_institution_mappings.csv")
        cifake = [
            row for row in mappings
            if row["paper_id"] == "openalex:W4391019749"
            and row["institution_id"] == "institution:c055ca96e505b797"
        ]
        self.assertTrue(cifake)

    def test_audit_output_is_deterministic_and_has_no_pending_high_confidence(self):
        command = ["python3", "scripts/audit_institution_types.py", "--check"]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        first = (ROOT / "data/processed/institution_type_audit.csv").read_text(encoding="utf-8")
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        second = (ROOT / "data/processed/institution_type_audit.csv").read_text(encoding="utf-8")
        self.assertEqual(first, second)
        rows = list(csv.DictReader(first.splitlines()))
        self.assertFalse([
            row for row in rows
            if row["confidence"] == "high"
            and row["current_type"] != row["proposed_type"]
        ])
        self.assertIn("Shenzhen University Health Science Center", {
            row["canonical_name"] for row in rows if row["review_required"] == "yes"
        })

    def test_references_still_use_stable_audited_ids(self):
        expected = {
            name: self.by_name[name]["institution_id"]
            for name in (
                "Rensselaer Polytechnic Institute", "École Polytechnique",
                "Alibaba Group", "SenseTime",
            )
        }
        self.assertEqual(len(read_csv("institution_aliases.csv")), 67)
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
