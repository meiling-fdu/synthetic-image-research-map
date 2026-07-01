"use strict";

const state = {
  token: "",
  papers: [],
  filtered: [],
  selectedId: "",
  selectedPaper: null,
  selectedMappings: [],
  locationReviews: [],
  locationSummary: {},
  confirmedLocations: [],
  locationStatusFilter: "",
  selectedLocationReviewId: "",
  dashboard: {},
  reviewQueues: {},
  paperMetadata: null,
  draftMappingCandidates: [],
};

const elements = {};
const workflowCommandIds = [
  "run-curated-validation",
  "run-export-preview",
  "run-public-validation",
  "run-full-refresh",
  "publish-changes",
];

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
    "openalex-search-debug",
    "openalex-weak-matches",
    "openalex-weak-match-summary",
    "openalex-weak-result-list",
    "add-manually-button",
    "paper-draft-form",
    "paper-draft-origin",
    "paper-draft-cancel",
    "paper-source-database",
    "paper-title",
    "paper-year",
    "paper-authors",
    "paper-affiliations",
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
    "paper-mapping-warning",
    "paper-acknowledge-missing-mappings",
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
    "mapping-diagnostic",
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
    "workflow-panel",
    "workflow-state",
    "workflow-guidance",
    "workflow-log-panel",
    "workflow-log",
    "run-curated-validation",
    "run-export-preview",
    "run-public-validation",
    "run-full-refresh",
    "publish-changes",
    "reload-preview-data",
    "show-git-status",
    "location-review-toggle",
    "location-review-panel",
    "location-review-close",
    "location-summary",
    "location-search",
    "location-status-filters",
    "location-review-list",
    "empty-location-reviews",
    "location-editor-placeholder",
    "location-form",
    "location-queue-id",
    "location-context",
    "confirmed-institution",
    "institution-language",
    "institution-review-status",
    "canonical-institution",
    "confirmed-city",
    "confirmed-region",
    "confirmed-country",
    "confirmed-country-code",
    "confirmed-lat",
    "confirmed-lon",
    "coordinate-source",
    "coordinate-source-url",
    "coordinate-review-note",
    "location-form-error",
    "location-confirm",
    "location-confirm-alias",
    "location-save-metadata",
    "location-create-new",
    "location-needs-coordinates",
    "location-mark-ambiguous",
    "location-ignore",
    "location-exclude",
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
    "console-nav",
    "dashboard-panel",
    "dashboard-grid",
    "reload-review-queues",
    "dashboard-git-status",
    "dashboard-run-full-refresh",
    "paper-metadata-section",
    "metadata-edit-button",
    "metadata-compare",
    "metadata-edit-form",
    "metadata-paper-id",
    "metadata-title",
    "metadata-year",
    "metadata-authors",
    "metadata-venue",
    "metadata-doi",
    "metadata-arxiv-id",
    "metadata-openalex-url",
    "metadata-paper-url",
    "metadata-publication-type",
    "metadata-task",
    "metadata-subtask",
    "metadata-scope-status",
    "metadata-curation-status",
    "metadata-review-status",
    "metadata-abstract",
    "metadata-review-note",
    "metadata-edit-error",
    "metadata-edit-cancel",
    "high-risk-review-panel",
    "marker-blocker-review-panel",
    "key-coverage-review-panel",
    "manual-import-review-panel",
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
  [
    ["run-curated-validation", "/api/run-curated-validation", "Curated validation"],
    ["run-export-preview", "/api/export-preview", "Preview export"],
    ["run-public-validation", "/api/run-public-validation", "Public-preview validation"],
    ["run-full-refresh", "/api/run-full-refresh", "Full refresh"],
  ].forEach(([id, path, label]) => {
    elements[id].addEventListener("click", () => runAdminWorkflow(path, label));
  });
  elements["publish-changes"].addEventListener("click", () => {
    const confirmed = window.confirm(
      "Publish Changes will refresh and validate the public preview, commit selected curated/manual/web-data/test files, and push the current branch. Continue?"
    );
    if (confirmed) {
      runAdminWorkflow(
        "/api/publish-changes",
        "Publish Changes",
        { confirmed: true }
      );
    }
  });
  elements["reload-preview-data"].addEventListener("click", reloadPreviewData);
  elements["show-git-status"].addEventListener("click", showGitStatus);
  elements["location-review-toggle"].addEventListener("click", openLocationReview);
  elements["location-review-close"].addEventListener("click", closeLocationReview);
  elements["location-search"].addEventListener("input", renderLocationReviewList);
  elements["location-form"].addEventListener("submit", confirmLocation);
  elements["location-mark-ambiguous"].addEventListener("click", () => {
    markLocationReview("ambiguous");
  });
  elements["location-needs-coordinates"].addEventListener("click", () => {
    markLocationReview("needs_coordinates");
  });
  elements["location-ignore"].addEventListener("click", () => markLocationReview("ignore"));
  elements["location-exclude"].addEventListener("click", () => markLocationReview("excluded"));
  elements["location-confirm-alias"].addEventListener("click", confirmLocationAlias);
  elements["location-save-metadata"].addEventListener("click", saveLocationMetadata);
  elements["location-create-new"].addEventListener("click", () => {
    elements["canonical-institution"].value = "";
    elements["confirmed-institution"].focus();
  });
  document.querySelectorAll("[data-console-target]").forEach((button) => {
    button.addEventListener("click", () => navigateConsole(button.dataset.consoleTarget));
  });
  elements["reload-review-queues"].addEventListener("click", loadDashboardAndQueues);
  elements["dashboard-git-status"].addEventListener("click", () => {
    navigateConsole("workflows");
    showGitStatus();
  });
  elements["dashboard-run-full-refresh"].addEventListener("click", () => {
    navigateConsole("workflows");
    runAdminWorkflow("/api/run-full-refresh", "Full refresh");
  });
  elements["metadata-edit-button"].addEventListener("click", openMetadataEditor);
  elements["metadata-edit-cancel"].addEventListener("click", closeMetadataEditor);
  elements["metadata-edit-form"].addEventListener("submit", saveMetadata);
  document.querySelectorAll(".review-queue-panel").forEach((panel) => {
    panel.querySelectorAll("input, select").forEach((control) => {
      control.addEventListener("input", () => renderReviewQueue(panel.dataset.queue));
      control.addEventListener("change", () => renderReviewQueue(panel.dataset.queue));
    });
  });

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
    const error = new Error(
      payload.error || payload.errors?.join("; ") || `Request failed (${response.status})`
    );
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
    const [status, papersPayload, workflowStatus, locationPayload] = await Promise.all([
      apiFetch("/api/status"),
      apiFetch("/api/papers"),
      apiFetch("/api/latest-validation-status"),
      apiFetch("/api/location-review"),
    ]);
    state.papers = papersPayload.records.slice().sort((left, right) =>
      text(left.title).localeCompare(text(right.title), undefined, { sensitivity: "base" })
    );
    renderSummary(status.counts);
    populateFilters();
    applyFilters();
    elements.workspace.hidden = false;
    setConnection("ok", "Local curation · connected");
    renderLatestWorkflowStatus(workflowStatus);
    applyLocationPayload(locationPayload);
    elements["console-nav"].hidden = false;
    await loadDashboardAndQueues();
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

