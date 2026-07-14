import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AdminDashboardFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")

    def test_navigation_has_five_primary_destinations(self):
        nav = self.html.split('<nav class="console-nav"', 1)[1].split("</nav>", 1)[0]
        labels = re.findall(r'(?:<button[^>]*>|<summary>)([^<]+)', nav)
        primary = [label.strip() for label in labels if label.strip() in {
            "Dashboard", "Review", "Papers", "Authors &amp; Institutions",
            "Validation",
        }]
        self.assertEqual(primary, [
            "Dashboard", "Review", "Papers", "Authors &amp; Institutions",
            "Validation",
        ])
        self.assertNotIn('data-console-target="publish"', nav)

    def test_navigation_matches_current_curation_domains(self):
        nav = self.html.split('<nav class="console-nav"', 1)[1].split("</nav>", 1)[0]

        def menu(label):
            return nav.split(f"<summary>{label}</summary>", 1)[1].split(
                "</div></details>", 1
            )[0]

        review = menu("Review")
        papers = menu("Papers")
        people = menu("Authors &amp; Institutions")
        validation = menu("Validation")

        self.assertIn(">Institution cleanup</button>", people)
        self.assertNotIn("Institution cleanup", review)
        self.assertIn('data-console-target="validation"', validation)
        self.assertIn(">Curated validation</button>", validation)
        self.assertIn('href="/"', validation)
        self.assertIn(">Public preview</a>", validation)
        self.assertNotIn("Paper metadata", nav)
        self.assertNotIn("Public preview", papers)

    def test_reorganized_navigation_keeps_existing_routes(self):
        self.assertIn('"institution-audit": elements["institution-audit-panel"]', self.javascript)
        self.assertIn('"institution-audit": "/api/review/institution-cleanup"', self.javascript)
        self.assertIn('validation: elements["workflow-panel"]', self.javascript)
        self.assertIn('href="/" target="_blank" rel="noreferrer">Public preview</a>', self.html)
        self.assertIn("function openMetadataEditor()", self.javascript)
        self.assertNotIn('"metadata-editor": elements["paper-metadata-section"]', self.javascript)

    def test_navigation_dropdowns_are_not_clipped(self):
        css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")
        nav_rule = css.split(".console-nav {", 1)[1].split("}", 1)[0]
        menu_rule = css.split(".nav-menu-items,", 1)[1].split("}", 1)[0]
        self.assertIn("overflow: visible", nav_rule)
        self.assertNotIn("overflow: hidden", nav_rule)
        self.assertNotIn("overflow-x: auto", nav_rule)
        self.assertIn("position: absolute", menu_rule)
        self.assertIn("z-index: 1000", menu_rule)
        self.assertIn("position: relative", css.split(".nav-menu {", 1)[1].split("}", 1)[0])

    def test_global_publish_control_reaches_existing_workflow(self):
        masthead = self.html.split('<header class="masthead">', 1)[1].split("</header>", 1)[0]
        self.assertLess(masthead.index('id="add-paper-toggle"'), masthead.index('id="global-publish-toggle"'))
        self.assertLess(masthead.index('id="global-publish-toggle"'), masthead.index('id="connection-status"'))
        self.assertIn(">Publish changes</button>", masthead)
        self.assertIn(
            'elements["global-publish-toggle"].addEventListener("click", () => navigateConsole("publish"))',
            self.javascript,
        )
        for control in (
            'id="show-git-status"', 'id="run-export-preview"',
            'id="run-curated-validation"', 'id="publish-changes"',
            'id="workflow-state"',
        ):
            self.assertIn(control, self.html)
        self.assertIn('"/api/publish-changes"', self.javascript)

    def test_navigation_and_publish_controls_have_keyboard_focus_styles(self):
        css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")
        self.assertIn(".console-nav :focus-visible", css)
        self.assertIn(".release-button:focus-visible", css)
        self.assertIn('summary aria-label="More publish actions"', self.html)

    def test_dashboard_hides_zero_count_queues(self):
        body = self.javascript.split("function renderDashboard()", 1)[1].split(
            "\nfunction navigateProjectHealthMetric", 1
        )[0]
        self.assertIn("Number(metric.value) > 0", body)
        self.assertIn('elements["action-queue-empty"].hidden = queue.length !== 0', body)
        for internal_name in (
            "missing_affiliation", "already_mapped", "review_count",
            "needs_review_or_low_confidence",
        ):
            dashboard = self.html.split('id="dashboard-panel"', 1)[1].split(
                'id="workflow-panel"', 1
            )[0]
            self.assertNotIn(internal_name, dashboard)

    def test_action_queue_rows_are_clickable_and_keyboard_native(self):
        body = self.javascript.split("function renderDashboard()", 1)[1].split(
            "\nfunction navigateProjectHealthMetric", 1
        )[0]
        self.assertIn('document.createElement("button")', body)
        self.assertIn('row.className = "action-queue-row"', body)
        self.assertIn('row.setAttribute("aria-label"', body)
        self.assertIn('row.addEventListener("click"', body)

    def test_priority_table_is_compact_and_limited(self):
        dashboard = self.html.split('id="dashboard-panel"', 1)[1].split(
            'id="workflow-panel"', 1
        )[0]
        self.assertIn("<th>Paper</th><th>Issue</th><th>Public-map impact</th><th>Action</th>", dashboard)
        self.assertIn(".slice(0, 5)", self.javascript)

    def test_navigation_is_accessible_and_tracks_active_pages(self):
        self.assertIn('aria-current="page">Dashboard', self.html)
        self.assertIn('role="menu"', self.html)
        self.assertIn('role="menuitem"', self.html)
        self.assertIn('trigger.setAttribute("aria-controls", popup.id)', self.javascript)
        self.assertIn('trigger.setAttribute("aria-expanded", "false")', self.javascript)
        for key in ("ArrowDown", "ArrowUp", "Escape"):
            self.assertIn(f'"{key}"', self.javascript)
        self.assertIn('control.setAttribute("aria-current", "page")', self.javascript)

    def test_global_search_uses_loaded_local_records(self):
        self.assertIn('id="global-search-input"', self.html)
        self.assertIn('id="global-search-results" role="listbox"', self.html)
        self.assertIn("function renderGlobalSearch()", self.javascript)
        self.assertIn("state.papers.filter", self.javascript)
        self.assertIn('event.key === "/"', self.javascript)

    def test_dashboard_queues_are_impact_ordered_and_capped(self):
        body = self.javascript.split("function renderDashboard()", 1)[1].split(
            "\nfunction initializeNavigationMenus", 1
        )[0]
        self.assertIn('marker_blockers: { title: "Marker blockers", priority: 1', body)
        self.assertIn(".sort((left, right)", body)
        self.assertIn("queue.slice(0, 5)", body)
        self.assertIn("View all review queues", body)
        self.assertIn("copy.impact", body)

    def test_publish_readiness_and_changed_count_are_staged(self):
        for stage in (
            "Changes detected", "Validation required", "Validation failed",
            "Preview refresh required", "Ready to publish", "Published",
        ):
            self.assertIn(stage, self.javascript)
        self.assertIn('`Publish changes · ${formatNumber(changed.length)}`', self.javascript)
        self.assertIn('id="dashboard-release-state"', self.html)

    def test_header_is_compact_and_uses_requested_copy(self):
        self.assertIn(
            "Review, correct, validate, and publish the data shown on the public map.",
            self.html,
        )
        css = (ROOT / "web" / "admin.css").read_text(encoding="utf-8")
        masthead = css.split(".masthead {", 1)[1].split("}", 1)[0]
        self.assertIn("padding: 0.8rem", masthead)
        heading = css.split("h1 {", 1)[1].split("}", 1)[0]
        self.assertIn("white-space: nowrap", heading)


if __name__ == "__main__":
    unittest.main()
