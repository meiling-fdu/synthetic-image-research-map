import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AdminGeocodingFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")

    def test_button_uses_canonical_id_and_location_evidence_and_blocks_duplicates(self):
        self.assertIn('apiFetch("/api/institution/geocode"', self.source)
        self.assertIn("institution_id: institutionId", self.source)
        self.assertIn("loaded_institution_id: loadedInstitutionId", self.source)
        for field in ("city", "region", "country", "country_code"):
            self.assertIn(f"{field}:", self.source)
        self.assertIn("button.disabled = true", self.source)
        self.assertIn('button.textContent = "Searching…"', self.source)

    def test_dialog_renders_candidate_details_and_explicit_confirmation(self):
        for field in ("candidate.institution_name", "candidate.address", "candidate.latitude", "candidate.longitude", "candidate.confidence", "candidate.provider"):
            self.assertIn(field, self.source)
        self.assertIn('<dialog id="geocode-dialog"', self.html)
        self.assertIn("Use this location", self.html)
        self.assertIn("state.selectedGeocodeCandidate = candidate", self.source)
        for label in ("Full address", "City", "Region/state", "Country", "ISO country code", "Latitude", "Longitude"):
            self.assertIn(f'candidateDetail("{label}"', self.source)
        self.assertIn('linkValue("Open in OpenStreetMap", candidate.map_url)', self.source)

    def test_map_url_is_not_treated_as_an_event_or_link_label(self):
        self.assertNotIn('linkValue(candidate.map_url, "Preview on OpenStreetMap")', self.source)
        self.assertNotIn("mapLink.target =", self.source)

    def test_selection_does_not_write_but_confirmation_does(self):
        selection = self.source.index("state.selectedGeocodeCandidate = candidate")
        confirmation = self.source.index("function confirmGeocodeCandidate()")
        self.assertNotIn('elements["confirmed-lat"].value =', self.source[selection:confirmation])
        self.assertIn('elements["confirmed-lat"].value = candidate.latitude', self.source[confirmation:])
        self.assertIn('elements["confirmed-lon"].value = candidate.longitude', self.source[confirmation:])
        for field in ("city", "region", "country", "country_code"):
            self.assertIn(f'candidate.{field}', self.source[confirmation:])
        self.assertIn('elements["coordinate-source"].value = "OpenStreetMap Nominatim"', self.source[confirmation:])

    def test_cancel_preserves_values_and_existing_coordinates_require_confirmation(self):
        close_body = self.source[self.source.index("function closeGeocodeDialog()") : self.source.index("function confirmGeocodeCandidate()")]
        self.assertNotIn("confirmed-lat", close_body)
        self.assertIn('window.confirm("Replace the existing latitude and longitude', self.source)

    def test_empty_errors_and_manual_inputs_remain_supported(self):
        self.assertIn("!result.no_safe_match", self.source)
        self.assertIn("Coordinate search failed:", self.source)
        self.assertIn('id="confirmed-lat" type="number"', self.html)
        self.assertIn('id="confirmed-lon" type="number"', self.html)
        self.assertIn('"/api/location-review/confirm"', self.source)
        self.assertIn('missing.textContent = "Unavailable — manual review required"', self.source)

    def test_canonical_edit_location_loads_exact_id_and_survives_action_close(self):
        action = self.source[self.source.index("function institutionActionButton") : self.source.index("function renderInstitutionManagement")]
        self.assertIn("event.preventDefault()", action)
        self.assertIn("event.stopPropagation()", action)
        opening = self.source[self.source.index("async function openCanonicalInstitutionLocation") : self.source.index("function selectCanonicalInstitutionLocation")]
        self.assertIn("institution?.institution_id", opening)
        self.assertIn("/api/institution?institution_id=", opening)
        self.assertIn("state.selectedInstitutionLocationId !== identifier", opening)
        self.assertIn("selectCanonicalInstitutionLocation(detail)", opening)

    def test_switching_institutions_invalidates_stale_geocoding(self):
        search = self.source[self.source.index("async function findInstitutionCoordinates") : self.source.index("function closeGeocodeDialog")]
        self.assertIn("requestSequence !== geocodeRequestSequence", search)
        self.assertIn("institutionId !== state.selectedInstitutionLocationId", search)
        self.assertIn("payload.data?.institution_id", search)

    def test_conflicting_candidates_are_visible_but_not_selectable(self):
        rendering = self.source[self.source.index("function renderGeocodeCandidates") : self.source.index("async function findInstitutionCoordinates")]
        self.assertIn("candidate.selectable === false", rendering)
        self.assertIn("geocode-candidate-conflict", rendering)
        self.assertIn("No location-consistent candidate", rendering)

    def test_switching_or_starting_a_review_clears_stale_location_values(self):
        selection = self.source[self.source.index("function selectLocationReview") : self.source.index("function renderLocationContext")]
        self.assertIn("clearLocationFields();", selection)
        self.assertIn('elements["location-create-new"].addEventListener', self.source)
        self.assertIn('"confirmed-country-code",', self.source[self.source.index("function clearLocationFields") :])

    def test_confirming_candidate_sets_note_without_overwriting_manual_text(self):
        expected = "Coordinates selected from an OpenStreetMap Nominatim result and confirmed by the reviewer."
        self.assertIn(f'"{expected}"', self.source)
        confirmation = self.source[self.source.index("function confirmGeocodeCandidate()") : self.source.index("async function confirmLocation")]
        self.assertIn('if (!reviewNote.value.trim() || reviewNote.value.trim() === NOMINATIM_REVIEW_NOTE)', confirmation)
        self.assertIn("reviewNote.value = NOMINATIM_REVIEW_NOTE", confirmation)
        self.assertNotIn("else", confirmation)

    def test_auto_note_is_cleared_between_reviews_and_remains_required(self):
        clear_fields = self.source[self.source.index("function clearLocationFields") : self.source.index("function candidateDetail")]
        self.assertIn('"coordinate-review-note",', clear_fields)
        self.assertIn('id="coordinate-review-note" rows="3" required', self.html)

    def test_location_actions_are_simplified_and_contextual(self):
        actions = self.html[self.html.index('<div class="location-form-actions">') : self.html.index("</form>", self.html.index('<div class="location-form-actions">'))]
        for action in ("Confirm location", "Save edited metadata", "Needs coordinate review"):
            self.assertIn(action, actions)
        self.assertIn("More actions", actions)
        for action in ("Mark ambiguous", "Ignore this institution", "Exclude from public map"):
            self.assertIn(action, actions)
        rendering = self.source[self.source.index("function renderLocationActions") : self.source.index("function renderLocationContext")]
        self.assertIn('elements["location-confirm-alias"].hidden = !hasCanonicalInstitution', rendering)
        self.assertIn('elements["location-create-new"].hidden = hasCanonicalInstitution', rendering)
        self.assertIn('elements["canonical-institution"].addEventListener("change", renderLocationActions)', self.source)

    def test_alias_candidates_show_evidence_and_require_confirmation(self):
        for field in (
            "candidate_suggestions", "canonical_record", "location_conflicts",
            "affected_papers", "affected_mappings",
        ):
            self.assertIn(field, self.source)
        confirmation = self.source[
            self.source.index("async function confirmLocationAlias"):
            self.source.index("async function saveLocationMetadata")
        ]
        self.assertIn("window.confirm(", confirmation)
        self.assertIn("does not merge canonical institutions or reassign mappings", confirmation)
        self.assertLess(confirmation.index("window.confirm("), confirmation.index('apiFetch("/api/location-review/confirm-alias"'))
        self.assertIn("Suggestions never merge canonical institutions", self.html)

    def test_more_actions_escapes_panel_clipping_and_has_viewport_positioning(self):
        css = (ROOT / "web/admin.css").read_text(encoding="utf-8")
        workspace = css[css.index(".location-review-workspace {") : css.index("}", css.index(".location-review-workspace {"))]
        self.assertIn("overflow: visible", workspace)
        menu = css[css.index(".location-more-actions .overflow-menu-items") : css.index("}", css.index(".location-more-actions .overflow-menu-items"))]
        self.assertIn("position: fixed", menu)
        self.assertIn("z-index: 2000", menu)
        self.assertIn("max-width: calc(100vw - 1rem)", menu)
        positioning = self.source[self.source.index("function positionLocationMoreActions") : self.source.index("function initializeLocationMoreActions")]
        self.assertIn("spaceBelow < menuHeight && spaceAbove > spaceBelow", positioning)
        self.assertIn('menu.dataset.placement = opensUpward ? "top" : "bottom"', positioning)
        self.assertIn("viewportWidth - menuWidth - viewportMargin", positioning)

    def test_more_actions_preserves_actions_keyboard_and_outside_click(self):
        behavior = self.source[self.source.index("function initializeLocationMoreActions") : self.source.index("function renderLocationContext")]
        self.assertIn('event.key === "Escape"', behavior)
        self.assertIn('event.key === "ArrowDown"', behavior)
        self.assertIn("trigger.focus()", behavior)
        self.assertIn('menu.querySelector("button")?.focus()', behavior)
        self.assertIn("!disclosure.contains(event.target)", behavior)
        self.assertIn('event.target.closest("button")', behavior)
        for element_id in ("location-mark-ambiguous", "location-ignore", "location-exclude"):
            self.assertIn(f'id="{element_id}"', self.html)


if __name__ == "__main__":
    unittest.main()