async function loadDashboardAndQueues() {
  const button = elements["reload-review-queues"];
  button.disabled = true;
  try {
    const paths = {
      dashboard: "/api/dashboard",
      "high-risk": "/api/review/high-risk-markers",
      "marker-blockers": "/api/review/marker-blockers",
      "key-paper-coverage": "/api/review/key-paper-coverage",
      "manual-import": "/api/review/manual-import",
    };
    const entries = await Promise.all(
      Object.entries(paths).map(async ([name, path]) => [name, await apiFetch(path)])
    );
    entries.forEach(([name, payload]) => {
      if (name === "dashboard") state.dashboard = payload.data || {};
      else state.reviewQueues[name] = payload.data || {};
    });
    renderDashboard();
    Object.keys(state.reviewQueues).forEach(renderReviewQueue);
  } catch (error) {
    showNotice(`Review queues could not be loaded: ${error.message}`, "error");
  } finally {
    button.disabled = false;
  }
}

function navigateConsole(target) {
  const targets = {
    dashboard: elements["dashboard-panel"],
    papers: elements.workspace,
    "add-paper": elements["add-paper-panel"],
    "scope-review": elements.workspace,
    "metadata-editor": elements["paper-metadata-section"],
    mappings: document.querySelector(".mappings-section"),
    "location-review": elements["location-review-panel"],
    "high-risk": elements["high-risk-review-panel"],
    "marker-blockers": elements["marker-blocker-review-panel"],
    "key-coverage": elements["key-coverage-review-panel"],
    "manual-import": elements["manual-import-review-panel"],
    workflows: elements["workflow-panel"],
  };
  if (target === "add-paper") openAddPaperPanel();
  if (target === "location-review") openLocationReview();
  const node = targets[target];
  if (!node) return;
  if ("hidden" in node) node.hidden = false;
  node.scrollIntoView({ behavior: "smooth", block: "start" });
  if (["metadata-editor", "mappings", "scope-review"].includes(target) && !state.selectedPaper) {
    showNotice("Select a paper first, then open its curation editor.", "error");
  }
  if (target === "metadata-editor" && state.selectedPaper) openMetadataEditor();
}

function renderDashboard() {
  const data = state.dashboard;
  const cards = [
    ["Public preview papers", data.counts?.public_preview_papers],
    ["Map markers", data.counts?.map_markers],
    ["Curated papers", data.counts?.curated_papers],
    ["Active exclusions", data.counts?.active_exclusions],
    ["Curated mappings", data.counts?.curated_mappings],
    ["Pending locations", data.counts?.pending_location_reviews],
    ["Confirmed locations", data.counts?.confirmed_institution_locations],
  ];
  elements["dashboard-grid"].replaceChildren();
  cards.forEach(([label, value]) => {
    const card = document.createElement("article");
    const strong = document.createElement("strong");
    strong.textContent = formatNumber(value);
    const span = document.createElement("span");
    span.textContent = label;
    card.append(strong, span);
    elements["dashboard-grid"].append(card);
  });
  Object.entries(data.queues || {}).forEach(([name, queue]) => {
    const card = document.createElement("article");
    const strong = document.createElement("strong");
    strong.textContent = formatNumber(queue.count);
    const span = document.createElement("span");
    const groups = Object.entries(queue.summary || {})
      .map(([key, count]) => `${key}: ${count}`).join(" · ");
    span.textContent = `${humanize(name)}${groups ? ` · ${groups}` : ""}`;
    card.append(strong, span);
    elements["dashboard-grid"].append(card);
  });
}

function queuePanel(name) {
  return document.querySelector(`.review-queue-panel[data-queue="${name}"]`);
}

function queueFields(name, row) {
  if (name === "high-risk") {
    return [row.priority, row.title, row.institution, row.review_type, row.recommended_action];
  }
  if (name === "marker-blockers") {
    return [row.blocker_type, row.title, row.institutions || row.institution, row.has_map_location, row.recommended_action];
  }
  if (name === "key-paper-coverage") {
    return [row.missing_stage, row.title, row.year, row.coverage_status, row.recommended_action];
  }
  return [
    row.candidate_status,
    row.title,
    row.candidate_title || row.best_match_title,
    row.similarity,
    row.source_file,
  ];
}

function queueGroupField(name) {
  return {
    "high-risk": "priority",
    "marker-blockers": "blocker_type",
    "key-paper-coverage": "missing_stage",
    "manual-import": "candidate_status",
  }[name];
}

