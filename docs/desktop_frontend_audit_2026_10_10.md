# Desktop frontend quality audit — 10 October 2026

Finalized 11 October 2026 (Asia/Shanghai). Scope: targeted desktop refinement and preservation checks for the existing static Leaflet site. No deployment, commit, push, branch update, data regeneration, or mobile redesign was performed.

The work continued from the interrupted working tree. HEAD and local `main` remained `f7e6f721dcca4c992285a86f3fc75706d6d3f091`. The observed `origin/main` was `805edcc5bbd2fb5c1afda348e900f32f02fcd450`; local `main` was **one commit behind**, with no local commits ahead. All 89 pre-existing untracked status entries remain present.

## Confirmed bugs fixed

| Issue | Final change | Verification |
| --- | --- | --- |
| Desktop result cards exposed a button role around independent links/buttons | Desktop cards are list items with a native, named **Details** button. Whole-card mouse selection and independent nested actions remain available. | Browser keyboard/mouse workflows, selection/marker checks, result-card regressions. |
| Resizing/zooming could leave staged cards with the previous breakpoint's interaction mode | Synchronize accessibility attributes when the breakpoint changes and immediately before prepared cards enter the list. Restore focus to the appropriate desktop/mobile target. | All 15 real-zoom cases; breakpoint semantics and mobile preservation checks. |
| An empty map implied no papers even when matching unmapped papers existed | The base map status distinguishes no matching unique papers, matching papers without mapped locations, and mapped institution/location markers. Uses the existing filtered-paper and marker collections. | Unit tests plus a real unmapped paper in both views. Selected-paper highlighting retains its separate existing status wording. |
| Sticky Filters could sit underneath the wrapped header | Use measured header height for the desktop sticky offset; remove the override when the small-screen breakpoint activates. | Header/Filters/Results toolbar geometry at every desktop matrix entry. |
| Task counts and their explanatory note exceeded the fixed header-chart allocation | Allow desktop chart height to grow and constrain the task grid's intrinsic width; wrap the overlap note. | No chart-container overflow in the 12 desktop-mode matrix entries. This does not certify every year-bar label; see remaining issues. |
| Methodology and homepage referenced different local asset versions | Synchronize local CSS/JS references to `20261009-desktop-1`. | Asset-reference regression; third-party URLs and integrity hashes unchanged. |
| An early parallel-loader implementation could let a paper-request failure supersede the original map validation outcome | Start both transfers together, handle the paper promise's rejection immediately, and retain map-first parsing/validation/error precedence before consuming the paper result. | A failing regression was reproduced and then passed for early paper network/body failures against empty, invalid, and valid map payloads. |

## Usability improvements implemented

- **Paper Details hierarchy:** title → venue/year → existing external links → taxonomy → authors/affiliations → abstract → metadata/review status. Existing DOM sections move; metadata, provenance, link construction, affiliation actions, and citations are retained. There is one external-link bar. Small-screen ordering is unchanged.
- **Predictable explicit Details action:** focuses the Details heading and reveals it when outside the visible area, including the stacked layout around 1024–1250 CSS pixels. Whole-card mouse selection keeps its established viewport behavior. No drawer redesign was needed.
- **Precise Publication Year entry:** desktop Start/End text fields use numeric input hints and the existing range state. Enter or change commits a complete valid year; typing a partial value does not filter. Invalid values get an accessible error; Escape restores the selected range. Slider, chart, reset, URL, and history synchronization remain intact, including the existing crossing-handle behavior.
- **Desktop skip navigation:** keyboard-visible links reach named Research Map and Paper Results sections, focus their targets, and clear the sticky header without changing the URL/hash/history contract.
- **Overlapping data transfers:** independent public JSON requests begin together with `cache: "no-cache"` preserved on both. Normalization, validation helpers, record ordering, and public data semantics are unchanged.

## Research discovery and scholarly clarity

Browser workflows exercised recent Source Attribution, Benchmark plus year, Tsinghua University search, Details and an external paper link, institution-control/marker/paper navigation, both result views, copy/restore of a filtered deep link, browser back/forward, a real unmapped paper, and actual downloads of both CSV views. The external-link check verified a separate browsing context; it was not an availability review of every paper URL.

The baseline contains 639 unique papers, 1,421 paper–institution records, 567 unique institutions, 684 institution/location markers, and 48 countries. Institutions and marker locations are distinct concepts: an institution can have several represented locations. Marker count is not a count of globally unique geographic coordinates. Facet options count unique papers with other filters applied; count definitions were retained.

