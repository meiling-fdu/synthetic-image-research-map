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
        self.assertNotIn('elements["coordinate-source"]', self.source[confirmation:])

    def test_cancel_preserves_values_and_existing_coordinates_require_confirmation(self):
        close_body = self.source[self.source.index("function closeGeocodeDialog()") : self.source.index("function confirmGeocodeCandidate()")]
        self.assertNotIn("confirmed-lat", close_body)
        self.assertIn('window.confirm("Replace the existing latitude and longitude', self.source)

    def test_empty_errors_and_manual_inputs_remain_supported(self):
        self.assertIn("!result.no_safe_match", self.source)
        self.assertIn("Coordinate search failed:", self.source)
        self.assertIn('id="confirmed-lat" type="text" inputmode="decimal"', self.html)
        self.assertIn('id="confirmed-lon" type="text" inputmode="decimal"', self.html)
        self.assertIn('"/api/location-review/confirm"', self.source)
        self.assertIn('missing.textContent = "Unavailable — manual review required"', self.source)

    def test_canonical_edit_location_loads_exact_id_and_survives_action_close(self):
        action = self.source[self.source.index("function institutionActionButton") : self.source.index("function renderInstitutionManagement")]
        self.assertIn("event.preventDefault()", action)
        self.assertIn("event.stopPropagation()", action)
        opening = self.source[self.source.index("async function openCanonicalInstitutionLocation") : self.source.index("function selectCanonicalInstitutionLocation")]
        self.assertIn("institution?.institution_id", opening)
        self.assertIn("/api/institution?institution_id=", opening)
        self.assertIn("isActiveCanonicalLocationRequest(requestSequence, identifier)", opening)
        self.assertIn("selectCanonicalInstitutionLocation(detail)", opening)
        self.assertIn("detail.editable_institution_id", opening)
        self.assertNotIn("detail.institution?.institution_id) !== identifier", opening)

    def test_direct_mode_is_independent_from_queue_rows_and_filters(self):
        applying = self.source[
            self.source.index("function applyLocationPayload"):
            self.source.index("async function loadLocationReviews")
        ]
        self.assertIn('state.locationEditorMode === "review"', applying)
        opening = self.source[
            self.source.index("async function openCanonicalInstitutionLocation"):
            self.source.index("function selectCanonicalInstitutionLocation")
        ]
        self.assertLess(
            opening.index('state.selectedLocationReviewId = ""'),
            opening.index("apiFetch(`/api/institution?institution_id=")
        )
        rendering = self.source[
            self.source.index("function renderLocationReviewList"):
            self.source.index("function selectLocationReview")
        ]
        self.assertNotIn("clearLocationEditor", rendering)

    def test_direct_loading_resolves_on_success_and_visible_error(self):
        opening = self.source[
            self.source.index("async function openCanonicalInstitutionLocation"):
            self.source.index("function selectCanonicalInstitutionLocation")
        ]
        self.assertIn("try {", opening)
        self.assertIn("catch (error)", opening)
        self.assertIn('"Could not load institution location"', opening)
        self.assertIn("error.message", opening)
        self.assertIn("isActiveCanonicalLocationRequest(requestSequence, identifier)", opening)
        canonical = self.source[
            self.source.index("function selectCanonicalInstitutionLocation"):
            self.source.index("function renderCanonicalLocationContext")
        ]
        self.assertIn('elements["location-editor-placeholder"].hidden = true', canonical)
        self.assertIn("(detail.location_reviews || [])[0] || {}", canonical)
        self.assertIn("detail.current_location || detail.location || {}", canonical)

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
        self.assertIn('"confirmed-country-code",', self.source[self.source.index("function clearLocationFields") :])

    def test_confirming_candidate_sets_only_location_fields(self):
        confirmation = self.source[self.source.index("function confirmGeocodeCandidate()") : self.source.index("async function confirmLocation")]
        self.assertNotIn("reviewNote", confirmation)
        self.assertNotIn("coordinate-source", confirmation)

    def test_removed_coordinate_provenance_fields_stay_absent(self):
        clear_fields = self.source[self.source.index("function clearLocationFields") : self.source.index("function candidateDetail")]
        self.assertNotIn('"coordinate-review-note",', clear_fields)
        self.assertNotIn('id="coordinate-review-note"', self.html)
        self.assertNotIn('id="coordinate-source"', self.html)

    def test_location_actions_are_simplified_and_contextual(self):
        actions = self.html[self.html.index('<div class="location-form-actions">') : self.html.index("</form>", self.html.index('<div class="location-form-actions">'))]
        for action in ("Confirm location",):
            self.assertIn(action, actions)
        for removed in ("Save edited metadata", "Needs coordinate review"):
            self.assertNotIn(removed, actions)
        self.assertNotIn("More actions", actions)
        for action in ("Mark ambiguous", "Ignore institution", "Exclude from public map"):
            self.assertIn(action, actions)
        rendering = self.source[self.source.index("function renderLocationActions") : self.source.index("function renderLocationContext")]
        self.assertIn('["pending_review", "ambiguous"].includes(status)', rendering)
        self.assertIn('elements["canonical-institution"].addEventListener("change", renderLocationActions)', self.source)

    def test_alias_candidates_show_evidence_and_require_confirmation(self):
        for field in (
            "candidate_suggestions", "canonical_record", "location_conflicts",
            "affected_papers", "affected_mappings",
        ):
            self.assertIn(field, self.source)
        confirmation = self.source[
            self.source.index("async function confirmLocationAlias"):
            self.source.index("function requestToken")
        ]
        self.assertIn("window.confirm(", confirmation)
        self.assertIn("does not merge canonical institutions or reassign mappings", confirmation)
        self.assertLess(confirmation.index("window.confirm("), confirmation.index('apiFetch("/api/location-review/confirm-alias"'))
        self.assertIn("Suggestions never merge canonical institutions", self.html)

    def test_actions_share_one_wrapping_aligned_row(self):
        css = (ROOT / "web/admin.css").read_text(encoding="utf-8")
        row = css[css.index(".location-form-actions {") : css.index("}", css.index(".location-form-actions {"))]
        self.assertIn("display: flex", row)
        self.assertIn("align-items: center", row)
        self.assertIn("flex-wrap: wrap", row)
        self.assertNotIn("location-more-actions", css)
        self.assertNotIn("initializeLocationMoreActions", self.source)

    def test_exceptional_actions_are_direct_buttons(self):
        for element_id in ("location-mark-ambiguous", "location-ignore", "location-exclude"):
            self.assertIn(f'id="{element_id}"', self.html)
        self.assertNotIn('id="location-more-actions"', self.html)


if __name__ == "__main__":
    unittest.main()
