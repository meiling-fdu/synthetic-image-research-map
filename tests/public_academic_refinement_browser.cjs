// Run against a repository-root static server on port 8899.
const {chromium} = require('/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert = require('node:assert/strict');
const base = process.env.PUBLIC_REFINEMENT_URL || 'http://127.0.0.1:8899/web/';
(async () => {
  const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
  try {
    const context = await browser.newContext({permissions:['clipboard-read', 'clipboard-write']});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const ready = () => page.waitForFunction(() => !keywordFilter.disabled && resultsList.getAttribute('aria-busy') === 'false');
    const visit = async (query = '') => { await page.goto(base + query); await ready(); };
    const keyword = async value => {
      await page.locator('#keyword-filter').fill(value);
      await page.waitForFunction(value => resultsPipeline && keywordFilter.value === value
        && resultsList.getAttribute('aria-busy') === 'false'
        && new URL(location.href).searchParams.get('keyword') === (value || null), value);
    };
    const sort = async value => {
      const field = page.locator('[data-filter-dropdown]').filter({has:page.locator('#sort-control')});
      await field.locator('button').first().click();
      await field.locator(`[data-filter-value="${value}"]`).click();
      await ready();
    };
    await page.setViewportSize({width:1440,height:1000});
    await visit();
    assert.deepEqual(await page.evaluate(() => [resultsView, sortControl.value]), ['papers','year-desc']);
    await keyword('image');
    assert.equal(await page.locator('#sort-control').inputValue(), 'relevance');
    await page.locator('#copy-view-link').click();
    const automatic = await page.evaluate(() => navigator.clipboard.readText());
    assert.equal(new URL(automatic).searchParams.get('sort'), null);
    await page.goto(automatic); await ready(); await keyword('');
    assert.equal(await page.locator('#sort-control').inputValue(), 'year-desc');
    await visit();
    await keyword('image');
    await page.evaluate(() => undoLastFilterChange()); await ready();
    assert.deepEqual(await page.evaluate(() => [keywordFilter.value, sortControl.value, explicitSortSelection]), ['', 'year-desc', false]);
    await keyword('image'); await sort('year-desc');
    assert.equal(new URL(page.url()).searchParams.get('sort'), 'year-desc');
    await page.reload(); await ready(); await keyword(''); await keyword('image');
    assert.equal(await page.locator('#sort-control').inputValue(), 'year-desc');
    await visit('?keyword=image&sort=title-asc&view=institutions');
    assert.deepEqual(await page.evaluate(() => [resultsView, sortControl.value]), ['institutions','title-asc']);
    await page.locator('[data-results-view="papers"]').click(); await ready();
    await page.goBack(); await ready();
    assert.equal(await page.evaluate(() => resultsView), 'institutions');
    await visit('?view=papers');

    const coverage = await page.evaluate(() => {
      const sample = paperRecords.find(r => normalizedDoi(r.doi) && recordArxivId(r));
      const author = recordAuthors(sample)[0];
      const institution = recordInstitution(records[0]);
      return {doi:sample.doi, arxiv:recordArxivId(sample), title:TitleMarkup.plainText(recordTitle(sample)),
        id:paperIdentity(sample), author, institution};
    });
    for (const query of [coverage.doi, `https://doi.org/${coverage.doi.replace(/^https?:\/\/doi.org\//,'')}`,
      coverage.arxiv, `arXiv:${coverage.arxiv}`, `https://arxiv.org/abs/${coverage.arxiv}`,
      coverage.title, coverage.author]) {
      await keyword(query);
      assert(await page.evaluate(id => currentFilteredPaperRecords.some(r => paperIdentity(r) === id), coverage.id), query);
    }
    await keyword(coverage.institution);
    assert(await page.evaluate(() => currentFilteredRecords.length > 0), 'Institution search');
    const fixtures = await page.evaluate(() => {
      keywordFilter.value = 'image forensics'; relevanceScoresByRecord = new WeakMap();
      const rows = [
        {paper_id:'abstract',title:'Other',year:2026,abstract:'image forensics'},
        {paper_id:'title',title:'Image Forensics',year:2020},
        {paper_id:'b',doi:'10.1234/b',title:'An Image Forensics Study',year:2025},
        {paper_id:'a',doi:'10.1234/a',title:'An Image Forensics Study',year:2025},
      ];
      const ordered = rows.sort((a,b) => compareRecordsForSort(a,b,'relevance')).map(r=>r.paper_id);
      const abstract = recordSearchText(rows.find(r=>r.paper_id==='abstract')).includes('image forensics');
      const citations = [
        paperCitation({title:'Formal',authors:['Alice'],venue:'CVPR',publication_type:'conference',publication_year:2026,
          doi:'10.1234/formal',arxiv_id:'2501.12345',arxiv_year:2025}),
        paperCitation({title:'Preprint',arxiv_id:'2501.12345'}),
        paperCitation({title:'Only title',doi:'invalid',year:null}),
        paperCitation({title:'Web paper',paper_url:'https://example.org/paper'}),
      ];
      return {ordered,abstract,citations};
    });
    assert.deepEqual(fixtures.ordered, ['title','a','b','abstract']);
    assert(fixtures.abstract);
    assert.equal(fixtures.citations[0], 'Alice. "Formal." CVPR, 2026. https://doi.org/10.1234/formal');
    assert.equal(fixtures.citations[1], '"Preprint." https://arxiv.org/abs/2501.12345');
    assert.equal(fixtures.citations[2], '"Only title."');
    assert.equal(fixtures.citations[3], '"Web paper." https://example.org/paper');
    await visit('?paper=' + encodeURIComponent(coverage.id));
    const citation = page.locator('[data-copy-citation]');
    await citation.focus(); await citation.press('Enter');
    await page.waitForFunction(() => document.querySelector('[data-copy-citation-status]').textContent === 'Citation copied to clipboard.');
    assert.equal(await page.locator('[data-copy-citation-status]').textContent(), 'Citation copied to clipboard.');
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), await citation.getAttribute('data-copy-citation'));
    assert.equal(await citation.textContent(), 'Copied');
    assert.equal(await page.locator('[data-copy-citation-status]').getAttribute('aria-live'), 'polite');
    await page.evaluate(async () => {
      const original = writeViewUrlToClipboard;
      writeViewUrlToClipboard = async () => { throw Error('Clipboard unavailable'); };
      try { await copyPaperCitation(document.querySelector('[data-copy-citation]')); }
      finally { writeViewUrlToClipboard = original; }
    });
    assert.equal(await page.locator('[data-copy-citation-status]').textContent(), 'Unable to copy the citation.');
    assert.equal(await citation.textContent(), 'Copy citation');
    assert.equal(await page.locator('[data-copy-paper-link]').count(), 1);
    assert.equal(await page.getByRole('link', {name:'Report a metadata issue for this paper (opens in a new tab)'}).count(), 1);
    await page.screenshot({path:'/tmp/public-refinement-details.png'});

    for (const width of [375,430,768,1024,1440]) {
      await page.setViewportSize({width,height:1000}); await visit();
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Map overflow at ${width}`);
      if (width <= 820) {
        await page.locator('#mobile-filters-trigger').click();
        await page.locator('#keyword-filter').fill('image');
        await page.locator('#keyword-filter').press('ArrowDown');
        await page.locator('#keyword-filter').press('Enter');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'paper-details-heading');
        assert(await page.locator('[data-copy-citation]').isVisible());
        assert((await page.locator('[data-copy-citation]').boundingBox()).height >= 38);
      }
      if (width === 375) await page.screenshot({path:'/tmp/public-refinement-mobile.png'});
      await page.goto(new URL('methodology.html', base).href);
      assert.equal(await page.locator('main h2').count(), 10);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Methodology overflow at ${width}`);
      if (width === 1440) await page.screenshot({path:'/tmp/public-refinement-methodology.png',fullPage:true});
    }
    assert.deepEqual(errors, []);
    console.log('PASS: defaults, explicit views, sort/history, identifier/title/author/institution search, relevance ties, citation/fallback/clipboard, Details, mobile drawer, and methodology at five widths.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
