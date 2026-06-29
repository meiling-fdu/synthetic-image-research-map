"use strict";

const state = {
  token: "",
  papers: [],
  filtered: [],
  selectedId: "",
  selectedPaper: null,
  selectedMappings: [],
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  [
    "connection-status",
    "add-paper-toggle",
    "add-paper-panel",
    "add-paper-close",
    "openalex-search-form",
    "openalex-title",
    "openalex-doi",
    "openalex-arxiv-id",
    "openalex-paper-url",
    "openalex-search-submit",
    "openalex-search-error",
    "openalex-results",
    "openalex-result-count",
    "openalex-result-list",
    "add-manually-button",
    "paper-draft-form",
    "paper-draft-origin",
    "paper-draft-cancel",
    "paper-source-database",
    "paper-title",
    "paper-year",
    "paper-authors",
    "paper-venue",
    "paper-doi",
    "paper-arxiv-id",
    "paper-openalex-url",
    "paper-url",
    "paper-publication-type",
    "paper-task",
    "paper-subtask",
    "paper-scope-status",
    "paper-review-status",
    "paper-abstract",
    "paper-review-note",
    "paper-duplicate-warning",
    "paper-create-error",
    "paper-create-submit",
    "token-panel",
    "token-form",
    "token-input",
    "workspace",
    "search-input",
    "filter-year",
    "filter-task",
    "filter-subtask",
    "filter-coverage",
    "filter-map",
    "filter-source",
    "filter-exclusion",
    "result-count",
    "paper-list",
    "empty-results",
    "detail-placeholder",
    "detail-content",
    "detail-source",
    "detail-title",
    "detail-badges",
    "metadata-grid",
    "detail-notes",
    "detail-exclude-button",
    "detail-restore-button",
    "marker-count",
    "marker-table-body",
    "empty-markers",
    "mapping-add-button",
    "mapping-replace-button",
    "mapping-paper-context",
    "mapping-table-body",
    "empty-mappings",
    "mapping-panel-error",
    "mapping-dialog",
    "mapping-form",
    "mapping-mode",
    "mapping-id",
    "mapping-dialog-title",
    "mapping-dialog-paper",
    "mapping-exclude-warning",
    "mapping-replace-warning",
    "mapping-fields",
    "mapping-institution",
    "mapping-authors",
    "mapping-raw-affiliation",
    "mapping-evidence-source",
    "mapping-evidence-url",
    "mapping-affiliation-note",
    "mapping-status",
    "mapping-review-note",
    "mapping-replace-confirmation",
    "mapping-confirm-replace",
    "mapping-form-error",
    "mapping-cancel",
    "mapping-submit",
    "count-total",
    "count-mapped",
    "count-affiliation",
    "count-coordinates",
    "count-curated",
    "count-exclusions",
    "action-notice",
    "scope-dialog",
    "scope-form",
    "scope-paper-id",
    "scope-mode",
    "scope-dialog-title",
    "scope-paper-title",
    "scope-exclusion-warning",
    "scope-restore-warning",
    "scope-reason-label",
    "scope-reason",
    "scope-note",
    "scope-note-label",
    "scope-form-error",
    "scope-cancel",
    "scope-submit",
  ].forEach((id) => {
    elements[id] = document.getElementById(id);
  });

  const query = new URLSearchParams(window.location.search);
  state.token = query.get("token") || sessionStorage.getItem("adminToken") || "";
  if (query.has("token")) {
    sessionStorage.setItem("adminToken", state.token);
    history.replaceState(null, "", `${window.location.pathname}${window.location.hash}`);
  }

  elements["token-form"].addEventListener("submit", (event) => {
    event.preventDefault();
    state.token = elements["token-input"].value.trim();
    sessionStorage.setItem("adminToken", state.token);
    loadApplication();
  });
  elements["search-input"].addEventListener("input", applyFilters);
  [
    "filter-year",
    "filter-task",
    "filter-subtask",
    "filter-coverage",
    "filter-map",
    "filter-source",
    "filter-exclusion",
  ].forEach((id) => elements[id].addEventListener("change", applyFilters));

  elements["detail-exclude-button"].addEventListener("click", () => {
    if (state.selectedPaper) openScopeDialog(state.selectedPaper, "exclude");
  });
  elements["detail-restore-button"].addEventListener("click", () => {
    if (state.selectedPaper) openScopeDialog(state.selectedPaper, "restore");
  });
  elements["scope-cancel"].addEventListener("click", closeScopeDialog);
  elements["scope-form"].addEventListener("submit", submitScopeDecision);
  elements["add-paper-toggle"].addEventListener("click", openAddPaperPanel);
  elements["add-paper-close"].addEventListener("click", closeAddPaperPanel);
  elements["openalex-search-form"].addEventListener("submit", searchOpenAlex);
  elements["add-manually-button"].addEventListener("click", () => startPaperDraft({}, "manual"));
  elements["paper-draft-cancel"].addEventListener("click", cancelPaperDraft);
  elements["paper-draft-form"].addEventListener("submit", createPaper);
  elements["mapping-add-button"].addEventListener("click", () => {
    if (state.selectedPaper) openMappingDialog("create");
  });
  elements["mapping-replace-button"].addEventListener("click", () => {
    if (state.selectedPaper) openMappingDialog("replace");
  });
  elements["mapping-cancel"].addEventListener("click", closeMappingDialog);
  elements["mapping-form"].addEventListener("submit", submitMapping);

  if (state.token) loadApplication();
  else requestToken();
});

