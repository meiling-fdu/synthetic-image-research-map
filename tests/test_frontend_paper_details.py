import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendPaperDetailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web/app.js").read_text()
        cls.css = (REPOSITORY / "web/style.css").read_text()
        cls.html = (REPOSITORY / "web/index.html").read_text()

    def test_author_names_order_and_disclosure_markup(self):
        helper = REPOSITORY / "web/paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const authors = [
  {name: "First Author"},
  {display_name: "Second Author"},
  "Third Author",
  {author: "Fourth Author"},
];
const html = helpers.renderPaperAuthors({authors}, escapeHtml, null, 2);
process.stdout.write(JSON.stringify({html}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)["html"]
        self.assertNotIn("[object Object]", rendered)
        self.assertLess(rendered.index("First Author"), rendered.index("Second Author"))
        self.assertLess(rendered.index("Second Author"), rendered.index("Third Author"))
        self.assertIn('class="paper-authors-overflow" hidden', rendered)
        self.assertIn('aria-expanded="false"', rendered)
        self.assertIn("Show all authors", rendered)

    def test_title_affiliations_badges_and_links_are_wrap_safe(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultContent", 1)[0]
        self.assertLess(
            details.index("paper-details-title"),
            details.index('class="popup-badges"'),
        )
        self.assertIn("${publicationMetadataBlock}", details)
        self.assertIn("paper-details-publication-type", self.app)
        self.assertIn("task-${escapeHtml(MarkerSizeHelpers.normalizeTaskLabel", details)
        self.assertIn("paper-details-affiliations", details)
        self.assertIn("affiliation.authors.map(escapeHtml).join", details)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("white-space: normal", self.css)
        self.assertNotIn("text-overflow: ellipsis", self.css.split(
            ".paper-details-affiliations", 1
        )[1].split(".result-author-affiliations", 1)[0])

    def test_reviewed_roles_are_visible_without_affiliation_numbers(self):
        script = r"""
const helpers = require(process.argv[1]);
const authors = [
  {name: "Reid Southen", affiliation_indices: [], affiliation_status: "non_institutional",
   affiliation_review: {status: "non_institutional", reason_kind: "role_only", source_text: "Concept Artist"}},
  {name: "Hainan Ren", affiliation_indices: [], affiliation_status: "non_institutional",
   affiliation_review: {status: "non_institutional", reason_kind: "contact_only", source_text: "Hainan Ren. email only"}},
  {name: "Jason Li", affiliation_indices: [], affiliation_status: "unresolved"}
];
process.stdout.write(helpers.renderPaperAuthors({authors}, String));
"""
        result = subprocess.run([str(NODE), "-e", script, str(REPOSITORY / "web/paper_details_helpers.js")],
                                check=True, capture_output=True, text=True)
        self.assertIn("Concept Artist", result.stdout)
        self.assertIn("No institution listed (contact only)", result.stdout)
        self.assertIn("Jason Li", result.stdout)
        self.assertNotIn("<sup", result.stdout)
        self.assertNotIn("is-active-institution-author", result.stdout)

    def test_publication_metadata_and_content_follow_reading_order(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        title = details.index("paper-details-title")
        badges = details.index('class="popup-badges"')
        venue = details.index("${publicationMetadataBlock}")
        authors = details.index('class="paper-details-group paper-details-authors"')
        affiliations = details.index("${affiliationsBlock}")
        links = details.index("${linksBlock}")
        self.assertLess(title, badges)
        self.assertLess(badges, venue)
        self.assertLess(venue, authors)
        self.assertLess(authors, affiliations)
        self.assertLess(affiliations, links)
        self.assertNotIn("venueDisplayHtml(record)", details)
        self.assertNotIn("venue-type-badge", details)
        self.assertIn("Publication type:", self.app)

    def test_only_primary_badges_remain_in_paper_details(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        self.assertIn("popup-task", details)
        self.assertNotIn("${publicationTypeBadge}", details)
        self.assertIn("${entryTypeBadge}", details)
        self.assertNotIn("arXiv version", details)
        self.assertNotIn("confidenceBadge", details)
        self.assertNotIn("affiliationBadge", details)
        self.assertNotIn("Preprint-only", details)

    def test_public_details_exclude_duplicate_and_curation_fields(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        for label in (
            "Location</dt>",
            "Current institution</dt>",
            "Resolution</dt>",
            "Resolution notes</dt>",
            "Needs review</dt>",
        ):
            self.assertNotIn(label, details)
        self.assertNotIn("<dt>Subtask</dt>", details)
        self.assertNotIn("moreDetails", details)

    def test_section_typography_and_removed_more_details(self):
        details = self.app.split(
            "function paperDetailsHtml(record, relatedEntries) {", 1
        )[1].split("\nfunction resultBadges", 1)[0]
        self.assertEqual(details.count('class="paper-details-section-heading"'), 3)
        title_css = self.css.split(".paper-details-title {", 1)[1].split("}", 1)[0]
        self.assertIn("text-align: left", title_css)
        self.assertNotIn("text-align: justify", title_css)
        self.assertNotIn("white-space: nowrap", title_css)
        self.assertNotIn("text-overflow", title_css)
        self.assertNotIn('class="paper-details-more-toggle"', details)
        self.assertNotIn('aria-controls="paper-details-more-content"', details)
        self.assertNotIn("if (moreDetailsToggle)", self.app)

    def test_publication_row_uses_public_label_before_venue_and_deduplicates(self):
        helper_source = (
            REPOSITORY / "web" / "paper_details_helpers.js"
        ).read_text(encoding="utf-8")
        for label in (
            "Conference", "Journal", "Workshop", "Preprint", "Book",
            "Book Chapter", "Thesis", "Report", "Position Paper",
            "Dataset Paper",
        ):
            self.assertIn(f'"{label}"', helper_source)
        self.assertIn("duplicatePrefix", helper_source)
        renderer = self.app.split("function paperDetailsPublicationHtml(record) {", 1)[1].split(
            "\nfunction paperDetailsHtml", 1
        )[0]
        self.assertLess(renderer.index("metadata.typeLabel"), renderer.index("metadata.venue"))
        self.assertLess(renderer.index("metadata.venue"), renderer.index("metadata.year"))

    def test_publication_metadata_all_missing_value_combinations(self):
        helper = REPOSITORY / "web" / "paper_details_helpers.js"
        app_path = REPOSITORY / "web" / "app.js"
        script = r"""
const fs = require("fs");
global.PaperDetailsHelpers = require(process.argv[1]);
global.venueDisplayLabel = (record) => record.venue || "";
global.escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const app = fs.readFileSync(process.argv[2], "utf8");
const start = app.indexOf("function paperDetailsPublication(record) {");
const end = app.indexOf("\nfunction paperDetailsHtml", start);
eval(app.slice(start, end));
const cases = [
  {key: "journal", record: {publication_type: "journal", venue: "Journal of Image and Graphics", year: 2026}},
  {key: "conference", record: {publication_type: "conference_paper", venue: "IEEE/CVF Conference on Computer Vision and Pattern Recognition", year: 2025}},
  {key: "bookChapter", record: {publication_type: "book_chapter", venue: "Artificial Intelligence and Society", year: 2024}},
  {key: "typeVenue", record: {publication_type: "journal", venue: "Venue"}},
  {key: "typeYear", record: {publication_type: "journal", year: 2026}},
  {key: "venueYear", record: {venue: "Venue", year: 2026}},
  {key: "typeOnly", record: {publication_type: "journal"}},
  {key: "venueOnly", record: {venue: "Venue"}},
  {key: "yearOnly", record: {year: 2026}},
  {key: "none", record: {}},
];
process.stdout.write(JSON.stringify(Object.fromEntries(
  cases.map(({key, record}) => [key, paperDetailsPublicationHtml(record)]),
)));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper), str(app_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        def visible_text(markup):
            without_hidden = re.sub(
                r'<span class="visually-hidden">.*?</span>', "", markup
            )
            return " ".join(re.sub(r"<[^>]+>", "", without_hidden).split())

        expected = {
            "journal": "Journal | Journal of Image and Graphics · 2026",
            "conference": "Conference | IEEE/CVF Conference on Computer Vision and Pattern Recognition · 2025",
            "bookChapter": "Book Chapter | Artificial Intelligence and Society · 2024",
            "typeVenue": "Journal | Venue",
            "typeYear": "Journal · 2026",
            "venueYear": "Venue · 2026",
            "typeOnly": "Journal",
            "venueOnly": "Venue",
            "yearOnly": "2026",
            "none": "",
        }
        self.assertEqual(
            {key: visible_text(value) for key, value in rendered.items()},
            expected,
        )
        for markup in rendered.values():
            self.assertNotIn("| |", visible_text(markup))
            self.assertNotIn("· ·", visible_text(markup))

    def test_narrow_panel_content_can_wrap_without_horizontal_overflow(self):
        content_css = self.css.split(".paper-details-content {", 1)[1].split("}", 1)[0]
        affiliations_css = self.css.split(
            ".paper-details-affiliations li {", 1
        )[1].split("}", 1)[0]
        self.assertIn("min-width: 0", content_css)
        self.assertIn("overflow-wrap: anywhere", content_css)
        self.assertIn("min-width: 0", affiliations_css)
        self.assertIn("overflow-wrap: anywhere", affiliations_css)
        self.assertIn("flex-wrap: wrap", self.css.split(
            ".paper-details-links {", 1
        )[1].split("}", 1)[0])

    def test_external_links_require_valid_urls_and_have_safe_labels(self):
        links = self.app.split(
            "function paperExternalLinks(record) {", 1
        )[1].split("\nfunction escapeCsvValue", 1)[0]
        external = self.app.split(
            "function externalLink(url, label) {", 1
        )[1].split("\nfunction normalizedDoi", 1)[0]
        self.assertIn("deduplicatePaperLinks", links)
        for label in ("Project", "Code", "Dataset"):
            self.assertIn(f'label: "{label}"', links)
        self.assertIn("safeHttpUrl(url)", external)
        self.assertIn("opens in a new tab", external)
        self.assertIn('rel="noopener noreferrer"', external)

    def test_accessible_region_close_and_author_toggle_behavior(self):
        self.assertIn('role="region"', self.html)
        self.assertIn('aria-label="Close paper details"', self.html)
        self.assertIn('"aria-label",\n    "Close paper details"', self.app)
        self.assertIn('closest(".paper-authors-toggle")', self.app)
        helper = (REPOSITORY / "web/paper_details_helpers.js").read_text()
        self.assertIn('PaperDetailsHelpers.togglePaperAuthors(authorToggle)', self.app)
        self.assertIn('setAttribute("aria-expanded", String(!isExpanded))', helper)
        self.assertIn('"Show fewer authors"', helper)

    def test_closing_details_restores_focus_to_the_selection_origin(self):
        close_handler = self.app.split(
            'closePaperDetailsButton.addEventListener("click", () => {', 1
        )[1].split("\n});", 1)[0]
        self.assertIn("interactionState.pinnedMapMarkerId", close_handler)
        self.assertIn("visibleMarkerEntryByInstitutionKey", close_handler)
        self.assertIn("(selectionOrigin || mapElement).focus({ preventScroll: true })", close_handler)

    def test_existing_pin_hover_and_filtered_selection_guards_remain(self):
        self.assertIn('detailMode: "empty"', self.app)
        self.assertIn("if (interactionState.detailMode !== \"empty\") return", self.app)
        clear_hover = self.app.split(
            "function clearHoverPreview(marker, event = null) {", 1
        )[1].split("\nfunction resultInstitutionSelection", 1)[0]
        self.assertNotIn("selectedPaperId = null", clear_hover)
        render = self.app.split("function renderRecords() {", 1)[1].split(
            "\nfunction configureYearRange()", 1
        )[0]
        self.assertIn("reconcilePersistentSelectionAfterFilter(", render)
        self.assertIn("filteredSets.matchingPaperIdentities", render)
        self.assertIn("clearPersistentSelection()", self.app)


class AuthorMarkupParser(HTMLParser):
    """Parse production disclosure markup for the small DOM contract below."""

    def __init__(self, markup):
        super().__init__()
        self.root = {"tag": "div", "attrs": {}, "children": []}
        self.stack = [self.root]
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": []}
        self.stack[-1]["children"].append(node)
        self.stack.append(node)

    def handle_endtag(self, tag):
        self.stack.pop()

    def handle_data(self, text):
        self.stack[-1]["children"].append(text)


class AuthorExpansionTests(unittest.TestCase):
    """Execute the real renderer/controller and delegated app click handler.

    The DOM double implements only their DOM contract; native keyboard activation
    requires real-browser QA, not a synthetic click simulation here.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = (REPOSITORY / "web/app.js").read_text()
        cls.helper = str(REPOSITORY / "web/paper_details_helpers.js")
        cls.papers = json.loads((REPOSITORY / "web/data/public_preview_papers.json").read_text())["records"]
        cls.delegation = '[resultsList, paperDetails].forEach' + cls.app.split(
            '[resultsList, paperDetails].forEach', 1
        )[1].split('resultsList.addEventListener("keydown"', 1)[0]

    def node(self, script, *args):
        result = subprocess.run([str(NODE), "-e", script, self.helper, *args],
                                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def markup(self, authors=None, context="pane", limit=None, region_id="test-overflow"):
        if authors is None:
            authors = [{"name": f"Author {i}", "affiliation_indices": [1]} for i in range(1, 11)]
        if limit is None:
            limit = 8 if context == "pane" else 4
        result_renderer = "function resultAuthors" + self.app.split(
            "function resultAuthors", 1
        )[1].split("\nfunction institutionResultContent", 1)[0]
        script = r"""
const PaperDetailsHelpers = require(process.argv[1]);
const escapeHtml = value => String(value).replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const [authors, context, limit, regionId] = JSON.parse(process.argv[2]);
""" + result_renderer + r"""
const html = context === 'card' ? resultAuthors(authors, 'Authors', regionId, limit)
  : '<section class="paper-details-authors"><p>' +
    PaperDetailsHelpers.renderPaperAuthors({authors}, escapeHtml, 1, limit, regionId) + '</p></section>';
process.stdout.write(JSON.stringify(html));
"""
        return self.node(script, json.dumps([authors, context, limit, region_id]))

    def exercise(self, markup, assertions, second=None):
        trees = [AuthorMarkupParser(m).root for m in [markup, second or markup]]
        self.node(r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const helpers = require(process.argv[1]);
// No HTML reimplementation: these trees come from parsing the real renderer.
class Element {
  constructor(data, parent = null) {
    this.tag = data.tag; this.attrs = {...data.attrs}; this.parentElement = parent;
    this.listeners = {};
    this.children = data.children.map(c => typeof c === 'string' ? c : new Element(c, this));
  }
  matches(s) {
    if (s.startsWith('.')) return (this.attrs.class || '').split(' ').includes(s.slice(1));
    if (s.startsWith('[')) return Object.hasOwn(this.attrs, s.slice(1, -1));
    return this.tag === s;
  }
  closest(s) { return this.matches(s) ? this : this.parentElement?.closest(s); }
  querySelectorAll(s) {
    return this.children.flatMap(c => typeof c === 'string' ? [] :
      [...(c.matches(s) ? [c] : []), ...c.querySelectorAll(s)]);
  }
  querySelector(s) { return this.querySelectorAll(s)[0] || null; }
  getAttribute(k) { return this.attrs[k] ?? null; }
  setAttribute(k, v) { this.attrs[k] = v; }
  get hidden() { return Object.hasOwn(this.attrs, 'hidden'); }
  set hidden(v) { if (v) this.attrs.hidden = ''; else delete this.attrs.hidden; }
  get textContent() { return this.children.map(c => typeof c === 'string' ? c : c.textContent).join(''); }
  set textContent(v) { this.children = [v]; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  click() {
    const event = {target: this, prevented: false, stopped: false,
      preventDefault() { this.prevented = true; }, stopPropagation() { this.stopped = true; }};
    for (let node = this; node; node = node.parentElement) {
      for (const fn of node.listeners.click || []) fn(event);
      if (event.stopped) break;
    }
    return event;
  }
}
const trees = JSON.parse(process.argv[2]);
const resultsList = new Element(trees[0]), paperDetails = new Element(trees[1]);
let transitions = 0, layouts = 0;
vm.runInNewContext(process.argv[3], {resultsList, paperDetails,
  PaperDetailsHelpers: {...helpers, togglePaperAuthors(button) {
    transitions++; return helpers.togglePaperAuthors(button);
  }}, scheduleResultsMasonryLayout() { layouts++; }});
const button = root => root.querySelector('.paper-authors-toggle');
const visible = root => root.querySelectorAll('.paper-author').filter(a => !a.closest('[hidden]'));
const names = root => visible(root).map(a => a.children[0]);
const first = button(resultsList), other = button(paperDetails);
""" + assertions + "\nprocess.stdout.write(JSON.stringify(true));",
                  json.dumps(trees), self.delegation)

    def test_short_and_threshold_lists_have_no_control(self):
        for count in (0, 3, 4):
            with self.subTest(count=count):
                html = self.markup([f"Author {i}" for i in range(count)], "card")
                self.assertNotIn('paper-authors-toggle', html)
                if not count:
                    self.assertIn('Unknown', html)

    def test_initial_limits_are_context_specific(self):
        self.exercise(self.markup(context="card"), """
assert.equal(visible(resultsList).length, 4);
assert.equal(visible(paperDetails).length, 8);
assert.equal(first.getAttribute('aria-expanded'), 'false');
assert.equal(other.getAttribute('aria-expanded'), 'false');
""", self.markup())

    def test_click_expands_all_authors_in_order_in_both_contexts(self):
        self.exercise(self.markup(context="card"), """
for (const root of [resultsList, paperDetails]) {
  button(root).click();
  assert.deepEqual(names(root), Array.from({length:10}, (_, i) => `Author ${i+1}`));
  assert.equal(button(root).getAttribute('aria-expanded'), 'true');
  assert.equal(button(root).textContent, 'Show fewer authors');
}
""", self.markup())

    def test_collapse_restores_each_initial_limit(self):
        self.exercise(self.markup(context="card"), """
for (const [root, count] of [[resultsList,4], [paperDetails,8]]) {
  button(root).click(); button(root).click();
  assert.equal(visible(root).length, count);
  assert.equal(button(root).getAttribute('aria-expanded'), 'false');
  assert.equal(button(root).textContent, 'Show all authors');
}
""", self.markup())

    def test_pinned_pane_does_not_require_result_card_ancestors(self):
        self.exercise(self.markup(), """
assert.equal(paperDetails.querySelector('.result-authors'), null);
other.click();
assert.equal(visible(paperDetails).length, 10);
assert.equal(other.getAttribute('aria-controls'), paperDetails.querySelector('.paper-authors-overflow').getAttribute('id'));
""")
        self.assertIn('"paper-details-authors-overflow",', self.app)

    def test_formal_survey_nine_author_order_and_superscripts(self):
        survey = next(p for p in self.papers if p.get('paper_id') == 'curated:c071c25bc2957d78569b')
        expected = ["Thanh Thi Nguyen", "Quoc Viet Hung Nguyen", "Dung Tien Nguyen",
                    "Duc Thanh Nguyen", "Thien Huynh-The", "Saeid Nahavandi",
                    "Thanh Tam Nguyen", "Quoc-Viet Pham", "Cuong M. Nguyen"]
        self.exercise(self.markup(survey['authors'], 'card'), """
assert.deepEqual(names(paperDetails), """ + json.dumps(expected[:8]) + """);
assert.equal(paperDetails.querySelector('.paper-authors-overflow').hidden, true);
assert.equal(paperDetails.querySelector('.paper-authors-overflow').querySelector('.paper-author').children[0], 'Cuong M. Nguyen');
for (const root of [resultsList, paperDetails]) {
  button(root).click();
  assert.deepEqual(names(root), """ + json.dumps(expected) + """);
  assert.deepEqual(visible(root).map(a => a.querySelector('sup').textContent), ['1','2','1','1','3','1','4','5','6']);
  assert.equal(root.querySelectorAll('.paper-author').length, 9);
}
""", self.markup(survey['authors']))

    def test_overflow_multi_affiliations_survive_repeated_toggles(self):
        record = next(p for p in self.papers if p['title'].startswith('SynerDetect:'))
        self.exercise(self.markup(record['authors']), """
for (let i = 0; i < 3; i++) {
  first.click();
  const author = visible(resultsList).find(a => a.children[0] === 'Lei Zhu');
  assert.equal(author.querySelector('sup').textContent, '1,2');
  assert.equal(author.querySelector('sup').getAttribute('aria-label'), 'Affiliations 1, 2');
  first.click();
}
""")

    def test_non_institutional_and_unresolved_overflow_never_gain_superscripts(self):
        authors = [f"Author {i}" for i in range(8)] + [
            {"name": "Reid Southen", "affiliation_indices": [], "affiliation_status": "non_institutional",
             "affiliation_review": {"status": "non_institutional", "reason_kind": "role_only", "source_text": "Concept Artist"}},
            {"name": "Unresolved Author", "affiliation_indices": [], "affiliation_status": "unresolved"}]
        self.exercise(self.markup(authors), """
first.click();
assert.equal(visible(resultsList).length, 10);
for (const author of visible(resultsList).slice(8)) {
  assert.equal(author.querySelector('sup'), null);
  assert.equal(author.matches('.is-active-institution-author'), false);
}
assert.equal(visible(resultsList)[8].querySelector('.author-role').textContent, ' (Concept Artist)');
""")

    def test_delegation_survives_repeated_content_replacement(self):
        self.exercise(self.markup(), """
for (let i = 0; i < 3; i++) {
  paperDetails.children = new Element(trees[1]).children;
  paperDetails.children.forEach(c => { if (typeof c !== 'string') c.parentElement = paperDetails; });
  assert.equal(button(paperDetails).getAttribute('aria-expanded'), 'false');
  button(paperDetails).click();
  assert.equal(visible(paperDetails).length, 10);
}
assert.equal(transitions, 3);
""")

    def test_blur_after_pinning_does_not_replace_the_next_click_target(self):
        clear_hover = "function clearHoveredSelection" + self.app.split(
            "function clearHoveredSelection", 1
        )[1].split("\nfunction selectPaper", 1)[0]
        self.node("""
const assert = require('node:assert/strict');
const marker = {};
const interactionState = {
  selectedPaperId: 'paper:one', detailMode: 'paper',
  transientHover: {marker},
};
const markerHoverIntent = {cancel() {}};
let renders = 0;
const renderActiveSelection = () => renders++;
""" + clear_hover + """
clearHoveredSelection({}); // unrelated marker
assert.equal(renders, 0);
clearHoveredSelection(marker);
assert.equal(renders, 1);
assert.equal(interactionState.transientHover, null);
assert.equal(interactionState.selectedPaperId, 'paper:one');
assert.equal(interactionState.detailMode, 'paper');
process.stdout.write(JSON.stringify(true));
""")

    def test_two_papers_do_not_share_expansion(self):
        second = self.markup([f"Other {i}" for i in range(10)])
        self.exercise(self.markup(), """
first.click();
assert.equal(other.getAttribute('aria-expanded'), 'false');
assert.equal(visible(paperDetails).length, 8);
other.click(); first.click();
assert.equal(visible(paperDetails).length, 10);
assert.equal(visible(resultsList).length, 8);
""", second)

    def test_native_keyboard_button_contract_has_no_duplicate_key_handler(self):
        self.exercise(self.markup(), """
assert.equal(first.tag, 'button');
assert.equal(first.getAttribute('type'), 'button');
assert.equal(first.textContent, 'Show all authors');
assert.equal(resultsList.listeners.keydown, undefined);
assert.equal(paperDetails.listeners.keydown, undefined);
""")

    def test_one_click_produces_exactly_one_transition(self):
        self.exercise(self.markup(), """
first.click();
assert.equal(transitions, 1);
assert.equal(layouts, 1);
assert.equal(first.getAttribute('aria-expanded'), 'true');
""")

    def test_same_paper_card_and_pane_remain_independent(self):
        self.exercise(self.markup(context='card'), """
first.click(); other.click(); other.click();
assert.equal(visible(resultsList).length, 10);
assert.equal(visible(paperDetails).length, 8);
""", self.markup())

    def test_toggle_preserves_nodes_and_stops_navigation(self):
        self.exercise(self.markup(), """
const originalAuthors = resultsList.querySelectorAll('.paper-author');
const event = first.click();
assert.equal(event.prevented, true);
assert.equal(event.stopped, true);
assert.equal(button(resultsList), first); // focused button is never replaced
assert.deepEqual(resultsList.querySelectorAll('.paper-author'), originalAuthors);
""")

    def test_absent_overflow_does_not_claim_expanded_state(self):
        self.exercise('<button type="button" class="paper-authors-toggle" aria-expanded="false">Show all authors</button>', """
assert.equal(helpers.togglePaperAuthors(first), false);
assert.equal(first.getAttribute('aria-expanded'), 'false');
""")

    def test_author_text_and_region_id_remain_escaped(self):
        markup = self.markup(['<img src=x onerror=alert(1)>', 'Other'], limit=1,
                             region_id='x" onclick="alert(1)')
        self.assertNotIn('<img', markup)
        self.exercise(markup, """
assert.equal(first.getAttribute('onclick'), null);
assert.equal(first.getAttribute('aria-controls'), 'x" onclick="alert(1)');
first.click();
assert.deepEqual(names(resultsList), ['<img src=x onerror=alert(1)>', 'Other']);
""")


if __name__ == "__main__":
    unittest.main()
