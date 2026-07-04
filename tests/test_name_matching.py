import unittest

from scripts.name_matching import (
    canonical_name_key,
    name_variants,
    names_match,
    unique_matching_name,
)


class NameMatchingTests(unittest.TestCase):
    def test_normalizes_case_spacing_punctuation_and_comma_format(self):
        self.assertEqual(canonical_name_key("  MÉILING   Li "), "meiling li")
        self.assertTrue(names_match("Li, Meiling", "Meiling Li"))

    def test_matches_two_token_chinese_and_western_orders(self):
        self.assertTrue(names_match("Li Meiling", "Meiling Li"))
        self.assertTrue(names_match("Qian Zhenxing", "Zhenxing Qian"))
        self.assertTrue(names_match("Zhang Xinpeng", "Xinpeng Zhang"))
        self.assertTrue(names_match("Meiling Li", "Meiling Li"))

    def test_supports_safe_middle_initial_matching(self):
        self.assertTrue(names_match("Jordan J Bird", "Jordan James Bird"))
        self.assertTrue(names_match("Bird J Jordan", "Jordan James Bird"))

    def test_does_not_match_on_one_shared_token(self):
        self.assertFalse(names_match("Li Wei", "Wei Zhang"))
        self.assertFalse(names_match("Meiling Li", "Meiling Zhang"))
        self.assertFalse(names_match("Li", "Meiling Li"))

    def test_variants_are_whole_name_variants(self):
        variants = name_variants("Li Meiling")
        self.assertIn("li meiling", variants)
        self.assertIn("meiling li", variants)
        self.assertNotIn("li", variants)

    def test_unique_match_prefers_exact_order_over_reversed_ambiguity(self):
        self.assertEqual(
            unique_matching_name(
                "Meiling Li",
                ["meiling li", "li meiling"],
            ),
            "meiling li",
        )


if __name__ == "__main__":
    unittest.main()
