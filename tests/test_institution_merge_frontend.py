import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstitutionMergeFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web/admin.html").read_text(encoding="utf-8")
        cls.source = (ROOT / "web/admin.js").read_text(encoding="utf-8")
        start = cls.source.index("function shortInstitutionId")
        end = cls.source.index("async function runInstitutionAction", start)
        cls.merge_source = cls.source[start:end]

    def test_target_selector_searches_canonical_names_aliases_and_ids(self):
        self.assertIn('id="institution-merge-search" type="search"', self.html)
        self.assertIn('id="institution-merge-results"', self.html)
        self.assertIn("institution.canonical_name", self.merge_source)
        self.assertIn("...(institution.aliases || [])", self.merge_source)
        self.assertIn("institution.institution_id", self.merge_source)
        self.assertIn("shortInstitutionId(institution.institution_id)", self.merge_source)
        self.assertIn("state.institutions.filter", self.merge_source)

    def test_short_full_and_whitespace_id_normalization(self):
        normalization = self.merge_source[
            self.merge_source.index("function normalizeInstitutionMergeId"):
            self.merge_source.index("function institutionMergeSearchText")
        ]
        self.assertIn("text(value).trim()", normalization)
        self.assertIn("/^institution:([0-9a-f]{16})$/i", normalization)
        self.assertIn("/^[0-9a-f]{16}$/i", normalization)
        self.assertIn("`institution:${", normalization)

    def test_malformed_unknown_and_identical_ids_show_visible_errors(self):
        self.assertIn("Enter a valid 16-character short institution ID.", self.merge_source)
        self.assertIn("Unknown canonical institution ID:", self.merge_source)
        self.assertIn("Source and target institutions must differ.", self.merge_source)
        self.assertIn('id="institution-merge-error" role="alert" hidden', self.html)
        self.assertIn("showInstitutionMergeError(error.message)", self.merge_source)

    def test_source_is_excluded_and_only_active_targets_are_listed(self):
        self.assertIn("institution.institution_id !== sourceId", self.merge_source)
        self.assertIn('institution.institution_status === "active"', self.merge_source)

    def test_merge_confirmation_alone_controls_destructive_button(self):
        self.assertIn('id="institution-merge-submit" type="submit" disabled', self.html)
        self.assertIn('value !== "MERGE"', self.merge_source)
        self.assertIn('value !== "MERGE"', self.merge_source)
        self.assertIn('Type <code>MERGE</code> to confirm', self.html)
        self.assertNotIn("Type exactly to confirm", self.merge_source)
        self.assertNotIn("window.prompt", self.merge_source)

    def test_confirmation_displays_names_and_short_ids(self):
        for element_id in (
            "institution-merge-source-name",
            "institution-merge-source-id",
            "institution-merge-target-name",
            "institution-merge-target-id",
        ):
            self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn("source.canonical_name", self.merge_source)
        self.assertIn("target.canonical_name", self.merge_source)
        self.assertIn("shortInstitutionId(source.institution_id)", self.merge_source)
        self.assertIn("shortInstitutionId(target.institution_id)", self.merge_source)

    def test_warning_and_buttons_are_concise(self):
        self.assertIn(
            "This action replaces the source institution with the target institution "
            "across mappings, aliases, locations, review records, and other institution references.",
            self.html,
        )
        self.assertIn(">Cancel</button>", self.html)
        self.assertIn(">Merge institution</button>", self.html)
        self.assertIn('class="danger-button" id="institution-merge-submit"', self.html)

    def test_backend_errors_remain_in_dialog_and_double_submit_is_blocked(self):
        self.assertIn("if (state.institutionMerge.submitting) return", self.merge_source)
        self.assertIn("state.institutionMerge.submitting = true", self.merge_source)
        self.assertIn('showInstitutionMergeError(`Merge failed: ${error.message}`)', self.merge_source)
        request = self.merge_source.index('await apiFetch("/api/institution/merge"')
        close = self.merge_source.index('elements["institution-merge-dialog"].close()', request)
        self.assertLess(request, close)

    def test_success_refreshes_only_after_api_success(self):
        request = self.merge_source.index('await apiFetch("/api/institution/merge"')
        refresh = self.merge_source.index("await Promise.all([refreshInstitutions(), loadLocationReviews()])", request)
        self.assertLess(request, refresh)
        catch = self.merge_source.index("} catch (error) {", request)
        self.assertLess(refresh, catch)

    def test_ui_keeps_long_backend_phrase_internal(self):
        self.assertIn(
            "`REPLACE ${source.canonical_name} WITH ${target.canonical_name} GLOBALLY`",
            self.merge_source,
        )
        self.assertIn("confirmation: backendConfirmation", self.merge_source)
        self.assertNotIn("Global replacement confirmation did not match", self.source)


if __name__ == "__main__":
    unittest.main()
