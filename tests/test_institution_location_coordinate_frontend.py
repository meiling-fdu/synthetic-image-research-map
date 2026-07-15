import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstitutionLocationCoordinateFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        parser_start = cls.source.index("const COORDINATE_INPUT_PATTERN")
        parser_end = cls.source.index("function geocodeAddress", parser_start)
        cls.coordinate_source = cls.source[parser_start:parser_end]
        confirm_start = cls.source.index("async function confirmLocation")
        confirm_end = cls.source.index("async function markLocationReview", confirm_start)
        cls.confirm_source = cls.source[confirm_start:confirm_end]
        metadata_start = cls.source.index("async function saveLocationMetadata")
        metadata_end = cls.source.index("function requestToken", metadata_start)
        cls.metadata_source = cls.source[metadata_start:metadata_end]

    def test_dot_decimal_coordinates_are_preserved(self):
        self.assertIn('let normalized = input.replace(",", ".")', self.coordinate_source)
        self.assertIn("return normalized", self.coordinate_source)
        self.assertNotIn("toFixed", self.coordinate_source)
        self.assertNotIn("toPrecision", self.coordinate_source)

    def test_comma_decimal_coordinates_are_normalized_for_zhejiang_lab(self):
        values = {"30,2639066": "30.2639066", "119,8911292": "119.8911292"}
        for localized, canonical in values.items():
            self.assertEqual(localized.replace(",", "."), canonical)
        self.assertIn('field.value = normalizeCoordinateInput(field.value', self.coordinate_source)
        self.assertIn("return locationDraft()", self.coordinate_source)

    def test_negative_comma_decimal_coordinates_are_supported(self):
        pattern = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)$")
        self.assertRegex("-30,2639066", pattern)
        self.assertEqual("-30,2639066".replace(",", "."), "-30.2639066")
        self.assertIn("[+-]?", self.coordinate_source)

    def test_mixed_and_thousands_separators_are_rejected(self):
        pattern = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)$")
        for invalid in ("30,263.9066", "30.263,9066", "1,234,567", "1 234.5"):
            self.assertNotRegex(invalid, pattern)
        self.assertIn("without thousands separators", self.coordinate_source)

    def test_latitude_and_longitude_ranges_are_distinct(self):
        self.assertIn('["confirmed-lat", "Latitude", -90, 90]', self.coordinate_source)
        self.assertIn('["confirmed-lon", "Longitude", -180, 180]', self.coordinate_source)
        self.assertIn("numericValue < minimum || numericValue > maximum", self.coordinate_source)
        self.assertIn("must be between ${minimum} and ${maximum}", self.coordinate_source)

    def test_invalid_coordinates_show_an_inline_error_and_focus_the_field(self):
        self.assertIn('elements["location-form-error"].hidden = false', self.coordinate_source)
        self.assertIn('field.setAttribute("aria-invalid", "true")', self.coordinate_source)
        self.assertIn("field.focus()", self.coordinate_source)
        self.assertIn("showLocationFormError(error.message, field)", self.coordinate_source)
        self.assertIn('id="location-form-error" role="alert"', self.html)

    def test_both_save_buttons_use_the_shared_validated_draft(self):
        self.assertIn("const draft = validatedLocationDraft()", self.confirm_source)
        self.assertIn("if (!draft) return", self.confirm_source)
        self.assertIn("const draft = validatedLocationDraft()", self.metadata_source)
        self.assertIn("if (!draft) return", self.metadata_source)
        self.assertIn('elements["location-form"].requestSubmit()', self.metadata_source)

    def test_api_submission_uses_the_normalized_draft(self):
        validation = self.confirm_source.index("const draft = validatedLocationDraft()")
        request = self.confirm_source.index("await apiFetch(")
        self.assertLess(validation, request)
        self.assertIn("lat: draft.confirmed_lat", self.confirm_source)
        self.assertIn("lon: draft.confirmed_lon", self.confirm_source)
        metadata_validation = self.metadata_source.index("const draft = validatedLocationDraft()")
        metadata_request = self.metadata_source.index('apiFetch("/api/location-review/save-metadata"')
        self.assertLess(metadata_validation, metadata_request)
        self.assertIn("body: JSON.stringify(draft)", self.metadata_source)

    def test_duplicate_submissions_and_backend_errors_are_visible(self):
        for action_source in (self.confirm_source, self.metadata_source):
            self.assertIn("if (state.locationSaveRunning) return", action_source)
            self.assertIn("showLocationFormError(error.message)", action_source)
            self.assertIn("setLocationSaveRunning(false)", action_source)
        self.assertIn('elements["location-confirm"].disabled = running', self.coordinate_source)
        self.assertIn('elements["location-save-metadata"].disabled = running', self.coordinate_source)


if __name__ == "__main__":
    unittest.main()