Top Mapped Institutions and Papers by Year describe corpus coverage. Existing explanatory text/tooltips and methodology distinguish coverage from research quality or impact. Overlapping task labels are explicitly explained. Venue/year, taxonomy, facet counts, map legend, metadata status, and provenance were inspected without a global font or branding change. The existing 2027 publication value was preserved as source data.

## Desktop browser and zoom verification

Chrome **153.0.8010.53**, disposable profile, 900-pixel initial viewport height. Zoom was changed through Chrome's actual page-zoom setting, not CSS zoom, device emulation, or pinch scaling. Device-pixel ratios matched 1, 1.25, and 1.5. CSS widths below the established 821-pixel desktop threshold legitimately activate the existing small-screen layout.

| Viewport width | Browser zoom | CSS width | Active layout | Header height (CSS px) | Result |
| ---: | ---: | ---: | --- | ---: | --- |
| 1024 | 100% | 1024 | Desktop | 153.3 | Pass |
| 1024 | 125% | 819 | Existing small-screen | 223.3 | Preservation pass; legacy chart overflow retained |
| 1024 | 150% | 683 | Existing small-screen | 223.0 | Preservation pass; legacy chart overflow retained |
| 1200 | 100% | 1200 | Desktop | 173.2 | Pass |
| 1200 | 125% | 960 | Desktop | 168.6 | Pass |
| 1200 | 150% | 800 | Existing small-screen | 223.0 | Preservation pass; legacy chart overflow retained |
| 1280 | 100% | 1280 | Desktop | 159.7 | Pass |
| 1280 | 125% | 1024 | Desktop | 152.7 | Pass |
| 1280 | 150% | 853 | Desktop | 178.0 | Pass; dense year labels remain |
| 1440 | 100% | 1440 | Desktop | 159.7 | Pass |
| 1440 | 125% | 1152 | Desktop | 146.6 | Pass |
| 1440 | 150% | 960 | Desktop | 168.2 | Pass |
| 1920 | 100% | 1920 | Desktop | 159.7 | Pass |
| 1920 | 125% | 1536 | Desktop | 159.3 | Pass |
| 1920 | 150% | 1280 | Desktop | 159.1 | Pass |

All 15 cases had no horizontal page overflow. Desktop checks covered card semantics, visible Details focus, single link bar/order, selection state, skip targets, sticky Filters, and visible Results toolbar. Desktop map widths ranged from approximately 550 to 1,613 CSS pixels. Separate baseline comparisons at 390, 683, 800, and 820 CSS pixels found equal rounded geometry for key regions/cards, preserved card roles/tab order, and working filter-drawer Escape/focus restoration. These are targeted preservation checks, not full pixel-diff or screen-reader certification. All six existing `max-width` CSS media blocks are byte-identical to the baseline.

Screenshots and temporary browser artifacts remain in `/private/tmp/sirm-desktop-audit/final/`. Machine-readable results are preserved in [the evidence JSON](desktop_frontend_audit_2026_10_10.json).

## Performance measurements

### Method and definitions

The already-existing temporary `measure.cjs` was reused; `tests/frontend_desktop_performance.cjs` does not exist. The declined large command from the interrupted run was not repeated. No new performance framework, dependency, worker, build system, or application backend was added.

Measurements used isolated headless Chrome at 1440 × 1000, one fresh-context load followed by two reloads in that context. The final baseline and candidate batches ran sequentially after the data tests stopped competing for CPU. Both used the same local static server, public files, browser, viewport, and instrumentation. Local HTTP served identity-encoded bodies; `no-cache` caused full local transfers. The live site used compressed HTTP/2 responses and cache revalidation, so local timings are not live-site forecasts.

`mapReady` is the completion of the initial `renderRecordsForGeneration` call. `mapPaint` is two animation frames later; neither guarantees all remote basemap tiles have loaded. Filter/search latency is event dispatch through two animation frames, not a formal INP measurement. JSON parsing and named functions were instrumented; nested function durations overlap and must not be added together. JS heap samples are not total process memory, were not normalized by forced GC, and cannot establish a leak.

### Final equivalent local baseline/candidate samples

All timings below are milliseconds. Each cell is **cold / warm 1 / warm 2**; MB uses decimal units.

