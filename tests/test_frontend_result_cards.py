import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/"
    "codex-primary-runtime/dependencies/node/bin/node"
)


class FrontendResultCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        cls.html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

    def function(self, name, next_name):
        return self.app.split(f"function {name}", 1)[1].split(
            f"\nfunction {next_name}", 1
        )[0]

    def test_views_use_distinct_entity_specific_card_renderers(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        paper = self.function("paperResultContent", "renderResults")
        render = self.function("renderResults", "selectResultsView")
        create = self.function("createResultItem", "initialResultChunkSize")
        self.assertIn("result-card-institution", institution)
        self.assertIn("Institution record", institution)
        self.assertIn("result-card-paper", paper)
        self.assertIn("Unique paper", paper)
        self.assertIn("institutionResultContent(record, relatedEntries, cardId)", create)
        self.assertIn("paperResultContent(record, relatedEntries, cardId)", create)
        self.assertIn(": visibleRecords", render)
        self.assertIn("paperListRecordsForDisplay(visiblePaperRecords)", render)

    def test_titles_are_accessibly_named_and_use_a_two_line_preview(self):
        self.assertIn('aria-labelledby="${cardId}"', self.app)
        self.assertIn('id="${cardId}"', self.app)
        self.assertIn("result-card-title-${pipeline.view}-${index}", self.app)
        result_title = self.css.split(".result-title {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-wrap: anywhere", result_title)
        self.assertIn("-webkit-line-clamp: 2", result_title)
        self.assertIn("overflow: hidden", result_title)

    def test_author_order_object_safety_and_accessible_expansion(self):
        authors = self.function("resultAuthors", "institutionResultContent")
        self.assertIn("PaperDetailsHelpers.renderPaperAuthors", authors)
        self.assertNotIn(".slice(", authors)
        self.assertIn("visibleLimit", authors)
        self.assertIn("Authors at this institution", self.app)
        self.assertIn("Paper authors", self.app)
        self.assertIn('closest(".paper-authors-toggle")', self.app)
        self.assertIn('setAttribute("aria-expanded"', self.app)
        self.assertIn('`${regionId}-overflow`', authors)
        self.assertNotIn("[object Object]", authors)

    def test_unique_paper_cards_reuse_author_affiliation_numbers(self):
        paper = self.function("paperResultContent", "renderResults")
        authors = self.function("resultAuthors", "institutionResultContent")
        self.assertIn("resultAuthors(normalizedRecord.authors", paper)
        self.assertIn("renderPaperAuthors", authors)
        self.assertIn("author-affiliation-numbers", (
            ROOT / "web" / "paper_details_helpers.js"
        ).read_text(encoding="utf-8"))

    def test_current_public_preview_record_matches_details_and_card_markers(self):
        preview = json.loads((
            ROOT / "web" / "data" / "public_preview_papers.json"
        ).read_text(encoding="utf-8"))
        title = (
            '"That\'s Another Doom I Haven\'t Thought About": A User Study on '
            "AI Labels as a Safeguard Against Image-Based Misinformation"
        )
        record = next(
            item for item in preview["records"] if item["title"] == title
        )
        helper = ROOT / "web" / "paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const record = JSON.parse(process.argv[2]);
const escapeHtml = (value) => String(value);
process.stdout.write(JSON.stringify({
  cardItems: helpers.renderPaperAuthorItems(record, escapeHtml),
  detailsHtml: helpers.renderPaperAuthors(record, escapeHtml),
}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper), json.dumps(record)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)

        self.assertEqual(
            [affiliation["index"] for affiliation in record["affiliations"]],
            [1, 2, 3, 4, 5],
        )
        expected = {
            author["name"]: ",".join(map(str, author["affiliation_indices"]))
            for author in record["authors"]
        }
        for author_name, numbers in expected.items():
            marker = f'>{numbers}</sup>'
            self.assertTrue(
                any(author_name in item and marker in item for item in rendered["cardItems"])
            )
            self.assertIn(author_name, rendered["detailsHtml"])
            self.assertIn(marker, rendered["detailsHtml"])

    def test_mapping_assets_share_a_current_cache_key(self):
        versions = {
            asset: self.html.split(f'{asset}?v=', 1)[1].split('"', 1)[0]
            for asset in (
                "style.css",
                "synthetic-image-detection-attribution-landscape-logo.png",
                "paper_details_helpers.js",
                "paper_link_helpers.js",
                "marker_size_helpers.js",
                "marker_interaction_helpers.js",
                "public_metadata.js",
                "institution_type_labels.js",
                "app.js",
            )
        }
        self.assertEqual(len(set(versions.values())), 1)

    def test_shared_author_items_preserve_mappings_across_visibility_slices(self):
        helper = ROOT / "web" / "paper_details_helpers.js"
        script = r"""
const helpers = require(process.argv[1]);
const escapeHtml = (value) => String(value);
const authors = [
  {name: "One", affiliation_indices: [1]},
  {name: "Shared", affiliation_indices: [1, 2, 2]},
  {name: "Unmapped", affiliation_indices: []},
  {name: "Overflow", affiliation_indices: [10]},
];
const items = helpers.renderPaperAuthorItems({authors}, escapeHtml);
process.stdout.write(JSON.stringify({items, collapsed: items.slice(0, 2), expanded: items}));
"""
        result = subprocess.run(
            [str(NODE), "-e", script, str(helper)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered["collapsed"], rendered["expanded"][:2])
        self.assertIn(">1,2</sup>", rendered["items"][1])
        self.assertNotIn("<sup", rendered["items"][2])
        self.assertIn(">10</sup>", rendered["items"][3])

    def test_institution_record_renderer_does_not_add_numbering(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertNotIn("result-institution-number", institution)

    def test_institution_cards_preserve_scoped_mappings(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertIn("institution?.authors?.length", institution)
        self.assertIn("recordInstitutionAuthors(record)", institution)
        self.assertIn("recordAuthors(normalizedRecord)", institution)
        self.assertIn("institutionFocusButtonHtml", institution)
        self.assertIn("recordLocation(record)", institution)
        self.assertIn("institutionTypeLabel(institutionType)", institution)
        self.assertIn('`${cardId}-authors`, 4', institution)

    def test_unique_papers_group_all_canonical_institutions(self):
        institutions = self.function("resultInstitutions", "paperResultContent")
        unique = self.function("uniquePaperInstitutions", "resultInstitutions")
        self.assertIn("uniquePaperInstitutions(affiliations)", institutions)
        self.assertIn("institutionIdentity", unique)
        self.assertIn("uniqueAffiliations.length", institutions)
        self.assertIn("result-institutions-overflow", institutions)
        self.assertIn('aria-expanded="false"', institutions)
        self.assertIn("Show all institutions", institutions)
        self.assertIn("Show fewer institutions", self.app)
        self.assertIn('aria-label="Paper institutions"', institutions)
        self.assertIn("affiliation.number", institutions)
        self.assertIn('aria-label="Institution ${escapeHtml(affiliation.number)}"', institutions)
        paper = self.function("paperResultContent", "renderResults")
        self.assertIn('`${cardId}-authors`, 4', paper)
        self.assertIn('`${cardId}-institutions`, 3', paper)

    def test_desktop_uses_two_independent_content_sized_columns(self):
        results_list = self.css.split(".results-list {", 1)[1].split("}", 1)[0]
        self.assertIn("display: grid", results_list)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", results_list)
        self.assertIn("grid-auto-rows: auto", results_list)
        self.assertIn("gap: var(--masonry-gap)", results_list)
        ready = self.css.split(
            ".results-list.is-masonry-ready {", 1
        )[1].split("}", 1)[0]
        self.assertIn("grid-auto-rows: var(--masonry-row)", ready)
        root = self.css.split(":root {", 1)[1].split("}", 1)[0]
        self.assertIn("--masonry-gap: 11px", root)
        self.assertIn("--masonry-row: 1px", root)
        item = self.css.split(".result-item {", 1)[1].split("}", 1)[0]
        self.assertIn("display: flow-root", item)
        self.assertIn("width: 100%", item)
        self.assertNotIn("margin", item)
        self.assertNotIn("height:", item)
        card = self.css.split(".result-card {", 1)[1].split("}", 1)[0]
        self.assertIn("display: flow-root", card)
        self.assertNotIn("flex-direction", card)
        self.assertNotIn("height:", card)
        self.assertNotIn("overflow: hidden", card)
        self.assertNotIn("--result-card-height", self.css)

    def test_masonry_preserves_list_semantics_and_dom_render_order(self):
        self.assertIn('<ol id="results-list" class="results-list"></ol>', self.html)
        create = self.function("createResultItem", "initialResultChunkSize")
        append = self.function("appendResultChunk", "observeResultSentinel")
        self.assertIn('document.createElement("li")', create)
        self.assertIn("fragment.append(card)", append)
        self.assertIn("resultsList.append(fragment)", append)
        self.assertNotIn("style.order", create + append)
        self.assertNotIn("appendToColumn", create + append)
        masonry = self.function("measureMasonryItems", "scheduleMasonryMeasurement")
        self.assertIn('style.gridRowEnd = `span ${span}`', masonry)
        self.assertIn('classList.add("is-masonry-ready")', masonry)
        self.assertIn("card.scrollHeight", masonry)
        self.assertIn('card.querySelector(".result-card")', masonry)
        self.assertIn("renderedCard?.getBoundingClientRect()", masonry)
        self.assertIn("renderedRect?.height", masonry)
        self.assertIn("renderedCard?.scrollHeight", masonry)
        self.assertIn("renderedCard?.lastElementChild", masonry)
        self.assertIn("finalChild?.getBoundingClientRect().bottom", masonry)
        self.assertIn("paddingBottom", masonry)
        self.assertIn("descendantHeight", masonry)
        self.assertIn("borderTopWidth", masonry)
        self.assertIn("borderBottomWidth", masonry)
        self.assertIn("listStyles.rowGap", masonry)
        self.assertIn('getPropertyValue("--masonry-gap")', masonry)
        self.assertIn('getPropertyValue("--masonry-row")', masonry)
        self.assertIn("mobileFiltersMedia.matches", masonry)
        self.assertNotIn("const rowGap = 11", masonry)

        scheduler = self.function("scheduleMasonryMeasurement", "createResultItem")
        self.assertEqual(scheduler.count("requestResultsAnimationFrame"), 2)
        self.assertIn("measureMasonryItems(list, cards, generation)", scheduler)

    def test_initial_skeleton_and_incremental_cards_are_revealed_after_measurement(self):
        self.assertIn('<div class="results-records-area">', self.html)
        self.assertIn('id="results-loading"', self.html)
        pending = self.css.split(
            ".result-item.is-masonry-pending {", 1
        )[1].split("}", 1)[0]
        self.assertIn("visibility: hidden", pending)
        loading = self.css.split(".results-loading {", 1)[1].split("}", 1)[0]
        self.assertIn("position: absolute", loading)
        self.assertIn("pointer-events: none", loading)

        layout = self.function(
            "setResultsLayoutPending", "invalidateResultsRenderPipeline"
        )
        self.assertIn('setAttribute("aria-busy", String(isPending))', layout)
        self.assertIn("showSkeleton", layout)

        scheduler = self.function(
            "scheduleMasonryMeasurement", "createResultItem"
        )
        measure_position = scheduler.index("measureMasonryItems(list, cards, generation)")
        reveal_position = scheduler.index('classList.remove("is-masonry-pending")')
        self.assertGreater(reveal_position, measure_position)
        self.assertIn("generation !== resultsRenderGeneration", scheduler)

    def test_progressive_rendering_keeps_full_results_but_appends_viewport_chunks(self):
        render = self.function("renderResults", "selectResultsView")
        append = self.function("appendResultChunk", "observeResultSentinel")
        observe = self.function("observeResultSentinel", "prepareFirstResultViewport")
        prepare = self.function("prepareFirstResultViewport", "scheduleResultsMasonryLayout")
        self.assertIn("currentDisplayedResults = displayedResults", render)
        self.assertNotIn("displayedResults.forEach", render)
        self.assertIn("initialResultChunkSize(pipeline)", prepare)
        self.assertIn("resultsList.replaceChildren(...preparedCards)", prepare)
        self.assertIn("resultsList.append(fragment)", append)
        self.assertIn("nextResultChunkSize(pipeline)", append)
        self.assertIn("new IntersectionObserver", observe)
        self.assertIn("rootMargin: RESULTS_OBSERVER_MARGIN", observe)
        self.assertIn('id="results-sentinel"', self.html)

    def test_render_generation_guards_async_work_and_coalesces_keyword_input(self):
        invalidation = self.function(
            "invalidateResultsRenderPipeline", "resultsColumnCount"
        )
        self.assertIn("resultsRenderGeneration += 1", invalidation)
        self.assertIn("cancelAnimationFrame", invalidation)
        self.assertIn("resultsObserver.disconnect()", invalidation)
        self.assertGreaterEqual(self.app.count("generation !== resultsRenderGeneration"), 12)
        self.assertNotIn("RESULTS_KEYWORD_DEBOUNCE_MS", self.app)
        self.assertIn("const RESULTS_RESIZE_DEBOUNCE_MS = 100", self.app)
        keyword_start = self.app.index("function scheduleKeywordRender")
        keyword = self.app[
            keyword_start:
            self.app.index('taskFilter.addEventListener', keyword_start)
        ]
        self.assertIn("requestResultsAnimationFrame", keyword)
        self.assertIn("invalidateResultsRenderPipeline()", keyword)
        self.assertIn("generation !== resultsRenderGeneration", keyword)
        self.assertIn('addEventListener("compositionstart"', keyword)
        self.assertIn('addEventListener("compositionend"', keyword)
        self.assertIn("event.isComposing", keyword)
        self.assertNotIn("setTimeout", keyword)
        self.assertIn("resultsLayoutSignature() !== resultsPipeline.layoutSignature", self.app)

    def test_search_text_cache_prewarms_once_after_the_first_viewport_paints(self):
        cache = self.function(
            "invalidateFilteringDataCaches", "institutionFilterIndexes"
        )
        prepare = self.function(
            "prepareFirstResultViewport", "scheduleResultsMasonryLayout"
        )
        self.assertIn('typeof requestIdleCallback === "function"', cache)
        self.assertIn("requestIdleCallback(callback, { timeout: 1000 })", cache)
        self.assertIn("setTimeout(() =>", cache)
        self.assertIn("dataGeneration !== filteringDataCacheGeneration", cache)
        self.assertIn("cachedRecordSearchText(sourceRecords[nextIndex])", cache)
        self.assertIn("searchTextPrewarmGeneration === dataGeneration", cache)
        reveal = prepare.index("resultsList.replaceChildren(...preparedCards)")
        post_paint_frame = prepare.index("requestResultsAnimationFrame", reveal)
        prewarm = prepare.index("scheduleSearchTextCachePrewarm()", post_paint_frame)
        self.assertGreater(post_paint_frame, reveal)
        self.assertGreater(prewarm, post_paint_frame)

    def test_same_frame_keyword_updates_render_only_the_latest_state(self):
        invalidation_start = self.app.index("function invalidateResultsRenderPipeline")
        invalidation_end = self.app.index("\nfunction resultsColumnCount", invalidation_start)
        keyword_start = self.app.index("function scheduleKeywordRender")
        keyword_end = self.app.index(
            '\nkeywordFilter.addEventListener("compositionstart"', keyword_start
        )
        script = r'''
let resultsRenderGeneration = 0;
let resultsKeywordFrame = null;
let resultsObserver = null;
let resultsPipeline = null;
const resultsMasonryFrames = new Set();
const callbacks = new Map();
let nextFrame = 1;
function requestAnimationFrame(callback) {
  const id = nextFrame++;
  callbacks.set(id, callback);
  return id;
}
function cancelAnimationFrame(id) { callbacks.delete(id); }
const document = {querySelector: () => null};
const resultsList = {querySelector: () => ({})};
function setResultsLayoutPending() {}
const keywordFilter = {value: ''};
const applied = [];
function renderRecordsForGeneration({generation}) {
  if (generation === resultsRenderGeneration) applied.push(keywordFilter.value);
}
''' + self.app[invalidation_start:invalidation_end] + self.app[keyword_start:keyword_end] + r'''
for (const value of ['d', 'diff', 'diffusion']) {
  keywordFilter.value = value;
  scheduleKeywordRender();
}
for (const callback of [...callbacks.values()]) callback();
process.stdout.write(JSON.stringify({
  applied,
  generation: resultsRenderGeneration,
  pendingFrames: callbacks.size,
}));
'''
        completed = subprocess.run(
            [str(NODE), "-e", script], check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["applied"], ["diffusion"])
        self.assertEqual(result["generation"], 3)

    def test_adaptive_content_and_metadata_follow_natural_flow(self):
        adaptive = self.css.split(".result-card-adaptive {", 1)[1].split("}", 1)[0]
        self.assertIn("min-width: 0", adaptive)
        self.assertNotIn("flex:", adaptive)
        self.assertNotIn("overflow:", adaptive)
        secondary = self.css.split(".result-secondary {", 1)[1].split("}", 1)[0]
        self.assertNotIn("margin-top: auto", secondary)
        self.assertNotIn("flex:", secondary)
        self.assertNotIn("max-height: 78px", self.css)
        self.assertNotIn(".result-authors.is-expanded", self.css)
        self.assertNotIn(".result-paper-institutions.is-expanded", self.css)

    def test_narrow_layout_keeps_natural_cards_in_a_single_column(self):
        narrow = self.css.split("@media (max-width: 820px) {", 1)[1].split(
            "@media (max-width: 820px) and", 1
        )[0]
        results_list = narrow.split(".results-list {", 1)[1].split("}", 1)[0]
        self.assertIn("grid-template-columns: 1fr", results_list)
        self.assertIn("grid-auto-rows: auto", results_list)
        self.assertNotIn("result-card-height", narrow)

    def test_both_card_types_share_the_compact_vertical_rhythm(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        paper = self.function("paperResultContent", "renderResults")
        self.assertIn("result-card result-card-institution", institution)
        self.assertIn("result-card result-card-paper", paper)

        card = self.css.split(".result-card {", 1)[1].split("}", 1)[0]
        title = self.css.split(".result-title {", 1)[1].split("}", 1)[0]
        institution_block = self.css.split(
            ".result-institution-primary {", 1
        )[1].split("}", 1)[0]
        entity = self.css.split(".result-entity-section {", 1)[1].split("}", 1)[0]
        secondary = self.css.split(".result-secondary {", 1)[1].split("}", 1)[0]
        self.assertIn("padding: 12px", card)
        self.assertIn("margin: 0 0 6px", title)
        self.assertIn("margin: 0 0 6px", institution_block)
        self.assertIn("padding: 7px 8px", institution_block)
        self.assertIn("margin-bottom: 6px", entity)
        self.assertIn("padding-top: 7px", secondary)

    def test_result_cards_stay_white_and_institution_blocks_use_subtle_surface(self):
        item = self.css.split(".result-item {", 1)[1].split("}", 1)[0]
        institution = self.css.split(
            ".result-institution-primary {", 1
        )[1].split("}", 1)[0]
        self.assertIn("background: var(--paper)", item)
        self.assertIn("background: var(--institution-surface)", institution)
        self.assertNotIn("background: var(--secondary-surface)", institution)

    def test_render_does_not_apply_stale_fixed_height_view_classes(self):
        render = self.function("renderResults", "selectResultsView")
        self.assertNotIn("results-list-institutions", render)
        self.assertNotIn("results-list-papers", render)
        self.assertNotIn("result-card-height", self.app)

    def test_expansion_uses_natural_growth_and_accessible_controls(self):
        self.assertIn("overflow.hidden = isExpanded", self.app)
        self.assertIn('aria-controls="${regionId}"', self.app)
        self.assertNotIn("style.height", self.app)
        self.assertNotIn('toggleAttribute("tabindex"', self.app)
        self.assertIn('window.addEventListener("resize", () => {', self.app)
        self.assertIn("document.fonts?.ready.then(() =>", self.app)
        self.assertGreaterEqual(self.app.count("scheduleResultsMasonryLayout();"), 2)
        self.assertIn('closest(".result-item")', self.app)

    def test_collapsed_overflow_content_is_not_forced_visible_by_card_css(self):
        hidden_overflow = self.css.split(
            ".result-institutions-overflow[hidden],", 1
        )[1].split("}", 1)[0]
        self.assertIn(".paper-authors-overflow[hidden]", hidden_overflow)
        self.assertIn("display: none", hidden_overflow)

    def test_publication_row_badges_and_links_are_nonduplicative(self):
        venue = self.function("resultVenueYear", "resultLinks")
        badges = self.function("resultBadges", "resultVenueYear")
        links = self.function("resultLinks", "resultAuthors")
        self.assertIn("paperDetailsPublication(record)", venue)
        self.assertIn("publicationYear(record)", venue)
        self.assertIn('join(" ")', venue)
        self.assertIn("/^unknown publication venue$/i", venue)
        self.assertIn('year !== null', venue)
        self.assertNotIn("venueDisplayHtml(record)", venue)
        self.assertNotIn("venue-type-badge", venue)
        self.assertIn("popup-badges result-badges", badges)
        self.assertIn("popup-badge popup-task task-", badges)
        self.assertIn("entry-type-badge", badges)
        self.assertNotIn("publication-type-badge", badges)
        self.assertNotIn("institution-type-badge", badges)
        self.assertNotIn("arXiv version", badges)
        self.assertNotIn("Preliminary affiliations", badges)
        self.assertNotIn("resolutionConfidence", badges)
        self.assertNotIn("reviewStatus", badges)
        self.assertIn("paperExternalLinks(record)", links)
        self.assertIn("paper-details-links result-links", links)

    def test_dfbench_badges_use_the_canonical_paper_record_in_both_views(self):
        map_data = json.loads((
            ROOT / "web" / "data" / "public_preview_map_data.json"
        ).read_text(encoding="utf-8"))
        paper_data = json.loads((
            ROOT / "web" / "data" / "public_preview_papers.json"
        ).read_text(encoding="utf-8"))
        title = (
            "DFBench: Benchmarking Deepfake Image Detection Capability of "
            "Large Multimodal Models"
        )
        institution_record = next(
            record for record in map_data["records"]
            if record["title"] == title
        )
        paper_record = next(
            record for record in paper_data["records"] if record["title"] == title
        )
        self.assertEqual(
            institution_record["paper_categories"], paper_record["paper_categories"]
        )
        # Exercise stale metadata explicitly; corrected exports no longer
        # retain an obsolete automatic marker as this test's fixture.
        institution_record = {**institution_record, "paper_categories": ["benchmark"]}

        sources = [
            "const ENTRY_TYPE_LABELS = {method: 'Method', dataset: 'Dataset', "
            "benchmark: 'Benchmark', survey: 'Survey', analysis: 'Analysis study'};",
            "const PUBLIC_TASK_LABELS = {detection: 'Detection', uncertain: 'Unknown'};",
            "const MarkerSizeHelpers = {normalizeTaskLabel: (value) => value || 'uncertain'};",
            "const escapeHtml = (value) => String(value);",
            "const isBookRecord = () => false;",
            "const paperIdentity = (record) => `doi:${String(record.doi).toLowerCase()}`;",
            "let canonicalPaperRecordsByIdentity = new Map();",
            "function formatPublicTask" + self.function(
                "formatPublicTask", "canonicalPaperRecord"
            ),
            "function canonicalPaperRecord" + self.function(
                "canonicalPaperRecord", "getPaperCategories"
            ),
            "function getPaperCategories" + self.function(
                "getPaperCategories", "getEntryTypeLabel"
            ),
            "function getEntryTypeLabel" + self.function(
                "getEntryTypeLabel", "recordTitle"
            ),
            "function resultBadges" + self.function(
                "resultBadges", "resultVenueYear"
            ),
            "const institutionRecord = JSON.parse(process.argv[1]);",
            "const paperRecord = JSON.parse(process.argv[2]);",
            "canonicalPaperRecordsByIdentity.set(paperIdentity(paperRecord), paperRecord);",
            "process.stdout.write(JSON.stringify({institution: resultBadges(institutionRecord), "
            "paper: resultBadges(paperRecord)}));",
        ]
        result = subprocess.run(
            [
                str(NODE), "-e", "\n".join(sources),
                json.dumps(institution_record), json.dumps(paper_record),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered["institution"], rendered["paper"])
        badges = rendered["paper"]
        self.assertLess(badges.index("Detection"), badges.index("Method"))
        self.assertLess(badges.index("Method"), badges.index("Dataset"))
        self.assertLess(badges.index("Dataset"), badges.index("Benchmark"))

    def test_institution_type_is_only_in_the_scoped_institution_block(self):
        institution = self.function(
            "institutionResultContent", "uniquePaperInstitutions"
        )
        self.assertEqual(institution.count("institutionTypeLabel(institutionType)"), 1)
        self.assertIn("${resultBadges(record)}", institution)
        self.assertNotIn("resultBadges(record, true)", institution)

    def test_sort_control_uses_shared_compact_dropdown_without_changing_options(self):
        self.assertIn(
            '<select id="sort-control" class="sort-control-compact" disabled>',
            self.html,
        )
        self.assertIn(
            '<div class="sort-control-label filter-dropdown-field" data-filter-dropdown>',
            self.html,
        )
        button_css = self.css.split(
            ".sort-control-label .filter-dropdown-button {", 1
        )[1].split(
            "}", 1
        )[0]
        self.assertIn("height: 32px", button_css)
        self.assertIn("min-height: 32px", button_css)
        self.assertIn("padding: 3px 8px", button_css)
        self.assertNotIn(".sort-control-label select {", self.css)
        sort_options = self.html.split(
            '<select id="sort-control" class="sort-control-compact" disabled>', 1
        )[1].split("</select>", 1)[0]
        self.assertEqual(sort_options.count('<option value="'), 5)

    def test_counts_states_list_semantics_and_nested_controls(self):
        render = self.function("renderResults", "selectResultsView")
        self.assertIn(
            'resultNoun = resultsView === "papers" ? "unique paper" : "institution record"',
            render,
        )
        self.assertIn("displayedResults.length", render)
        self.assertIn("No matching ${resultNoun}s", render)
        self.assertIn('<ol id="results-list"', self.html)
        self.assertIn("Data unavailable", self.app)
        self.assertIn("Loading…", self.html)
        self.assertNotIn('tabindex="0"', render)
        self.assertIn(":is(a, button):focus-visible", self.css)

    def test_result_content_has_no_horizontal_overflow_patterns(self):
        card_css = self.css.split(".result-item {", 1)[1].split(
            ".results-empty", 1
        )[0]
        self.assertIn("min-width: 0", card_css)
        self.assertIn("overflow-wrap: anywhere", card_css)
        self.assertIn("flex-wrap: wrap", card_css)
        self.assertIn("text-overflow: ellipsis", card_css)
        self.assertIn("white-space: nowrap", card_css)


if __name__ == "__main__":
    unittest.main()
