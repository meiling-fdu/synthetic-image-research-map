// Read-only smoke checks against current public data. Start a static server first.
// NODE_PATH must resolve playwright; CHROME_EXECUTABLE is optional.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.PUBLIC_PREVIEW_URL || 'http://127.0.0.1:8899';

(async () => {
  const browser = await chromium.launch({
    headless: true, executablePath: process.env.CHROME_EXECUTABLE || undefined,
  });
  try {
    for (const width of [1440, 375]) {
      const page = await browser.newPage({viewport: {width, height: 1000}, hasTouch: width === 375});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const ready = () => page.waitForFunction(() =>
        !document.querySelector('#keyword-filter').disabled
        && resultsKeywordFrame === null
        && document.querySelector('#results-list').getAttribute('aria-busy') === 'false');
      const load = async (query = '') => { await page.goto(base + '/' + query); await ready(); };
      const filters = async () => {
        if (width <= 820 && !await page.locator('#filters-panel').evaluate(e => e.classList.contains('is-open')))
          await page.locator('#mobile-filters-trigger').click();
      };
      const done = async () => {
        if (width <= 820 && await page.locator('#filters-panel').evaluate(e => e.classList.contains('is-open')))
          await page.locator('#done-filters').click();
      };
      const dropdown = async (id, value) => {
        await filters();
        const field = page.locator('[data-filter-dropdown]').filter({has: page.locator('#' + id)});
        await field.locator('button').first().click();
        await field.locator('[data-filter-value="' + value + '"]').click();
        await ready();
      };
      const search = async value => {
        await filters(); await page.locator('#keyword-filter').fill(value);
        // Filtered identities update before the asynchronous card render finishes.
        await ready();
      };
      const reset = async () => {
        await filters(); await page.locator('#reset-filters').click(); await ready();
        await page.waitForFunction(() => currentFilteredPaperRecords.length === 620);
      };
      await load();
      assert.equal(await page.evaluate(() => currentFilteredPaperRecords.length), 620);
      assert(await page.locator('#map .leaflet-interactive').count() > 0);
      await dropdown('published-only-filter', 'published-only');
      await page.waitForFunction(() => currentFilteredPaperRecords.length === 520);
      assert.equal(new URL(page.url()).searchParams.get('published_only'), '1');
      await page.locator('#more-filters-toggle').click();
      assert.equal(await page.locator('#more-filters-toggle').getAttribute('aria-expanded'), 'true');
      await page.locator('#more-filters-toggle').click();
      assert.equal(await page.locator('#more-filters-toggle').getAttribute('aria-expanded'), 'false');
      await dropdown('task-filter', 'localization');
      await page.waitForFunction(() => currentFilteredPaperRecords.length > 0
        && currentFilteredPaperRecords.every(record => getTasks(record).includes('localization')));
      await page.locator('#keyword-filter').press('Escape');
      await reset();
      const samples = await page.evaluate(() => ({
        author: recordAuthors(paperRecords.find(record => recordAuthors(record).length))[0],
        institution: recordInstitution(visibleMarkerEntries[0].record),
        // A direct parent affiliation correctly suppresses descendant provenance.
        // This reviewed laboratory has a descendant-only public paper match.
        parent: institutionHierarchy.find(edge => edge.review_status === 'confirmed'
          && edge.child_institution_name === 'Observatory on Social Media').parent_institution_name,
        markerless: (() => {
          const record = paperRecords.find(record => !record.has_map_location);
          return {id: paperIdentity(record), title: recordTitle(record)};
        })(),
      }));
      await search('image');
      await page.locator('#keyword-suggestions [aria-label="Papers"] [role="option"]').first().click();
      await page.waitForFunction(() => interactionState.detailMode === 'paper');
      assert(await page.locator('#paper-details').isVisible());
      assert(new URL(page.url()).searchParams.get('paper'));
      await reset();
      await search(samples.author);
      await page.locator('#keyword-suggestions [aria-label="Authors"] [role="option"]').first().click();
      await page.waitForFunction(() => currentFilteredPaperRecords.length > 0 && currentFilteredPaperRecords.length < 620);
      assert.equal(await page.locator('#keyword-filter').inputValue(), samples.author);
      await reset();
      await search(samples.institution);
      await page.locator('#keyword-suggestions [aria-label="Institutions"] [role="option"]').first().click();
      await page.waitForFunction(() => interactionState.detailMode === 'institution-papers');
      assert(await page.locator('#paper-details').isVisible());
      await reset();
      await search(samples.parent);
      await page.locator('#keyword-filter').press('Escape');
      await done();
      await page.waitForSelector('.result-institution-match-context');
      const provenance = await page.locator('.result-institution-match-context').first().innerText();
      assert(provenance.includes('Matched via') && provenance.includes(samples.parent));
      await reset(); await done();
      const marker = page.locator('#map .leaflet-interactive').first();
      await marker.focus(); await marker.press('Enter');
      await page.waitForFunction(() => interactionState.detailMode === 'institution-papers');
      await page.locator('[data-marker-paper]').first().click();
      await page.waitForFunction(() => interactionState.detailMode === 'paper');
      assert(await page.locator('#paper-details').isVisible());
      await reset();
      await search('zzzz-baseline-no-results-zzzz'); await done();
      await page.waitForFunction(() => currentFilteredPaperRecords.length === 0);
      await page.locator('#clear-empty-filters').click();
      await page.waitForFunction(() => currentFilteredPaperRecords.length === 620);
      await page.locator('[data-results-view="papers"]').click();
      await search(samples.markerless.title); await done();
      await page.waitForFunction(id => currentFilteredPaperRecords.some(record => paperIdentity(record) === id), samples.markerless.id);
      await page.waitForFunction(() => currentDisplayedResults.length > 0 && currentDisplayedResults.length < 620);
      assert((await page.locator('#results-list').innerText()).includes(samples.markerless.title));
      await load('?view=papers&paper=' + encodeURIComponent(samples.markerless.id));
      await page.waitForFunction(id => interactionState.selectedPaperId === id, samples.markerless.id);
      assert(await page.locator('#paper-details').isVisible());
      await load('?keyword=zzzz-baseline-no-results-zzzz&paper=' + encodeURIComponent(samples.markerless.id));
      await page.waitForFunction(() => currentFilteredPaperRecords.length === 0);
      assert.equal(await page.evaluate(() => interactionState.selectedPaperId), samples.markerless.id);
      assert(await page.locator('#paper-details').isVisible());
      await load('?paper=missing-baseline-paper');
      assert((await page.locator('#paper-details').innerText()).includes('Linked paper unavailable'));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      assert.deepEqual(errors, []);
      console.log(JSON.stringify({width, publicPapers: 620, publishedOnly: 520,
        markerless: samples.markerless.id, hierarchyProvenance: provenance, pageErrors: errors}));
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
