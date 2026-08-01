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

    def test_creation_uses_public_taxonomy_without_workshop_type(self):
        creation = self.html.split('id="venue-create-type"', 1)[1].split("</select>", 1)[0]
        self.assertNotIn('value="workshop"', creation)
        for venue_type in ("conference", "journal", "preprint", "book"):
            self.assertIn(f'value="{venue_type}"', creation)
        self.assertIn('value="workshops"', self.html)
        self.assertNotIn('venueType === "workshop"', self.source)

    def test_selection_populates_structured_fields_and_type(self):
        body = self.source.split("function selectCanonicalVenue(option", 1)[1].split(
            "\nfunction selectCanonicalVenueById", 1
        )[0]
        for field in ("venue-id", "venue-name", "venue-acronym", "venue-type", "venue-track"):
            self.assertIn(f'metadata-{field}', body)
        self.assertIn("publicationTypeForVenueType(option.venue_type)", body)
        self.assertIn('elements["metadata-publication-type"].disabled = true', body)
        self.assertIn("state.venueSelectionConfirmed = explicitSelection", body)

    def test_explicit_selection_confirmation_survives_form_edits_and_is_submitted(self):
        snapshot = self.source.split("function metadataFormSnapshot()", 1)[1].split(
            "\nfunction metadataFormIsDirty", 1
        )[0]
        save = self.source.split("async function saveMetadata(event)", 1)[1].split(
            "\nasync function refreshAfterMetadataSave", 1
        )[0]
        self.assertIn("values.venue_selection_confirmed = state.venueSelectionConfirmed", snapshot)
        self.assertIn("state.venueSelectionConfirmed", save)
        self.assertIn("venue_selection_confirmed: state.venueSelectionConfirmed", save)
        self.assertNotIn("venueSelectionConfirmed = false", "\n".join(
            line for line in self.source.splitlines()
            if "handleMetadataFormChange" in line
        ))

    def test_hydration_and_cancel_clear_unsaved_selection_confirmation(self):
        populate = self.source.split("function populateMetadataForm()", 1)[1].split(
            "\nfunction closeMetadataEditor", 1
        )[0]
        close = self.source.split("function closeMetadataEditor()", 1)[1].split(
            "\nasync function saveMetadata", 1
        )[0]
        clear = self.source.split("function clearPaperMetadata", 1)[1].split(
            "\nfunction renderMetadataComparison", 1
        )[0]
        self.assertIn("state.venueSelectionConfirmed = false", populate)
        self.assertIn("selectCanonicalVenue(state.selectedVenue, false, false)", populate)
        self.assertIn("populateMetadataForm()", close)
        self.assertIn("state.venueSelectionConfirmed = false", clear)

    def test_override_provenance_creation_and_stale_guards(self):
        self.assertIn("publication_type_override: state.publicationTypeOverride", self.source)
        self.assertIn("Publication type conflicts with the selected canonical venue", self.source)
        self.assertIn("replace_raw_venue", self.source)
        self.assertIn("draft.venue_proposal = state.pendingVenueProposal", self.source)
        self.assertIn("Assigned by the backend when saved", self.source)
        self.assertNotIn('apiFetch("/api/venues/create"', self.source)
        self.assertIn("possible_matches", self.source)
        self.assertIn("selectionSequence !== paperSelectionSequence || state.selectedId !== selectedId", self.source)
        self.assertIn("venueLoadSequence !== paperSelectionSequence || venueLoadPaperId !== state.selectedId", self.source)

    def test_paper_track_is_an_editable_control_independent_of_venue(self):
        track = self.html.split('id="metadata-venue-track"', 1)[1].split("</select>", 1)[0]
        for value, label in (
            ("main", "Main"), ("workshops", "Workshop"),
            ("findings", "Findings"), ("posters", "Poster"),
            ("industry", "Industry"), ("demo", "Demo"),
            ("doctoral_consortium", "Doctoral consortium"), ("other", "Other"),
        ):
            self.assertIn(f'value="{value}">{label}', track)
        selection = self.source.split("function selectCanonicalVenue(option", 1)[1].split(
            "\nfunction selectCanonicalVenueById", 1
        )[0]
        self.assertIn("Selecting a canonical venue must preserve it", selection)
        self.assertNotIn('value = option.venue_track', selection)
        self.assertIn("trackChanged", self.source)


if __name__ == "__main__":
    unittest.main()