| Metric | Sequential baseline | Final parallel candidate |
| --- | --- | --- |
| Navigation → map-ready | 2025.9 / 530.6 / 509.7 | 2424.0 / 525.3 / 512.2 |
| Navigation → map-paint | 2049.0 / 546.0 / 524.4 | 2455.3 / 541.7 / 527.2 |
| First JSON request → map-paint | 614.7 / 511.6 / 493.0 | 547.4 / 508.4 / 496.2 |
| Map JSON request duration | 48.5 / 30.3 / 28.8 | 56.4 / 44.2 / 32.2 |
| Paper JSON request duration | 12.2 / 12.3 / 9.7 | 38.1 / 92.7 / 89.9 |
| Gap between request starts | 167.9 / 138.3 / 131.5 | 0.1 / 0.3 / 0.1 |
| JSON parse, both large payloads | 62.1 / 56.3 / 55.6 | 60.8 / 55.4 / 55.5 |
| Country/region normalization, aggregate | 38.6 / 33.5 / 30.0 | 35.4 / 32.7 / 31.8 |
| Public-dataset canonicalization | 62.4 / 56.0 / 52.6 | 58.8 / 55.6 / 52.6 |
| Initialization (`displayDataset`) | 363.7 / 300.5 / 295.2 | 337.7 / 301.0 / 295.8 |
| First 18 result cards, aggregate construction | 17.6 / 4.8 / 4.9 | 10.0 / 4.9 / 4.7 |
| Masonry measurement | 3.1 / 2.2 / 2.3 | 3.7 / 2.4 / 2.3 |
| First Source Attribution filter | 169.7 / 164.4 / 161.2 | 176.5 / 163.3 / 162.3 |
| Search `Tsinghua` within that filter | 287.8 / 239.0 / 235.9 | 227.4 / 219.9 / 256.7 |
| Largest initial main-thread long task | 390 / 326 / 320 | 419 / 326 / 320 |
| Sampled JS heap (MB) | 72.7 / 50.1 / 55.9 | 62.4 / 50.2 / 57.1 |

Payload-envelope normalization itself measured 0–0.2 ms. Local decoded JSON sizes were 19,872,256 and 8,827,603 bytes. Parallel requests overlap, but their individual ResourceTiming durations can grow while the main thread is busy. Warm page timings are essentially unchanged. Cold navigation was slower for the candidate in this pair: JSON loading began at 1,907.9 ms versus 1,434.3 ms in the baseline, before loader work. External resource/startup variation prevents attributing this difference to the loader.

The evidence supports removing a sequential network dependency, **not a fixed speedup**. Remaining 320–419 ms initial long tasks and roughly 162–177 ms filtering merit a separate CPU profile. Masonry's 2–4 ms measurement was not the principal measured cost. No speculative computation/cache refactor was made.

### Published-site and remote diagnostic samples

The published site transferred **1,493,548 + 1,014,764 = 2,508,312 bytes of compressed JSON bodies** (about 2.51 MB), with decoded bodies of 19,873,781 + 8,827,908 bytes (28.70 MB). ResourceTiming included approximately 300 additional transfer bytes per response. Follow-up response headers explicitly confirmed **gzip**, HTTP/2, ETags, `Vary: Accept-Encoding`, and `Cache-Control: max-age=600` for both resources. The published data revision is ahead of the local reference; these values are diagnostic and not the local equivalence baseline.

The live sequential loader measured 6,152.2 ms cold and 638.9/673.8 ms warm to map-paint. JSON request durations were 1,630.4/1,297.3 ms cold; warm map requests were 141.3/190.9 ms and paper requests 103.0/98.7 ms. Warm ResourceTiming transfer sizes were 300 bytes per file, consistent with revalidated cached bodies. Large JSON parsing was 55.4 ms cold and 44.2/43.9 ms warm; initialization was 268.9/237.5/229.3 ms. Filter latency was 153.9/141.8/139.5 ms; search was 222.5/207.8/212.5 ms.

Earlier local prototypes loading identical live URLs measured first-data-request → map-paint of 7,721.5 / 938.6 / 576.3 ms sequential versus 4,087.6 / 1,240.0 / 471.0 ms parallel. One warm parallel sample was slower. Variable network conditions, small sample size, cross-origin ResourceTiming restrictions, and the prototype's earlier error-handling implementation limit this comparison. It is not final-code deployment evidence. The final local samples above are the controlled code comparison; the live site was not changed.

An earlier candidate run overlapped public-data tests and had a 169 MB heap outlier. It is retained in evidence but excluded from the primary timing table because of CPU/GC confounding. No artificial-latency experiment or statistical benchmark campaign was completed. Three loads per variant cannot establish percentiles or a dependable improvement percentage.