function renderReviewQueue(name) {
  const panel = queuePanel(name);
  const queue = state.reviewQueues[name] || {};
  if (!panel) return;
  const records = queue.records || [];
  const group = panel.querySelector('[data-role="group"]');
  const previous = group.value;
  const values = [...new Set(records.map((row) => text(row[queueGroupField(name)]) || "unknown"))].sort();
  group.replaceChildren(new Option(group.options[0]?.textContent || "All", ""));
  values.forEach((value) => group.append(new Option(value, value)));
  group.value = previous;
  const search = normalize(panel.querySelector('[data-role="search"]').value);
  const actionFilter = panel.querySelector('[data-role="action-filter"]');
  const typeFilter = panel.querySelector('[data-role="type-filter"]');
  [actionFilter, typeFilter].filter(Boolean).forEach((select) => {
    const field = select === actionFilter ? "recommended_action" : "review_type";
    const selected = select.value;
    const first = select.options[0]?.textContent || "All";
    select.replaceChildren(new Option(first, ""));
    [...new Set(records.map((row) => text(row[field])).filter(Boolean))].sort()
      .forEach((value) => select.append(new Option(value, value)));
    select.value = selected;
  });
  const filtered = records.filter((row) => {
    if (group.value && text(row[queueGroupField(name)]) !== group.value) return false;
    if (actionFilter?.value && text(row.recommended_action) !== actionFilter.value) return false;
    if (typeFilter?.value && text(row.review_type) !== typeFilter.value) return false;
    return !search || normalize(Object.values(row).join(" ")).includes(search);
  }).slice(0, 500);
  const body = panel.querySelector('[data-role="rows"]');
  body.replaceChildren();
  filtered.forEach((row) => {
    const tr = document.createElement("tr");
    queueFields(name, row).forEach((value) => {
      const td = document.createElement("td");
      td.textContent = text(value) || "—";
      tr.append(td);
    });
    tr.tabIndex = 0;
    tr.addEventListener("click", () => renderReviewDetail(name, row));
    tr.addEventListener("keydown", (event) => {
      if (event.key === "Enter") renderReviewDetail(name, row);
    });
    body.append(tr);
  });
  const empty = panel.querySelector('[data-role="empty"]');
  empty.textContent = !queue.available
    ? "Diagnostic report is missing. Run the full refresh pipeline."
    : filtered.length ? "" : "No rows match these filters.";
}

function renderReviewDetail(name, row) {
  const detail = queuePanel(name).querySelector('[data-role="detail"]');
  detail.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = text(row.title) || "Review row";
  const dl = document.createElement("dl");
  Object.entries(row).filter(([, value]) => text(value)).forEach(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = humanize(key);
    const dd = document.createElement("dd");
    dd.textContent = text(value);
    dl.append(dt, dd);
  });
  const actions = document.createElement("div");
  actions.className = "review-actions";
  reviewActionsFor(name, row).forEach(([label, action]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "secondary-button";
    button.textContent = label;
    button.addEventListener("click", () => handleReviewAction(name, row, action));
    actions.append(button);
  });
  detail.append(heading, dl, actions);
}

function reviewActionsFor(name, row) {
  const common = [["Open metadata", "open_metadata"], ["Open scope review", "open_scope"]];
  if (name === "high-risk") return [
    ["Confirm marker", "confirm_marker"],
    ["Replace mapping", "replace_author_institution_mapping"],
    ["Exclude wrong mapping", "exclude_wrong_mapping"],
    ["Send to location review", "send_to_location_review"],
    ["No action after review", "no_action_after_review"],
    ...common,
  ];
  if (name === "marker-blockers") return [
    ["Open mapping editor", "replace_author_institution_mapping"],
    ["Send to location review", "send_to_location_review"],
    ["Open high-risk review", "open_high_risk"],
    ["No action after review", "no_action_after_review"],
    ...common,
  ];
  if (name === "key-paper-coverage") return [
    ["Open blocker review", "open_blockers"],
    ["Open mapping editor", "replace_author_institution_mapping"],
    ["Add manually", "add_manually"],
    ["Confirm same paper", "no_action_after_review"],
    ["Mark unresolved", "unresolved"],
    ...common,
  ];
  return [
    ["Use OpenAlex record", "use_openalex"],
    ["Add manually", "add_manually"],
    ["Retry search", "retry_search"],
    ["Reject as out-of-scope", "open_scope"],
    ["Mark weak match unresolved", "unresolved"],
    ["No action after review", "no_action_after_review"],
  ];
}

