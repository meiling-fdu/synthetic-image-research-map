// Run against the local static preview; no application or data writes.
const {chromium} = require('/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  const errors=[];
  for (const width of [375,430,768,1024,1440]) {
    const page = await browser.newPage({hasTouch:width<=768});
    page.on('pageerror', e=>errors.push(e.message));
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.setViewportSize({width,height:900});
    await page.goto('http://127.0.0.1:8899');
    await page.waitForFunction(()=>!document.querySelector('#keyword-filter').disabled);
    const help=page.locator('#map-help summary');
    await help.focus();await help.press('Enter');
    const helpRect=await page.locator('#map-help-content').boundingBox();
    if(helpRect.x<0 || helpRect.x+helpRect.width>width) throw Error('Help overflow');
    await help.press('Escape');
    if(width<=820) await page.locator('#mobile-filters-trigger').click();
    await page.locator('#keyword-filter').fill('image');
    await page.locator('#keyword-filter').press('ArrowDown');
    const popup = await page.locator('#keyword-suggestions').boundingBox();
    if(popup.x < 0 || popup.x + popup.width > width || popup.y + popup.height > 900) throw Error('Autocomplete clipping');
    const active=await page.locator('#keyword-filter').getAttribute('aria-activedescendant');
    if(!active) throw Error('Missing active suggestion');
    await page.locator('#keyword-filter').press('Escape');
    if(width<=820 && !await page.locator('#filters-panel').evaluate(e=>e.classList.contains('is-open'))) throw Error('Escape closed drawer');
    await page.locator('#keyword-filter').fill('');
    const status = page.locator('[data-filter-dropdown]').filter({has:page.locator('#published-only-filter')}).locator('button').first();
    await status.click();
    await status.press('Escape');
    if(width<=820 && !await page.locator('#filters-panel').evaluate(e=>e.classList.contains('is-open'))) throw Error('Dropdown Escape closed drawer');
    if(width<=820) await page.locator('#done-filters').click();
    await page.evaluate(()=>window.scrollTo(0,document.querySelector('.results-panel').offsetTop+500));
    await page.waitForTimeout(150);
    const metrics=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,
      header:document.querySelector('.site-header').getBoundingClientRect().bottom,
      toolbar:document.querySelector('.results-heading-row').getBoundingClientRect().toJSON()}));
    if(metrics.scroll>width) throw Error('Overflow '+JSON.stringify(metrics));
    if(metrics.toolbar.top < metrics.header-1) throw Error('Header overlap '+JSON.stringify(metrics));
    if(await page.locator('.results-list').evaluate(e=>getComputedStyle(e).transitionDuration)!=='0s') throw Error('Reduced motion');
    await page.evaluate(()=>window.scrollTo(0,0));
    if(width<=820) await page.locator('#mobile-filters-trigger').click();
    await page.locator('#keyword-filter').fill('image');
    await page.locator('#keyword-filter').press('ArrowDown');
    await page.locator('#keyword-filter').press('Enter');
    if(await page.evaluate(()=>document.activeElement.id)!=='paper-details-heading') throw Error('Suggestion focus lost');
    await page.evaluate(()=>{
      document.querySelector('#paper-details-content button')?.focus();
      renderActiveSelection();
    });
    if(await page.evaluate(()=>document.activeElement===document.body)) throw Error('Details rerender lost focus');
    if(width>1250) {
      await page.locator('#close-paper-details').click();
      if(await page.locator('#open-paper-details').getAttribute('aria-expanded')!=='false') throw Error('Details collapsed ARIA');
      await page.locator('#open-paper-details').click();
      if(await page.locator('#open-paper-details').getAttribute('aria-expanded')!=='true') throw Error('Details expanded ARIA');
    }
    await page.locator('#results-list .result-item').first().focus();
    await page.evaluate(()=>renderRecords());
    await page.waitForFunction(()=>document.querySelector('#results-list').getAttribute('aria-busy')==='false');
    if(!await page.evaluate(()=>document.activeElement.classList.contains('result-item'))) throw Error('Result rerender lost focus');
    const chartFocus = await page.evaluate(()=>{
      const button=document.querySelector('button[data-chart-filter="tasks"]');
      const value=button.dataset.chartValue;
      button.click();
      return document.activeElement.dataset.chartValue===value;
    });
    if(!chartFocus) throw Error('Dashboard focus lost');
    await page.evaluate(()=>window.scrollTo(0,0));
    if(width<=820) await page.locator('#mobile-filters-trigger').click();
    await page.locator('#keyword-filter').fill('zzzznoresultzzzz');
    await page.waitForFunction(()=>!document.querySelector('#results-empty').hidden);
    if(await page.locator('#results-empty-heading').getAttribute('aria-live')!=='polite') throw Error('Empty announcement');
    if(width<=820) await page.locator('#done-filters').click();
    if(await page.locator('#results-empty').evaluate(e=>e.getBoundingClientRect().height)>200) throw Error('Empty state too tall');
    if(width<=768 && await page.locator('.sort-control-label .filter-dropdown-button').evaluate(e=>e.getBoundingClientRect().height)<44) throw Error('Small sort touch target');
    console.log(JSON.stringify(metrics));
    await page.close();
  }
  if(errors.length) throw Error(errors.join('\n'));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
