import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class AdminVenueComboboxFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")

    def test_accessible_combobox_and_keyboard_behaviors_exist(self):
        self.assertIn('role="combobox"', self.html)
        self.assertIn('role="searchbox"', self.html)
        self.assertIn('role="listbox"', self.html)
        for behavior in (
            "handleVenueButtonKeydown", "handleVenueSearchKeydown",
            "handleVenueOutsidePointerDown", "positionVenueComboboxPanel",
            "scrollIntoView({ block: \"nearest\" })", "closeVenueCombobox(true)",
        ):
            self.assertIn(behavior, self.source)
        self.assertIn("overflow-y: auto", self.css)

    def test_search_uses_every_canonical_and_historical_field(self):
        body = self.source.split("function venueOptionMatches", 1)[1].split(
            "\nfunction visibleVenueOptionElements", 1
        )[0]
        for field in (
            "venue_name", "venue_acronym", "venue_type", "venue_track",
            "option.aliases", "option.raw_variants",
        ):
            self.assertIn(field, body)

    def test_selection_populates_structured_fields_and_type(self):
        body = self.source.split("function selectCanonicalVenue(option", 1)[1].split(
            "\nfunction selectCanonicalVenueById", 1
        )[0]
        for field in ("venue-id", "venue-name", "venue-acronym", "venue-type", "venue-track"):
            self.assertIn(f'metadata-{field}', body)
        self.assertIn("publicationTypeForVenueType(option.venue_type)", body)
        self.assertIn('elements["metadata-publication-type"].disabled = true', body)

    def test_override_provenance_creation_and_stale_guards(self):
        self.assertIn("publication_type_override: state.publicationTypeOverride", self.source)
        self.assertIn("Publication type conflicts with the selected canonical venue", self.source)
        self.assertIn("replace_raw_venue", self.source)
        self.assertIn('apiFetch("/api/venues/create"', self.source)
        self.assertIn("possible_matches", self.source)
        self.assertIn("selectionSequence !== paperSelectionSequence || selectedId !== state.selectedId", self.source)
        self.assertIn("venueLoadSequence !== paperSelectionSequence || venueLoadPaperId !== state.selectedId", self.source)


if __name__ == "__main__":
    unittest.main()