function findRelatedPaper(row) {
  const doi = normalize(text(row.doi).replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, ""));
  const openalex = normalize(row.openalex_url);
  const title = normalize(row.title);
  const year = text(row.year);
  return state.papers.find((paper) =>
    (doi && normalize(text(paper.doi).replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")) === doi) ||
    (openalex && normalize(paper.openalex_url) === openalex) ||
    (title && normalize(paper.title) === title && text(paper.year || paper.publication_year) === year)
  );
}

async function openRelatedPaper(row) {
  const paper = findRelatedPaper(row);
  if (!paper) {
    showNotice("No matching paper is currently visible. Use Add Paper or refresh the preview.", "error");
    return null;
  }
  navigateConsole("papers");
  await selectPaper(paper.display_id);
  return paper;
}

async function handleReviewAction(name, row, action) {
  if (action === "open_high_risk") return navigateConsole("high-risk");
  if (action === "open_blockers") return navigateConsole("marker-blockers");
  if (action === "open_metadata") {
    if (await openRelatedPaper(row)) openMetadataEditor();
    return;
  }
  if (action === "open_scope") {
    const paper = await openRelatedPaper(row);
    if (paper) openScopeDialog(state.selectedPaper, "exclude");
    else {
      const note = window.prompt("Review note for this out-of-scope candidate:");
      if (note) await saveReviewDecision(name, row, "exclude_paper_scope", note);
    }
    return;
  }
  if (action === "replace_author_institution_mapping") {
    if (await openRelatedPaper(row)) openMappingDialog("replace");
    return;
  }
  if (action === "send_to_location_review" && !text(row.institution)) {
    openLocationReview();
    elements["location-search"].value = text(row.title);
    renderLocationReviewList();
    showNotice("Opened the existing location queue filtered to this paper.");
    return;
  }
  if (action === "use_openalex" || action === "add_manually") {
    openAddPaperPanel();
    const candidate = action === "use_openalex" ? {
      ...row,
      title: row.candidate_title || row.best_match_title || row.title,
      year: row.candidate_year || row.best_match_year || row.year,
      venue: row.venue || row.publication_venue,
    } : row;
    startPaperDraft(candidate, action === "use_openalex" ? "openalex" : "manual");
    return;
  }
  if (action === "retry_search") {
    openAddPaperPanel();
    elements["openalex-title"].value = text(row.title);
    elements["openalex-doi"].value = text(row.doi);
    elements["openalex-paper-url"].value = text(row.openalex_url);
    await searchOpenAlex({ preventDefault() {} });
    return;
  }
  const note = window.prompt("Required review note:");
  if (!note) return;
  await saveReviewDecision(name, row, action, note);
}

async function saveReviewDecision(name, row, action, note) {
  const endpoints = {
    "high-risk": "/api/review/high-risk-markers/action",
    "marker-blockers": "/api/review/marker-blockers/action",
    "key-paper-coverage": "/api/review/key-paper-coverage/action",
    "manual-import": "/api/review/manual-import/action",
  };
  try {
    const payload = await apiFetch(endpoints[name], {
      method: "POST",
      body: JSON.stringify({
        ...row,
        action,
        review_note: note,
        target_type: row.institution ? "marker" : "paper",
      }),
    });
    await rebuildPaper(paperIdForRecord(row));
    showNotice(payload.message);
    await loadDashboardAndQueues();
  } catch (error) {
    showNotice(`Could not save review action: ${error.message}`, "error");
  }
}

function paperIdForRecord(record = {}) {
  return record.display_id
    || record.paper_id
    || record.related_paper_id
    || record.id
    || (record.openalex_url
      ? `openalex:${record.openalex_url.split("/").pop()}`
      : "");
}

function selectedLocationPaperId() {
  const row = state.locationReviews.find(
    (candidate) => candidate.queue_id === state.selectedLocationReviewId,
  );
  return paperIdForRecord(row);
}

function applyLocationPayload(payload) {
  state.locationReviews = payload.records || [];
  state.confirmedLocations = payload.confirmed_locations || [];
  state.locationSummary = payload.summary || {};
  renderLocationSummary();
  renderLocationReviewList();
  if (state.selectedLocationReviewId) {
    const selected = state.locationReviews.find(
      (row) => row.queue_id === state.selectedLocationReviewId
    );
    if (selected) selectLocationReview(selected.queue_id);
    else clearLocationEditor();
  }
}

async function loadLocationReviews() {
  const payload = await apiFetch("/api/location-review");
  applyLocationPayload(payload);
}

function openLocationReview() {
  elements["location-review-panel"].hidden = false;
  elements["location-review-panel"].scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function closeLocationReview() {
  elements["location-review-panel"].hidden = true;
}

function renderLocationSummary() {
  const summary = state.locationSummary;
  const items = [
    ["Queue", summary.total_queue_rows],
    ["Pending Review", summary.pending_review],
    ["Needs Coordinates", summary.needs_coordinates],
    ["Ambiguous", summary.ambiguous],
    ["Alias Candidates", summary.alias_candidate],
    ["Confirmed", summary.confirmed],
    ["Aliases", summary.alias_of_confirmed],
    ["Ignored", summary.ignore],
    ["Excluded", summary.excluded],
    ["Confirmed locations", summary.confirmed_locations_count],
  ];
  elements["location-summary"].replaceChildren();
  items.forEach(([label, value]) => {
    const item = document.createElement("span");
    const strong = document.createElement("strong");
    strong.textContent = formatNumber(value);
    item.append(strong, ` ${label}`);
    elements["location-summary"].append(item);
  });
  const filters = [
    ["", "All", summary.total_queue_rows],
    ["pending_review", "Pending Review", summary.pending_review],
    ["needs_coordinates", "Needs Coordinates", summary.needs_coordinates],
    ["ambiguous", "Ambiguous", summary.ambiguous],
    ["alias_candidate", "Alias Candidates", summary.alias_candidate],
    [
      "confirmed",
      "Confirmed",
      (summary.confirmed || 0) + (summary.alias_of_confirmed || 0),
    ],
    ["ignore", "Ignored", summary.ignore],
    ["excluded", "Excluded", summary.excluded],
  ];
  elements["location-status-filters"].replaceChildren();
  filters.forEach(([value, label, count]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${label} (${count || 0})`;
    button.dataset.active = String(state.locationStatusFilter === value);
    button.addEventListener("click", () => {
      state.locationStatusFilter = value;
      renderLocationSummary();
      renderLocationReviewList();
    });
    elements["location-status-filters"].append(button);
  });
}

function renderLocationReviewList() {
  const query = normalize(elements["location-search"].value);
  const records = state.locationReviews.filter((row) => {
    if (
      state.locationStatusFilter &&
      !(
        state.locationStatusFilter === "confirmed"
          ? ["confirmed", "alias_of_confirmed"].includes(row.review_status)
          : row.review_status === state.locationStatusFilter
      )
    ) return false;
    if (!query) return true;
    return normalize([
      row.institution,
      row.title,
      row.year,
      row.institution_authors,
      row.raw_affiliation,
      row.location_status,
      row.coordinate_status,
      row.review_status,
      row.canonical_institution_name,
      row.suggested_city,
      row.suggested_country,
    ].join(" ")).includes(query);
  });
  const list = elements["location-review-list"];
  list.replaceChildren();
  records.forEach((row) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.selected =
      row.queue_id === state.selectedLocationReviewId ? "true" : "false";
    const institution = document.createElement("strong");
    institution.textContent = text(row.institution) || "Unnamed institution";
    const paper = document.createElement("span");
    paper.textContent = [row.title, row.year].filter(Boolean).join(" · ") || "Paper unknown";
    const status = document.createElement("small");
    status.className = "institution-status-badge";
    status.dataset.status = row.review_status || "pending_review";
    status.textContent = humanize(row.review_status || "pending_review");
    const diagnostic = document.createElement("small");
    diagnostic.textContent = `Diagnostics: ${humanize(row.location_status)} · ${humanize(row.coordinate_status)}`;
    button.append(institution, paper, status, diagnostic);
    button.addEventListener("click", () => selectLocationReview(row.queue_id));
    item.append(button);
    list.append(item);
  });
  elements["empty-location-reviews"].hidden = records.length !== 0;
}

function selectLocationReview(queueId) {
  const row = state.locationReviews.find((entry) => entry.queue_id === queueId);
  if (!row) return;
  state.selectedLocationReviewId = queueId;
  renderLocationReviewList();
  elements["location-editor-placeholder"].hidden = true;
  elements["location-form"].hidden = false;
  elements["location-form"].reset();
  elements["location-queue-id"].value = queueId;
  const confirmed = row.confirmed_location || {};
  elements["confirmed-institution"].value =
    text(confirmed.institution || row.canonical_institution_name || row.institution);
  elements["institution-language"].value = text(row.detected_language);
  elements["institution-review-status"].value = text(row.review_status || "pending_review");
  const canonicalSelect = elements["canonical-institution"];
  canonicalSelect.replaceChildren(new Option("Select confirmed institution…", ""));
  state.confirmedLocations
    .slice()
    .sort((a, b) => text(a.institution).localeCompare(text(b.institution)))
    .forEach((location) => canonicalSelect.add(new Option(location.institution, location.institution)));
  canonicalSelect.value = text(row.canonical_institution_name || row.suggested_canonical_institution || row.matched_institution);
  elements["confirmed-city"].value =
    text(confirmed.city || row.suggested_city);
  elements["confirmed-region"].value = text(confirmed.region);
  elements["confirmed-country"].value =
    text(confirmed.country || row.suggested_country);
  elements["confirmed-country-code"].value =
    text(confirmed.country_code).toUpperCase();
  elements["confirmed-lat"].value = text(confirmed.lat);
  elements["confirmed-lon"].value = text(confirmed.lon);
  elements["coordinate-source"].value = text(confirmed.coordinate_source);
  elements["coordinate-source-url"].value =
    text(confirmed.coordinate_source_url);
  elements["coordinate-review-note"].value = text(confirmed.review_note);
  elements["location-form-error"].hidden = true;
  renderLocationContext(row);
}

function renderLocationContext(row) {
  const fields = [
    ["Raw institution name", row.institution],
    ["Canonical institution name", row.canonical_institution_name],
    ["Detected language", row.detected_language],
    ["Paper", [row.title, row.year].filter(Boolean).join(" · ")],
    ["Institution authors", row.institution_authors],
    ["Raw affiliation", row.raw_affiliation],
    ["Evidence source", row.evidence_source],
    ["Evidence URL", row.evidence_url],
    ["Suggested location", [row.suggested_city, row.suggested_country].filter(Boolean).join(", ")],
    ["Current review status", humanize(row.review_status)],
    ["Existing matched institution", row.matched_institution],
    ["Suggested canonical institution", row.suggested_canonical_institution],
    ["Match diagnostics", [row.match_method, row.similarity_score, row.confidence].filter(Boolean).join(" · ")],
    ["External IDs", [row.openalex_institution_id, row.ror_id, row.wikidata_id].filter(Boolean).join(" · ")],
    ["Existing aliases", (row.existing_aliases || []).join("; ")],
    ["Legacy diagnostics", [row.location_status, row.coordinate_status].filter(Boolean).map(humanize).join(" · ")],
    ["Review note", row.review_note],
  ];
  elements["location-context"].replaceChildren();
  fields.forEach(([label, value]) => {
    const wrapper = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    wrapper.append(strong);
    if (label === "Evidence URL" && safeUrl(value)) {
      wrapper.append(linkValue(value, value));
    } else {
      wrapper.append(text(value) || "—");
    }
    elements["location-context"].append(wrapper);
  });
}

function clearLocationEditor() {
  state.selectedLocationReviewId = "";
  elements["location-editor-placeholder"].hidden = false;
  elements["location-form"].hidden = true;
  renderLocationReviewList();
}

function locationDraft() {
  return {
    queue_id: elements["location-queue-id"].value,
    confirmed_institution: elements["confirmed-institution"].value.trim(),
    canonical_institution_name: elements["canonical-institution"].value,
    detected_language: elements["institution-language"].value.trim(),
    review_status: elements["institution-review-status"].value,
    confirmed_city: elements["confirmed-city"].value.trim(),
    confirmed_region: elements["confirmed-region"].value.trim(),
    confirmed_country: elements["confirmed-country"].value.trim(),
    confirmed_country_code:
      elements["confirmed-country-code"].value.trim().toUpperCase(),
    confirmed_lat: elements["confirmed-lat"].value.trim(),
    confirmed_lon: elements["confirmed-lon"].value.trim(),
    coordinate_source: elements["coordinate-source"].value.trim(),
    coordinate_source_url: elements["coordinate-source-url"].value.trim(),
    coordinate_review_note:
      elements["coordinate-review-note"].value.trim(),
  };
}

async function confirmLocation(event) {
  event.preventDefault();
  const draft = locationDraft();
  elements["location-form-error"].hidden = true;
  if (!(draft.coordinate_source || draft.coordinate_source_url)) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent =
      "Enter a coordinate source or coordinate source URL.";
    return;
  }
  elements["location-confirm"].disabled = true;
  try {
    const result = await apiFetch("/api/location-review/confirm", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    await rebuildPaper(selectedLocationPaperId());
    showNotice(result.message);
    await loadLocationReviews();
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = error.message;
  } finally {
    elements["location-confirm"].disabled = false;
  }
}

async function markLocationReview(status) {
  const note = elements["coordinate-review-note"].value.trim();
  elements["location-form-error"].hidden = true;
  if (!note) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent =
      "Enter a coordinate review note before changing the status.";
    return;
  }
  const buttonIds = {
    ambiguous: "location-mark-ambiguous",
    needs_coordinates: "location-needs-coordinates",
    ignore: "location-ignore",
    excluded: "location-exclude",
  };
  const button = elements[buttonIds[status]];
  button.disabled = true;
  try {
    const result = await apiFetch(
      `/api/location-review/mark-${status}`,
      {
        method: "POST",
        body: JSON.stringify({
          queue_id: elements["location-queue-id"].value,
          coordinate_review_note: note,
        }),
      }
    );
    await rebuildPaper(selectedLocationPaperId());
    showNotice(result.message);
    await loadLocationReviews();
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

async function confirmLocationAlias() {
  const draft = locationDraft();
  if (!draft.canonical_institution_name) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = "Select a confirmed canonical institution.";
    return;
  }
  try {
    const result = await apiFetch("/api/location-review/confirm-alias", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    await rebuildPaper(selectedLocationPaperId());
    showNotice(result.message);
    await loadLocationReviews();
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = error.message;
  }
}

async function saveLocationMetadata() {
  try {
    const result = await apiFetch("/api/location-review/save-metadata", {
      method: "POST",
      body: JSON.stringify(locationDraft()),
    });
    await rebuildPaper(selectedLocationPaperId());
    showNotice(result.message);
    await loadLocationReviews();
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = error.message;
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

function setWorkflowRunning(running, label = "") {
  workflowCommandIds.forEach((id) => {
    elements[id].disabled = running;
  });
  elements["reload-preview-data"].disabled = running;
  elements["show-git-status"].disabled = running;
  if (running) {
    elements["workflow-state"].dataset.state = "running";
    elements["workflow-state"].textContent = `${label} running…`;
  }
}

function renderLatestWorkflowStatus(status) {
  if (!status || status.state === "idle") {
    elements["workflow-state"].dataset.state = "idle";
    elements["workflow-state"].textContent = "No workflow run yet";
    return;
  }
  if (status.state === "running") {
    setWorkflowRunning(true, humanize(status.workflow));
    return;
  }
  setWorkflowRunning(false);
  elements["workflow-state"].dataset.state =
    status.state === "succeeded" ? "success" : "error";
  elements["workflow-state"].textContent = [
    humanize(status.workflow),
    status.state,
    status.result?.duration_seconds !== undefined
      ? `${status.result.duration_seconds}s`
      : "",
  ].filter(Boolean).join(" · ");
  if (status.result) renderWorkflowLog(status.result);
}

function renderWorkflowLog(result, heading = "") {
  const command = Array.isArray(result.command)
    ? result.command.join("\n")
    : text(result.command);
  const changedFiles = (result.changed_files || []).length
    ? result.changed_files.join("\n")
    : "None detected";
  elements["workflow-log"].textContent = [
    heading,
    `Success: ${result.success ? "yes" : "no"}`,
    `Exit code: ${result.exit_code}`,
    `Duration: ${result.duration_seconds}s`,
    "Command(s):",
    command || "—",
    "Changed files:",
    changedFiles,
    "Standard output:",
    result.stdout_tail || "—",
    "Standard error:",
    result.stderr_tail || "—",
  ].filter((part) => part !== "").join("\n");
}

async function runAdminWorkflow(path, label, payload = null) {
  setWorkflowRunning(true, label);
  elements["workflow-log"].textContent = `${label} is running…`;
  try {
    const result = await apiFetch(path, {
      method: "POST",
      ...(payload ? { body: JSON.stringify(payload) } : {}),
    });
    renderWorkflowLog(result, label);
    elements["workflow-log-panel"].open = true;
    elements["workflow-state"].dataset.state =
      result.success ? "success" : "error";
    elements["workflow-state"].textContent =
      `${label} ${result.success ? "succeeded" : "failed"} · ${result.duration_seconds}s`;
    if (!result.success) {
      showNotice(`${label} failed. Review the command log; preview data was not treated as validated.`, "error");
      return;
    }
    if (path === "/api/publish-changes") {
      await loadApplication(true);
      showNotice("Changes committed and pushed. GitHub Pages will update after deployment.");
    } else if (path === "/api/export-preview" || path === "/api/run-full-refresh") {
      await loadApplication(true);
      showNotice(
        "Local preview updated. Use Publish Changes when you are ready to commit and push."
      );
    } else {
      showNotice(`${label} completed successfully.`);
    }
  } catch (error) {
    elements["workflow-state"].dataset.state = "error";
    elements["workflow-state"].textContent = `${label} failed`;
    elements["workflow-log"].textContent =
      error.payload?.stderr_tail || error.message;
    elements["workflow-log-panel"].open = true;
    showNotice(`${label} failed: ${error.message}`, "error");
  } finally {
    setWorkflowRunning(false);
  }
}

async function rebuildPaper(paperId) {
  if (!paperId) return;
  const result = await apiFetch(
    `/rebuild-paper/${encodeURIComponent(paperId)}`,
    { method: "POST" },
  );
  if (!result.success) {
    throw new Error(result.stderr_tail || "Paper rebuild failed.");
  }
  window.dispatchEvent(new Event("paperUpdated"));
  localStorage.setItem("paperUpdated", String(Date.now()));
}

async function reloadPreviewData() {
  elements["reload-preview-data"].disabled = true;
  try {
    await loadApplication(true);
    showNotice("Preview data reloaded from local public-preview JSON.");
  } finally {
    elements["reload-preview-data"].disabled = false;
  }
}

async function showGitStatus() {
  elements["show-git-status"].disabled = true;
  try {
    const result = await apiFetch("/api/git-status");
    renderWorkflowLog(result, "git status --short");
    elements["workflow-log-panel"].open = true;
  } catch (error) {
    showNotice(`Could not read git status: ${error.message}`, "error");
  } finally {
    elements["show-git-status"].disabled = false;
  }
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
    renderOpenAlexResults(payload.results || [], payload.debug || {});
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

function renderOpenAlexResults(results, debug = {}) {
  const list = elements["openalex-result-list"];
  list.replaceChildren();
  const weakList = elements["openalex-weak-result-list"];
  weakList.replaceChildren();
  const variants = (debug.query_variants || []).map((variant) => variant.name).join(", ");
  elements["openalex-search-debug"].textContent = [
    variants ? `Queries: ${variants}` : "",
    Number.isFinite(debug.raw_candidates_fetched)
      ? `raw candidates: ${formatNumber(debug.raw_candidates_fetched)}`
      : "",
    Number.isFinite(debug.best_normalized_title_similarity)
      ? `best title similarity: ${Number(debug.best_normalized_title_similarity).toFixed(3)}`
      : "",
    `exact DOI lookup: ${debug.doi_exact_lookup_attempted ? "yes" : "no"}`,
    `exact arXiv lookup: ${debug.arxiv_exact_lookup_attempted ? "yes" : "no"}`,
    debug.arxiv_fallback_used ? "arXiv fallback used" : "",
  ].filter(Boolean).join(" · ");
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
    if (candidate.match_warning) {
      const warning = document.createElement("span");
      warning.className = "weak-match-warning";
      warning.textContent = candidate.match_warning;
      identifiers.append(document.createElement("br"), warning);
    }
    const abstract = document.createElement("p");
    abstract.className = "candidate-abstract";
    abstract.textContent = text(candidate.abstract) || "Abstract unavailable.";

    const actions = document.createElement("div");
    actions.className = "candidate-actions";
    const useButton = document.createElement("button");
    useButton.type = "button";
    useButton.className = "primary-button";
    const source = candidate.candidate_source === "arxiv" ? "arxiv" : "openalex";
    useButton.textContent =
      source === "arxiv" ? "Use this arXiv record" : "Use this OpenAlex record";
    useButton.addEventListener("click", () => startPaperDraft(candidate, source));
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
    (candidate.match_strength === "weak" ? weakList : list).append(card);
  });
  const weakCount = weakList.children.length;
  elements["openalex-weak-matches"].hidden = weakCount === 0;
  elements["openalex-weak-match-summary"].textContent =
    `Weak matches (${formatNumber(weakCount)})`;
  elements["openalex-results"].hidden = results.length === 0;
  updateOpenAlexResultCount();
}

function updateOpenAlexResultCount() {
  const strongCount = elements["openalex-result-list"].children.length;
  const weakCount = elements["openalex-weak-result-list"].children.length;
  const count = strongCount + weakCount;
  elements["openalex-result-count"].textContent =
    `${formatNumber(strongCount)} strong · ${formatNumber(weakCount)} weak`;
  elements["openalex-weak-matches"].hidden = weakCount === 0;
  if (count === 0) elements["openalex-results"].hidden = true;
}

function startPaperDraft(candidate, source) {
  state.draftMappingCandidates = Array.isArray(candidate.mapping_candidates)
    ? candidate.mapping_candidates
    : [];
  if (
    state.draftMappingCandidates.length === 0
    && text(candidate.institution)
    && text(candidate.institution_authors || candidate.authors)
  ) {
    const sourceAuthors = candidate.institution_authors || candidate.authors;
    state.draftMappingCandidates = [{
      institution: text(candidate.institution),
      institution_authors: (Array.isArray(sourceAuthors)
        ? sourceAuthors
        : text(sourceAuthors).split(";")
      ).map((author) => text(author).trim()).filter(Boolean),
      raw_affiliation: text(
        candidate.raw_affiliation || candidate.institution,
      ),
      provenance_source: text(
        candidate.evidence_source || "Manual import review",
      ),
      evidence_url: text(candidate.evidence_url || candidate.paper_url),
    }];
  }
  elements["paper-draft-form"].reset();
  elements["paper-source-database"].value = source;
  elements["paper-draft-origin"].textContent =
    source === "openalex"
      ? "Confirmed OpenAlex draft"
      : source === "arxiv"
        ? "Confirmed arXiv fallback draft"
        : "Manual paper draft";
  elements["paper-title"].value = text(candidate.title);
  elements["paper-year"].value = text(candidate.year);
  elements["paper-authors"].value = listText(candidate.authors);
  elements["paper-affiliations"].value = "";
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
  elements["paper-mapping-warning"].hidden =
    state.draftMappingCandidates.length !== 0;
  elements["paper-acknowledge-missing-mappings"].checked = false;
  elements["paper-create-error"].hidden = true;
  elements["paper-draft-form"].hidden = false;
  elements["paper-title"].focus();
  elements["paper-draft-form"].scrollIntoView({ behavior: "smooth", block: "start" });
}

function cancelPaperDraft() {
  state.draftMappingCandidates = [];
  elements["paper-draft-form"].reset();
  elements["paper-draft-form"].hidden = true;
  elements["paper-duplicate-warning"].hidden = true;
  elements["paper-mapping-warning"].hidden = true;
  elements["paper-create-error"].hidden = true;
}

function paperDraftPayload() {
  const manualCandidates = elements["paper-affiliations"].value
    .split(/\r?\n/)
    .map((line) => line.split("|").map((value) => value.trim()))
    .filter((parts) => parts.length >= 2 && parts[0] && parts[1])
    .map(([authors, institution, rawAffiliation = ""]) => ({
      institution,
      institution_authors: authors.split(";").map((author) => author.trim()).filter(Boolean),
      raw_affiliation: rawAffiliation || institution,
      provenance_source: "Manual Add Paper affiliation input",
    }));
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
    mapping_candidates: [
      ...state.draftMappingCandidates,
      ...manualCandidates,
    ],
    acknowledge_missing_mappings:
      elements["paper-acknowledge-missing-mappings"].checked,
  };
}

async function createPaper(event) {
  event.preventDefault();
  elements["paper-create-error"].hidden = true;
  elements["paper-duplicate-warning"].hidden = true;
  elements["paper-create-submit"].disabled = true;
  try {
    const draft = paperDraftPayload();
    if (
      draft.mapping_candidates.length === 0
      && !draft.acknowledge_missing_mappings
    ) {
      elements["paper-mapping-warning"].hidden = false;
      elements["paper-create-error"].hidden = false;
      elements["paper-create-error"].textContent =
        "Add author affiliation evidence or acknowledge the missing mapping.";
      return;
    }
    const result = await apiFetch("/api/paper/create", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    await rebuildPaper(paperIdForRecord(result.paper));
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
    const [paperPayload, mappingsPayload, metadataPayload] = await Promise.all([
      apiFetch(`/api/paper?id=${encodeURIComponent(id)}`),
      apiFetch(`/api/paper/mappings?id=${encodeURIComponent(id)}`),
      apiFetch(`/api/paper/metadata?id=${encodeURIComponent(id)}`),
    ]);
    state.selectedPaper = paperPayload.paper;
    state.selectedMappings = mappingsPayload.curated_mappings || [];
    state.paperMetadata = metadataPayload.data;
    renderPaperDetail(paperPayload.paper);
    renderMappings(mappingsPayload);
    renderMetadataComparison();
  } catch (error) {
    elements["detail-title"].textContent = "Could not load paper";
    elements["detail-notes"].textContent = error.message;
    elements["mapping-panel-error"].hidden = false;
    elements["mapping-panel-error"].textContent = error.message;
  }
}

function renderMetadataComparison() {
  const payload = state.paperMetadata || {};
  const sources = [
    ["Effective metadata", payload.effective_record],
    ["Original public preview metadata", payload.public_preview_record],
    ["Curated override metadata", payload.curated_record],
  ];
  elements["metadata-compare"].replaceChildren();
  sources.forEach(([label, record]) => {
    const details = document.createElement("details");
    if (label === "Effective metadata") details.open = true;
    const summary = document.createElement("summary");
    summary.textContent = `${label}${record ? "" : " · none"}`;
    const pre = document.createElement("pre");
    pre.textContent = record ? JSON.stringify(record, null, 2) : "No record.";
    details.append(summary, pre);
    elements["metadata-compare"].append(details);
  });
}

function metadataValue(record, field) {
  const value = record?.[field];
  return Array.isArray(value) ? value.join("; ") : text(value);
}

function openMetadataEditor() {
  if (!state.selectedPaper || !state.paperMetadata) {
    showNotice("Select a paper before editing metadata.", "error");
    return;
  }
  const record = state.paperMetadata.effective_record || state.selectedPaper;
  const fields = [
    "title", "year", "authors", "venue", "doi", "arxiv_id", "openalex_url",
    "paper_url", "publication_type", "task", "subtask", "scope_status",
    "curation_status", "review_status", "abstract", "review_note",
  ];
  fields.forEach((field) => {
    const id = `metadata-${field.replaceAll("_", "-")}`;
    if (elements[id]) elements[id].value = metadataValue(record, field);
  });
  elements["metadata-paper-id"].value = state.selectedId;
  elements["metadata-curation-status"].value =
    metadataValue(record, "curation_status") || "corrected_by_admin";
  elements["metadata-review-status"].value =
    metadataValue(record, "review_status") || "reviewed";
  elements["metadata-scope-status"].value =
    metadataValue(record, "scope_status") || "in_scope";
  elements["metadata-edit-error"].hidden = true;
  elements["metadata-edit-form"].hidden = false;
  elements["metadata-title"].focus();
}

function closeMetadataEditor() {
  elements["metadata-edit-form"].hidden = true;
}

async function saveMetadata(event) {
  event.preventDefault();
  const fields = [
    "title", "year", "authors", "venue", "doi", "arxiv_id", "openalex_url",
    "paper_url", "publication_type", "task", "subtask", "scope_status",
    "curation_status", "review_status", "abstract", "review_note",
  ];
  const draft = { id: elements["metadata-paper-id"].value };
  fields.forEach((field) => {
    draft[field] = elements[`metadata-${field.replaceAll("_", "-")}`].value.trim();
  });
  elements["metadata-edit-error"].hidden = true;
  try {
    const payload = await apiFetch("/api/paper/metadata/update", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    await rebuildPaper(draft.id);
    showNotice(payload.message);
    closeMetadataEditor();
    await loadApplication(false);
    const updated = state.papers.find((paper) =>
      normalize(paper.openalex_url) === normalize(draft.openalex_url) ||
      (normalize(paper.title) === normalize(draft.title) && text(paper.year) === draft.year)
    );
    if (updated) await selectPaper(updated.display_id);
  } catch (error) {
    elements["metadata-edit-error"].hidden = false;
    elements["metadata-edit-error"].textContent = error.message;
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
  const diagnostic = payload.mapping_diagnostic || {};
  elements["mapping-diagnostic"].hidden =
    diagnostic.status !== "missing_mapping";
  elements["mapping-diagnostic"].textContent = text(diagnostic.message);
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
      mapping.openalex_institution_id,
      [mapping.institution_city, mapping.institution_country].filter(Boolean).join(", "),
      [mapping.institution_latitude, mapping.institution_longitude].filter(Boolean).join(", "),
      mapping.provenance_source,
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
    await rebuildPaper(state.selectedId);
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
    await rebuildPaper(elements["scope-paper-id"].value);
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
