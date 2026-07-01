import unittest

from scripts.canonical_authorship import load_canonical_dataset


class CuratedLocationResolutionTests(unittest.TestCase):
    def test_markers_reference_canonical_institutions(self):
        data = load_canonical_dataset(check_runtime=False)
        papers = {paper["paper_id"]: paper for paper in data["papers"]}
        for marker in data["markers"]:
            ids = {
                item["institution_id"]
                for item in papers[marker["paper_id"]]["canonical_authorship"]["institutions"]
            }
            self.assertIn(marker["institution_id"], ids)


if __name__ == "__main__":
    unittest.main()
