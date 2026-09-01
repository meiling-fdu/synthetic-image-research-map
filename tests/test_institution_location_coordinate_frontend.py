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

    def test_confirmation_uses_the_validated_draft(self):
        self.assertIn("const draft = validatedLocationDraft()", self.confirm_source)
        self.assertIn("if (!draft) return", self.confirm_source)

    def test_api_submission_uses_the_normalized_draft(self):
        validation = self.confirm_source.index("const draft = validatedLocationDraft()")
        request = self.confirm_source.index("await apiFetch(")
        self.assertLess(validation, request)
        self.assertIn("lat: draft.confirmed_lat", self.confirm_source)
        self.assertIn("lon: draft.confirmed_lon", self.confirm_source)

    def test_canonical_confirmation_uses_path_id_and_location_only_body(self):
        self.assertIn(
            "/api/admin/institutions/${encodeURIComponent(boundInstitutionId)}/confirm-location",
            self.confirm_source,
        )
        canonical_body = self.confirm_source[
            self.confirm_source.index("body: JSON.stringify(canonicalPersistence ? {"):
            self.confirm_source.index("} : draft)", self.confirm_source.index("body: JSON.stringify(canonicalPersistence ? {"))
        ]
        self.assertNotIn("institution_id:", canonical_body)
        self.assertNotIn("loaded_institution_id:", canonical_body)
        self.assertIn("selectCanonicalInstitutionLocation({", self.confirm_source)
        self.assertIn("renderInstitutionManagement();", self.confirm_source)
        self.assertIn("loadLocationReviews", self.confirm_source)
        self.assertIn("refreshInstitutions", self.confirm_source)

    def test_duplicate_submissions_and_backend_errors_are_visible(self):
        self.assertIn("if (state.locationSaveRunning) return", self.confirm_source)
        self.assertIn("showLocationFormError(", self.confirm_source)
        self.assertIn("setLocationSaveRunning(false)", self.confirm_source)
        self.assertIn('elements["location-confirm"].disabled = running', self.coordinate_source)

    def test_removed_provenance_fields_and_redundant_action_are_absent(self):
        for obsolete in (
            "coordinate-source", "coordinate-source-url", "coordinate-review-note",
            "location-save-metadata", "location-needs-coordinates",
        ):
            self.assertNotIn(obsolete, self.html)
            self.assertNotIn(obsolete, self.source)


if __name__ == "__main__":
    unittest.main()
