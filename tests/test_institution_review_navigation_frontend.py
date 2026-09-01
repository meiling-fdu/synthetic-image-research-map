import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstitutionReviewNavigationFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")

    def test_all_seven_filters_use_one_delegated_binding(self):
        summary = self.source[self.source.index("function renderLocationSummary") : self.source.index("function locationReviewMatches")]
        filters = (
            '["", "All"',
            '["pending_review", "Pending Review", summary.pending_review]',
            '["needs_coordinates", "Needs Coordinates"',
            '["ambiguous", "Ambiguous"',
            '"confirmed",',
            '["ignore", "Ignored"',
            '["excluded", "Excluded"',
        )
        for value in filters:
            self.assertIn(value, summary)
        self.assertLess(summary.index(filters[0]), summary.index(filters[1]))
        self.assertLess(summary.index(filters[1]), summary.index(filters[2]))
        self.assertIn('button.dataset.locationStatus = value', summary)
        self.assertIn('elements["location-status-filters"].addEventListener("click", selectLocationStatusFilter)', self.source)
        self.assertNotIn('button.addEventListener("click"', summary)

    def test_filter_search_pagination_and_selection_are_composed(self):
        matching = self.source[self.source.index("function locationReviewMatches") : self.source.index("function renderLocationReviewList")]
        self.assertIn("state.locationStatusFilter", matching)
        self.assertIn('normalize(elements["location-search"].value)', matching)
        self.assertIn("state.locationReviewPage = 1", matching)
        self.assertIn("clearLocationEditor()", matching)
        rendering = self.source[self.source.index("function renderLocationReviewList") : self.source.index("function selectLocationReview(queueId)")]
        self.assertIn("state.locationReviewPageSize", rendering)
        self.assertIn("button.dataset.locationReviewId = row.queue_id", rendering)
        self.assertNotIn('button.addEventListener("click"', rendering)

    def test_pending_filter_is_exact_and_composes_with_search_and_pagination(self):
        matching = self.source[
            self.source.index("function locationReviewMatches"):
            self.source.index("function filteredLocationReviewRecords")
        ]
        self.assertIn("row.review_status === state.locationStatusFilter", matching)
        self.assertIn('normalize(elements["location-search"].value)', matching)
        selection = self.source[
            self.source.index("function selectLocationStatusFilter"):
            self.source.index("function selectLocationReviewResult")
        ]
        self.assertIn("state.locationReviewPage = 1", selection)
        rendering = self.source[
            self.source.index("function renderLocationReviewList"):
            self.source.index("function selectLocationReview(queueId)")
        ]
        self.assertIn("records.slice(start, start + state.locationReviewPageSize)", rendering)
        self.assertIn("· ${records.length}", rendering)

    def test_direct_and_management_entry_paths_are_distinct_and_deterministic(self):
        self.assertIn('openLocationReview({ direct: true })', self.source)
        opening = self.source[self.source.index("function openLocationReview") : self.source.index("function closeLocationReview")]
        self.assertIn('if (direct && state.locationEditorMode !== "review") clearLocationEditor()', opening)
        management = self.source[self.source.index("async function openCanonicalInstitutionLocation") : self.source.index("function isActiveCanonicalLocationRequest")]
        self.assertIn("openLocationReview();", management)
        self.assertIn('elements["location-review-list"].addEventListener("click", selectLocationReviewResult)', self.source)

    def test_normal_identity_and_location_saves_patch_without_full_reload(self):
        identity = self.source[self.source.index("async function submitInstitutionIdentity") : self.source.index("function shortInstitutionId")]
        self.assertIn("patchInstitutionRecord(payload.data)", identity)
        self.assertNotIn("refreshInstitutions", identity)
        self.assertNotIn("loadLocationReviews", identity)
        location = self.source[self.source.index("async function confirmLocation(event)") : self.source.index("async function markLocationReview")]
        normal_review_save = location[
            location.index("} else {", location.index("if (canonicalPersistence)")):
            location.index("\n    }\n  } catch")
        ]
        self.assertIn("patchLocationReviewRecord", normal_review_save)
        self.assertIn("renderInstitutionManagement", location)
        self.assertNotIn("loadLocationReviews", normal_review_save)
        self.assertNotIn("refreshInstitutions", normal_review_save)
        server = (ROOT / "scripts/serve_admin.py").read_text(encoding="utf-8")
        actions = server[server.index("institution_actions = {") : server.index("location_actions = {")]
        self.assertNotIn("export_preview", actions)
        self.assertNotIn("export_public_preview", actions)

    def test_local_transition_recomputes_counts_and_advances_filtered_queue(self):
        patching = self.source[
            self.source.index("function patchLocationReviewRecord"):
            self.source.index("async function loadLocationReviews")
        ]
        self.assertIn("pending_review: counts.pending_review || 0", patching)
        self.assertIn("const remaining = filteredLocationReviewRecords()", patching)
        self.assertIn("selectLocationReview(next.queue_id)", patching)
        self.assertIn("else clearLocationEditor()", patching)
        self.assertNotIn("loadLocationReviews", patching)
        confirm = self.source[
            self.source.index("async function confirmLocation(event)"):
            self.source.index("async function markLocationReview")
        ]
        normal_review_save = confirm[
            confirm.index("} else {", confirm.index("if (canonicalPersistence)")):
            confirm.index("\n    }\n  } catch")
        ]
        self.assertIn("patchLocationReviewRecord", normal_review_save)
        self.assertNotIn("loadLocationReviews", normal_review_save)
        for function_name, end_name in (
            ("async function markLocationReview", "async function confirmLocationAlias"),
            ("async function confirmLocationAlias", "function requestToken"),
        ):
            action = self.source[self.source.index(function_name):self.source.index(end_name)]
            self.assertIn("patchLocationReviewRecord", action)
            self.assertNotIn("loadLocationReviews", action)

    def test_action_bar_is_direct_ordered_and_contextual(self):
        form_start = self.html.index('<div class="location-form-actions">')
        actions = self.html[form_start:self.html.index("</form>", form_start)]
        labels = (
            "Save identity", "Confirm location", "Confirm as alias",
            "Mark ambiguous", "Ignore institution", "Exclude from public map",
        )
        positions = [actions.index(label) for label in labels]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("More actions", actions)
        self.assertNotIn("<details", actions)
        rendering = self.source[
            self.source.index("function renderLocationActions"):
            self.source.index("async function saveLocationInstitutionIdentity")
        ]
        self.assertIn('status === "pending_review"', rendering)
        self.assertIn('status !== "ignore"', rendering)
        self.assertIn('status !== "excluded"', rendering)
        self.assertIn('status === "confirmed" && !locationChanged', rendering)
        self.assertIn('["pending_review", "ambiguous"].includes(status)', rendering)
        self.assertIn("&& hasCanonicalInstitution", rendering)
        self.assertIn('elements["location-form"].addEventListener("input", renderLocationActions)', self.source)

    def test_streamlined_form_has_separate_identity_fields_and_details(self):
        form = self.html[self.html.index('<form id="location-form"') : self.html.index("</form>", self.html.index('<form id="location-form"'))]
        for element_id in ("confirmed-institution", "institution-abbreviation", "institution-aliases", "confirmed-city", "confirmed-region", "confirmed-country", "confirmed-lat", "confirmed-lon"):
            self.assertIn(f'id="{element_id}"', form)
        self.assertIn('<details class="location-details">', form)
        self.assertNotIn("Detected language", form)
        self.assertNotIn(">Country code", form)
        self.assertIn('id="canonical-institution-label" hidden', form)


if __name__ == "__main__":
    unittest.main()