## Tests and protected-contract verification

| Check executed after final application changes | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_frontend*.py'` with Node on PATH | **323 passed**, 8.210 s |
| Targeted public/export/repository/institution/data suite using existing pytest runtime | **245 passed, 22 subtests passed**, 32.48 s |
| `tests/frontend_desktop_audit.cjs` against frozen baseline | **15 width/zoom cases, 11 workflow records, 18 contract comparisons, 4 mobile checks; PASS** |
| Existing `tests/public_accessibility_browser.cjs` | **PASS** at 375, 430, 768, 1024, 1440; focus restoration, dropdown/autocomplete Escape, reduced motion, drawer, chart focus, empty-state live region, sticky toolbar |
| JavaScript syntax | **14 files passed**: all 12 `web/*.js` plus the two relevant browser test scripts |
| `git diff --check` | **Passed** |
| Protected tracked-file SHA-256 comparison with the initial manifest | **No changes** under `data/`, `web/data/`, or `scripts/` |
| Original untracked status entries | **All 89 remain present** |

The initial attempt to run pytest-based public tests through unittest could not import pytest. It was superseded by the successful pytest run using an already-installed temporary runtime; no package installation was needed. This is not an outstanding test failure.

The public/data run included: `test_public_academic_refinement.py`, `test_repository_baseline.py`, `test_public_preview_deduplication.py`, `test_public_export_metadata.py`, `test_public_export_shrinkage.py`, `test_export_performance_indexes.py`, `test_public_header_metadata.py`, `test_public_metadata_status.py`, `test_public_institution_consistency.py`, `test_public_location_display.py`, `test_public_relationship_location_completeness.py`, `test_paper_links.py`, `test_institution_display_frontend.py`, and `test_institution_location_coordinate_frontend.py`.

Baseline browser comparisons covered nine filter scenarios in both views: unfiltered; Source Attribution from 2024; Benchmark from 2023; Tsinghua University; a real unmapped paper title; Italy plus published-only; Detection/Localization plus Fully Generated; diffusion sorted by title; and an empty search. For every scenario, exact comparisons preserved displayed identities/order, filtered paper and institution-record identities, marker coordinates/radius/colors/opacity/weight, facet labels/counts/selections, URL query, citations, and BOM-prefixed CSV bytes including line endings.

Actual downloaded Source Attribution-from-2024 CSV files matched the baseline-derived export bytes: **42,980 bytes / 61 papers** and **73,044 bytes / 118 institution records**. Unfiltered exports matched at **465,267 bytes / 639 papers** and **877,017 bytes / 1,421 records**. The evidence JSON records all 18 export sizes and SHA-256 hashes.

The complete loaded/normalized records plus institution aliases, hierarchy, search relationships/index, and redirects had the same SHA-256 in both browsers:

`0eff38e58bdcd2bbe7c09a6cdf9950f2cb28de01eb66bd8187656c963db845b1`

Public file SHA-256 values remained:

- Map JSON: `4e3101e023e2d19af5989a9bb5a1cd1ca097133f2d04034a3c0ed825e98515a7`
- Paper JSON: `492874171c7cfc1c653ebe07915dcdb0973d448ed886ca3336a6563be254888b`

The loader regressions verify simultaneous starts, unchanged `no-cache` options, single-resource fallback, paper HTTP failure, and map-first handling of empty/invalid maps when the paper network/body rejects. Existing validation code remains in place; actual complete-data hashes confirm normalization equivalence. A browser-injected paper HTTP 503 displays **Data unavailable**, distinct from a valid empty result.

## Publication findings and deferred work

