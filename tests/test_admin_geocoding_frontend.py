import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AdminGeocodingFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")

    def test_button_uses_current_name_and_address_and_blocks_duplicates(self):
        self.assertIn('apiFetch("/api/institution/geocode"', self.source)
        self.assertIn('institution_name: elements["confirmed-institution"].value.trim()', self.source)
        self.assertIn("address: geocodeAddress()", self.source)
        self.assertIn("button.disabled = true", self.source)
        self.assertIn('button.textContent = "Searching…"', self.source)

    def test_dialog_renders_candidate_details_and_explicit_confirmation(self):
        for field in ("candidate.institution_name", "candidate.address", "candidate.latitude", "candidate.longitude", "candidate.confidence", "candidate.provider"):
            self.assertIn(field, self.source)
        self.assertIn('<dialog id="geocode-dialog"', self.html)
        self.assertIn("Use selected coordinates", self.html)
        self.assertIn("state.selectedGeocodeCandidate = candidate", self.source)

    def test_selection_does_not_write_but_confirmation_does(self):
        selection = self.source.index("state.selectedGeocodeCandidate = candidate")
        confirmation = self.source.index("function confirmGeocodeCandidate()")
        self.assertNotIn('elements["confirmed-lat"].value =', self.source[selection:confirmation])
        self.assertIn('elements["confirmed-lat"].value = candidate.latitude', self.source[confirmation:])
        self.assertIn('elements["confirmed-lon"].value = candidate.longitude', self.source[confirmation:])

    def test_cancel_preserves_values_and_existing_coordinates_require_confirmation(self):
        close_body = self.source[self.source.index("function closeGeocodeDialog()") : self.source.index("function confirmGeocodeCandidate()")]
        self.assertNotIn("confirmed-lat", close_body)
        self.assertIn('window.confirm("Replace the existing latitude and longitude', self.source)

    def test_empty_errors_and_manual_inputs_remain_supported(self):
        self.assertIn('elements["geocode-empty"].hidden = candidates.length !== 0', self.source)
        self.assertIn("Coordinate search failed:", self.source)
        self.assertIn('id="confirmed-lat" type="number"', self.html)
        self.assertIn('id="confirmed-lon" type="number"', self.html)
        self.assertIn('apiFetch("/api/location-review/confirm"', self.source)


if __name__ == "__main__":
    unittest.main()
