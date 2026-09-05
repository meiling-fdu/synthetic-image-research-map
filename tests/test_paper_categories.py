import unittest

from scripts.paper_taxonomy import (
    PaperTaxonomyError,
    normalize_image_scopes,
    normalize_research_types,
    normalize_tasks,
    serialize_image_scopes,
    serialize_research_types,
    serialize_tasks,
)


class PaperTaxonomyTests(unittest.TestCase):
    def test_all_dimensions_are_multi_value_and_canonically_ordered(self):
        self.assertEqual(normalize_tasks(["localization", "detection", "detection"]), ["detection", "localization"])
        self.assertEqual(normalize_image_scopes(["deepfake", "fully_generated"]), ["fully_generated", "deepfake"])
        self.assertEqual(normalize_research_types(["survey", "dataset", "method"]), ["method", "dataset", "survey"])

    def test_csv_serializers_use_semicolon_delimited_canonical_values(self):
        self.assertEqual(serialize_tasks("localization;detection"), "detection;localization")
        self.assertEqual(serialize_image_scopes("deepfake;generative_editing"), "generative_editing;deepfake")
        self.assertEqual(serialize_research_types("benchmark;dataset"), "dataset;benchmark")

    def test_strict_mode_rejects_scalars_unknowns_and_empty_members(self):
        for normalizer, scalar in (
            (normalize_tasks, "detection"),
            (normalize_image_scopes, "fully_generated"),
            (normalize_research_types, "method"),
        ):
            with self.subTest(normalizer=normalizer.__name__):
                with self.assertRaises(PaperTaxonomyError):
                    normalizer(scalar)
                with self.assertRaises(PaperTaxonomyError):
                    normalizer([scalar, ""])
                with self.assertRaises(PaperTaxonomyError):
                    normalizer(["unsupported"])

    def test_missing_values_normalize_to_empty_arrays(self):
        for normalizer in (normalize_tasks, normalize_image_scopes, normalize_research_types):
            self.assertEqual(normalizer(None), [])
            self.assertEqual(normalizer("", compatibility=True), [])


if __name__ == "__main__":
    unittest.main()