| Classification | Finding | Decision/reason |
| --- | --- | --- |
| Remaining confirmed readability issue | At 1280 px / 150% zoom (853 CSS px), three-digit year-bar counts remain crowded/clipped inside narrow bars; institution labels are heavily ellipsized. Full institution names remain available through existing tooltip/accessibility text. | Header-container overflow is fixed, but text inside bars needs a separate compact-chart allocation decision. No global font increase or redesign. |
| Remaining existing small-screen issue | Fixed-height chart overflow and legacy card button semantics remain when the established small-screen breakpoint activates. | Preserved under the explicit mobile constraint, including the three high-zoom matrix cases. A separate mobile accessibility task is needed. |
| Recommended enhancement | Whole-card mouse selection can leave stacked Details offscreen; the new explicit Details action reveals/focuses them. | Automatically scrolling every card/marker selection would change established behavior. The targeted explicit action is implemented. |
| Requires filtering/URL design decision | There is no dedicated unmapped-only filter. A real unmapped paper is discoverable by keyword in Unique Papers. | Adding a new filter would expand protected filtering and URL contracts; deferred. Accurate base-map messaging is implemented. |
| Confirmed existing root-URL limitation | Root redirect preserves the hash but replaces query parameters with `web/?dataset=preview`. Canonicals consistently point to `/web/`; app-generated `/web/` deep links restore correctly. | Root query forwarding changes an existing URL contract, so this subtask stops at documentation. |
| Recommended quick win | No declared favicon; the probed project `/favicon.ico` returns 404. | Reusing an appropriately sized existing mark is a small follow-up; no artwork/branding change in this pass. |
| Requires artwork/preview decision | OG/Twitter title, description and canonical metadata exist; no explicit social preview image. | Choose artwork/crop and preview format separately. |
| Recommended enhancement | Methodology and How-to-cite are available through existing help/footer/about content, but are less discoverable while browsing many results. | Consider a lightweight upper-page link in a separate change; no navigation redesign here. |
| Verified publication behavior | Public attribution, OSM credit, and data-source/manual-curation wording are present. Loading, valid-empty, unavailable-data, and unavailable-linked-paper states are separate. | Existing semantics retained; no new provenance or research claims. |
| Link-check limitation | 34 public resource/probe URLs were checked: 32 initially returned 200, favicon returned 404, and one JS request had a TLS transport error. The JS retry returned HTTP/2 200. | Availability checks are not proof that the new asset contents were deployed; query-version URLs can resolve to the old published file. Individual corpus paper links were not exhaustively checked. |
| Performance follow-up | Initial main-thread work and filter/search latency remain measurable. | Further CPU profiling before changing computation, caching, workers, or schemas. No fixed speedup claim. |

No Safari/Firefox run, formal assistive-technology audit, or WCAG certification was performed. These are coverage limits, not passing checks. No required audit work remains blocked. The optional artificial-latency experiment was not run; existing measurements and final regressions provide the documented validation.

## Exact changed files and final repository state

Nine modified tracked files:

| File | Purpose |
| --- | --- |
| `web/app.js` | Desktop interactions, year inputs, status text, Details ordering/reveal, sticky offset, skip focus, concurrent loader/error handling |
| `web/index.html` | Desktop controls/landmarks and synchronized local asset versions |
| `web/style.css` | Desktop-only control/focus/chart rules |
| `web/methodology.html` | Local stylesheet version consistency |
| `tests/test_frontend_chart_filters.py` | Updated accurate empty-map wording expectation |
| `tests/test_frontend_public_labels_layout.py` | Updated accurate empty-map wording expectation |
| `tests/test_frontend_result_cards.py` | Updated synchronized asset-version expectation |
| `tests/test_frontend_year_range_slider.py` | Keeps slider constraint tests focused while accommodating the new input-synchronization call |
| `tests/public_accessibility_browser.cjs` | Desktop Details focus expectation and configurable audit URL |

Four new files:

| File | Purpose |
| --- | --- |
| `tests/test_frontend_desktop_audit.py` | Seven focused regression tests for new behavior and loader preservation |
| `tests/frontend_desktop_audit.cjs` | Real browser zoom, discovery workflow, baseline contract and mobile preservation checks |
| `docs/desktop_frontend_audit_2026_10_10.md` | This report |
| `docs/desktop_frontend_audit_2026_10_10.json` | Browser results, raw timing samples, public checks, logs, source hashes, final status, and measurement source |

Final status: **9 modified tracked files, 4 new audit files, and the 89 pre-existing untracked entries** (93 untracked status entries total). Nothing staged; no tracked files deleted. Full status is in the evidence JSON. No files in protected data or preprocessing paths changed. No merge, rebase, reset, stash, checkout, commit, push, or deployment was performed.

For reproduction, the browser regression accepts `AUDIT_URL`, `BASELINE_URL`, `AUDIT_OUTPUT`, and `CHROME_EXECUTABLE`, and uses an existing Playwright installation. Both compared trees were served through Python's standard static HTTP server on `127.0.0.1:8873`; this is test infrastructure, not an application backend. The measurement source and raw results are embedded in the evidence JSON so the temporary probe remains reviewable without adding a repository performance framework.
