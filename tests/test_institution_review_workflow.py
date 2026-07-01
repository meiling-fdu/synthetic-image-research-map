import unittest

from scripts.canonical_authorship import load_canonical_dataset


class InstitutionReviewWorkflowTests(unittest.TestCase):
    def test_no_duplicate_institutions_per_paper(self):
        for paper in load_canonical_dataset(check_runtime=False)["papers"]:
            ids = [
                item["institution_id"]
                for item in paper["canonical_authorship"]["institutions"]
            ]
            self.assertEqual(len(ids), len(set(ids)), paper["title"])


if __name__ == "__main__":
    unittest.main()
