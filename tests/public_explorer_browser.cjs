// Run against a repository-root static server on port 8899.
const {chromium} = require('/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert = require('node:assert/strict');
const base = process.env.PUBLIC_EXPLORER_URL || 'http://127.0.0.1:8899/web/';

(async () => {
  const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
  try {
    const context = await browser.newContext({permissions:['clipboard-read','clipboard-write']});
    const page = await context.newPage({viewport:{width:1440,height:1100}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const ready = () => page.waitForFunction(() => !keywordFilter.disabled && resultsList.getAttribute('aria-busy') === 'false');
    const visit = async (query = '') => { await page.goto(base + query); await ready(); };
    const choose = async (id,value) => {
      const field = page.locator('[data-filter-dropdown]').filter({has:page.locator('#'+id)});
      await field.locator('button').first().click();
      await field.locator(`[data-filter-value="${value}"]`).click();
      await ready();
      if (await field.locator('button').first().getAttribute('aria-expanded') === 'true') {
        await field.locator('button').first().press('Escape');
      }
    };
    const facets = () => page.evaluate(() => {
      const controls = [taskFilter,imageScopeFilter,entryTypeFilter,publishedOnlyFilter,
        venueTypeFilter,venueFilter,countryFilter,institutionTypeFilter,preprintFilter];
      return Object.fromEntries(controls.map(control => [control.id,
        [...control.options].map(option => [option.value,option.textContent,option.selected])]));
    });
    // Independently compare each count with the results from selecting that option.
    // Do not render or change history while probing; restore the native selections.
    const auditCounts = async label => {
      const result = await page.evaluate(() => {
        const controls = [taskFilter,imageScopeFilter,entryTypeFilter,publishedOnlyFilter,
          venueTypeFilter,venueFilter,countryFilter,institutionTypeFilter,preprintFilter];
        const indexes = institutionFilterIndexes();
        const expanded = identities => institutionIdentitiesWithSearchExpansion(
          identities,indexes.hierarchy,indexes.searchRelationships);
        const resolvedInstitutionIdentities = expanded(resolveInstitutionSearchIdentities(
          normalizedSearchText(keywordFilter.value),indexes.search));
        const activeInstitutionIdentities = expanded(new Set(activeInstitutionFilter ? [activeInstitutionFilter.identity] : []));
        const terms = PaperSearchHelpers.queryTerms(keywordFilter.value,normalizedSearchText);
        const options = {resolvedInstitutionIdentities,activeInstitutionIdentities};
        const failures = [];
        let checked = 0;
        for (const control of controls) {
          const selected = [...control.options].map(option => option.selected);
          for (const option of [...control.options].filter(option => option.value !== 'all')) {
            const actual = Number(option.textContent.match(/\((\d+)\)$/)?.[1]);
            [...control.options].forEach(candidate => { candidate.selected = candidate === option; });
            const expected = deriveFilteredRecordSets(records,paperRecords,
              record => recordMatchesActiveFilters(record,terms,{...options,institutionRecord:true}),
              record => recordMatchesActiveFilters(record,terms,options)).filteredPapers.length;
            if (actual !== expected) failures.push({facet:control.id,value:option.value,actual,expected});
            checked++;
          }
          [...control.options].forEach((option,i) => { option.selected = selected[i]; });
        }
        return {checked,failures};
      });
      assert.deepEqual(result.failures,[],label);
      console.log(`${label}: ${result.checked} facet options match unique-paper results`);
    };
    await visit();
    assert(await page.locator('#workspace-filter-context').isHidden());
    const initial = await facets();
    await auditCounts('No filters');
    await choose('task-filter','source_attribution');
    const one = await facets();
    assert.deepEqual(one['task-filter'].map(row=>row.slice(0,2)),initial['task-filter'].map(row=>row.slice(0,2)));
    await auditCounts('One task');
    await choose('task-filter','detection');
    await auditCounts('Multiple tasks');
    await choose('research-type-filter','benchmark');
    await page.locator('#more-filters-toggle').click();
    await choose('country-filter','Italy');
    await auditCounts('Tasks + benchmark + Italy');
    const multi = await facets();
    const multiContext = await page.locator('#workspace-filter-button').textContent();
    await page.locator('#copy-view-link').click();
    const copied = await page.evaluate(() => navigator.clipboard.readText());
    await page.goto(copied); await ready();
    assert.deepEqual(await facets(),multi);
    assert.equal(await page.locator('#workspace-filter-button').textContent(),multiContext);
    await auditCounts('Copied link');
    await choose('country-filter','China');
    const changed = await facets();
    await page.goBack(); await ready();
    assert.deepEqual(await facets(),multi);
    await page.goForward(); await ready();
    assert.deepEqual(await facets(),changed);
    await auditCounts('History forward');
    await page.locator('#keyword-filter').fill('zzzz-no-such-paper-zzzz');
    await page.waitForFunction(() => currentFilteredPaperRecords.length === 0 && resultsList.getAttribute('aria-busy') === 'false');
    assert.equal(await page.locator('#country-filter').inputValue(),'China');
    assert.equal(await page.locator('#research-type-filter').inputValue(),'benchmark');
    await auditCounts('Zero-result keyword combination');
    for (const [id,rows] of Object.entries(await facets())) {
      assert.deepEqual(rows.map(row=>row[0]).sort(),initial[id].map(row=>row[0]).sort(),`${id} removed zero options`);
    }
    await visit('?venue=venue:cvpr&publication_type=journal&country=Italy');
    assert.equal(await page.locator('#venue-filter').inputValue(),'venue:cvpr');
    assert.equal(await page.locator('#venue-type-filter').inputValue(),'journal');
    assert.equal(await page.evaluate(() => currentFilteredPaperRecords.length),0);
    await auditCounts('Incompatible venue/type retained');

    // Explicit navigation, with all semantic state left intact.
    const viewport = () => page.evaluate(() => ({center:map.getCenter(),zoom:map.getZoom()}));
    const assertViewportRetained = async (before,message) => {
      const change = await page.evaluate(before => ({zoom:map.getZoom(),
        drift:map.project(map.getCenter()).distanceTo(map.project(before.center))}),before);
      assert.equal(change.zoom,before.zoom,message);
      // Leaflet invalidateSize can round the center by a pixel as context appears.
      assert(change.drift <= 1.5,message);
    };
    const assertNormalMinZoom = () => page.waitForFunction(() => (
      Math.abs(map.getMinZoom() - noWrapMinZoomForWidth(map.getSize().x)) < 0.000001
    ));
    const semantic = () => page.evaluate(() => ({url:location.href,state:currentViewState(),
      ids:currentDisplayedResults.map(paperIdentity),selectedPaper:interactionState.selectedPaperId,
      detailMode:interactionState.detailMode,details:paperDetailsContent.innerHTML}));
    const assertFitted = async () => {
      const state = await semantic();
      await page.locator('#fit-map-results').click();
      assert.deepEqual(await semantic(),state);
      assert(await page.evaluate(() => visibleMarkerEntries.every(({marker}) => map.getBounds().contains(marker.getLatLng()))));
    };
    await visit();
    await assertFitted();
    await page.evaluate(() => window.dispatchEvent(new Event('resize')));
    await assertNormalMinZoom();
    await assertFitted();
    await choose('task-filter','detection');
    await assertNormalMinZoom();
    await visit();
    await page.locator('#reset-map-world').click();
    const world = await viewport();
    await page.evaluate(() => map.setView([42,12],5,{animate:false}));
    const panned = await viewport();
    await choose('task-filter','source_attribution');
    await assertViewportRetained(panned,'Filtering must not refit the map');
    await visit('?country=Italy');
    assert(await page.evaluate(() => visibleMarkerEntries.length > 1));
    await assertFitted();
    const state = await semantic();
    await page.locator('#reset-map-world').click();
    assert.deepEqual(await semantic(),state);
    await assertViewportRetained(world,'Reset world restores the default viewport');
    await assertNormalMinZoom();
    await visit();
    const single = await page.evaluate(() => {
      const entry = visibleMarkerEntries.find(({institutionKey}) => institutionKey.startsWith('id:'));
      return {identity:institutionIdentity(entry.record),label:recordInstitution(entry.record)};
    });
    await visit('?institution='+encodeURIComponent(single.identity)+'&institution_label='+encodeURIComponent(single.label));
    assert.equal(await page.evaluate(() => visibleMarkerEntries.length),1);
    const singleMarker = page.locator('#map .leaflet-interactive').first();
    await singleMarker.focus(); await singleMarker.press('Enter');
    await page.waitForFunction(() => interactionState.detailMode === 'institution-papers');
    await assertFitted();
    assert(await page.evaluate(() => map.getZoom() <= 8));
    const pinnedState = await semantic();
    await page.locator('#reset-map-world').click();
    assert.deepEqual(await semantic(),pinnedState);
    await assertNormalMinZoom();
    await auditCounts('Institution context');
    await visit('?keyword=zzzz-no-such-paper-zzzz');
    assert(await page.locator('#fit-map-results').isDisabled());
    const emptyViewport = await viewport();
    await page.evaluate(() => fitMapResults());
    assert.deepEqual(await viewport(),emptyViewport);
    await visit();
    const unmappedQuery = await page.evaluate(() => {
      const mapped = new Set(records.map(paperIdentity));
      const paper = paperRecords.find(record => !mapped.has(paperIdentity(record)));
      return paper && (paper.doi || TitleMarkup.plainText(recordTitle(paper)));
    });
    assert(unmappedQuery,'Expected a standalone paper fixture');
    await visit('?keyword='+encodeURIComponent(unmappedQuery));
    assert(await page.evaluate(() => currentFilteredPaperRecords.length > 0 && visibleMarkerEntries.length === 0));
    assert(await page.locator('#fit-map-results').isDisabled());

    // Interaction and responsive checks include a long current-view context.
    for (const width of [375,768,1024,1440,1920]) {
      await page.setViewportSize({width,height:1100});
      await assertNormalMinZoom();
      await visit('?tasks=detection,source_attribution&research_types=benchmark&year_start=2024&country=Italy');
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      const contextBox = await page.locator('#workspace-filter-button').boundingBox();
      assert(contextBox.height <= 44);
      await assertFitted();
      assert.match(await page.locator('#workspace-filter-button').textContent(),/\+2 filters/);
      await page.locator('#workspace-filter-button').focus();
      await page.locator('#workspace-filter-button').press('Enter');
      assert.equal(await page.evaluate(() => document.activeElement.id),'filters-heading');
      if (width <= 820) {
        assert.equal(await page.locator('#filters-panel').getAttribute('aria-modal'),'true');
        await page.locator('#close-filters').click();
      }
      await page.locator('#workspace-filter-clear').click(); await ready();
      assert(await page.locator('#workspace-filter-context').isHidden());
      assert.equal(new URL(page.url()).searchParams.get('country'),null);
      await assertFitted();
      await page.locator('#reset-map-world').click();
      await assertNormalMinZoom();
      await page.evaluate(() => scrollTo(0,0));
      await page.waitForFunction(() => [...document.querySelectorAll('#map img.leaflet-tile')]
        .every(img => img.complete && img.naturalWidth > 0 && Number(getComputedStyle(img).opacity) >= 0.99));
      await page.screenshot({path:`/tmp/sif-explorer-final-${width}.png`,animations:'disabled'});
      const card = page.locator('.result-card-paper').first();
      assert.equal(await card.locator('.result-entity-kicker').count(),0);
      const order = await card.evaluate(el => ['.result-title','.result-authors','.result-venue-year',
        '.result-badges','.result-paper-institutions','.result-links'].map(selector => el.querySelector(selector)?.getBoundingClientRect().top));
      assert.deepEqual(order,order.slice().sort((a,b)=>a-b));
      await page.locator('[data-results-view="institutions"]').click(); await ready();
      assert.equal(await page.locator('.result-card-institution .result-entity-kicker').first().textContent(),'Institution record');
      console.log(`${width}px: no overflow, context focus/clear and both card views passed`);
    }
    const touch = await browser.newContext({viewport:{width:375,height:900},hasTouch:true,isMobile:true});
    const mobile = await touch.newPage();
    await mobile.goto(base+'?tasks=detection');
    await mobile.waitForFunction(() => !keywordFilter.disabled && resultsList.getAttribute('aria-busy') === 'false');
    const targets = await mobile.locator('.map-navigation button,.workspace-filter-context button').evaluateAll(
      buttons=>buttons.map(button=>button.getBoundingClientRect().height));
    assert(targets.every(height=>height>=44));
    assert(await mobile.evaluate(() => document.documentElement.scrollWidth<=innerWidth));
    await touch.close();
    assert.deepEqual(errors,[]);
    console.log('Map navigation, history, card hierarchy, touch targets and runtime checks passed');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
