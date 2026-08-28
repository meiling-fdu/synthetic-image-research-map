const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('web/admin.js', 'utf8');

class Element {
  constructor() { this.children = []; this.value = ''; this.textContent = ''; this.options = []; this.handlers = {}; this.dataset = {}; }
  append(...nodes) { this.children.push(...nodes); this.options = this.children; }
  replaceChildren(...nodes) { this.children = [...nodes]; this.options = this.children; }
  setAttribute(name, value) { this[name] = value; }
  addEventListener(name, handler) { this.handlers[name] = handler; }
  remove(index) { this.options.splice(index, 1); }
}
const context = vm.createContext({ console, Option: class extends Element {
  constructor(label, value) { super(); this.textContent = label; this.value = value; }
}});
vm.runInContext(source, context);
vm.runInContext(`
  var notices = [];
  var panels = {};
  var elementsById = {};
  var ElementClass;
`, context);
context.ElementClass = Element;
vm.runInContext(`
  document = {
    createElement: () => new ElementClass(),
    createDocumentFragment: () => new ElementClass(),
    querySelector: (selector) => panels[selector.match(/data-queue="([^"]+)"/)?.[1]],
  };
  function setupPanel(name) {
    const nodes = {};
    for (const role of ['group', 'search', 'rows', 'counts', 'empty', 'detail']) nodes[role] = new ElementClass();
    nodes.group.options = [new Option('All', '')];
    panels[name] = {
      nodes,
      querySelector: (selector) => nodes[selector.match(/data-role="([^"]+)"/)?.[1]],
      querySelectorAll: () => [nodes.group, nodes.search],
    };
  }
  ['high-risk', 'marker-blockers', 'key-paper-coverage', 'manual-import',
   'high-risk-papers', 'missing-locations', 'missing-author-mappings', 'missing-affiliations'].forEach(setupPanel);
  ['reload-review-queues', 'dashboard-grid', 'action-queue-empty',
   'curation-dashboard-count', 'curation-dashboard-summary', 'curation-dashboard-table', 'curation-dashboard-rows',
   'search-input', 'filter-year', 'filter-task', 'filter-coverage', 'filter-map', 'filter-source',
   'filter-exclusion', 'filter-curation-status', 'paper-list', 'result-count', 'empty-results'
  ].forEach(id => elements[id] = new ElementClass());
  var TitleMarkup = {
    plainText: value => value, searchText: value => value,
    render: (element, value) => { element.textContent = value; },
  };
  showNotice = message => notices.push(message);
  applyLocationPayload = payload => { state.locationReviews = payload.records; };
  renderInstitutionAudit = () => {};
  renderMappingCoverage = () => {};
  var navigation = '';
  navigateConsole = target => { navigation = target; };
`, context);

function snapshot(version = 1, curationCount = 7) {
  const mappings = [
    ['marker_blocker', 'marker_blockers', 'marker-blockers'],
    ['high_risk_marker', 'high_risk_markers', 'high-risk'],
    ['high_risk_paper', 'high_risk_papers', 'high-risk-papers'],
    ['key_paper_coverage', 'key_paper_coverage_queue', 'key-coverage'],
    ['manual_import', 'manual_import_queue', 'manual-import'],
    ['missing_coordinates', 'missing_coordinates', 'missing-locations'],
    ['missing_author_mappings', 'missing_author_mappings', 'missing-author-mappings'],
    ['missing_affiliations', 'missing_affiliations', 'missing-affiliations'],
  ];
  const records = Array.from({length: curationCount}, (_, index) => ({
    display_id: 'paper:' + index, title: 'Paper ' + index, year: 2026,
    curation_status: 'needs_review', review_status: 'reviewed', scope_status: 'in_scope',
    is_active_corpus: true, notes: 'Check source',
  }));
  return {
    version,
    papers: [...records, {display_id: 'excluded', curation_status: 'needs_review', is_active_corpus: false},
      {display_id: 'confirmed', curation_status: 'confirmed', is_active_corpus: true}],
    papers_needing_curation: { count: records.length, records },
    action_required: mappings.map(([queue, key, target]) => ({ queue, key, target, value: 1 })),
    action_queues: Object.fromEntries(mappings.map(([queue]) => [queue, {
      available: true, count: 1, records: [{ title: 'Unresolved', year: '2026', actionable_id: queue }],
    }])),
    location_review: { records: [{ version }] },
    author_mapping_coverage: { records: [] },
  };
}