async function apiFetch(path, options = {}) {
  const headers = { "X-Admin-Token": state.token, ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(path, {
    ...options,
    headers,
    cache: "no-store",
  });
  const payload = await response.json().catch(() => ({ error: "Invalid server response" }));
  if (!response.ok) {
    const error = new Error(payload.error || `Request failed (${response.status})`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

async function loadApplication(preserveSelection = false) {
  setConnection("loading", "Loading…");
  elements["token-panel"].hidden = true;
  try {
    const [status, papersPayload] = await Promise.all([
      apiFetch("/api/status"),
      apiFetch("/api/papers"),
    ]);
    state.papers = papersPayload.records.slice().sort((left, right) =>
      text(left.title).localeCompare(text(right.title), undefined, { sensitivity: "base" })
    );
    renderSummary(status.counts);
    populateFilters();
    applyFilters();
    elements.workspace.hidden = false;
    setConnection("ok", "Local curation · connected");
    if (preserveSelection && state.selectedId) {
      const stillPresent = state.papers.some((paper) => paper.display_id === state.selectedId);
      if (stillPresent) await selectPaper(state.selectedId);
    }
  } catch (error) {
    if (error.status === 401) {
      sessionStorage.removeItem("adminToken");
      state.token = "";
      requestToken("That token was not accepted.");
      return;
    }
    requestToken(`Could not load admin data: ${error.message}`);
    setConnection("error", "Connection error");
  }
}

function requestToken(message = "") {
  elements.workspace.hidden = true;
  elements["token-panel"].hidden = false;
  elements["token-input"].value = "";
  elements["token-input"].focus();
  setConnection("locked", message || "Token required");
}

function setConnection(status, label) {
  elements["connection-status"].dataset.state = status;
  elements["connection-status"].textContent = label;
}

function showNotice(message, variant = "success") {
  elements["action-notice"].hidden = false;
  elements["action-notice"].dataset.variant = variant;
  elements["action-notice"].textContent = message;
}

function openAddPaperPanel() {
  elements["add-paper-panel"].hidden = false;
  elements["openalex-title"].focus();
  elements["add-paper-panel"].scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeAddPaperPanel() {
  elements["add-paper-panel"].hidden = true;
  cancelPaperDraft();
}

async function searchOpenAlex(event) {
  event.preventDefault();
  const query = {
    title: elements["openalex-title"].value.trim(),
    doi: elements["openalex-doi"].value.trim(),
    arxiv_id: elements["openalex-arxiv-id"].value.trim(),
    paper_url: elements["openalex-paper-url"].value.trim(),
  };
  elements["openalex-search-error"].hidden = true;
  elements["openalex-results"].hidden = true;
  if (!Object.values(query).some(Boolean)) {
    elements["openalex-search-error"].hidden = false;
    elements["openalex-search-error"].textContent =
      "Enter at least one title, DOI, arXiv ID, or paper URL.";
    return;
  }
  elements["openalex-search-submit"].disabled = true;
  elements["openalex-search-submit"].textContent = "Searching…";
  try {
    const payload = await apiFetch("/api/openalex/search-paper", {
      method: "POST",
      body: JSON.stringify(query),
    });
    renderOpenAlexResults(payload.results || []);
    if (!payload.results?.length) {
      elements["openalex-search-error"].hidden = false;
      elements["openalex-search-error"].textContent =
        "OpenAlex returned no candidates. You can add the paper manually instead.";
    }
  } catch (error) {
    elements["openalex-search-error"].hidden = false;
    elements["openalex-search-error"].textContent =
      `${error.message} Manual entry remains available.`;
  } finally {
    elements["openalex-search-submit"].disabled = false;
    elements["openalex-search-submit"].textContent = "Search OpenAlex";
  }
}

function renderOpenAlexResults(results) {
  const list = elements["openalex-result-list"];
  list.replaceChildren();
  results.forEach((candidate) => {
    const card = document.createElement("article");
    card.className = "openalex-result-card";

    const heading = document.createElement("h4");
    heading.textContent = text(candidate.title) || "Untitled OpenAlex record";
    const meta = document.createElement("p");
    meta.className = "candidate-meta";
    meta.textContent = [
      candidate.year,
      candidate.venue,
      humanize(candidate.publication_type),
      candidate.similarity_score === null || candidate.similarity_score === undefined
        ? ""
        : `title similarity ${Number(candidate.similarity_score).toFixed(3)}`,
    ].filter(Boolean).join(" · ");
    const authors = document.createElement("p");
    authors.textContent = listText(candidate.authors) || "Authors unavailable";
    const identifiers = document.createElement("p");
    identifiers.className = "candidate-identifiers";
    identifiers.textContent = [
      candidate.doi ? `DOI: ${candidate.doi}` : "",
      candidate.openalex_url ? `OpenAlex: ${candidate.openalex_url}` : "",
      candidate.primary_url ? `Primary URL: ${candidate.primary_url}` : "",
    ].filter(Boolean).join("\n");
    const abstract = document.createElement("p");
    abstract.className = "candidate-abstract";
    abstract.textContent = text(candidate.abstract) || "Abstract unavailable.";

    const actions = document.createElement("div");
    actions.className = "candidate-actions";
    const useButton = document.createElement("button");
    useButton.type = "button";
    useButton.className = "primary-button";
    useButton.textContent = "Use this OpenAlex record";
    useButton.addEventListener("click", () => startPaperDraft(candidate, "openalex"));
    const rejectButton = document.createElement("button");
    rejectButton.type = "button";
    rejectButton.className = "secondary-button";
    rejectButton.textContent = "Not correct";
    rejectButton.addEventListener("click", () => {
      card.remove();
      updateOpenAlexResultCount();
    });
    actions.append(useButton, rejectButton);
    card.append(heading, meta, authors, identifiers, abstract, actions);
    list.append(card);
  });
  elements["openalex-results"].hidden = results.length === 0;
  updateOpenAlexResultCount();
}

function updateOpenAlexResultCount() {
  const count = elements["openalex-result-list"].children.length;
  elements["openalex-result-count"].textContent =
    `${formatNumber(count)} candidate${count === 1 ? "" : "s"}`;
  if (count === 0) elements["openalex-results"].hidden = true;
}

function startPaperDraft(candidate, source) {
  elements["paper-draft-form"].reset();
  elements["paper-source-database"].value = source;
  elements["paper-draft-origin"].textContent =
    source === "openalex" ? "Confirmed OpenAlex draft" : "Manual paper draft";
  elements["paper-title"].value = text(candidate.title);
  elements["paper-year"].value = text(candidate.year);
  elements["paper-authors"].value = listText(candidate.authors);
  elements["paper-venue"].value = text(candidate.venue);
  elements["paper-doi"].value = text(candidate.doi);
  elements["paper-arxiv-id"].value = text(candidate.arxiv_id);
  elements["paper-openalex-url"].value = text(candidate.openalex_url);
  elements["paper-url"].value = text(candidate.paper_url || candidate.primary_url);
  elements["paper-publication-type"].value = text(candidate.publication_type);
  elements["paper-abstract"].value = text(candidate.abstract);
  elements["paper-scope-status"].value = "in_scope";
  elements["paper-review-status"].value =
    source === "openalex" ? "reviewed" : "pending";
  elements["paper-duplicate-warning"].hidden = true;
  elements["paper-create-error"].hidden = true;
  elements["paper-draft-form"].hidden = false;
  elements["paper-title"].focus();
  elements["paper-draft-form"].scrollIntoView({ behavior: "smooth", block: "start" });
}

function cancelPaperDraft() {
  elements["paper-draft-form"].reset();
  elements["paper-draft-form"].hidden = true;
  elements["paper-duplicate-warning"].hidden = true;
  elements["paper-create-error"].hidden = true;
}

function paperDraftPayload() {
  return {
    source_database: elements["paper-source-database"].value,
    title: elements["paper-title"].value.trim(),
    year: elements["paper-year"].value.trim(),
    authors: elements["paper-authors"].value.trim(),
    venue: elements["paper-venue"].value.trim(),
    doi: elements["paper-doi"].value.trim(),
    arxiv_id: elements["paper-arxiv-id"].value.trim(),
    openalex_url: elements["paper-openalex-url"].value.trim(),
    paper_url: elements["paper-url"].value.trim(),
    publication_type: elements["paper-publication-type"].value.trim(),
    abstract: elements["paper-abstract"].value.trim(),
    task: elements["paper-task"].value,
    subtask: elements["paper-subtask"].value.trim(),
    scope_status: elements["paper-scope-status"].value.trim(),
    review_status: elements["paper-review-status"].value,
    review_note: elements["paper-review-note"].value.trim(),
  };
}

async function createPaper(event) {
  event.preventDefault();
  elements["paper-create-error"].hidden = true;
  elements["paper-duplicate-warning"].hidden = true;
  elements["paper-create-submit"].disabled = true;
  try {
    const result = await apiFetch("/api/paper/create", {
      method: "POST",
      body: JSON.stringify(paperDraftPayload()),
    });
    showNotice(result.message);
    cancelPaperDraft();
    await loadApplication();
  } catch (error) {
    if (error.status === 409 && error.payload?.duplicate_matches) {
      renderDuplicateWarning(error.payload.duplicate_matches);
    } else {
      elements["paper-create-error"].hidden = false;
      elements["paper-create-error"].textContent = error.message;
    }
  } finally {
    elements["paper-create-submit"].disabled = false;
  }
}

function renderDuplicateWarning(matches) {
  const warning = elements["paper-duplicate-warning"];
  warning.replaceChildren();
  const heading = document.createElement("strong");
  heading.textContent = "Duplicate paper blocked";
  const intro = document.createElement("p");
  intro.textContent =
    "Edit or cancel this draft. Step 4 does not merge with existing records.";
  const list = document.createElement("ul");
  matches.forEach((match) => {
    const item = document.createElement("li");
    item.textContent = [
      match.source,
      match.title || "Untitled",
      match.year,
      match.doi,
      match.openalex_url,
    ].filter(Boolean).join(" · ");
    list.append(item);
  });
  warning.append(heading, intro, list);
  warning.hidden = false;
}

function renderSummary(counts) {
  elements["count-total"].textContent = formatNumber(counts.total_papers);
  elements["count-mapped"].textContent = formatNumber(counts.papers_with_map_locations);
  elements["count-affiliation"].textContent = formatNumber(counts.papers_missing_affiliations);
  elements["count-coordinates"].textContent = formatNumber(counts.papers_missing_coordinates);
  elements["count-curated"].textContent = formatNumber(counts.curated_papers);
  elements["count-exclusions"].textContent = formatNumber(counts.active_exclusions);
}

function populateFilters() {
  setOptions("filter-year", uniqueValues("year", true));
  setOptions("filter-task", uniqueValues("task"));
  setOptions("filter-subtask", uniqueValues("subtask"));
  setOptions("filter-coverage", uniqueValues("coverage_status"));
  setOptions("filter-source", uniqueValues("source_database"));
}

function uniqueValues(field, numericDescending = false) {
  const values = new Set(state.papers.map((paper) => text(paper[field])).filter(Boolean));
  return [...values].sort((left, right) =>
    numericDescending
      ? Number(right) - Number(left)
      : left.localeCompare(right, undefined, { sensitivity: "base" })
  );
}

function setOptions(id, values) {
  const select = elements[id];
  const selected = select.value;
  while (select.options.length > 1) select.remove(1);
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = humanize(value);
    select.append(option);
  });
  if ([...select.options].some((option) => option.value === selected)) {
    select.value = selected;
  }
}

function exclusionStatus(paper) {
  if (paper.has_active_exclusion) return "active";
  if (paper.is_in_curated_exclusions) return "restored";
  return "none";
}

function applyFilters() {
  const query = normalize(elements["search-input"].value);
  const filters = {
    year: elements["filter-year"].value,
    task: elements["filter-task"].value,
    subtask: elements["filter-subtask"].value,
    coverage_status: elements["filter-coverage"].value,
    source_database: elements["filter-source"].value,
  };
  const mapFilter = elements["filter-map"].value;
  const exclusionFilter = elements["filter-exclusion"].value;

  state.filtered = state.papers.filter((paper) => {
    if (query && !normalize(paper.title).includes(query)) return false;
    if (Object.entries(filters).some(([field, expected]) =>
      expected && text(paper[field]) !== expected
    )) return false;
    if (mapFilter && String(Boolean(paper.has_map_location)) !== mapFilter) return false;
    if (exclusionFilter && exclusionStatus(paper) !== exclusionFilter) return false;
    return true;
  });
  renderPaperList();
}

function renderPaperList() {
  const list = elements["paper-list"];
  list.replaceChildren();
  const fragment = document.createDocumentFragment();

  state.filtered.forEach((paper) => {
    const item = document.createElement("li");
    const card = document.createElement("article");
    card.className = "paper-card";
    card.dataset.paperId = paper.display_id;
    if (paper.display_id === state.selectedId) card.dataset.selected = "true";

    const selectButton = document.createElement("button");
    selectButton.type = "button";
    selectButton.className = "paper-select";
    selectButton.setAttribute("aria-label", `Inspect ${text(paper.title) || "untitled paper"}`);
    selectButton.addEventListener("click", () => selectPaper(paper.display_id));

    const title = document.createElement("strong");
    title.textContent = text(paper.title) || "Untitled paper";
    const authors = document.createElement("span");
    authors.textContent = listText(paper.authors) || "Authors unavailable";
    const venue = document.createElement("span");
    venue.textContent = text(paper.venue || paper.venue_name) || "Venue unavailable";
    const identifiers = document.createElement("span");
    identifiers.className = "paper-identifiers";
    identifiers.textContent = [
      paper.doi ? `DOI ${paper.doi}` : "",
      paper.openalex_url ? `OpenAlex ${paper.openalex_url}` : "",
    ].filter(Boolean).join(" · ") || "No DOI or OpenAlex URL";
    const classification = document.createElement("span");
    classification.className = "paper-meta";
    classification.textContent = [
      paper.year || paper.publication_year,
      humanize(paper.task),
      humanize(paper.subtask),
      text(paper.source_database),
      text(paper.metadata_source),
    ].filter(Boolean).join(" · ");
    const coverage = document.createElement("span");
    coverage.textContent = [
      humanize(paper.coverage_status),
      paper.has_map_location ? "has map location" : "no map location",
      `${formatNumber(paper.map_record_count)} map record${paper.map_record_count === 1 ? "" : "s"}`,
      `exclusion: ${exclusionStatus(paper)}`,
    ].join(" · ");
    selectButton.append(title, authors, venue, identifiers, classification, coverage);

    const footer = document.createElement("div");
    footer.className = "paper-card-footer";
    const badges = document.createElement("span");
    badges.className = "card-badges";
    if (paper.has_map_location) badges.append(makeBadge("Mapped", "map"));
    if (paper.is_in_curated_papers) badges.append(makeBadge("Curated", "curated"));
    if (paper.has_active_exclusion) badges.append(makeBadge("Actively excluded", "excluded"));
    else if (paper.is_in_curated_exclusions) badges.append(makeBadge("Restored", "restored"));

    const action = document.createElement("button");
    action.type = "button";
    if (paper.has_active_exclusion) {
      action.className = "restore-button compact-action";
      action.textContent = "Restore";
      action.addEventListener("click", () => openScopeDialog(paper, "restore"));
    } else {
      action.className = "danger-button compact-action";
      action.textContent = "Delete / Exclude from site";
      action.addEventListener("click", () => openScopeDialog(paper, "exclude"));
    }
    footer.append(badges, action);
    card.append(selectButton, footer);
    item.append(card);
    fragment.append(item);
  });
  list.append(fragment);
  elements["result-count"].textContent =
    `${formatNumber(state.filtered.length)} of ${formatNumber(state.papers.length)} papers`;
  elements["empty-results"].hidden = state.filtered.length !== 0;
}

async function selectPaper(id) {
  state.selectedId = id;
  renderPaperList();
  elements["detail-placeholder"].hidden = true;
  elements["detail-content"].hidden = false;
  elements["detail-title"].textContent = "Loading…";
  elements["mapping-panel-error"].hidden = true;
  try {
    const [paperPayload, mappingsPayload] = await Promise.all([
      apiFetch(`/api/paper?id=${encodeURIComponent(id)}`),
      apiFetch(`/api/paper/mappings?id=${encodeURIComponent(id)}`),
    ]);
    state.selectedPaper = paperPayload.paper;
    state.selectedMappings = mappingsPayload.curated_mappings || [];
    renderPaperDetail(paperPayload.paper);
    renderMappings(mappingsPayload);
  } catch (error) {
    elements["detail-title"].textContent = "Could not load paper";
    elements["detail-notes"].textContent = error.message;
    elements["mapping-panel-error"].hidden = false;
    elements["mapping-panel-error"].textContent = error.message;
  }
}

function renderPaperDetail(paper) {
  const sourceLabels = {
    curated_only: "Curated-only record",
    exclusion_only: "Exclusion audit record",
    public_preview: "Public preview record",
  };
  elements["detail-source"].textContent = sourceLabels[paper.record_source] || "Admin record";
  elements["detail-title"].textContent = text(paper.title) || "Untitled paper";
  elements["detail-badges"].replaceChildren();
  if (paper.has_map_location) elements["detail-badges"].append(makeBadge("Mapped", "map"));
  if (paper.is_in_curated_papers) elements["detail-badges"].append(makeBadge("Curated", "curated"));
  if (paper.has_active_exclusion) elements["detail-badges"].append(makeBadge("Actively excluded", "excluded"));
  else if (paper.is_in_curated_exclusions) elements["detail-badges"].append(makeBadge("Restored exclusion", "restored"));

  const metadata = [
    ["Display ID", paper.display_id],
    ["Year", paper.year || paper.publication_year],
    ["Authors", listText(paper.authors)],
    ["Venue", paper.venue || paper.venue_name],
    ["DOI", linkValue(paper.doi, doiUrl(paper.doi))],
    ["OpenAlex", linkValue(paper.openalex_url, paper.openalex_url)],
    ["Paper URL", linkValue(paper.paper_url, paper.paper_url)],
    ["Task", humanize(paper.task)],
    ["Subtask", humanize(paper.subtask)],
    ["Coverage", humanize(paper.coverage_status)],
    ["Has map location", yesNo(paper.has_map_location)],
    ["Map record count", paper.map_record_count],
    ["Source database", paper.source_database],
    ["Metadata source", paper.metadata_source],
    ["Exclusion status", exclusionStatus(paper)],
    ["Exclusion reasons", listText(paper.exclusion_reasons)],
    ["Normalized title + year", paper.normalized_title_year_key],
  ];
  const grid = elements["metadata-grid"];
  grid.replaceChildren();
  metadata.forEach(([label, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    if (value instanceof Node) dd.append(value);
    else dd.textContent = text(value) || "—";
    grid.append(dt, dd);
  });

  elements["detail-notes"].textContent = text(paper.notes || paper.review_note) || "No notes.";
  elements["detail-exclude-button"].hidden = Boolean(paper.has_active_exclusion);
  elements["detail-restore-button"].hidden = !paper.has_active_exclusion;
  renderMarkers(paper.marker_records || []);
}

function renderMappings(payload) {
  const paper = payload.paper || state.selectedPaper || {};
  const mappings = payload.curated_mappings || [];
  state.selectedMappings = mappings;
  elements["mapping-paper-context"].textContent = [
    text(paper.title),
    paper.year || paper.publication_year,
    listText(paper.authors),
    paper.doi ? `DOI ${paper.doi}` : "",
    paper.openalex_url,
  ].filter(Boolean).join(" · ");

  const body = elements["mapping-table-body"];
  body.replaceChildren();
  mappings.forEach((mapping) => {
    const row = document.createElement("tr");
    const evidence = [
      mapping.raw_affiliation,
      mapping.evidence_source,
      mapping.evidence_url,
      mapping.affiliation_note,
    ].filter(Boolean).join(" · ");
    [
      mapping.institution,
      mapping.institution_authors,
      evidence,
      humanize(mapping.mapping_status),
      humanize(mapping.location_status),
      mapping.review_note,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });

    const actions = document.createElement("td");
    actions.className = "mapping-actions";
    if (mapping.mapping_status !== "excluded") {
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "secondary-button compact-action";
      edit.textContent = "Edit";
      edit.addEventListener("click", () => openMappingDialog("update", mapping));
      const exclude = document.createElement("button");
      exclude.type = "button";
      exclude.className = "danger-button compact-action";
      exclude.textContent = "Exclude";
      exclude.addEventListener("click", () => openMappingDialog("exclude", mapping));
      actions.append(edit, exclude);
    } else {
      actions.textContent = "Audit row";
    }
    row.append(actions);
    body.append(row);
  });
  elements["empty-mappings"].hidden = mappings.length !== 0;
  body.parentElement.hidden = mappings.length === 0;
  elements["mapping-panel-error"].hidden = true;
}

function openMappingDialog(mode, mapping = {}) {
  elements["mapping-form"].reset();
  elements["mapping-mode"].value = mode;
  elements["mapping-id"].value = text(mapping.mapping_id);
  elements["mapping-dialog-paper"].textContent =
    `${text(state.selectedPaper?.title) || "Untitled paper"} (${text(
      state.selectedPaper?.year || state.selectedPaper?.publication_year
    ) || "year unknown"})`;
  elements["mapping-institution"].value = text(mapping.institution);
  elements["mapping-authors"].value = text(mapping.institution_authors);
  elements["mapping-raw-affiliation"].value = text(mapping.raw_affiliation);
  elements["mapping-evidence-source"].value = text(mapping.evidence_source);
  elements["mapping-evidence-url"].value = text(mapping.evidence_url);
  elements["mapping-affiliation-note"].value = text(mapping.affiliation_note);
  elements["mapping-status"].value =
    mapping.mapping_status === "needs_review" ? "needs_review" : "active";
  elements["mapping-review-note"].value =
    mode === "update" ? text(mapping.review_note) : "";
  elements["mapping-form-error"].hidden = true;

  const excluding = mode === "exclude";
  const replacing = mode === "replace";
  elements["mapping-fields"].hidden = excluding;
  elements["mapping-institution"].required = !excluding;
  elements["mapping-authors"].required = !excluding;
  elements["mapping-exclude-warning"].hidden = !excluding;
  elements["mapping-replace-warning"].hidden = !replacing;
  elements["mapping-replace-confirmation"].hidden = !replacing;
  elements["mapping-confirm-replace"].required = replacing;

  const titles = {
    create: "Add author–institution mapping",
    update: "Edit author–institution mapping",
    exclude: "Exclude author–institution mapping",
    replace: "Replace all author–institution mappings",
  };
  const submitLabels = {
    create: "Save mapping",
    update: "Update mapping",
    exclude: "Exclude mapping",
    replace: "Replace all mappings",
  };
  elements["mapping-dialog-title"].textContent = titles[mode];
  elements["mapping-submit"].textContent = submitLabels[mode];
  elements["mapping-submit"].className =
    mode === "exclude" ? "danger-button" : "primary-button";
  elements["mapping-dialog"].showModal();
  (excluding
    ? elements["mapping-review-note"]
    : elements["mapping-institution"]
  ).focus();
}

function closeMappingDialog() {
  elements["mapping-dialog"].close();
}

function mappingDraft() {
  return {
    institution: elements["mapping-institution"].value.trim(),
    institution_authors: elements["mapping-authors"].value.trim(),
    raw_affiliation: elements["mapping-raw-affiliation"].value.trim(),
    evidence_source: elements["mapping-evidence-source"].value.trim(),
    evidence_url: elements["mapping-evidence-url"].value.trim(),
    affiliation_note: elements["mapping-affiliation-note"].value.trim(),
    mapping_status: elements["mapping-status"].value,
    review_note: elements["mapping-review-note"].value.trim(),
  };
}

async function submitMapping(event) {
  event.preventDefault();
  const mode = elements["mapping-mode"].value;
  const draft = mappingDraft();
  elements["mapping-form-error"].hidden = true;
  if (mode !== "exclude" && !(
    draft.raw_affiliation || draft.evidence_source || draft.evidence_url
  )) {
    elements["mapping-form-error"].hidden = false;
    elements["mapping-form-error"].textContent =
      "Enter a raw affiliation, evidence source, or evidence URL.";
    return;
  }
  if (mode === "replace" && !elements["mapping-confirm-replace"].checked) {
    elements["mapping-form-error"].hidden = false;
    elements["mapping-form-error"].textContent =
      "Confirm that all active mappings should be replaced.";
    return;
  }

  const paths = {
    create: "/api/paper/mapping/create",
    update: "/api/paper/mapping/update",
    exclude: "/api/paper/mapping/exclude",
    replace: "/api/paper/mappings/replace-all",
  };
  let body = {
    id: state.selectedId,
    mapping_id: elements["mapping-id"].value,
    ...draft,
  };
  if (mode === "replace") {
    body = {
      id: state.selectedId,
      confirm_replace_all: true,
      review_note: draft.review_note,
      mappings: [draft],
    };
  }
  elements["mapping-submit"].disabled = true;
  try {
    const result = await apiFetch(paths[mode], {
      method: "POST",
      body: JSON.stringify(body),
    });
    closeMappingDialog();
    showNotice(result.message);
    await loadSelectedMappings();
  } catch (error) {
    elements["mapping-form-error"].hidden = false;
    elements["mapping-form-error"].textContent =
      error.status === 409
        ? `${error.message}. Edit the existing mapping instead.`
        : error.message;
  } finally {
    elements["mapping-submit"].disabled = false;
  }
}

async function loadSelectedMappings() {
  if (!state.selectedId) return;
  try {
    const payload = await apiFetch(
      `/api/paper/mappings?id=${encodeURIComponent(state.selectedId)}`
    );
    renderMappings(payload);
  } catch (error) {
    elements["mapping-panel-error"].hidden = false;
    elements["mapping-panel-error"].textContent = error.message;
  }
}

function openScopeDialog(paper, mode) {
  state.selectedPaper = paper;
  elements["scope-form"].reset();
  elements["scope-paper-id"].value = paper.display_id;
  elements["scope-mode"].value = mode;
  elements["scope-paper-title"].textContent = text(paper.title) || "Untitled paper";
  elements["scope-form-error"].hidden = true;
  const restoring = mode === "restore";
  elements["scope-dialog-title"].textContent = restoring
    ? "Restore paper to future exports?"
    : "Exclude paper from site?";
  elements["scope-exclusion-warning"].hidden = restoring;
  elements["scope-restore-warning"].hidden = !restoring;
  elements["scope-reason-label"].hidden = restoring;
  elements["scope-reason"].required = !restoring;
  elements["scope-note-label"].textContent = restoring ? "Restore note" : "Review note";
  elements["scope-submit"].textContent = restoring ? "Confirm restore" : "Confirm exclusion";
  elements["scope-submit"].className = restoring ? "restore-button" : "danger-button";
  elements["scope-dialog"].showModal();
}

function closeScopeDialog() {
  elements["scope-dialog"].close();
}

async function submitScopeDecision(event) {
  event.preventDefault();
  const mode = elements["scope-mode"].value;
  const note = elements["scope-note"].value.trim();
  const reason = elements["scope-reason"].value;
  if (!note || (mode === "exclude" && !reason)) {
    elements["scope-form-error"].hidden = false;
    elements["scope-form-error"].textContent =
      mode === "exclude"
        ? "Choose a deletion reason and enter a review note."
        : "Enter a restore note.";
    return;
  }
  elements["scope-submit"].disabled = true;
  elements["scope-form-error"].hidden = true;
  try {
    const path = mode === "restore"
      ? "/api/paper/restore"
      : "/api/paper/delete-or-exclude";
    const body = mode === "restore"
      ? { id: elements["scope-paper-id"].value, restore_note: note }
      : {
          id: elements["scope-paper-id"].value,
          reason,
          review_note: note,
        };
    const result = await apiFetch(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
    closeScopeDialog();
    showNotice(result.message);
    await loadApplication(true);
  } catch (error) {
    elements["scope-form-error"].hidden = false;
    elements["scope-form-error"].textContent = error.message;
  } finally {
    elements["scope-submit"].disabled = false;
  }
}

function renderMarkers(markers) {
  elements["marker-count"].textContent =
    `${formatNumber(markers.length)} record${markers.length === 1 ? "" : "s"}`;
  const body = elements["marker-table-body"];
  body.replaceChildren();
  markers.forEach((marker) => {
    const row = document.createElement("tr");
    [
      marker.institution,
      listText(marker.institution_authors),
      [marker.city, marker.country_code].filter(Boolean).join(", "),
      coordinateText(marker),
      [humanize(marker.resolution_method), humanize(marker.resolution_confidence)]
        .filter(Boolean).join(" · "),
      marker.needs_review ? "Needs review" : "No flag",
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });
    body.append(row);
  });
  elements["empty-markers"].hidden = markers.length !== 0;
  body.parentElement.hidden = markers.length === 0;
}

function makeBadge(label, variant) {
  const badge = document.createElement("span");
  badge.className = `badge badge-${variant}`;
  badge.textContent = label;
  return badge;
}

function linkValue(label, href) {
  const cleanHref = safeUrl(href);
  if (!label || !cleanHref) return text(label);
  const link = document.createElement("a");
  link.href = cleanHref;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = text(label);
  return link;
}

function safeUrl(value) {
  if (!value) return "";
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

function doiUrl(doi) {
  const value = text(doi).replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "");
  return value ? `https://doi.org/${encodeURI(value)}` : "";
}

function coordinateText(marker) {
  const latitude = marker.latitude ?? marker.lat;
  const longitude = marker.longitude ?? marker.lon;
  if (latitude === null || latitude === undefined || longitude === null || longitude === undefined) return "";
  return `${latitude}, ${longitude}`;
}

function listText(value) {
  return Array.isArray(value) ? value.join(", ") : text(value);
}

function normalize(value) {
  return text(value).toLocaleLowerCase();
}

function text(value) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function yesNo(value) {
  return value ? "Yes" : "No";
}

function humanize(value) {
  return text(value).replaceAll("_", " ");
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}
