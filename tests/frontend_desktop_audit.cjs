/* Run with an existing Playwright installation; no application dependency.
 * AUDIT_URL=http://127.0.0.1:8873/candidate/web/ BASELINE_URL=.../baseline/web/
 * AUDIT_OUTPUT=/tmp/sirm-audit node tests/frontend_desktop_audit.cjs
 * CHROME_EXECUTABLE can select a local Chrome. Uses a disposable profile.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const url = process.env.AUDIT_URL || 'http://127.0.0.1:8873/candidate/web/';
const baselineUrl = process.env.BASELINE_URL;
const output = process.env.AUDIT_OUTPUT || fs.mkdtempSync(path.join(os.tmpdir(), 'sirm-desktop-results-'));
fs.mkdirSync(output, {recursive:true});
const report = {matrix:[], workflows:[], contracts:[], mobile:[], errors:[]};
const hash = text => crypto.createHash('sha256').update(text).digest('hex');
const ready = page => page.waitForFunction(() => urlStateReady && (!resultsPipeline || !resultsPipeline.isPreparing));
const settle = page => page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
async function restore(page, query = '') {
  await page.evaluate(query => { history.replaceState(null, '', location.pathname + query); restoreViewStateFromLocation(); }, query);
  await ready(page); await settle(page);
}
async function snapshot(page) {
  return page.evaluate(() => ({
    ids:currentDisplayedResults.map(r => [paperIdentity(r), institutionIdentity(r), markerInstitutionIdentity(r)]),
    papers:currentFilteredPaperRecords.map(paperIdentity),
    records:currentFilteredRecords.map(r => [paperIdentity(r), markerInstitutionIdentity(r)]),
    markers:visibleMarkerEntries.map(e => ({key:e.institutionKey, count:e.paperCount, task:e.taskKey,
      radius:e.marker.options.radius, color:e.marker.options.color, fillColor:e.marker.options.fillColor,
      weight:e.marker.options.weight, opacity:e.marker.options.opacity, fillOpacity:e.marker.options.fillOpacity,
      latlng:e.marker.getLatLng()})),
    facets:[taskFilter,imageScopeFilter,entryTypeFilter,venueFilter,venueTypeFilter,countryFilter,
      institutionTypeFilter,preprintFilter,publishedOnlyFilter].map(s => [...s.options].map(o => [o.value,o.text,o.selected])),
    csv:'\ufeff' + buildCsv(currentDisplayedResults, resultsView === 'papers' ? PAPER_CSV_COLUMNS : INSTITUTION_CSV_COLUMNS),
    citations:currentFilteredPaperRecords.map(paperCitation),
    search:location.search,
  }));
}
async function chooseFacet(page, id, label) {
  await page.locator(`#${id}-dropdown-button`).click();
  await page.locator(`#${id}-dropdown-options`).getByRole('option', {name:new RegExp(label)}).click();
  await page.keyboard.press('Escape'); await ready(page);
}
async function loadedDataHash(page) {
  return page.evaluate(async () => {
    const bytes = new TextEncoder().encode(JSON.stringify({records,paperRecords,
      institutionAliases,institutionHierarchy,institutionSearchRelationships,
      canonicalInstitutionSearchIndex,institutionIdRedirects}));
    const digest = await window.crypto.subtle.digest('SHA-256', bytes);
    return [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2,'0')).join('');
  });
}
(async () => {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'sirm-desktop-chrome-'));
  const context = await chromium.launchPersistentContext(profile, {
    executablePath:process.env.CHROME_EXECUTABLE || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless:true, viewport:{width:1440,height:900}, acceptDownloads:true,
  });
  try {
    report.browser = context.browser().version();
    const settings = await context.newPage();
    await settings.goto('chrome://settings/appearance');
    await settings.locator('#zoomLevel').waitFor();
    await settings.locator('#zoomLevel').selectOption('1');
    const page = await context.newPage();
    page.on('pageerror', e => report.errors.push(e.message));
    await page.goto(url); await ready(page);
    // Real Chrome default page zoom, not CSS zoom or pinch scaling.
    for (const width of [1024,1200,1280,1440,1920]) {
      await page.setViewportSize({width,height:900});
      for (const zoom of ['1','1.25','1.5']) {
        await settings.locator('#zoomLevel').selectOption(zoom);
        await restore(page); await page.evaluate(() => window.scrollTo(0,0));
        await page.waitForTimeout(180);
        const layout = await page.evaluate(() => ({
          cssWidth:innerWidth,cssHeight:innerHeight,dpr:devicePixelRatio,mobile:mobileFiltersMedia.matches,
          header:document.querySelector('.site-header').getBoundingClientRect().height,
          filterTop:parseFloat(getComputedStyle(filtersPanel).top),
          overflow:document.documentElement.scrollWidth > innerWidth + 1,
          mapWidth:mapElement.getBoundingClientRect().width,
          clippedCharts:[...document.querySelectorAll('.header-chart')].filter(e =>
            e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1).map(e => e.className),
        }));
        assert.equal(layout.overflow, false, `${width}/${zoom}: page overflow`);
        assert(Math.abs(layout.dpr - Number(zoom)) < 0.01);
        if (!layout.mobile) {
          assert(layout.filterTop >= layout.header - 1, `${width}/${zoom}: filters underneath header`);
          assert.deepEqual(layout.clippedCharts, [], `${width}/${zoom}: chart clipping`);
          assert.equal(await page.locator('#results-list > [role="button"]').count(), 0);
          assert.equal(await page.locator('#results-list [role="button"] :is(a,button)').count(), 0);
          await page.locator('.desktop-skip-navigation a[href="#paper-results"]').focus();
          await page.keyboard.press('Enter');
          assert.equal(await page.evaluate(() => document.activeElement.id), 'paper-results');
          const skipTop = await page.locator('#paper-results').evaluate(e => e.getBoundingClientRect().top);
          assert(skipTop >= layout.header - 1, `Results skip target obscured at ${width}/${zoom}: ${skipTop} vs ${layout.header}`);
          await page.evaluate(() => window.scrollBy(0,240)); await settle(page);
          const toolbar = await page.locator('.results-heading-row').evaluate(e => e.getBoundingClientRect().toJSON());
          assert(toolbar.top >= layout.header - 1 && toolbar.bottom < layout.cssHeight,
            `${width}/${zoom}: sticky results toolbar obscured`);
          const action = page.locator('.result-details-action').first();
          await action.focus(); await page.keyboard.press('Enter'); await settle(page);
          assert.equal(await page.evaluate(() => document.activeElement.id), 'paper-details-heading');
          const detailTop = await page.locator('#paper-details-heading').evaluate(e => e.getBoundingClientRect().top);
          assert(detailTop >= layout.header - 1 && detailTop < layout.cssHeight, 'Details focus outside visible viewport');
          const hierarchy = await page.locator('#paper-details-content').evaluate(e =>
            [...e.children].map(n => n.className));
          assert(hierarchy.indexOf('paper-details-links') < hierarchy.findIndex(c => c.includes('paper-details-authors')));
          assert.equal(await page.locator('#paper-details-content > .paper-details-links').count(), 1);
          assert(await page.locator('.result-item[aria-current="true"]').count() > 0);
          // Closing and reopening preserves the existing wide-desktop selection behavior.
          if (layout.cssWidth > 1250) {
            const identity = await page.evaluate(() => interactionState.selectedPaperId);
            await page.locator('#close-paper-details').click();
            assert.equal(await page.evaluate(() => interactionState.selectedPaperId), identity);
            await page.locator('#open-paper-details').click();
            assert.equal(await page.evaluate(() => document.activeElement.id), 'close-paper-details');
          }
          await page.locator('.desktop-skip-navigation a[href="#research-map"]').focus();
          await page.keyboard.press('Enter');
          assert.equal(await page.evaluate(() => document.activeElement.id), 'research-map');
        } else {
          assert.equal(await page.locator('.desktop-year-controls').isVisible(), false);
          assert.equal(await page.locator('.desktop-skip-navigation').isVisible(), false);
        }
        await page.screenshot({path:path.join(output, `desktop-${width}-${zoom}.png`)});
        report.matrix.push({width,zoom:Number(zoom),...layout});
      }
    }
    await settings.locator('#zoomLevel').selectOption('1');
    await page.setViewportSize({width:1440,height:1000}); await restore(page);
    // Precise year input is a draft until Enter/blur; slider and chart reuse that state.
    const initialSearch = await page.evaluate(() => location.search);
    await page.locator('#year-start-input').fill('20');
    assert.equal(await page.evaluate(() => location.search), initialSearch);
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#year-start-input').getAttribute('aria-invalid'), 'true');
    assert.equal(await page.evaluate(() => location.search), initialSearch);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#year-start-input').inputValue(), '2018');
    for (const invalid of ['2017','2028','']) {
      await page.locator('#year-start-input').fill(invalid); await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => location.search), initialSearch);
      assert.equal(await page.locator('#year-start-input').getAttribute('aria-invalid'), 'true');
    }
    await page.locator('#year-start-input').fill('2024'); await page.keyboard.press('Enter'); await ready(page);
    assert.equal(await page.locator('#min-year-filter').inputValue(), '2024');
    const yearUrl = await page.evaluate(() => location.search);
    await page.locator('#min-year-filter').focus(); await page.keyboard.press('ArrowRight'); await ready(page);
    assert.equal(await page.locator('#year-start-input').inputValue(), '2025');
    await page.goBack(); await ready(page);
    assert.equal(await page.locator('#year-start-input').inputValue(), '2024');
    assert.equal(await page.evaluate(() => location.search), yearUrl);
    await page.goForward(); await ready(page);
    assert.equal(await page.locator('#year-start-input').inputValue(), '2025');
    await page.locator('.year-chart-item[data-chart-value="2026"]').click(); await ready(page);
    assert.equal(await page.locator('#year-start-input').inputValue(), '2026');
    assert.equal(await page.locator('#year-end-input').inputValue(), '2026');
    report.workflows.push('Year drafts, invalid input, slider keyboard, chart, back/forward');
    await restore(page);
    await chooseFacet(page, 'task-filter', 'Source Attribution');
    await page.locator('#year-start-input').fill('2024'); await page.keyboard.press('Enter'); await ready(page);
    assert(await page.evaluate(() => currentFilteredPaperRecords.length > 0 && currentFilteredPaperRecords.every(r => getTasks(r).includes('source_attribution') && publicationYear(r) >= 2024)));
    report.workflows.push('Recent Source Attribution');
    await restore(page);
    await chooseFacet(page, 'research-type-filter', 'Benchmark');
    await page.locator('#year-start-input').fill('2024'); await page.keyboard.press('Enter'); await ready(page);
    assert(await page.evaluate(() => currentFilteredPaperRecords.length > 0 && currentFilteredPaperRecords.every(r => getPaperCategories(r).includes('benchmark') && publicationYear(r) >= 2024)));
    report.workflows.push('Benchmark + Publication Year');
    await restore(page);
    await page.locator('#keyword-filter').fill('Tsinghua University'); await ready(page); await settle(page);
    assert(await page.evaluate(() => currentFilteredPaperRecords.length > 0));
    await page.locator('.result-details-action').first().click();
    assert(await page.locator('#paper-details-content .paper-details-links a').count() > 0);
    const link = page.locator('#paper-details-content .paper-details-links a').first();
    const popupPromise = context.waitForEvent('page'); await link.click(); const popup = await popupPromise;
    assert(popup.url() === 'about:blank' || /^https?:/.test(popup.url())); await popup.close();
    report.workflows.push('University search, Details, external paper link opens separately');
    // Capture the actual clipboard write rather than mutate the system clipboard.
    await page.evaluate(() => { window.auditCopied = ''; Object.defineProperty(navigator, 'clipboard', {configurable:true,value:{writeText:async text => {window.auditCopied=text}}}); });
    await page.locator('#copy-view-link').click();
    const copied = await page.evaluate(() => window.auditCopied);
    assert(copied.includes('keyword=Tsinghua'));
    const beforeDeep = await snapshot(page);
    await page.goto(copied); await ready(page);
    assert.deepEqual(await snapshot(page), beforeDeep);
    report.workflows.push('Copy filtered deep link and restore selection, ordering, CSV and facets');
    await restore(page);
    await page.locator('.result-item [data-focus-institution]:not([disabled])').first().click();
    assert.equal(await page.evaluate(() => interactionState.detailMode), 'paper');
    assert(await page.evaluate(() => Boolean(interactionState.contextualInstitutionId)));
    await page.locator('.desktop-skip-navigation a[href="#research-map"]').focus();
    await page.keyboard.press('Enter');
    await page.locator('.leaflet-interactive[tabindex="0"]').first().focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => interactionState.detailMode), 'institution-papers');
    const parent = await page.evaluate(() => interactionState.pinnedMapMarkerId);
    await page.locator('[data-marker-paper]').first().click();
    assert.equal(await page.evaluate(() => interactionState.mapParentMarkerId), parent);
    assert(await page.locator('.leaflet-interactive.is-paper-pinned').count() > 0);
    await page.locator('[data-back-to-institution]').click();
    assert.equal(await page.evaluate(() => interactionState.detailMode), 'institution-papers');
    report.workflows.push('Institution control → marker papers → paper → Back to institution');
    const unmapped = await page.evaluate(() => paperRecords.find(r => !mapRecordsByPaperIdentity.has(paperIdentity(r))));
    assert(unmapped, 'Need a real unmapped paper fixture');
    const unmappedQuery = await page.evaluate(r => recordTitle(r), unmapped);
    await restore(page, '?keyword=' + encodeURIComponent(unmappedQuery));
    assert.match(await page.locator('#map-status').innerText(), /matching unique paper.*no mapped institution/);
    assert(await page.locator('.result-details-action').count() > 0);
    await page.locator('[data-results-view="institutions"]').click(); await ready(page);
    assert(await page.locator('#results-empty').isVisible());
    assert.match(await page.locator('#map-status').innerText(), /matching unique paper/);
    await page.locator('[data-results-view="papers"]').click(); await ready(page);
    report.workflows.push('Real unmapped paper, both views, accurate empty-map message');
    await restore(page, '?keyword=__no_such_paper_audit__');
    assert.equal(await page.locator('#map-status').innerText(), 'No unique papers match the current filters.');
    // Independent native links/author toggles must not select a paper.
    await restore(page);
    const toggle = page.locator('.result-item .paper-authors-toggle').first();
    if (await toggle.count()) { await toggle.click(); assert.equal(await toggle.getAttribute('aria-expanded'), 'true'); }
    assert.equal(await page.evaluate(() => interactionState.selectedPaperId), null);
    const cardPopupPromise = context.waitForEvent('page');
    await page.locator('.result-item .result-links a').first().click();
    const cardPopup = await cardPopupPromise; await cardPopup.close();
    assert.equal(await page.evaluate(() => interactionState.selectedPaperId), null);
    await page.locator('.result-item .result-title').first().click();
    assert(await page.evaluate(() => Boolean(interactionState.selectedPaperId)));
    report.workflows.push('Whole-card selection; independent nested controls');
    for (const view of ['papers','institutions']) {
      await restore(page, '?tasks=source_attribution&year_start=2024&view=' + view);
      const expected = (await snapshot(page)).csv;
      const downloadPromise = page.waitForEvent('download'); await page.locator('#export-csv').click();
      const download = await downloadPromise; const bytes = fs.readFileSync(await download.path());
      assert.deepEqual(bytes, Buffer.from(expected));
      report.workflows.push(`Downloaded ${view} CSV matches the authoritative export bytes (${bytes.length} bytes)`);
    }
    if (baselineUrl) {
      const baseline = await context.newPage(); await baseline.goto(baselineUrl); await ready(baseline);
      const beforeHash = await loadedDataHash(baseline), afterHash = await loadedDataHash(page);
      assert.equal(afterHash, beforeHash, 'Loaded/normalized data changed');
      report.loadedDataSha256 = afterHash;
      const queries = ['', '?tasks=source_attribution&year_start=2024', '?research_types=benchmark&year_start=2023',
        '?keyword=Tsinghua%20University', '?keyword=' + encodeURIComponent(unmappedQuery),
        '?country=Italy&published_only=published-only', '?tasks=detection,localization&image_scopes=fully_generated',
        '?keyword=diffusion&sort=title-asc', '?keyword=__no_such_paper_audit__'];
      for (const query of queries) for (const view of ['papers','institutions']) {
        const q = query + (query ? '&' : '?') + 'view=' + view;
        await restore(baseline,q); await restore(page,q);
        const before = await snapshot(baseline), after = await snapshot(page);
        assert.deepEqual(after,before, `Protected contract changed: ${q}`);
        report.contracts.push({query:q,rows:after.ids.length,csvBytes:Buffer.byteLength(after.csv),sha256:hash(after.csv)});
      }
      // These are preservation checks, not mobile design changes.
      for (const width of [390,683,800,820]) {
        const frames=[];
        for (const p of [baseline,page]) {
          await p.setViewportSize({width,height:900}); await restore(p); await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(180);
          frames.push(await p.evaluate(() => ({
            rects:['.site-header','#map','#paper-details','.results-heading-row','.result-item'].map(s => {
              const r=document.querySelector(s).getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(v=>Math.round(v));}),
            role:document.querySelector('.result-item').getAttribute('role'),
            tabIndex:document.querySelector('.result-item').tabIndex,
          })));
          await p.locator('#mobile-filters-trigger').click();
          assert.equal(await p.locator('#filters-panel').getAttribute('aria-modal'),'true');
          await p.keyboard.press('Escape');
          assert.equal(await p.evaluate(()=>document.activeElement.id),'mobile-filters-trigger');
        }
        assert.deepEqual(frames[1],frames[0],`Mobile geometry/semantics changed at ${width}`);
        report.mobile.push({width,geometryIdentical:true,drawerKeyboard:true});
      }
      await baseline.close();
    }
    const failure = await context.newPage();
    await failure.route('**/public_preview_papers.json', route => route.fulfill({status:503,body:'Unavailable'}));
    await failure.goto(url); await failure.waitForFunction(() => document.querySelector('#results-count').textContent === 'Data unavailable');
    assert.match(await failure.locator('#map-status').innerText(), /Unable to load public data/);
    await failure.close(); report.workflows.push('Paper-data HTTP failure stays distinct from zero results');
    assert.deepEqual(report.errors, []);
    report.result = 'PASS';
  } finally {
    fs.writeFileSync(path.join(output,'desktop-audit.json'),JSON.stringify(report,null,2));
    await context.close();
  }
  console.log(JSON.stringify({result:report.result,matrix:report.matrix.length,workflows:report.workflows.length,
    contractComparisons:report.contracts.length,mobile:report.mobile.length,output}));
})().catch(error => { console.error(error); process.exitCode=1; });