async function run() {
  context.nextSnapshot = snapshot();
  vm.runInContext(`apiFetch = async path => ({data: path === '/api/dashboard' ? nextSnapshot : {records: []}})`, context);
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(vm.runInContext("elements['dashboard-grid'].children.length", context), 8);
  vm.runInContext(`
    ['search-input', 'filter-year', 'filter-task', 'filter-coverage', 'filter-map',
     'filter-source', 'filter-exclusion'].forEach(id => { elements[id].value = 'stale'; });
    reviewPapersNeedingCuration();
  `, context);
  assert.equal(vm.runInContext('navigation', context), 'papers');
  assert.equal(vm.runInContext("elements['filter-curation-status'].value", context), 'needs_review');
  assert.equal(vm.runInContext('state.filtered.length', context), 7);
  assert.equal(vm.runInContext("elements['curation-dashboard-count'].textContent", context), '7');
  assert.equal(vm.runInContext("elements['curation-dashboard-rows'].children.length", context), 5);
  // Both title and Open/Edit navigate using the exact identifier and existing editor.
  vm.runInContext(`
    var opened = [];
    selectPaper = async id => { state.selectedId = id; state.paperMetadata = {}; opened.push(id); };
    openMetadataEditor = () => { opened.push('editor'); };
  `, context);
  await vm.runInContext("elements['curation-dashboard-rows'].children[2].children[0].children[0].handlers.click()", context);
  await vm.runInContext("elements['curation-dashboard-rows'].children[4].children[7].children[0].handlers.click()", context);
  assert.deepEqual(Array.from(context.opened), ['paper:2', 'editor', 'paper:4', 'editor']);
  for (const metric of context.nextSnapshot.action_required) {
    context.metric = metric;
    vm.runInContext(`
      const panelName = metric.target === 'key-coverage' ? 'key-paper-coverage' : metric.target;
      panels[panelName].nodes.search.value = 'old filter';
      navigateProjectHealthMetric(metric);
    `.replace('const panelName', 'var panelName'), context);
    assert.equal(vm.runInContext('navigation', context), metric.target);
    const name = metric.target === 'key-coverage' ? 'key-paper-coverage' : metric.target;
    assert.equal(context.panels[name].nodes.rows.children.length, metric.value);
    assert.match(context.panels[name].nodes.counts.textContent, /^1 unresolved/);
  }
  // Reproduce the original failure: Refresh request fails while old counts exist.
  // The old implementation cleared queues to zero before the request completed.
  vm.runInContext(`apiFetch = async () => { throw new Error('request failed'); }`, context);
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(context.panels['marker-blockers'].nodes.rows.children.length, 1);
  assert.equal(vm.runInContext("state.dashboard.action_required[0].value", context), 1);
  assert.match(vm.runInContext('notices.join(" ")', context), /last complete snapshot is retained/);
  assert.equal(vm.runInContext('state.filtered.length', context), 7);
  assert.equal(vm.runInContext("elements['curation-dashboard-count'].textContent", context), '7');

  // A failed auxiliary request cannot discard a successful actionable snapshot.
  context.nextSnapshot = snapshot(2);
  vm.runInContext(`apiFetch = async path => {
    if (path !== '/api/dashboard') throw new Error('cleanup unavailable');
    return {data: nextSnapshot};
  }`, context);
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(vm.runInContext('state.dashboard.version', context), 2);
  assert.equal(context.panels['high-risk'].nodes.rows.children.length, 1);
  // Save refresh preserves both sides until the authoritative response arrives.
  vm.runInContext(`
    renderPaperDetail = () => {};
    renderMetadataComparison = () => {};
    populateMetadataForm = () => {};
    state.selectedId = 'paper:0';
  `, context);
  let finishSaveRefresh;
  context.apiFetch = async path => path === '/api/dashboard'
    ? new Promise(resolve => { finishSaveRefresh = resolve; }) : {data: {records: []}};
  const saveRefresh = vm.runInContext(`refreshAfterMetadataSave('paper:0', {data: {
    paper: {curation_status: 'confirmed'}, paper_summary: {display_id: 'paper:0', curation_status: 'confirmed'}
  }}, paperSelectionSequence)`, context);
  assert.equal(vm.runInContext('state.filtered.length', context), 7);
  assert.equal(vm.runInContext("elements['curation-dashboard-count'].textContent", context), '7');
  finishSaveRefresh({data: snapshot(6, 0)});
  await saveRefresh;
  assert.equal(vm.runInContext('state.filtered.length', context), 0);
  assert.equal(vm.runInContext("elements['curation-dashboard-count'].textContent", context), '0');
  assert.equal(vm.runInContext("elements['curation-dashboard-table'].hidden", context), true);
  assert.equal(vm.runInContext("elements['curation-dashboard-summary'].textContent", context), 'No papers currently need curation.');
  context.apiFetch = async path => ({data: path === '/api/dashboard' ? snapshot(7, 1) : {records: []}});
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(vm.runInContext('state.filtered.length', context), 1);
  assert.equal(vm.runInContext("elements['curation-dashboard-count'].textContent", context), '1');

  for (const corrupt of [
    s => { s.papers_needing_curation.count++; },
    s => { s.papers.push(s.papers[0]); },
    s => { s.papers_needing_curation.records[0] = {...s.papers[0], review_status: 'stale'}; },
  ]) {
    const bad = snapshot(8); corrupt(bad);
    context.apiFetch = async path => ({data: path === '/api/dashboard' ? bad : {records: []}});
    await vm.runInContext('loadDashboardAndQueues()', context);
    assert.equal(vm.runInContext('state.dashboard.version', context), 7);
    assert.equal(vm.runInContext('state.filtered.length', context), 1);
  }

  // An unrelated coverage renderer failure must not leave queues at zero.
  context.nextSnapshot = snapshot(5);
  vm.runInContext(`
    apiFetch = async path => ({data: path === '/api/dashboard' ? nextSnapshot : {records: []}});
    renderMappingCoverage = () => { throw new Error('coverage rendering failed'); };
  `, context);
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(vm.runInContext('state.dashboard.version', context), 5);
  assert.equal(context.panels['high-risk'].nodes.rows.children.length, 1);
  vm.runInContext('renderMappingCoverage = () => {}', context);

  // Slow earlier refreshes cannot overwrite a newer summary/detail snapshot.
  let release;
  const old = new Promise(resolve => { release = resolve; });
  let requests = 0;
  context.apiFetch = async path => path === '/api/dashboard'
    ? (++requests === 1 ? old : {data: snapshot(4)}) : {data: {records: []}};
  const first = vm.runInContext('loadDashboardAndQueues()', context);
  await vm.runInContext('loadDashboardAndQueues()', context);
  release({data: snapshot(3)});
  await first;
  assert.equal(vm.runInContext('state.dashboard.version', context), 4);
  assert.equal(vm.runInContext('state.locationReviews[0].version', context), 4);

  // An incompatible/stale server never replaces a complete snapshot with empty rows.
  context.apiFetch = async () => ({data: {project_health: {groups: []}}});
  await vm.runInContext('loadDashboardAndQueues()', context);
  assert.equal(vm.runInContext('state.dashboard.version', context), 4);
  assert.equal(context.panels['high-risk'].nodes.rows.children.length, 1);
  console.log('Action Required frontend invariants passed (8 categories, failure, auxiliary failure, race, stale server).');
}
run().catch(error => { console.error(error); process.exitCode = 1; });
