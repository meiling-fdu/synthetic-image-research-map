"use strict";

const NOMINATIM_REVIEW_NOTE =
  "Coordinates selected from an OpenStreetMap Nominatim result and confirmed by the reviewer.";

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
  institutions: [],
  institutionAudit: { records: [], summary: {} },
  institutionCleanupSelection: new Set(),
  pendingInstitutionResolution: null,
  institutionEvidenceCase: null,
  institutionMerge: { source: null, target: null, submitting: false },
  locationStatusFilter: "",
  selectedLocationReviewId: "",
  dashboard: {},
  reviewQueues: {},
  selectedReviewKeys: {},
  authorMappingCoverage: null,
  paperMetadata: null,
  arxivEnrichment: { records: [], summary: {}, discovery: {} },
  draftMappingCandidates: [],
  selectedGeocodeCandidate: null,
  locationEditorMode: "review",
  selectedInstitutionLocationId: "",
  release: { validation: "required", preview: "required", changedFiles: 0 },
};

const elements = {};
let arxivAutofillPollTimer = null;
let arxivAutofillPolling = false;
let noticeTimer = null;
let paperSelectionSequence = 0;
let institutionLocationSequence = 0;
let geocodeRequestSequence = 0;
const workflowCommandIds = [
  "run-curated-validation",
  "run-export-preview",
  "run-public-validation",
  "run-full-refresh",
  "publish-changes",
];

if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", () => {
  [
    "connection-status",
    "add-paper-toggle",
    "global-publish-toggle",
    "global-search-input",
    "global-search-results",
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
    "historical-mappings",
    "historical-mapping-count",
    "historical-mapping-table-body",
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
    "mapping-institution-id",
    "mapping-institution-options",
    "mapping-authors",
    "mapping-raw-affiliation",
    "mapping-evidence-source",
    "mapping-evidence-url",
    "mapping-affiliation-note",
    "mapping-status",
    "mapping-review-note",
    "mapping-review-note-label",
    "mapping-replace-confirmation",
    "mapping-confirm-replace",
    "mapping-form-error",
    "mapping-cancel",
    "mapping-submit",
    "action-notice",
    "workflow-panel",
    "workflow-state",
    "workflow-guidance",
    "workflow-log-panel",
    "workflow-log",
    "run-curated-validation",
    "run-export-preview",
    "run-public-validation",
    "autofill-arxiv",
    "arxiv-enrichment-panel",
    "arxiv-enrichment-summary",
    "arxiv-enrichment-list",
    "arxiv-enrichment-empty",
    "run-full-refresh",
    "publish-changes",
    "reload-preview-data",
    "show-git-status",
    "location-review-panel",
    "institution-management-panel",
    "institution-management-close",
    "institution-management-search",
    "institution-management-rows",
    "institution-management-empty",
    "institution-merge-dialog",
    "institution-merge-form",
    "institution-merge-target-step",
    "institution-merge-confirm-step",
    "institution-merge-source-label",
    "institution-merge-search",
    "institution-merge-results",
    "institution-merge-target-cancel",
    "institution-merge-resolve",
    "institution-merge-source-name",
    "institution-merge-source-id",
    "institution-merge-target-name",
    "institution-merge-target-id",
    "institution-merge-confirm-cancel",
    "institution-merge-submit",
    "institution-merge-error",
    "location-review-close",
    "location-summary",
    "location-search",
    "location-status-filters",
    "location-review-list",
    "location-review-counts",
    "empty-location-reviews",
    "location-editor-placeholder",
    "location-form",
    "location-queue-id",
    "location-institution-id",
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
    "location-geocode",
    "location-create-new",
    "location-needs-coordinates",
    "location-mark-ambiguous",
    "location-ignore",
    "location-exclude",
    "location-more-actions",
    "location-more-actions-menu",
    "geocode-dialog",
    "geocode-form",
    "geocode-dialog-title",
    "geocode-query",
    "geocode-replace-warning",
    "geocode-candidates",
    "geocode-empty",
    "geocode-error",
    "geocode-cancel",
    "geocode-confirm",
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
    "action-queue-empty",
    "reload-review-queues",
    "dashboard-open-publish",
    "dashboard-changed-files",
    "dashboard-validation-status",
    "dashboard-preview-status",
    "dashboard-git-summary",
    "dashboard-release-state",
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
    "metadata-entry-type",
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
    "institution-audit-panel",
    "institution-audit-counts",
    "institution-audit-search",
    "institution-audit-severity",
    "institution-audit-provenance",
    "institution-audit-issue",
    "institution-audit-rows",
    "institution-audit-empty",
    "institution-audit-detail",
    "institution-archived-findings",
    "institution-archived-count",
    "institution-archived-rows",
    "institution-cleanup-batch",
    "institution-resolution-batch",
    "institution-cleanup-blocker",
    "institution-resolution-dialog",
    "institution-resolution-form",
    "institution-resolution-title",
    "institution-resolution-issue",
    "institution-resolution-paper",
    "institution-resolution-author",
    "institution-resolution-current",
    "institution-resolution-action",
    "institution-resolution-preset",
    "institution-resolution-note",
    "institution-resolution-note-optional",
    "institution-resolution-error",
    "institution-resolution-cancel",
    "institution-resolution-submit",
    "institution-evidence-dialog",
    "institution-evidence-title",
    "institution-evidence-content",
    "institution-evidence-actions",
    "institution-evidence-close",
    "marker-blocker-review-panel",
    "key-coverage-review-panel",
    "manual-import-review-panel",
    "author-mapping-coverage-panel",
    "mapping-coverage-summary",
    "mapping-coverage-empty-state",
    "generate-mapping-report",
    "mapping-priority-heading",
    "mapping-priority-table-wrap",
    "mapping-priority-rows",
    "mapping-priority-empty",
    "reload-mapping-coverage-full",
    "mapping-coverage-search",
    "mapping-coverage-status",
    "mapping-coverage-triage",
    "mapping-coverage-sort",
    "mapping-coverage-key",
    "mapping-coverage-full-empty-state",
    "mapping-coverage-counts",
    "generate-mapping-report-full",
    "mapping-coverage-table-wrap",
    "mapping-coverage-rows",
    "mapping-coverage-empty",
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
  elements["global-publish-toggle"].addEventListener("click", () => navigateConsole("publish"));
  elements["global-search-input"].addEventListener("input", renderGlobalSearch);
  elements["global-search-input"].addEventListener("keydown", handleGlobalSearchKeydown);
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
  elements["mapping-institution"].addEventListener("input", syncMappingInstitutionId);
  [
    ["run-curated-validation", "/api/run-curated-validation", "Curated validation"],
    ["run-export-preview", "/api/export-preview", "Preview export"],
    ["run-public-validation", "/api/run-public-validation", "Public-preview validation"],
    ["run-full-refresh", "/api/run-full-refresh", "Full refresh"],
  ].forEach(([id, path, label]) => {
    elements[id].addEventListener("click", () => runAdminWorkflow(path, label));
  });
  elements["autofill-arxiv"].addEventListener("click", autofillArxivIds);
  elements["publish-changes"].addEventListener("click", () => {
    const confirmed = window.confirm(
      "Publish Changes will validate curated data, regenerate and validate every public-preview output, commit all changed admin-managed files (plus modified frontend assets), and push the current branch. Continue?"
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
  elements["location-review-close"].addEventListener("click", closeLocationReview);
  elements["institution-audit-search"].addEventListener("input", renderInstitutionAudit);
  elements["institution-audit-severity"].addEventListener("change", renderInstitutionAudit);
  elements["institution-audit-provenance"].addEventListener("change", renderInstitutionAudit);
  elements["institution-audit-issue"].addEventListener("change", renderInstitutionAudit);
  elements["institution-cleanup-batch"].addEventListener("click", applySelectedInstitutionFixes);
  elements["institution-resolution-batch"].addEventListener("click", openBatchInstitutionResolution);
  elements["institution-resolution-preset"].addEventListener("change", applyInstitutionResolutionPreset);
  elements["institution-resolution-cancel"].addEventListener("click", closeInstitutionResolutionDialog);
  elements["institution-resolution-form"].addEventListener("submit", submitInstitutionResolution);
  elements["institution-evidence-close"].addEventListener("click", closeInstitutionEvidence);
  elements["institution-management-close"].addEventListener("click", () => {
    elements["institution-management-panel"].hidden = true;
  });
  elements["institution-management-search"].addEventListener("input", renderInstitutionManagement);
  elements["institution-merge-search"].addEventListener("input", renderInstitutionMergeTargets);
  elements["institution-merge-results"].addEventListener("change", selectInstitutionMergeResult);
  elements["institution-merge-resolve"].addEventListener("click", resolveInstitutionMergeTarget);
  elements["institution-merge-target-cancel"].addEventListener("click", closeInstitutionMergeDialog);
  elements["institution-merge-confirm-cancel"].addEventListener("click", closeInstitutionMergeDialog);
  elements["institution-merge-form"].addEventListener("submit", submitInstitutionMerge);
  elements["institution-merge-dialog"].addEventListener("cancel", (event) => {
    if (state.institutionMerge.submitting) event.preventDefault();
  });
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
  elements["canonical-institution"].addEventListener("change", renderLocationActions);
  elements["location-geocode"].addEventListener("click", findInstitutionCoordinates);
  elements["geocode-cancel"].addEventListener("click", closeGeocodeDialog);
  elements["geocode-confirm"].addEventListener("click", confirmGeocodeCandidate);
  elements["geocode-dialog"].addEventListener("close", () => {
    state.selectedGeocodeCandidate = null;
  });
  elements["location-create-new"].addEventListener("click", openInstitutionManagement);
  initializeLocationMoreActions();
  document.querySelectorAll("[data-console-target]").forEach((button) => {
    button.addEventListener("click", () => navigateConsole(button.dataset.consoleTarget));
  });
  initializeNavigationMenus();
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
      event.preventDefault();
      elements["global-search-input"].focus();
    }
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".global-search")) closeGlobalSearch();
  });
  elements["reload-review-queues"].addEventListener("click", loadDashboardAndQueues);
  elements["reload-mapping-coverage-full"].addEventListener("click", loadAuthorMappingCoverage);
  elements["generate-mapping-report"].addEventListener("click", generateAuthorMappingReport);
  elements["generate-mapping-report-full"].addEventListener("click", generateAuthorMappingReport);
  [
    "mapping-coverage-search",
    "mapping-coverage-status",
    "mapping-coverage-triage",
    "mapping-coverage-sort",
    "mapping-coverage-key",
  ].forEach((id) => elements[id].addEventListener("input", renderFullMappingCoverage));
  elements["dashboard-open-publish"].addEventListener("click", () => navigateConsole("publish"));
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
  setConnection("loading", "● Local curation loading…");
  elements["token-panel"].hidden = true;
  try {
    const [status, papersPayload, workflowStatus, locationPayload, institutionPayload, autofillStatus, gitStatus, arxivEnrichment] = await Promise.all([
      apiFetch("/api/status"),
      apiFetch("/api/papers"),
      apiFetch("/api/latest-validation-status"),
      apiFetch("/api/location-review"),
      apiFetch("/api/institutions"),
      apiFetch("/api/admin/papers/autofill-arxiv/status"),
      apiFetch("/api/git-status").catch(() => null),
      apiFetch("/api/admin/papers/arxiv-enrichment").catch(() => null),
    ]);
    state.papers = papersPayload.records.slice().sort((left, right) =>
      text(left.title).localeCompare(text(right.title), undefined, { sensitivity: "base" })
    );
    populateFilters();
    applyFilters();
    elements.workspace.hidden = false;
    setConnection("ok", "● Local curation connected");
    renderLatestWorkflowStatus(workflowStatus);
    renderGitSummary(gitStatus);
    applyLocationPayload(locationPayload);
    state.institutions = institutionPayload.records || [];
    renderInstitutionManagement();
    renderArxivAutofillStatus(autofillStatus);
    state.arxivEnrichment = arxivEnrichment?.data || state.arxivEnrichment;
    renderArxivEnrichment();
    if (autofillStatus.status === "running") scheduleArxivAutofillPoll();
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
  const buttons = [elements["reload-review-queues"]];
  buttons.forEach((button) => {
    button.disabled = true;
  });
  const paths = {
    dashboard: "/api/dashboard",
    "high-risk": "/api/review/high-risk-markers",
    "marker-blockers": "/api/review/marker-blockers",
    "key-paper-coverage": "/api/review/key-paper-coverage",
    "manual-import": "/api/review/manual-import",
    "institution-audit": "/api/review/institution-cleanup",
  };
  Object.keys(paths).filter((name) => !["dashboard", "institution-audit"].includes(name)).forEach((name) => {
    state.reviewQueues[name] = { available: true, records: [], hidden_resolved: 0 };
    renderReviewQueue(name);
  });
  try {
    const entries = await Promise.all(
      Object.entries(paths).map(async ([name, path]) => [name, await apiFetch(path)])
    );
    entries.forEach(([name, payload]) => {
      if (name === "dashboard") {
        state.dashboard = payload.data || {};
        if (state.dashboard.author_mapping_coverage) {
          state.authorMappingCoverage = state.dashboard.author_mapping_coverage;
        }
      }
      else if (name === "institution-audit") state.institutionAudit = payload.data || { records: [], summary: {} };
      else state.reviewQueues[name] = payload.data || {};
    });
    renderDashboard();
    renderMappingCoverage();
    Object.keys(state.reviewQueues).forEach(renderReviewQueue);
    renderInstitutionAudit();
  } catch (error) {
    showNotice(`Review queues could not be loaded: ${error.message}`, "error");
  } finally {
    buttons.forEach((button) => {
      button.disabled = false;
    });
  }
  await loadAuthorMappingCoverage({ showError: false });
}

async function loadAuthorMappingCoverage({ showError = true } = {}) {
  const buttons = [elements["reload-mapping-coverage-full"]].filter(Boolean);
  buttons.forEach((button) => {
    button.disabled = true;
  });
  try {
    const payload = await apiFetch(
      `/api/review/author-mapping-coverage?reload=${Date.now()}`
    );
    state.authorMappingCoverage = payload.data || {};
  } catch (error) {
    state.authorMappingCoverage = {
      available: false,
      message: "Author mapping report has not been generated.",
      records: [],
    };
    if (showError) {
      showNotice(
        "Mapping coverage could not be loaded. Restart the local Admin server and generate the report.",
        "error"
      );
    }
  } finally {
    buttons.forEach((button) => {
      button.disabled = false;
    });
  }
  renderMappingCoverage();
}

async function generateAuthorMappingReport() {
  const buttons = [
    elements["generate-mapping-report"],
    elements["generate-mapping-report-full"],
  ];
  buttons.forEach((button) => {
    button.disabled = true;
    button.textContent = "Generating…";
  });
  try {
    const payload = await apiFetch(
      "/api/review/author-mapping-coverage/generate",
      { method: "POST" }
    );
    state.authorMappingCoverage = payload.data || {};
    renderMappingCoverage();
    await loadDashboardAndQueues();
    showNotice(payload.message || "Author mapping report generated.");
  } catch (error) {
    showNotice(`Author mapping report could not be generated: ${error.message}`, "error");
  } finally {
    buttons.forEach((button) => {
      button.disabled = false;
      button.textContent = "Generate Report";
    });
  }
}

function navigateConsole(target) {
  const targets = {
    dashboard: elements["dashboard-panel"],
    papers: elements.workspace,
    "add-paper": elements["add-paper-panel"],
    "arxiv-enrichment": elements["arxiv-enrichment-panel"],
    "scope-review": elements.workspace,
    mappings: document.querySelector(".mappings-section"),
    "institution-management": elements["institution-management-panel"],
    "location-review": elements["location-review-panel"],
    "high-risk": elements["high-risk-review-panel"],
    "institution-audit": elements["institution-audit-panel"],
    "marker-blockers": elements["marker-blocker-review-panel"],
    "key-coverage": elements["key-coverage-review-panel"],
    "author-mapping-coverage": elements["author-mapping-coverage-panel"],
    "manual-import": elements["manual-import-review-panel"],
    validation: elements["workflow-panel"],
    publish: elements["workflow-panel"],
    workflows: elements["workflow-panel"],
  };
  if (target === "add-paper") openAddPaperPanel();
  if (target === "location-review") openLocationReview();
  if (target === "institution-management") openInstitutionManagement();
  if (target === "arxiv-enrichment") loadArxivEnrichment();
  const node = targets[target];
  if (!node) return;
  document.querySelectorAll("[data-console-target]").forEach((control) => {
    if (control.dataset.consoleTarget === target) control.setAttribute("aria-current", "page");
    else control.removeAttribute("aria-current");
  });
  document.querySelectorAll(".nav-menu").forEach((menu) => {
    menu.dataset.childActive = String(Boolean(menu.querySelector('[aria-current="page"]')));
    menu.open = false;
  });
  if ("hidden" in node) node.hidden = false;
  node.scrollIntoView({ behavior: "smooth", block: "start" });
  if (["mappings", "scope-review"].includes(target) && !state.selectedPaper) {
    showNotice("Select a paper first, then open its curation editor.", "error");
  }
}

function renderDashboard() {
  const metrics = (state.dashboard.project_health?.groups || [])
    .flatMap((group) => group.metrics || []);
  const wanted = {
    marker_blockers: { title: "Marker blockers", priority: 1, impact: "Preventing papers from appearing correctly on the public map." },
    identity_unresolved: { title: "Unresolved paper identities", priority: 2, impact: "Canonical papers cannot yet be resolved reliably." },
    retracted_publications: { title: "Retracted or invalid publications", priority: 3, impact: "Publication status may make public display incorrect." },
    missing_author_mappings: { title: "Missing author mappings", priority: 4, impact: "Author identities cannot yet be resolved reliably." },
    missing_affiliations: { title: "Missing affiliations", priority: 4, impact: "Papers are missing institution context on the public map." },
    missing_coordinates: { title: "Missing institution locations", priority: 5, impact: "Institutions cannot be placed on the map." },
    high_risk_markers: { title: "High-risk papers", priority: 6, impact: "Low-confidence metadata needs review before release." },
    key_paper_coverage_queue: { title: "Key-paper coverage", priority: 7, impact: "Important corpus coverage needs maintainer review." },
    manual_import_queue: { title: "Manual imports", priority: 7, impact: "Imported records still need cleanup or confirmation." },
  };
  const queue = metrics.filter((metric) =>
    wanted[metric.key] && metric.available !== false && Number(metric.value) > 0
  ).sort((left, right) => wanted[left.key].priority - wanted[right.key].priority);
  elements["dashboard-grid"].replaceChildren();
  elements["action-queue-empty"].hidden = queue.length !== 0;
  queue.slice(0, 5).forEach((metric) => {
    const copy = wanted[metric.key];
    const row = document.createElement("button");
    row.type = "button";
    row.className = "action-queue-row";
    row.setAttribute("aria-label", `${copy.title}: ${metric.value}. ${copy.impact} Review`);
    const description = document.createElement("span");
    const label = document.createElement("strong");
    label.textContent = copy.title;
    const impact = document.createElement("span");
    impact.className = "action-impact";
    impact.textContent = copy.impact;
    description.append(label, impact);
    const count = document.createElement("span");
    count.className = "action-count";
    count.textContent = formatNumber(metric.value);
    const action = document.createElement("span");
    action.className = "action-link";
    action.textContent = "Review";
    row.append(description, count, action);
    row.addEventListener("click", () => navigateProjectHealthMetric(metric));
    elements["dashboard-grid"].append(row);
  });
  if (queue.length > 5) {
    const expand = document.createElement("button");
    expand.type = "button";
    expand.className = "text-button queue-expand";
    expand.textContent = "View all review queues";
    expand.addEventListener("click", () => navigateConsole("validation"));
    elements["dashboard-grid"].append(expand);
  }
}

function initializeNavigationMenus() {
  const menus = [...document.querySelectorAll(".nav-menu")];
  menus.forEach((menu, index) => {
    const trigger = menu.querySelector("summary");
    const popup = menu.querySelector(".nav-menu-items");
    popup.id = popup.id || `admin-nav-menu-${index + 1}`;
    trigger.setAttribute("aria-controls", popup.id);
    trigger.setAttribute("aria-expanded", "false");
    menu.addEventListener("toggle", () => {
      trigger.setAttribute("aria-expanded", String(menu.open));
      if (menu.open) menus.filter((other) => other !== menu).forEach((other) => { other.open = false; });
    });
    trigger.addEventListener("keydown", (event) => {
      if (!["ArrowDown", "ArrowUp", "Escape"].includes(event.key)) return;
      event.preventDefault();
      if (event.key === "Escape") { menu.open = false; trigger.focus(); return; }
      menu.open = true;
      const items = [...popup.querySelectorAll('[role="menuitem"]')];
      items[event.key === "ArrowUp" ? items.length - 1 : 0]?.focus();
    });
    popup.addEventListener("keydown", (event) => {
      const items = [...popup.querySelectorAll('[role="menuitem"]')];
      const current = items.indexOf(document.activeElement);
      if (event.key === "Escape") { event.preventDefault(); menu.open = false; trigger.focus(); }
      if (["ArrowDown", "ArrowUp"].includes(event.key)) {
        event.preventDefault();
        const delta = event.key === "ArrowDown" ? 1 : -1;
        items[(current + delta + items.length) % items.length]?.focus();
      }
    });
  });
  document.addEventListener("click", (event) => {
    menus.filter((menu) => !menu.contains(event.target)).forEach((menu) => { menu.open = false; });
  });
}

function closeGlobalSearch() {
  elements["global-search-results"].hidden = true;
  elements["global-search-input"].setAttribute("aria-expanded", "false");
}

function renderGlobalSearch() {
  const query = normalize(elements["global-search-input"].value);
  const results = elements["global-search-results"];
  results.replaceChildren();
  if (query.length < 2) { closeGlobalSearch(); return; }
  const matches = state.papers.filter((paper) => normalize([
    paper.title, paper.doi, paper.arxiv_id, paper.authors, paper.affiliations,
    paper.institutions, paper.openalex_id,
  ].map((value) => typeof value === "object" ? JSON.stringify(value) : text(value)).join(" ")).includes(query)).slice(0, 8);
  matches.forEach((paper) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "global-search-result";
    button.setAttribute("role", "option");
    const title = document.createElement("strong");
    title.textContent = text(paper.title) || "Untitled paper";
    const meta = document.createElement("small");
    meta.textContent = `Paper · ${text(paper.doi || paper.arxiv_id || paper.display_id) || "local record"}`;
    button.append(title, meta);
    button.addEventListener("click", () => {
      elements["search-input"].value = text(paper.title);
      applyFilters();
      navigateConsole("papers");
      closeGlobalSearch();
    });
    results.append(button);
  });
  if (!matches.length) results.textContent = "No matching local records.";
  results.hidden = false;
  elements["global-search-input"].setAttribute("aria-expanded", "true");
}

function handleGlobalSearchKeydown(event) {
  const options = [...elements["global-search-results"].querySelectorAll('[role="option"]')];
  if (event.key === "Escape") { closeGlobalSearch(); elements["global-search-input"].focus(); }
  if (event.key === "ArrowDown" && options.length) { event.preventDefault(); options[0].focus(); }
}

function navigateProjectHealthMetric(metric) {
  const navigation = metric.navigation || {};
  if (metric.target === "author-mapping-coverage") {
    elements["mapping-coverage-status"].value = navigation.mapping_status || "";
    elements["mapping-coverage-sort"].value = navigation.mapping_sort || "rank-asc";
    renderFullMappingCoverage();
  }
  if (metric.target === "location-review" && navigation.location_status) {
    state.locationStatusFilter = navigation.location_status;
    renderLocationSummary();
    renderLocationReviewList();
  }
  navigateConsole(metric.target);
}

function mappingStatusBadge(status) {
  const variants = { complete: "curated", partial: "restored", zero: "excluded" };
  return makeBadge(humanize(status), variants[status] || "map");
}

function mappingTextCell(value) {
  const cell = document.createElement("td");
  cell.textContent = text(value) || "—";
  return cell;
}

function mappingCoverageRow(row, { includeRank = false } = {}) {
  const tr = document.createElement("tr");
  if (includeRank) tr.append(mappingTextCell(row.priority_rank));

  const statusCell = document.createElement("td");
  statusCell.append(mappingStatusBadge(row.mapping_status));
  const priorityCell = mappingTextCell(row.priority);

  const titleCell = document.createElement("td");
  titleCell.className = "mapping-report-title";
  const titleButton = document.createElement("button");
  titleButton.type = "button";
  titleButton.className = "mapping-report-link";
  titleButton.textContent = text(row.title) || "Untitled paper";
  titleButton.addEventListener("click", () => openCoverageMappingEditor(row));
  titleCell.append(titleButton);

  const missingCell = document.createElement("td");
  missingCell.className = "mapping-report-missing-authors";
  if (row.missing_authors) {
    const names = document.createElement("span");
    names.textContent = text(row.missing_author_names) || "Unnamed authors";
    const locateButton = document.createElement("button");
    locateButton.type = "button";
    locateButton.className = "secondary-button compact-action";
    locateButton.textContent = "Map missing authors";
    locateButton.addEventListener("click", () => {
      openCoverageMappingEditor(row, { mapMissingAuthors: true });
    });
    missingCell.append(names, locateButton);
  } else {
    missingCell.textContent = "—";
  }

  const evidenceCell = document.createElement("td");
  evidenceCell.className = "mapping-report-evidence";
  const institutions = document.createElement("span");
  institutions.textContent =
    text(row.known_canonical_institutions) || "No canonical institution yet";
  evidenceCell.append(institutions);
  if (
    row.existing_mapping_authors
    || row.suggested_author_matches
    || row.raw_affiliation_evidence
    || row.doi
    || row.arxiv_id
    || row.openalex_id
  ) {
    const evidence = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Review evidence";
    evidence.append(summary);
    [
      ["Mapping state", humanize(row.current_mapping_state)],
      ["Mapped author text", row.existing_mapping_authors],
      ["Suggested name reconciliation", row.suggested_author_matches],
      ["Raw affiliation", row.raw_affiliation_evidence],
      ["DOI", row.doi],
      ["arXiv", row.arxiv_id],
      ["OpenAlex", row.openalex_id],
    ]
      .filter(([, value]) => text(value))
      .forEach(([label, value]) => {
        const line = document.createElement("p");
        const strong = document.createElement("strong");
        strong.textContent = `${label}: `;
        line.append(strong, document.createTextNode(text(value)));
        evidence.append(line);
      });
    evidenceCell.append(evidence);
  }

  tr.append(statusCell, priorityCell, titleCell, mappingTextCell(row.year));
  if (includeRank) {
    tr.append(
      mappingTextCell(
        `${formatNumber(row.mapped_authors)} / ${formatNumber(row.total_authors)}`
      )
    );
  }
  tr.append(
    mappingTextCell(row.missing_authors),
    missingCell,
    evidenceCell,
    mappingTextCell(row.suggested_action),
    mappingTextCell(row.public_impact),
    mappingTextCell(row.marker_count),
    mappingTextCell(row.is_key_paper ? "Yes" : "—")
  );
  return tr;
}

function priorityPaperRow(row) {
  const tr = document.createElement("tr");
  const paper = mappingTextCell(row.title || "Untitled paper");
  paper.className = "priority-paper-title";
  const issue = mappingTextCell(
    row.mapping_status === "zero"
      ? "No resolved author mappings"
      : `${formatNumber(row.missing_authors)} missing author mapping${Number(row.missing_authors) === 1 ? "" : "s"}`
  );
  const impact = mappingTextCell(row.public_impact || "May affect public-map coverage");
  const action = document.createElement("td");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "secondary-button compact-action";
  button.textContent = "Review";
  button.setAttribute("aria-label", `Review ${text(row.title) || "priority paper"}`);
  button.addEventListener("click", () => openCoverageMappingEditor(row));
  action.append(button);
  tr.append(paper, issue, impact, action);
  return tr;
}

function renderMappingCoverage() {
  const report = state.authorMappingCoverage;
  const summaryNode = elements["mapping-coverage-summary"];
  const priorityBody = elements["mapping-priority-rows"];
  summaryNode.replaceChildren();
  priorityBody.replaceChildren();
  elements["mapping-coverage-counts"].textContent = report?.available
    ? suppressionCountText(report)
    : "";
  if (!report?.available) {
    summaryNode.hidden = true;
    elements["mapping-coverage-empty-state"].hidden = false;
    elements["mapping-priority-heading"].hidden = true;
    elements["mapping-priority-table-wrap"].hidden = true;
    elements["mapping-priority-empty"].textContent = "";
    renderFullMappingCoverage();
    return;
  }
  summaryNode.hidden = false;
  elements["mapping-coverage-empty-state"].hidden = true;
  elements["mapping-priority-heading"].hidden = false;
  elements["mapping-priority-table-wrap"].hidden = false;
  const summary = report.summary || {};
  const priorityRows = (report.records || [])
    .filter((row) => row.mapping_status !== "complete")
    .slice(0, 5);
  priorityRows.forEach((row) => priorityBody.append(priorityPaperRow(row)));
  elements["mapping-priority-empty"].textContent = priorityRows.length
    ? ""
    : "No missing mappings are present in the report.";
  renderFullMappingCoverage();
}

function renderFullMappingCoverage() {
  const report = state.authorMappingCoverage;
  const body = elements["mapping-coverage-rows"];
  body.replaceChildren();
  if (!report?.available) {
    elements["mapping-coverage-full-empty-state"].hidden = false;
    elements["mapping-coverage-table-wrap"].hidden = true;
    elements["mapping-coverage-empty"].textContent = "";
    return;
  }
  elements["mapping-coverage-full-empty-state"].hidden = true;
  elements["mapping-coverage-table-wrap"].hidden = false;
  const search = normalize(elements["mapping-coverage-search"].value);
  const status = elements["mapping-coverage-status"].value;
  const triage = elements["mapping-coverage-triage"].value;
  const sort = elements["mapping-coverage-sort"].value;
  const keyFilter = elements["mapping-coverage-key"].value;
  const filtered = (report.records || []).filter((row) => {
    if (status === "warning" && row.mapping_status === "complete") return false;
    if (status && status !== "warning" && row.mapping_status !== status) return false;
    if (triage && row.triage_status !== triage) return false;
    if (keyFilter && String(Boolean(row.is_key_paper)) !== keyFilter) return false;
    return !search || normalize(Object.values(row).join(" ")).includes(search);
  });
  filtered.sort((left, right) => {
    if (sort === "rank-desc") return right.priority_rank - left.priority_rank;
    if (sort === "missing-desc") {
      return right.missing_authors - left.missing_authors
        || left.priority_rank - right.priority_rank;
    }
    if (sort === "missing-asc") {
      return left.missing_authors - right.missing_authors
        || left.priority_rank - right.priority_rank;
    }
    return left.priority_rank - right.priority_rank;
  });
  filtered.forEach((row) => body.append(mappingCoverageRow(row, { includeRank: true })));
  elements["mapping-coverage-empty"].textContent = filtered.length
    ? `${formatNumber(filtered.length)} report rows`
    : "No rows match these filters.";
}

function queuePanel(name) {
  return document.querySelector(`.review-queue-panel[data-queue="${name}"]`);
}

function queueFields(name, row) {
  return [
    row.priority || row.priority_rank || "—",
    row.title || row.requested_title,
    row.year || row.candidate_year,
    row.institution || row.institutions,
    row.institution_authors,
    row.review_type || row.blocker_type || row.missing_stage || "import candidate",
    row.recommended_action,
    row.current_public_preview_status || row.coverage_status || row.candidate_status || row.review_status,
    row.public_visibility_label || "Not visible on map",
  ];
}

function suppressionCountText(queue, unresolvedCount = null) {
  const reasons = Object.entries(queue.suppression_reasons || {});
  const breakdown = reasons.length
    ? ` · ${reasons.map(([reason, count]) => `${humanize(reason)}: ${formatNumber(count)}`).join(" · ")}`
    : "";
  const unresolved = unresolvedCount === null
    ? (queue.records || []).length
    : unresolvedCount;
  return `${formatNumber(unresolved)} unresolved · ${formatNumber(queue.hidden_resolved || 0)} hidden/resolved${breakdown}`;
}

function reviewRecordKey(row) {
  return [
    row.paper_id,
    row.doi,
    row.openalex_url || row.openalex_id,
    row.title || row.requested_title,
    row.year || row.candidate_year,
    row.institution || row.institutions,
    row.institution_authors,
    row.review_type || row.blocker_type || row.missing_stage || row.candidate_status,
  ].map((value) => normalize(value)).join("|");
}

function clearReviewDetail(name) {
  delete state.selectedReviewKeys[name];
  const detail = queuePanel(name)?.querySelector('[data-role="detail"]');
  if (detail) detail.textContent = "Select a row.";
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
  const visibleKeys = new Set(filtered.map(reviewRecordKey));
  if (
    state.selectedReviewKeys[name]
    && !visibleKeys.has(state.selectedReviewKeys[name])
  ) clearReviewDetail(name);
  const counts = panel.querySelector('[data-role="counts"]');
  if (counts) counts.textContent = suppressionCountText(queue, filtered.length);
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

function renderInstitutionAudit() {
  if (!elements["institution-audit-rows"]) return;
  const audit = state.institutionAudit || { records: [], summary: {} };
  const search = normalize(elements["institution-audit-search"].value);
  const severity = elements["institution-audit-severity"].value;
  const provenance = elements["institution-audit-provenance"].value;
  const issueType = elements["institution-audit-issue"].value;
  const records = (audit.records || []).filter((row) => {
    if (row.status !== "open") return false;
    if (severity && row.severity !== severity) return false;
    if (provenance && !(row.provenance_values || []).includes(provenance)) return false;
    if (issueType && !(row.issue_types || []).includes(issueType)) return false;
    return !search || normalize(Object.values(row).join(" ")).includes(search);
  });
  const summary = audit.summary || {};
  elements["institution-audit-counts"].textContent = `${audit.total_unresolved || 0} open · ${summary.high || 0} high · ${summary.medium || 0} medium · ${summary.low || 0} low · ${audit.resolved_count || 0} resolved · ${audit.archived_count || 0} archived`;
  const blocker = elements["institution-cleanup-blocker"];
  const blockingCount = audit.blocking_count || 0;
  blocker.hidden = !(blockingCount > 0);
  blocker.querySelector("span").textContent = blockingCount > 0
    ? `Publishing is blocked by ${blockingCount} true institution-corruption finding${blockingCount === 1 ? "" : "s"}.`
    : "";
  elements["publish-changes"].disabled = blockingCount > 0;
  const body = elements["institution-audit-rows"];
  body.replaceChildren();
  records.forEach((item) => {
    const row = document.createElement("tr");
    const selectionCell = document.createElement("td");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = state.institutionCleanupSelection.has(item.review_group_id);
    checkbox.disabled = item.status !== "open" || !(item.queue_ids || []).length;
    checkbox.setAttribute("aria-label", `Select review case for ${item.paper_title || item.review_group_id}`);
    checkbox.addEventListener("click", (event) => event.stopPropagation());
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) state.institutionCleanupSelection.add(item.review_group_id);
      else state.institutionCleanupSelection.delete(item.review_group_id);
      updateInstitutionBatchActions();
    });
    selectionCell.append(checkbox);
    row.append(selectionCell);
    [item.severity, item.paper_title, item.author, (item.current_institutions || []).join("; "), (item.historical_institutions || []).join("; "), item.classification, (item.suggested_institutions || []).join("; ")].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });
    row.tabIndex = 0;
    row.addEventListener("click", () => renderInstitutionAuditDetail(item));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter") renderInstitutionAuditDetail(item);
    });
    body.append(row);
  });
  updateInstitutionBatchActions();
  elements["institution-audit-empty"].textContent = records.length ? "" : "No actionable open institution findings match these filters.";

  const archived = audit.archived_records || [];
  const archivedBody = elements["institution-archived-rows"];
  archivedBody.replaceChildren();
  archived.forEach((item) => {
    const row = document.createElement("tr");
    row.className = "archived-finding-row";
    const resolution = (item.findings || []).map((finding) =>
      [humanize(finding.resolution_action), finding.resolution_note]
        .filter(Boolean).join(": ")
    ).filter(Boolean).join(" | ");
    [
      humanize(item.status),
      item.paper_title,
      item.author,
      (item.historical_institutions || []).join("; ") || item.current_institution,
      (item.issue_types || []).map(humanize).join("; "),
      resolution,
      item.updated_at,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });
    row.tabIndex = 0;
    row.addEventListener("click", () => openInstitutionEvidence(item));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter") openInstitutionEvidence(item);
    });
    archivedBody.append(row);
  });
  elements["institution-archived-findings"].hidden = archived.length === 0;
  elements["institution-archived-findings"].open = false;
  elements["institution-archived-count"].textContent = `(${archived.length})`;
}

function selectedInstitutionCases() {
  return (state.institutionAudit?.records || []).filter((item) =>
    item.status === "open" && state.institutionCleanupSelection.has(item.review_group_id)
  );
}

function updateInstitutionBatchActions() {
  const selected = selectedInstitutionCases();
  const fixable = selected.flatMap((item) => item.findings || []).some((finding) =>
    finding.finding_status === "open" && finding.mapping_id && finding.suggested_institution_id
  );
  elements["institution-cleanup-batch"].disabled = !fixable;
  elements["institution-resolution-batch"].disabled = selected.length === 0;
}

function auditDetailLine(label, value) {
  const paragraph = document.createElement("p");
  const strong = document.createElement("strong");
  strong.textContent = `${label}: `;
  paragraph.append(strong, document.createTextNode(text(value) || "—"));
  return paragraph;
}

function renderInstitutionAuditDetail(item) {
  const detail = elements["institution-audit-detail"];
  detail.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = item.paper_title || "Institution review case";
  const actions = document.createElement("div");
  actions.className = "form-actions";
  const evidenceButton = document.createElement("button");
  evidenceButton.type = "button";
  evidenceButton.className = "secondary-button";
  evidenceButton.textContent = "View evidence";
  evidenceButton.addEventListener("click", () => openInstitutionEvidence(item));
  actions.append(evidenceButton);
  [["Accept suggestion", "accept_suggestion"], ["Keep multiple affiliations", "keep_multiple_affiliations"], ["Ignore finding", "ignore"]].forEach(([label, action]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = action === "ignore" ? "secondary-button" : "primary-button";
    button.textContent = label;
    button.addEventListener("click", () => resolveInstitutionAudit(item, action));
    actions.append(button);
  });
  const replace = document.createElement("button");
  replace.type = "button";
  replace.className = "secondary-button";
  replace.textContent = "Replace mapping";
  replace.addEventListener("click", async () => {
    const finding = (item.findings || [item])[0];
    const row = { ...finding, title: item.paper_title, institution: finding.current_institution };
    if (await openRelatedPaper(row)) openMappingDialog("replace");
  });
  const institution = document.createElement("button");
  institution.type = "button";
  institution.className = "secondary-button";
  institution.textContent = "Add alias / Open institution editor";
  institution.addEventListener("click", () => {
    elements["institution-management-search"].value = (item.current_institutions || [item.current_institution]).join(" ");
    openInstitutionManagement();
  });
  const parent = document.createElement("button");
  parent.type = "button";
  parent.className = "secondary-button";
  parent.textContent = "Set parent institution";
  parent.addEventListener("click", () => {
    elements["institution-management-search"].value = (item.current_institutions || [item.current_institution]).join(" ");
    openInstitutionManagement();
  });
  actions.append(replace, institution, parent);
  const manual = document.createElement("button");
  manual.type = "button";
  manual.className = "secondary-button";
  manual.textContent = "Mark manually resolved";
  manual.addEventListener("click", () => resolveInstitutionAudit(item, "manually_resolved"));
  actions.append(manual);
  detail.append(
    heading,
    auditDetailLine("Author", item.author),
    auditDetailLine("Current active institutions", (item.current_institutions || []).join("; ")),
    auditDetailLine("Historical/excluded institutions", (item.historical_institutions || []).join("; ")),
    auditDetailLine("Suggested institutions", (item.suggested_institutions || []).join("; ")),
    auditDetailLine("Evidence", (item.evidence || []).join(" | ")),
    auditDetailLine("Classification", item.classification),
    auditDetailLine("Provenance", (item.provenance_values || []).join("; ")),
    auditDetailLine("Why flagged", (item.findings || []).map((finding) => finding.reason).join(" | ")),
    actions,
  );
}

function evidenceSection(title) {
  const section = document.createElement("section");
  section.className = "evidence-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  section.append(heading);
  return section;
}

function appendEvidenceFields(section, fields) {
  const list = document.createElement("dl");
  list.className = "metadata-grid";
  fields.forEach(([label, value]) => {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    if (value instanceof Node) detail.append(value);
    else detail.textContent = text(value) || "—";
    list.append(term, detail);
  });
  section.append(list);
}

function evidenceList(values) {
  const list = document.createElement("ul");
  list.className = "evidence-list";
  (values || []).forEach((value) => {
    const item = document.createElement("li");
    item.textContent = text(value);
    list.append(item);
  });
  if (!list.children.length) {
    const item = document.createElement("li");
    item.textContent = "None recorded";
    list.append(item);
  }
  return list;
}

function evidenceLink(label, url) {
  const href = safeUrl(url);
  if (!href) return text(label || url);
  const link = document.createElement("a");
  link.href = href;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = text(label) || href;
  return link;
}

function openInstitutionEvidence(item) {
  state.institutionEvidenceCase = item;
  const evidence = item.evidence_detail || {};
  const paper = evidence.paper || {};
  const author = evidence.author || {};
  const affiliation = evidence.affiliation || {};
  const audit = evidence.audit || {};
  const risk = audit.risk_factors || {};
  const content = elements["institution-evidence-content"];
  content.replaceChildren();
  elements["institution-evidence-title"].textContent = item.paper_title || "Evidence inspection";

  const paperSection = evidenceSection("Paper information");
  appendEvidenceFields(paperSection, [
    ["Title", paper.title],
    ["Year", paper.year],
    ["Venue", paper.venue],
    ["DOI", paper.doi],
    ["arXiv identifier", paper.arxiv_id],
    ["Paper link", evidenceLink("Open paper", paper.paper_url)],
  ]);

  const authorSection = evidenceSection("Author information");
  appendEvidenceFields(authorSection, [["Author", author.name], ["Author ID", author.author_id]]);

  const mappingsSection = evidenceSection("Current mappings");
  (evidence.current_mappings || []).forEach((mapping) => {
    const heading = document.createElement("h4");
    heading.textContent = mapping.institution_name || "Current institution";
    mappingsSection.append(heading);
    appendEvidenceFields(mappingsSection, [
      ["Institution ID", mapping.institution_id],
      ["Provenance source", mapping.provenance_source || mapping.provenance],
      ["Mapping status", mapping.mapping_status],
      ["Review status", mapping.review_status],
      ["Evidence source", mapping.evidence_source],
      ["Evidence link", evidenceLink("Open evidence", mapping.evidence_url)],
      ["Review history", mapping.review_note],
    ]);
  });
  if (!(evidence.current_mappings || []).length) mappingsSection.append(evidenceList([]));

  const historicalSection = evidenceSection("Historical/excluded mappings");
  (evidence.historical_mappings || []).forEach((mapping) => {
    const heading = document.createElement("h4");
    heading.textContent = mapping.institution_name || "Historical institution";
    historicalSection.append(heading);
    appendEvidenceFields(historicalSection, [
      ["Institution ID", mapping.institution_id],
      ["Mapping status", mapping.mapping_status],
      ["Provenance source", mapping.provenance_source || mapping.provenance],
      ["Raw affiliation", mapping.raw_affiliation],
      ["Audit history", mapping.review_note],
    ]);
  });
  if (!(evidence.historical_mappings || []).length) historicalSection.append(evidenceList([]));

  const affiliationSection = evidenceSection("Affiliation evidence");
  const rawHeading = document.createElement("h4");
  rawHeading.textContent = "Raw affiliation text";
  affiliationSection.append(rawHeading);
  (affiliation.raw_affiliations || []).forEach((value) => {
    const raw = document.createElement("blockquote");
    raw.className = "evidence-raw";
    raw.textContent = value;
    affiliationSection.append(raw);
  });
  if (!(affiliation.raw_affiliations || []).length) affiliationSection.append(evidenceList([]));
  appendEvidenceFields(affiliationSection, [
    ["Parsed institution candidates", (affiliation.parsed_candidates || []).join("; ")],
    ["Original metadata sources", (affiliation.metadata_sources || []).join("; ")],
    ["Confidence", (affiliation.confidence || []).join("; ")],
  ]);

  const relationshipSection = evidenceSection("Institution relationships");
  (evidence.relationships || []).forEach((relationship) => {
    const heading = document.createElement("h4");
    heading.textContent = relationship.canonical_name || relationship.institution_id;
    relationshipSection.append(heading);
    appendEvidenceFields(relationshipSection, [
      ["Institution ID", relationship.institution_id],
      ["Aliases", (relationship.aliases || []).join("; ")],
      ["Parent", relationship.parent ? `${relationship.parent.canonical_name || relationship.parent.institution_id} (${relationship.parent.institution_id})` : ""],
      ["Children", (relationship.children || []).map((child) => `${child.canonical_name || child.institution_id} (${child.institution_id})`).join("; ")],
    ]);
  });
  if (!(evidence.relationships || []).length) relationshipSection.append(evidenceList([]));

  const auditSection = evidenceSection("Audit explanation and risk");
  appendEvidenceFields(auditSection, [
    ["Why flagged", (audit.why_flagged || []).join(" | ")],
    ["Provenance", (risk.provenance || []).join("; ")],
    ["Similarity score", (risk.similarity_scores || []).join("; ")],
    ["Issue type", (risk.issue_types || []).join("; ")],
    ["Severity", (risk.severities || []).join("; ")],
  ]);

  content.append(paperSection, authorSection, mappingsSection, historicalSection, affiliationSection, relationshipSection, auditSection);
  if (evidence.comparison) {
    const comparisonSection = evidenceSection("Suspicious replacement comparison");
    const comparison = document.createElement("div");
    comparison.className = "evidence-comparison";
    const before = evidenceSection("Before");
    appendEvidenceFields(before, [
      ["Current mapping", (evidence.comparison.before || []).join("; ")],
      ["Evidence", (evidence.comparison.evidence || []).join(" | ")],
    ]);
    const after = evidenceSection("After");
    appendEvidenceFields(after, [
      ["Suggested institution", (evidence.comparison.after || []).join("; ")],
      ["Similarity / reason", (evidence.comparison.reason || []).join(" | ")],
    ]);
    comparison.append(before, after);
    comparisonSection.append(comparison);
    content.append(comparisonSection);
  }
  renderInstitutionEvidenceActions(item);
  elements["institution-evidence-dialog"].showModal();
}

function closeInstitutionEvidence() {
  state.institutionEvidenceCase = null;
  elements["institution-evidence-dialog"].close();
}

function evidenceShortcut(label, handler, primary = false) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = primary ? "primary-button" : "secondary-button";
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

function renderInstitutionEvidenceActions(item) {
  const actions = elements["institution-evidence-actions"];
  actions.replaceChildren();
  if (item.status !== "open") {
    const note = document.createElement("p");
    note.className = "historical-mapping-availability";
    note.textContent = `${humanize(item.status)} audit record — no cleanup actions available`;
    actions.append(note);
    return;
  }
  const resolutionAction = (label, action, primary = false) => evidenceShortcut(label, () => {
    closeInstitutionEvidence();
    resolveInstitutionAudit(item, action);
  }, primary);
  actions.append(
    resolutionAction("Accept suggestion", "accept_suggestion", true),
    resolutionAction("Keep multiple affiliations", "keep_multiple_affiliations"),
    evidenceShortcut("Add alias", () => {
      closeInstitutionEvidence();
      elements["institution-management-search"].value = (item.current_institutions || []).join(" ");
      openInstitutionManagement();
    }),
    evidenceShortcut("Set parent institution", () => {
      closeInstitutionEvidence();
      elements["institution-management-search"].value = (item.current_institutions || []).join(" ");
      openInstitutionManagement();
    }),
    evidenceShortcut("Replace mapping", async () => {
      closeInstitutionEvidence();
      const finding = (item.findings || [item])[0];
      const row = { ...finding, title: item.paper_title, institution: finding.current_institution };
      if (await openRelatedPaper(row)) openMappingDialog("replace");
    }),
    resolutionAction("Mark manually resolved", "manually_resolved"),
  );
}

function resolveInstitutionAudit(item, action) {
  const queueIds = action === "accept_suggestion"
    ? (item.findings || []).filter((finding) => finding.finding_status === "open" && finding.mapping_id && finding.suggested_institution_id).map((finding) => finding.queue_id)
    : (item.queue_ids || [item.queue_id].filter(Boolean));
  if (!queueIds.length) return;
  openInstitutionResolutionDialog(item, action, queueIds);
}

const institutionResolutionNotes = {
  existing: "Confirmed existing curated institution mapping after manual review.",
  alias: "Resolved manually; alias/name variation only and existing mapping retained.",
  parent: "Resolved manually; confirmed parent-child institution relationship.",
  multiple: "Multiple affiliations confirmed after manual review.",
  custom: "",
};

const institutionResolutionLabels = {
  accept_suggestion: "Accept suggestion",
  keep_multiple_affiliations: "Keep multiple affiliations",
  ignore: "Ignore review case",
  manually_resolved: "Mark manually resolved",
};

function openInstitutionResolutionDialog(item, action, queueIds, batch = false) {
  const destructive = action === "accept_suggestion" || action === "replace_mapping";
  state.pendingInstitutionResolution = { item, action, queueIds, batch, destructive };
  elements["institution-resolution-title"].textContent = batch
    ? `Resolve ${item.batch_count} selected review cases`
    : "Resolve institution review case";
  elements["institution-resolution-issue"].textContent = (item.issue_types || [item.issue_type]).filter(Boolean).join(", ") || "—";
  elements["institution-resolution-paper"].textContent = text(item.paper_title) || "—";
  elements["institution-resolution-author"].textContent = text(item.author) || "—";
  elements["institution-resolution-current"].textContent = (item.current_institutions || [item.current_institution]).filter(Boolean).join("; ") || "—";
  elements["institution-resolution-action"].textContent = institutionResolutionLabels[action] || humanize(action);
  const preset = action === "keep_multiple_affiliations"
    ? "multiple"
    : item.classification === "alias issue"
      ? "alias"
      : item.classification === "parent-child issue"
        ? "parent"
        : "existing";
  elements["institution-resolution-preset"].value = preset;
  elements["institution-resolution-note"].required = destructive;
  elements["institution-resolution-note-optional"].hidden = destructive;
  elements["institution-resolution-error"].hidden = true;
  applyInstitutionResolutionPreset();
  elements["institution-resolution-dialog"].showModal();
}

function applyInstitutionResolutionPreset() {
  const preset = elements["institution-resolution-preset"].value;
  elements["institution-resolution-note"].value = institutionResolutionNotes[preset] || "";
  if (preset === "custom") elements["institution-resolution-note"].focus();
}

function closeInstitutionResolutionDialog() {
  state.pendingInstitutionResolution = null;
  elements["institution-resolution-dialog"].close();
}

function openBatchInstitutionResolution() {
  const cases = selectedInstitutionCases();
  const queueIds = cases.flatMap((item) => item.queue_ids || []);
  if (!queueIds.length) return;
  openInstitutionResolutionDialog({
    batch_count: cases.length,
    issue_types: [...new Set(cases.flatMap((item) => item.issue_types || []))],
    paper_title: cases.map((item) => item.paper_title).filter(Boolean).join("; "),
    author: cases.map((item) => item.author).filter(Boolean).join("; "),
    current_institutions: [...new Set(cases.flatMap((item) => item.current_institutions || []))],
    classification: "",
  }, "manually_resolved", queueIds, true);
}

async function submitInstitutionResolution(event) {
  event.preventDefault();
  const pending = state.pendingInstitutionResolution;
  if (!pending) return;
  let note = elements["institution-resolution-note"].value.trim();
  if (pending.destructive && !note) {
    elements["institution-resolution-error"].hidden = false;
    elements["institution-resolution-error"].textContent = "A review note is required because this action changes a mapping.";
    return;
  }
  if (pending.batch && note) note = `Batch resolution (${pending.item.batch_count} cases): ${note}`;
  elements["institution-resolution-submit"].disabled = true;
  try {
    await apiFetch(pending.batch && pending.action === "accept_suggestion"
      ? "/api/review/institution-cleanup/batch"
      : "/api/review/institution-cleanup/action", {
      method: "POST",
      body: JSON.stringify({
        queue_ids: pending.queueIds,
        action: pending.action,
        review_note: note,
        confirmed: pending.destructive,
      }),
    });
    const payload = await apiFetch("/api/review/institution-cleanup");
    state.institutionAudit = payload.data || { records: [], summary: {} };
    state.institutionCleanupSelection.clear();
    closeInstitutionResolutionDialog();
    renderInstitutionAudit();
    elements["institution-audit-detail"].textContent = "Select a paper-author review case.";
    showNotice(pending.action === "accept_suggestion" ? "Institution mapping corrected and cleanup finding resolved." : "Institution cleanup decision saved.");
  } catch (error) {
    elements["institution-resolution-error"].hidden = false;
    elements["institution-resolution-error"].textContent = error.message;
  } finally {
    elements["institution-resolution-submit"].disabled = false;
  }
}

function applySelectedInstitutionFixes() {
  const cases = selectedInstitutionCases();
  const findings = cases.flatMap((item) => item.findings || []).filter((finding) =>
    finding.finding_status === "open" && finding.mapping_id && finding.suggested_institution_id
  );
  const queueIds = findings.map((finding) => finding.queue_id);
  if (!queueIds.length) return;
  openInstitutionResolutionDialog({
    batch_count: cases.length,
    issue_types: [...new Set(cases.flatMap((item) => item.issue_types || []))],
    paper_title: cases.map((item) => item.paper_title).filter(Boolean).join("; "),
    author: cases.map((item) => item.author).filter(Boolean).join("; "),
    current_institutions: [...new Set(cases.flatMap((item) => item.current_institutions || []))],
    classification: "",
  }, "accept_suggestion", queueIds, true);
}

function renderReviewDetail(name, row) {
  const detail = queuePanel(name).querySelector('[data-role="detail"]');
  state.selectedReviewKeys[name] = reviewRecordKey(row);
  detail.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = text(row.title) || "Review row";
  const groups = [
    ["Paper", [["Title", row.title || row.requested_title], ["Year", row.year || row.candidate_year], ["DOI", row.doi], ["OpenAlex", row.openalex_url || row.openalex_id]]],
    ["Marker / Institution", [["Institution", row.institution || row.institutions], ["Institution authors", row.institution_authors], ["Location", [row.city, row.region, row.country].filter(Boolean).join(", ")]]],
    ["Evidence", [["Evidence source", row.evidence_source || row.source_file], ["Evidence URL", row.evidence_url], ["Resolution", row.resolution_notes || row.notes]]],
    ["Current curated status", [["Public visibility", row.public_visibility_label || "Not visible on map"], ["Status", row.current_public_preview_status || row.coverage_status || row.candidate_status || row.review_status], ["Review type", row.review_type || row.blocker_type || row.missing_stage]]],
    ["Recommended action", [["Action", row.recommended_action], ["Priority", row.priority]]],
  ];
  const grouped = document.createElement("div");
  grouped.className = "review-detail-groups";
  groups.forEach(([label, fields]) => {
    const section = document.createElement("section");
    const groupHeading = document.createElement("h4");
    groupHeading.textContent = label;
    const dl = document.createElement("dl");
    fields.filter(([, value]) => text(value)).forEach(([key, value]) => {
      const dt = document.createElement("dt");
      dt.textContent = key;
      const dd = document.createElement("dd");
      dd.textContent = text(value);
      dl.append(dt, dd);
    });
    section.append(groupHeading, dl);
    grouped.append(section);
  });
  const extra = document.createElement("details");
  extra.innerHTML = "<summary>Additional generated metadata</summary>";
  const extraDl = document.createElement("dl");
  Object.entries(row).filter(([, value]) => text(value)).forEach(([key, value]) => {
    const dt = document.createElement("dt"); dt.textContent = humanize(key);
    const dd = document.createElement("dd"); dd.textContent = text(value);
    extraDl.append(dt, dd);
  });
  extra.append(extraDl);
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
  detail.append(heading, grouped, extra, actions);
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
  const openalex = normalize(
    row.openalex_url
      || (row.openalex_id ? `https://openalex.org/${row.openalex_id}` : "")
  );
  const paperId = normalize(row.paper_id);
  const title = normalize(row.title);
  const year = text(row.year);
  return state.papers.find((paper) =>
    (paperId && [paper.display_id, paper.paper_id].map(normalize).includes(paperId)) ||
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

async function openCoverageMappingEditor(row, { mapMissingAuthors = false } = {}) {
  const paper = await openRelatedPaper(row);
  if (!paper) return;
  navigateConsole("mappings");
  if (mapMissingAuthors) {
    openMappingDialog("create", {
      institution_authors: row.missing_author_names,
    });
    elements["mapping-institution"].focus();
    showNotice(
      "Missing authors are prefilled. Add the verified institution and affiliation evidence."
    );
  }
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
    showNotice(payload.message);
    await loadDashboardAndQueues();
  } catch (error) {
    showNotice(`Could not save review action: ${error.message}`, "error");
  }
}

function applyLocationPayload(payload) {
  state.locationReviews = payload.records || [];
  state.confirmedLocations = payload.confirmed_locations || [];
  state.locationSummary = payload.summary || {};
  elements["location-review-counts"].textContent = suppressionCountText(payload);
  renderLocationSummary();
  renderLocationReviewList();
  if (state.locationEditorMode === "review" && state.selectedLocationReviewId) {
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

function openInstitutionManagement() {
  elements["institution-management-panel"].hidden = false;
  renderInstitutionManagement();
  elements["institution-management-panel"].scrollIntoView({ behavior: "smooth", block: "start" });
}

async function refreshInstitutions() {
  const payload = await apiFetch("/api/institutions");
  state.institutions = payload.records || [];
  renderInstitutionManagement();
}

function institutionActionButton(label, action, institution) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = action === "ignore" || action === "merge" ? "danger-button" : "secondary-button";
  button.textContent = label;
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    runInstitutionAction(action, institution);
  });
  return button;
}

function renderInstitutionManagement() {
  if (!elements["institution-management-rows"]) return;
  const query = normalize(elements["institution-management-search"].value);
  const records = state.institutions.filter((row) => normalize([
    row.canonical_name, row.institution_type, row.institution_status,
    ...(row.aliases || []), row.parent_institution_id,
  ].join(" ")).includes(query));
  const body = elements["institution-management-rows"];
  body.replaceChildren();
  records.forEach((institution) => {
    const row = document.createElement("tr");
    const identity = document.createElement("td");
    identity.append(document.createTextNode(institution.canonical_name), document.createElement("br"), document.createTextNode(institution.institution_id));
    const hierarchy = document.createElement("td");
    hierarchy.textContent = `${(institution.aliases || []).join(", ") || "No aliases"}${institution.parent_institution_id ? ` · parent ${institution.parent_institution_id}` : ""}`;
    const status = document.createElement("td");
    status.textContent = `${institution.institution_status} · ${institution.institution_type}`;
    const usage = document.createElement("td");
    const impact = institution.usage || {};
    usage.textContent = `${impact.papers || 0} papers · ${impact.author_mappings || 0} mappings · ${impact.markers || 0} markers · ${(impact.authors || []).length} authors`;
    const actions = document.createElement("td");
    actions.className = "form-actions";
    [
      ["Edit identity", "identity"], ["Edit location", "location"],
      ["Add alias", "alias"], ["Set parent", "parent"],
      ["Merge", "merge"], ["Ignore", "ignore"],
    ].forEach(([label, action]) => actions.append(institutionActionButton(label, action, institution)));
    row.append(identity, hierarchy, status, usage, actions);
    body.append(row);
  });
  elements["institution-management-empty"].hidden = records.length !== 0;
}

async function postInstitutionAction(path, body) {
  await apiFetch(path, { method: "POST", body: JSON.stringify(body) });
  await Promise.all([refreshInstitutions(), loadLocationReviews()]);
}

function shortInstitutionId(value) {
  return text(value).trim().replace(/^institution:/i, "");
}

function normalizeInstitutionMergeId(value) {
  const input = text(value).trim();
  if (!input) return "";
  const full = input.match(/^institution:([0-9a-f]{16})$/i);
  if (full) return `institution:${full[1].toLocaleLowerCase()}`;
  if (/^[0-9a-f]{16}$/i.test(input)) {
    return `institution:${input.toLocaleLowerCase()}`;
  }
  if (/institution:/i.test(input) || /^[0-9a-f]+$/i.test(input)) {
    throw new Error("Enter a valid 16-character short institution ID.");
  }
  return "";
}

function institutionMergeSearchText(institution) {
  return [
    institution.canonical_name,
    ...(institution.aliases || []),
    institution.institution_id,
    shortInstitutionId(institution.institution_id),
  ].join(" ").toLocaleLowerCase();
}

function availableInstitutionMergeTargets() {
  const sourceId = text(state.institutionMerge.source?.institution_id);
  return state.institutions.filter((institution) =>
    institution.institution_id !== sourceId
    && institution.institution_status === "active"
  );
}

function renderInstitutionMergeTargets() {
  const query = elements["institution-merge-search"].value.trim().toLocaleLowerCase();
  const matches = availableInstitutionMergeTargets()
    .filter((institution) => !query || institutionMergeSearchText(institution).includes(query))
    .slice(0, 100);
  const options = matches.map((institution) => {
    const option = document.createElement("option");
    option.value = institution.institution_id;
    option.textContent = `${institution.canonical_name} — ${shortInstitutionId(institution.institution_id)}`;
    return option;
  });
  elements["institution-merge-results"].replaceChildren(...options);
}

function selectInstitutionMergeResult() {
  const selectedId = elements["institution-merge-results"].value;
  if (selectedId) elements["institution-merge-search"].value = selectedId;
  hideInstitutionMergeError();
}

function showInstitutionMergeError(message) {
  elements["institution-merge-error"].textContent = message;
  elements["institution-merge-error"].hidden = false;
}

function hideInstitutionMergeError() {
  elements["institution-merge-error"].hidden = true;
  elements["institution-merge-error"].textContent = "";
}

function closeInstitutionMergeDialog() {
  if (state.institutionMerge.submitting) return;
  elements["institution-merge-dialog"].close();
  state.institutionMerge = { source: null, target: null, submitting: false };
}

function openInstitutionMergeDialog(source) {
  state.institutionMerge = { source, target: null, submitting: false };
  elements["institution-merge-form"].reset();
  elements["institution-merge-source-label"].textContent = source.canonical_name;
  elements["institution-merge-target-step"].hidden = false;
  elements["institution-merge-confirm-step"].hidden = true;
  elements["institution-merge-submit"].disabled = true;
  hideInstitutionMergeError();
  renderInstitutionMergeTargets();
  elements["institution-merge-dialog"].showModal();
  elements["institution-merge-search"].focus();
}

function resolveInstitutionMergeTarget() {
  hideInstitutionMergeError();
  try {
    const input = elements["institution-merge-search"].value.trim();
    if (!input) throw new Error("Choose or enter a target institution.");
    const normalizedId = normalizeInstitutionMergeId(input);
    let matches = [];
    if (normalizedId) {
      matches = state.institutions.filter((row) => row.institution_id === normalizedId);
      if (!matches.length) throw new Error(`Unknown canonical institution ID: ${normalizedId}`);
    } else {
      const key = canonicalInstitutionKey(input);
      matches = state.institutions.filter((row) => [
        row.canonical_name,
        ...(row.aliases || []),
      ].some((name) => canonicalInstitutionKey(name) === key));
      if (!matches.length) throw new Error("No canonical institution matches that name or alias.");
      if (matches.length > 1) throw new Error("That name or alias is ambiguous; select a canonical target from the results.");
    }
    const target = matches[0];
    const source = state.institutionMerge.source;
    if (target.institution_id === source.institution_id) {
      throw new Error("Source and target institutions must differ.");
    }
    if (target.institution_status !== "active") {
      throw new Error("The target institution must be active in the canonical registry.");
    }
    state.institutionMerge.target = target;
    elements["institution-merge-source-name"].textContent = source.canonical_name;
    elements["institution-merge-source-id"].textContent = shortInstitutionId(source.institution_id);
    elements["institution-merge-target-name"].textContent = target.canonical_name;
    elements["institution-merge-target-id"].textContent = shortInstitutionId(target.institution_id);
    elements["institution-merge-target-step"].hidden = true;
    elements["institution-merge-confirm-step"].hidden = false;
    elements["institution-merge-submit"].disabled = false;
    elements["institution-merge-submit"].focus();
  } catch (error) {
    state.institutionMerge.target = null;
    elements["institution-merge-submit"].disabled = true;
    showInstitutionMergeError(error.message);
  }
}

async function submitInstitutionMerge(event) {
  event.preventDefault();
  if (state.institutionMerge.submitting) return;
  hideInstitutionMergeError();
  const { source, target } = state.institutionMerge;
  if (!source || !target) {
    showInstitutionMergeError("Resolve a canonical target before merging.");
    elements["institution-merge-submit"].disabled = true;
    return;
  }
  const backendConfirmation =
    `REPLACE ${source.canonical_name} WITH ${target.canonical_name} GLOBALLY`;
  state.institutionMerge.submitting = true;
  elements["institution-merge-submit"].disabled = true;
  try {
    await apiFetch("/api/institution/merge", {
      method: "POST",
      body: JSON.stringify({
        source_institution_id: source.institution_id,
        target_institution_id: target.institution_id,
        confirmation: backendConfirmation,
      }),
    });
    state.institutionMerge.submitting = false;
    elements["institution-merge-dialog"].close();
    state.institutionMerge = { source: null, target: null, submitting: false };
    showNotice("Institution merge saved.");
    try {
      await Promise.all([refreshInstitutions(), loadLocationReviews()]);
    } catch (refreshError) {
      showNotice(`Institution merge saved, but refresh failed: ${refreshError.message}`, "error");
    }
  } catch (error) {
    state.institutionMerge.submitting = false;
    showInstitutionMergeError(`Merge failed: ${error.message}`);
    elements["institution-merge-submit"].disabled = false;
  }
}

async function runInstitutionAction(action, institution) {
  try {
    if (action === "location") {
      await openCanonicalInstitutionLocation(institution);
      return;
    }
    if (action === "identity") {
      const canonicalName = window.prompt("Canonical name (identity only; this does not reassign mappings):", institution.canonical_name);
      if (!canonicalName) return;
      const institutionType = window.prompt("Institution type: university, department, institute, laboratory, company, or research_unit", institution.institution_type);
      if (!institutionType) return;
      await postInstitutionAction("/api/institution/identity", { institution_id: institution.institution_id, canonical_name: canonicalName, institution_type: institutionType, institution_status: institution.institution_status });
    } else if (action === "alias") {
      const aliasName = window.prompt("Alias to resolve to this canonical institution:");
      if (!aliasName) return;
      await postInstitutionAction("/api/institution/alias", { institution_id: institution.institution_id, alias_name: aliasName, review_note: "Confirmed in institution management." });
    } else if (action === "parent") {
      const parentId = window.prompt("Parent institution ID (blank removes parent):", institution.parent_institution_id || "");
      if (parentId === null) return;
      await postInstitutionAction("/api/institution/parent", { institution_id: institution.institution_id, parent_institution_id: parentId });
    } else if (action === "ignore") {
      if (!window.confirm("This hides this institution from public outputs without deleting data.")) return;
      const note = window.prompt("Review note for the audit trail:");
      if (!note) return;
      await postInstitutionAction("/api/institution/ignore", { institution_id: institution.institution_id, confirmation: true, review_note: note });
    } else if (action === "merge") {
      openInstitutionMergeDialog(institution);
      return;
    }
    showNotice(`Institution ${action} action saved.`);
  } catch (error) {
    showNotice(`Institution action failed: ${error.message}`, "error");
  }
}

async function openCanonicalInstitutionLocation(institution) {
  const identifier = text(institution?.institution_id);
  if (!identifier) throw new Error("The selected canonical institution has no institution_id.");
  const requestSequence = ++institutionLocationSequence;
  geocodeRequestSequence += 1;
  state.locationEditorMode = "canonical";
  state.selectedInstitutionLocationId = identifier;
  state.selectedLocationReviewId = "";
  state.selectedGeocodeCandidate = null;
  openLocationReview();
  showLocationEditorPlaceholder(
    "Loading institution location…",
    `Loading canonical institution ${identifier}.`
  );
  elements["location-form"].hidden = true;
  renderLocationReviewList();
  try {
    const payload = await apiFetch(`/api/institution?institution_id=${encodeURIComponent(identifier)}`);
    if (!isActiveCanonicalLocationRequest(requestSequence, identifier)) return;
    const detail = payload.data || {};
    if (text(detail.institution?.institution_id) !== identifier) {
      throw new Error("Loaded institution details do not match the selected institution_id.");
    }
    selectCanonicalInstitutionLocation(detail);
  } catch (error) {
    if (!isActiveCanonicalLocationRequest(requestSequence, identifier)) return;
    elements["location-form"].hidden = true;
    showLocationEditorPlaceholder(
      "Could not load institution location",
      error.message
    );
  }
}

function isActiveCanonicalLocationRequest(requestSequence, identifier) {
  return requestSequence === institutionLocationSequence &&
    state.locationEditorMode === "canonical" &&
    state.selectedInstitutionLocationId === identifier;
}

function showLocationEditorPlaceholder(title, message) {
  const placeholder = elements["location-editor-placeholder"];
  placeholder.hidden = false;
  placeholder.querySelector("h3").textContent = title;
  placeholder.querySelector("p").textContent = message;
}

function selectCanonicalInstitutionLocation(detail) {
  const institution = detail.institution || {};
  const identifier = text(institution.institution_id);
  const location = detail.current_location || detail.location || {};
  const review = (detail.location_reviews || [])[0] || {};
  state.locationEditorMode = "canonical";
  state.selectedInstitutionLocationId = identifier;
  state.selectedLocationReviewId = "";
  clearLocationFields();
  elements["location-editor-placeholder"].hidden = true;
  elements["location-form"].hidden = false;
  elements["location-form"].reset();
  elements["location-queue-id"].value = "";
  elements["location-institution-id"].value = identifier;
  elements["confirmed-institution"].value = text(institution.canonical_name);
  elements["institution-language"].value = text(review.detected_language);
  elements["institution-review-status"].value = text(review.review_status || "pending_review");
  const canonicalSelect = elements["canonical-institution"];
  canonicalSelect.replaceChildren(new Option(institution.canonical_name, institution.canonical_name));
  canonicalSelect.value = institution.canonical_name;
  elements["confirmed-city"].value = text(location.city || review.suggested_city);
  elements["confirmed-region"].value = text(location.region);
  elements["confirmed-country"].value = text(location.country || review.suggested_country);
  elements["confirmed-country-code"].value = text(location.country_code).toUpperCase();
  elements["confirmed-lat"].value = text(location.lat);
  elements["confirmed-lon"].value = text(location.lon);
  elements["coordinate-source"].value = text(location.coordinate_source);
  elements["coordinate-source-url"].value = text(location.coordinate_source_url);
  elements["coordinate-review-note"].value = text(location.review_note || review.review_note);
  elements["location-form-error"].hidden = true;
  renderLocationActions();
  renderCanonicalLocationContext(detail);
  elements["confirmed-city"].focus();
  showNotice(`Editing location for ${institution.canonical_name}; identity and mappings remain unchanged.`);
}

function renderCanonicalLocationContext(detail) {
  const institution = detail.institution || {};
  const location = detail.current_location || detail.location || {};
  const reviews = detail.location_reviews || [];
  const fields = [
    ["Canonical institution ID", institution.institution_id],
    ["Canonical institution name", institution.canonical_name],
    ["Aliases", (detail.aliases || []).map((row) => row.alias_name).join("; ")],
    ["Current location", [location.city, location.region, location.country].filter(Boolean).join(", ")],
    ["Current location review", reviews.map((row) => row.review_status).filter(Boolean).join("; ")],
    ["Affiliation evidence", (detail.affiliation_evidence || []).map((row) => row.raw_affiliation).filter(Boolean).join("; ")],
  ];
  elements["location-context"].replaceChildren();
  fields.forEach(([label, value]) => {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    paragraph.append(strong, text(value) || "—");
    elements["location-context"].append(paragraph);
  });
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
    const candidateCount = (row.candidate_suggestions || []).length;
    diagnostic.textContent = `Diagnostics: ${humanize(row.location_status)} · ${humanize(row.coordinate_status)}${candidateCount ? ` · ${candidateCount} alias/duplicate candidate${candidateCount === 1 ? "" : "s"}` : ""}`;
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
  institutionLocationSequence += 1;
  geocodeRequestSequence += 1;
  state.locationEditorMode = "review";
  state.selectedInstitutionLocationId = text(row.institution_id);
  state.selectedLocationReviewId = queueId;
  renderLocationReviewList();
  elements["location-editor-placeholder"].hidden = true;
  elements["location-form"].hidden = false;
  elements["location-form"].reset();
  clearLocationFields();
  elements["location-queue-id"].value = queueId;
  elements["location-institution-id"].value = text(row.institution_id);
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
  renderLocationActions();
  renderLocationContext(row);
}

function renderLocationActions() {
  const hasCanonicalInstitution = Boolean(
    elements["canonical-institution"].value.trim()
  );
  elements["location-confirm-alias"].hidden = !hasCanonicalInstitution;
  elements["location-create-new"].hidden = hasCanonicalInstitution;
}

function positionLocationMoreActions() {
  const disclosure = elements["location-more-actions"];
  const menu = elements["location-more-actions-menu"];
  if (!disclosure.open) return;

  const trigger = disclosure.querySelector("summary");
  const triggerRect = trigger.getBoundingClientRect();
  const viewportWidth = window.visualViewport?.width || window.innerWidth;
  const viewportHeight = window.visualViewport?.height || window.innerHeight;
  const viewportMargin = 8;
  const triggerGap = 6;
  const menuWidth = Math.min(menu.offsetWidth, viewportWidth - viewportMargin * 2);
  const menuHeight = menu.offsetHeight;
  const spaceBelow = viewportHeight - triggerRect.bottom - viewportMargin - triggerGap;
  const spaceAbove = triggerRect.top - viewportMargin - triggerGap;
  const opensUpward = spaceBelow < menuHeight && spaceAbove > spaceBelow;
  const availableHeight = Math.max(opensUpward ? spaceAbove : spaceBelow, 0);

  menu.dataset.placement = opensUpward ? "top" : "bottom";
  menu.style.width = `${menuWidth}px`;
  menu.style.maxHeight = `${availableHeight}px`;
  menu.style.left = `${Math.max(
    viewportMargin,
    Math.min(triggerRect.right - menuWidth, viewportWidth - menuWidth - viewportMargin)
  )}px`;
  menu.style.top = `${opensUpward
    ? Math.max(viewportMargin, triggerRect.top - menuHeight - triggerGap)
    : Math.min(triggerRect.bottom + triggerGap, viewportHeight - viewportMargin)}px`;
}

function initializeLocationMoreActions() {
  const disclosure = elements["location-more-actions"];
  const menu = elements["location-more-actions-menu"];
  const trigger = disclosure.querySelector("summary");

  disclosure.addEventListener("toggle", () => {
    if (disclosure.open) positionLocationMoreActions();
  });
  disclosure.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && disclosure.open) {
      event.preventDefault();
      disclosure.open = false;
      trigger.focus();
    } else if (event.key === "ArrowDown" && document.activeElement === trigger) {
      event.preventDefault();
      disclosure.open = true;
      positionLocationMoreActions();
      menu.querySelector("button")?.focus();
    }
  });
  menu.addEventListener("click", (event) => {
    if (event.target.closest("button")) disclosure.open = false;
  });
  document.addEventListener("click", (event) => {
    if (disclosure.open && !disclosure.contains(event.target)) disclosure.open = false;
  });
  window.addEventListener("resize", positionLocationMoreActions);
  window.addEventListener("scroll", positionLocationMoreActions, { capture: true, passive: true });
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
    ["Affected papers", (row.affected_papers || []).map((paper) => [paper.title, paper.year].filter(Boolean).join(" · ")).join("; ")],
    ["Affected mappings", (row.affected_mappings || []).map((mapping) => [mapping.mapping_id, mapping.institution, mapping.mapping_status].filter(Boolean).join(" · ")).join("; ")],
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
  const candidates = row.candidate_suggestions || [];
  if (candidates.length) {
    const section = document.createElement("section");
    section.className = "institution-candidate-evidence";
    const heading = document.createElement("h4");
    heading.textContent = "Possible canonical matches — review only";
    section.append(heading);
    candidates.forEach((candidate) => {
      const card = document.createElement("article");
      const title = document.createElement("strong");
      title.textContent = candidate.canonical_institution_name;
      const location = candidate.canonical_record || {};
      const details = document.createElement("p");
      details.textContent = [
        candidate.evidence,
        [location.city, location.region, location.country].filter(Boolean).join(", "),
        location.lat !== undefined && location.lon !== undefined
          ? `${location.lat}, ${location.lon}`
          : "",
        (candidate.aliases || []).length ? `Aliases: ${candidate.aliases.join("; ")}` : "",
        (candidate.location_conflicts || []).length
          ? `Conflict: ${candidate.location_conflicts.join(", ")}`
          : "",
      ].filter(Boolean).join(" · ");
      const choose = document.createElement("button");
      choose.type = "button";
      choose.className = "secondary-button";
      choose.textContent = "Select as canonical alias target";
      choose.addEventListener("click", () => {
        elements["canonical-institution"].value = candidate.canonical_institution_name;
        renderLocationActions();
      });
      card.append(title, details, choose);
      section.append(card);
    });
    elements["location-context"].append(section);
  }
}

function clearLocationEditor() {
  institutionLocationSequence += 1;
  geocodeRequestSequence += 1;
  state.selectedInstitutionLocationId = "";
  state.selectedLocationReviewId = "";
  state.locationEditorMode = "review";
  showLocationEditorPlaceholder(
    "Select a queued institution",
    "Its paper context, affiliation evidence, suggestions, and current review state will appear here."
  );
  elements["location-form"].hidden = true;
  renderLocationReviewList();
}

function locationDraft() {
  return {
    queue_id: elements["location-queue-id"].value,
    institution_id: elements["location-institution-id"].value,
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

function geocodeAddress() {
  const entity = state.institutions.find(
    (row) => row.institution_id === elements["location-institution-id"].value
  );
  const parent = state.institutions.find(
    (row) => row.institution_id === entity?.parent_institution_id
  );
  return [
    elements["confirmed-city"].value.trim(),
    elements["confirmed-region"].value.trim(),
    elements["confirmed-country"].value.trim(),
    parent?.canonical_name,
  ].filter(Boolean).join(", ");
}

function clearLocationFields() {
  [
    "confirmed-city",
    "confirmed-region",
    "confirmed-country",
    "confirmed-country-code",
    "confirmed-lat",
    "confirmed-lon",
    "coordinate-source",
    "coordinate-source-url",
    "coordinate-review-note",
  ].forEach((id) => {
    elements[id].value = "";
  });
  state.selectedGeocodeCandidate = null;
}

function candidateDetail(label, value) {
  const row = document.createElement("span");
  const heading = document.createElement("strong");
  heading.textContent = `${label}: `;
  row.append(heading);
  if (text(value)) {
    row.append(text(value));
  } else {
    const missing = document.createElement("em");
    missing.className = "geocode-missing";
    missing.textContent = "Unavailable — manual review required";
    row.append(missing);
  }
  return row;
}

function renderGeocodeCandidates(result) {
  const candidates = result.candidates || [];
  state.selectedGeocodeCandidate = null;
  elements["geocode-query"].textContent = `Query: ${text(result.query)}`;
  elements["geocode-candidates"].replaceChildren();
  elements["geocode-candidates"].hidden = candidates.length === 0;
  elements["geocode-empty"].hidden = candidates.length !== 0 && !result.no_safe_match;
  elements["geocode-empty"].textContent = result.no_safe_match
    ? "No location-consistent candidate was found. Conflicting results cannot be selected; refine the confirmed city, region, or country."
    : "No location candidates were found. Existing form values are unchanged.";
  elements["geocode-error"].hidden = true;
  elements["geocode-confirm"].disabled = true;
  elements["geocode-replace-warning"].hidden = !(
    elements["confirmed-lat"].value.trim() || elements["confirmed-lon"].value.trim()
  );
  candidates.forEach((candidate, index) => {
    const label = document.createElement("label");
    label.className = "geocode-candidate";
    if (candidate.selectable === false) label.classList.add("geocode-candidate-conflict");
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "geocode-candidate";
    radio.value = String(index);
    radio.disabled = candidate.selectable === false;
    const content = document.createElement("span");
    const title = document.createElement("strong");
    title.textContent = text(candidate.institution_name || candidate.display_name);
    const address = candidateDetail("Full address", candidate.address || candidate.display_name);
    const coordinates = candidateDetail(
      "Coordinates",
      `${candidate.latitude}, ${candidate.longitude}`
    );
    const confidence = candidate.confidence === null || candidate.confidence === undefined
      ? ""
      : ` · relevance ${Number(candidate.confidence).toFixed(3)}`;
    coordinates.append(`${confidence} · ${text(candidate.provider)}`);
    content.append(
      title,
      address,
      candidateDetail("City", candidate.city),
      candidateDetail("Region/state", candidate.region),
      candidateDetail("Country", candidate.country),
      candidateDetail("ISO country code", candidate.country_code),
      candidateDetail("Latitude", candidate.latitude),
      candidateDetail("Longitude", candidate.longitude),
      coordinates
    );
    if ((candidate.conflicts || []).length) {
      content.append(candidateDetail("Evidence conflict", candidate.conflicts.join("; ")));
    }
    if ((candidate.ranking_factors || []).length) {
      content.append(candidateDetail("Ranking evidence", candidate.ranking_factors.join("; ")));
    }
    if (safeUrl(candidate.map_url)) {
      const mapLink = linkValue("Open in OpenStreetMap", candidate.map_url);
      content.append(mapLink);
    }
    radio.addEventListener("change", () => {
      state.selectedGeocodeCandidate = candidate;
      elements["geocode-confirm"].disabled = false;
    });
    label.append(radio, content);
    elements["geocode-candidates"].append(label);
  });
  elements["geocode-dialog"].showModal();
  (elements["geocode-candidates"].querySelector("input") || elements["geocode-cancel"]).focus();
}

async function findInstitutionCoordinates() {
  const button = elements["location-geocode"];
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "Searching…";
  elements["location-form-error"].hidden = true;
  const institutionId = elements["location-institution-id"].value.trim();
  const loadedInstitutionId = state.selectedInstitutionLocationId;
  if (!institutionId || institutionId !== loadedInstitutionId) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = "The location editor is not bound to the selected canonical institution.";
    button.disabled = false;
    button.textContent = originalLabel;
    return;
  }
  const requestSequence = ++geocodeRequestSequence;
  try {
    const payload = await apiFetch("/api/institution/geocode", {
      method: "POST",
      body: JSON.stringify({
        institution_id: institutionId,
        loaded_institution_id: loadedInstitutionId,
        city: elements["confirmed-city"].value.trim(),
        region: elements["confirmed-region"].value.trim(),
        country: elements["confirmed-country"].value.trim(),
        country_code: elements["confirmed-country-code"].value.trim().toUpperCase(),
      }),
    });
    if (
      requestSequence !== geocodeRequestSequence ||
      institutionId !== state.selectedInstitutionLocationId ||
      text(payload.data?.institution_id) !== institutionId
    ) return;
    renderGeocodeCandidates(payload.data || {});
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = `Coordinate search failed: ${error.message}`;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

function closeGeocodeDialog() {
  elements["geocode-dialog"].close();
}

function confirmGeocodeCandidate() {
  const candidate = state.selectedGeocodeCandidate;
  if (
    !candidate || candidate.selectable === false ||
    !state.selectedInstitutionLocationId ||
    state.selectedInstitutionLocationId !== elements["location-institution-id"].value
  ) return;
  const hasExisting = elements["confirmed-lat"].value.trim() || elements["confirmed-lon"].value.trim();
  if (hasExisting && !window.confirm("Replace the existing latitude and longitude with the selected candidate?")) {
    return;
  }
  elements["confirmed-lat"].value = candidate.latitude;
  elements["confirmed-lon"].value = candidate.longitude;
  elements["confirmed-city"].value = text(candidate.city);
  elements["confirmed-region"].value = text(candidate.region);
  elements["confirmed-country"].value = text(candidate.country);
  elements["confirmed-country-code"].value = text(candidate.country_code).toUpperCase();
  elements["coordinate-source"].value = "OpenStreetMap Nominatim";
  elements["coordinate-source-url"].value = safeUrl(candidate.map_url) ? candidate.map_url : "";
  const reviewNote = elements["coordinate-review-note"];
  if (!reviewNote.value.trim() || reviewNote.value.trim() === NOMINATIM_REVIEW_NOTE) {
    reviewNote.value = NOMINATIM_REVIEW_NOTE;
  }
  closeGeocodeDialog();
}

async function confirmLocation(event) {
  event.preventDefault();
  const draft = locationDraft();
  if (!draft.institution_id || draft.institution_id !== state.selectedInstitutionLocationId) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = "The location editor is not bound to the selected canonical institution.";
    return;
  }
  elements["location-form-error"].hidden = true;
  if (!(draft.coordinate_source || draft.coordinate_source_url)) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent =
      "Enter a coordinate source or coordinate source URL.";
    return;
  }
  elements["location-confirm"].disabled = true;
  try {
    const canonicalMode = state.locationEditorMode === "canonical";
    const result = await apiFetch(canonicalMode ? "/api/institution/location" : "/api/location-review/confirm", {
      method: "POST",
      body: JSON.stringify(canonicalMode ? {
        institution_id: draft.institution_id,
        loaded_institution_id: state.selectedInstitutionLocationId,
        city: draft.confirmed_city,
        region: draft.confirmed_region,
        country: draft.confirmed_country,
        country_code: draft.confirmed_country_code,
        lat: draft.confirmed_lat,
        lon: draft.confirmed_lon,
        coordinate_source: draft.coordinate_source,
        coordinate_source_url: draft.coordinate_source_url,
        coordinate_status: "known",
        review_note: draft.coordinate_review_note,
      } : draft),
    });
    showNotice(result.message);
    await Promise.all([loadLocationReviews(), refreshInstitutions()]);
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
  const selected = state.locationReviews.find(
    (row) => row.queue_id === draft.queue_id
  );
  const aliasName = text(selected?.institution) || "this institution name";
  const confirmed = window.confirm(
    `Add “${aliasName}” as a confirmed alias of “${draft.canonical_institution_name}”? This writes one alias row only; it does not merge canonical institutions or reassign mappings.`
  );
  if (!confirmed) return;
  try {
    const result = await apiFetch("/api/location-review/confirm-alias", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    showNotice(result.message);
    await loadLocationReviews();
  } catch (error) {
    elements["location-form-error"].hidden = false;
    elements["location-form-error"].textContent = error.message;
  }
}

async function saveLocationMetadata() {
  if (state.locationEditorMode === "canonical") {
    elements["location-form"].requestSubmit();
    return;
  }
  try {
    const result = await apiFetch("/api/location-review/save-metadata", {
      method: "POST",
      body: JSON.stringify(locationDraft()),
    });
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
  if (noticeTimer !== null) window.clearTimeout(noticeTimer);
  elements["action-notice"].hidden = false;
  elements["action-notice"].dataset.variant = variant;
  elements["action-notice"].textContent = message;
  if (variant === "success") {
    noticeTimer = window.setTimeout(() => {
      elements["action-notice"].hidden = true;
      noticeTimer = null;
    }, 4000);
  }
}

function setWorkflowRunning(running, label = "") {
  workflowCommandIds.forEach((id) => {
    elements[id].disabled = running || (
      id === "publish-changes"
      && Number(state.institutionAudit?.summary?.high || 0) > 0
    );
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
    elements["dashboard-validation-status"].textContent = "Not run";
    elements["dashboard-preview-status"].textContent = "Not refreshed";
    state.release.validation = "required";
    state.release.preview = "required";
    updatePublishReadiness();
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
  elements["dashboard-validation-status"].textContent =
    status.state === "succeeded" ? "Passed" : humanize(status.state);
  elements["dashboard-preview-status"].textContent =
    status.state === "succeeded" ? "Ready" : "Needs attention";
  state.release.validation = status.state === "succeeded" ? "passed" : "failed";
  state.release.preview = status.state === "succeeded" ? "ready" : "required";
  updatePublishReadiness();
  if (status.result) renderWorkflowLog(status.result);
}

function renderWorkflowLog(result, heading = "") {
  const command = Array.isArray(result.command)
    ? result.command.join("\n")
    : text(result.command);
  const changedFiles = (result.changed_files || []).length
    ? result.changed_files.join("\n")
    : "None detected";
  const steps = (result.steps || []).map((step, index) =>
    `${index + 1}. ${step.success ? "PASS" : "FAIL"} ${step.command} (${step.duration_seconds}s)`
  ).join("\n") || "None";
  elements["workflow-log"].textContent = [
    heading,
    `Success: ${result.success ? "yes" : "no"}`,
    `Exit code: ${result.exit_code}`,
    `Duration: ${result.duration_seconds}s`,
    "Command(s):",
    command || "—",
    "Changed files:",
    changedFiles,
    "Validation/export steps executed:",
    steps,
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

async function autofillArxivIds() {
  const button = elements["autofill-arxiv"];
  if (button.disabled) return;
  button.disabled = true;
  button.textContent = "Finding candidates…";
  try {
    await apiFetch("/api/admin/papers/autofill-arxiv", {
      method: "POST",
      body: JSON.stringify({}),
    });
    await pollArxivAutofillStatus();
  } catch (error) {
    if (error.status === 409) {
      await pollArxivAutofillStatus();
    } else {
      restoreArxivAutofillButton();
      showNotice(`arXiv candidate discovery failed: ${error.message}`, "error");
    }
  }
}

function restoreArxivAutofillButton() {
  elements["autofill-arxiv"].disabled = false;
  elements["autofill-arxiv"].textContent = "Find candidates";
}

function renderArxivAutofillStatus(status) {
  const running = status?.status === "running";
  const button = elements["autofill-arxiv"];
  button.disabled = running;
  button.textContent = running
    ? "Finding candidates…"
    : "Find candidates";
  if (!status || status.status === "idle") return;
  elements["arxiv-enrichment-summary"].textContent = running
    ? `Searching ${status.processed_lookups ?? 0} of ${status.papers_requiring_lookup ?? 0} missing papers${status.current_paper_title ? ` · ${status.current_paper_title}` : ""}`
    : elements["arxiv-enrichment-summary"].textContent;
}

function scheduleArxivAutofillPoll() {
  if (arxivAutofillPollTimer !== null) return;
  arxivAutofillPollTimer = window.setTimeout(() => {
    arxivAutofillPollTimer = null;
    pollArxivAutofillStatus();
  }, 1500);
}

async function pollArxivAutofillStatus() {
  if (arxivAutofillPolling) return;
  arxivAutofillPolling = true;
  try {
    const status = await apiFetch("/api/admin/papers/autofill-arxiv/status");
    renderArxivAutofillStatus(status);
    if (status.status === "running") {
      scheduleArxivAutofillPoll();
    } else {
      restoreArxivAutofillButton();
      if (status.status === "completed") {
        await loadArxivEnrichment();
        showNotice("Candidate discovery completed. No curated links were changed.");
      } else if (status.status === "failed") {
        showNotice(`arXiv candidate discovery failed: ${status.final_error || "unknown error"}`, "error");
      }
    }
  } catch (error) {
    restoreArxivAutofillButton();
    showNotice(`Could not read arXiv discovery progress: ${error.message}`, "error");
  } finally {
    arxivAutofillPolling = false;
  }
}

async function loadArxivEnrichment() {
  try {
    const payload = await apiFetch("/api/admin/papers/arxiv-enrichment");
    state.arxivEnrichment = payload.data || { records: [], summary: {}, discovery: {} };
    renderArxivEnrichment();
  } catch (error) {
    showNotice(`Could not load arXiv enrichment: ${error.message}`, "error");
  }
}

function renderArxivEnrichment() {
  if (!elements["arxiv-enrichment-list"]) return;
  const records = state.arxivEnrichment.records || [];
  const summary = state.arxivEnrichment.summary || {};
  elements["arxiv-enrichment-summary"].textContent =
    `${summary.unresolved ?? records.length} unresolved · ${summary.with_candidates ?? 0} with candidates · ${summary.ignored ?? 0} ignored`;
  elements["arxiv-enrichment-empty"].hidden = records.length !== 0;
  elements["arxiv-enrichment-list"].replaceChildren();
  records.forEach((paper) => {
    const card = document.createElement("article");
    card.className = "arxiv-enrichment-card";
    const heading = document.createElement("h3");
    heading.textContent = paper.title || "Untitled paper";
    const metadata = document.createElement("p");
    metadata.className = "candidate-meta";
    metadata.textContent = [paper.year, paper.doi && `DOI ${paper.doi}`, paper.openalex_url]
      .filter(Boolean).join(" · ");
    card.append(heading, metadata);
    if (!(paper.candidates || []).length) {
      const pending = document.createElement("p");
      pending.textContent = "No candidate loaded. Run Find candidates to search arXiv.";
      card.append(pending);
    }
    (paper.candidates || []).forEach((candidate) => {
      const candidateCard = document.createElement("div");
      candidateCard.className = "arxiv-candidate";
      const link = document.createElement("a");
      link.href = candidate.arxiv_url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = `arXiv:${candidate.arxiv_id}`;
      const evidence = document.createElement("dl");
      [["Evidence", candidate.evidence], ["Source", candidate.source], ["Confidence", candidate.confidence]].forEach(([label, value]) => {
        const term = document.createElement("dt");
        term.textContent = label;
        const detail = document.createElement("dd");
        detail.textContent = value || "Unavailable";
        evidence.append(term, detail);
      });
      const actions = document.createElement("div");
      actions.className = "candidate-actions";
      const accept = document.createElement("button");
      accept.type = "button";
      accept.className = "primary-button";
      accept.textContent = "Accept";
      accept.addEventListener("click", () => submitArxivDecision(paper, candidate, "accept"));
      const ignore = document.createElement("button");
      ignore.type = "button";
      ignore.className = "secondary-button";
      ignore.textContent = "Ignore";
      ignore.addEventListener("click", () => submitArxivDecision(paper, candidate, "ignore"));
      actions.append(accept, ignore);
      candidateCard.append(link, evidence, actions);
      card.append(candidateCard);
    });
    elements["arxiv-enrichment-list"].append(card);
  });
}

async function submitArxivDecision(paper, candidate, action) {
  const verb = action === "accept" ? "save this curated arXiv link" : "ignore this candidate";
  if (!window.confirm(`Confirm you want to ${verb}?\n\n${paper.title}\narXiv:${candidate.arxiv_id}`)) return;
  try {
    const payload = await apiFetch("/api/admin/papers/arxiv-enrichment/action", {
      method: "POST",
      body: JSON.stringify({ ...paper, arxiv_id: candidate.arxiv_id, action, confirmed: true }),
    });
    await loadArxivEnrichment();
    showNotice(payload.message || "arXiv enrichment decision saved.");
  } catch (error) {
    showNotice(`Could not save arXiv decision: ${error.message}`, "error");
  }
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
    renderGitSummary(result);
  } catch (error) {
    showNotice(`Could not read git status: ${error.message}`, "error");
  } finally {
    elements["show-git-status"].disabled = false;
  }
}

function renderGitSummary(result) {
  if (!result) return;
  const changed = (result.changed_files || []).length
    ? result.changed_files
    : text(result.stdout_tail).split("\n").filter((line) => line.trim());
  elements["dashboard-changed-files"].textContent = formatNumber(changed.length);
  elements["dashboard-git-summary"].textContent = changed.length
    ? "Unpublished changes"
    : "Working tree clean";
  state.release.changedFiles = changed.length;
  elements["global-publish-toggle"].textContent = changed.length
    ? `Publish changes · ${formatNumber(changed.length)}`
    : "Publish changes";
  updatePublishReadiness();
}

function updatePublishReadiness() {
  const { validation, preview, changedFiles } = state.release;
  let stage = "Published";
  let action = "View publish status";
  if (changedFiles > 0) { stage = "Changes detected"; action = "Review changes"; }
  if (changedFiles > 0 && validation === "required") { stage = "Validation required"; action = "Run validation"; }
  if (validation === "failed") { stage = "Validation failed"; action = "Inspect failure"; }
  if (changedFiles > 0 && validation === "passed" && preview !== "ready") { stage = "Preview refresh required"; action = "Refresh preview"; }
  if (changedFiles > 0 && validation === "passed" && preview === "ready") { stage = "Ready to publish"; action = "Publish changes"; }
  elements["dashboard-release-state"].textContent = stage;
  elements["dashboard-open-publish"].textContent = action;
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
    authors.textContent = authorListText(candidate.authors) || "Authors unavailable";
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
  elements["paper-authors"].value = authorListText(candidate.authors, "; ");
  elements["paper-affiliations"].value = "";
  elements["paper-venue"].value = text(candidate.venue);
  elements["paper-doi"].value = text(candidate.doi);
  elements["paper-arxiv-id"].value = text(candidate.arxiv_id);
  elements["paper-openalex-url"].value = text(candidate.openalex_url);
  elements["paper-url"].value = text(candidate.paper_url || candidate.primary_url);
  elements["paper-publication-type"].value = normalizePublicationTypeForForm(
    candidate.publication_type
  );
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
    authors.textContent = authorListText(paper.authors) || "Authors unavailable";
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
    action.dataset.paperId = paper.display_id;
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
  const selectionSequence = ++paperSelectionSequence;
  state.selectedId = id;
  state.selectedPaper = null;
  state.selectedMappings = [];
  clearPaperMetadata("Loading metadata…");
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
    if (selectionSequence !== paperSelectionSequence || state.selectedId !== id) return;
    state.selectedPaper = paperPayload.paper;
    state.selectedMappings = mappingsPayload.curated_mappings || [];
    state.paperMetadata = metadataPayload.data;
    renderPaperDetail(paperPayload.paper);
    renderMappings(mappingsPayload);
    renderMetadataComparison();
    populateMetadataForm();
  } catch (error) {
    if (selectionSequence !== paperSelectionSequence || state.selectedId !== id) return;
    state.selectedPaper = null;
    state.selectedMappings = [];
    clearPaperMetadata(`Could not load metadata: ${error.message}`, true);
    elements["detail-title"].textContent = "Could not load paper";
    elements["detail-notes"].textContent = error.message;
    elements["mapping-panel-error"].hidden = false;
    elements["mapping-panel-error"].textContent = error.message;
  }
}

function clearPaperMetadata(message, isError = false) {
  state.paperMetadata = null;
  elements["metadata-compare"].replaceChildren();
  const status = document.createElement("p");
  status.className = isError ? "form-error" : "muted";
  status.textContent = message;
  elements["metadata-compare"].append(status);
  elements["metadata-edit-button"].disabled = true;
  elements["metadata-edit-form"].hidden = true;
  elements["metadata-paper-id"].value = "";
  elements["metadata-edit-form"].querySelectorAll("input, textarea, select").forEach((control) => {
    if (control.id !== "metadata-paper-id") control.value = "";
  });
}

function renderMetadataComparison() {
  const payload = state.paperMetadata || {};
  const sources = [
    ["Effective metadata", payload.effective_record],
    ["Original public preview metadata", payload.public_preview_record],
    ["Curated override metadata", payload.curated_record],
  ];
  elements["metadata-compare"].replaceChildren();
  elements["metadata-edit-button"].disabled = false;
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
  if (field === "authors") return authorListText(value, "; ");
  return Array.isArray(value) ? value.join("; ") : text(value);
}

function normalizePublicationTypeForForm(value) {
  const normalized = text(value).trim().toLowerCase().replaceAll("_", "-");
  if (["article", "article-journal", "journal-article", "journal article"].includes(normalized)) {
    return "journal";
  }
  return normalized;
}

function openMetadataEditor() {
  if (!state.selectedPaper || !state.paperMetadata) {
    showNotice("Select a paper before editing metadata.", "error");
    return;
  }
  elements["metadata-edit-error"].hidden = true;
  elements["metadata-edit-form"].hidden = false;
  elements["metadata-title"].focus();
}

function populateMetadataForm() {
  if (!state.selectedPaper || !state.paperMetadata) return;
  const record = state.paperMetadata.effective_record || state.selectedPaper;
  const fields = [
    "title", "year", "authors", "venue", "doi", "arxiv_id", "openalex_url",
    "paper_url", "publication_type", "entry_type", "task", "subtask", "scope_status",
    "curation_status", "review_status", "abstract", "review_note",
  ];
  fields.forEach((field) => {
    const id = `metadata-${field.replaceAll("_", "-")}`;
    if (elements[id]) {
      elements[id].value = field === "publication_type"
        ? normalizePublicationTypeForForm(record?.[field])
        : metadataValue(record, field);
    }
  });
  elements["metadata-paper-id"].value = state.selectedId;
  elements["metadata-curation-status"].value =
    metadataValue(record, "curation_status") || "corrected_by_admin";
  elements["metadata-review-status"].value =
    metadataValue(record, "review_status") || "reviewed";
  elements["metadata-scope-status"].value =
    metadataValue(record, "scope_status") || "in_scope";
  elements["metadata-arxiv-id"].dataset.originalValue =
    metadataValue(record, "arxiv_id").trim();
  elements["metadata-edit-error"].hidden = true;
}

function closeMetadataEditor() {
  elements["metadata-edit-form"].hidden = true;
}

async function saveMetadata(event) {
  event.preventDefault();
  const selectedId = state.selectedId;
  const selectionSequence = paperSelectionSequence;
  if (!state.paperMetadata || !state.selectedPaper ||
      !selectedId || elements["metadata-paper-id"].value !== selectedId) {
    elements["metadata-edit-error"].hidden = false;
    elements["metadata-edit-error"].textContent =
      "Metadata is not loaded for the currently selected paper.";
    return;
  }
  const fields = [
    "title", "year", "authors", "venue", "doi", "arxiv_id", "openalex_url",
    "paper_url", "publication_type", "entry_type", "task", "subtask", "scope_status",
    "curation_status", "review_status", "abstract", "review_note",
  ];
  const draft = { id: elements["metadata-paper-id"].value };
  fields.forEach((field) => {
    draft[field] = elements[`metadata-${field.replaceAll("_", "-")}`].value.trim();
  });
  draft.arxiv_id_changed =
    draft.arxiv_id !== elements["metadata-arxiv-id"].dataset.originalValue;
  elements["metadata-edit-error"].hidden = true;
  try {
    const payload = await apiFetch("/api/paper/metadata/update", {
      method: "POST",
      body: JSON.stringify(draft),
    });
    if (selectionSequence !== paperSelectionSequence || state.selectedId !== selectedId) return;
    showNotice(payload.message);
    closeMetadataEditor();
    await loadApplication(false);
    if (selectionSequence === paperSelectionSequence && state.selectedId === selectedId) {
      await selectPaper(selectedId);
    }
  } catch (error) {
    if (selectionSequence !== paperSelectionSequence || state.selectedId !== selectedId) return;
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
    ["Authors", authorListText(paper.authors)],
    ["Venue", paper.venue || paper.venue_name],
    ["DOI", linkValue(paper.doi, doiUrl(paper.doi))],
    ["OpenAlex", linkValue(paper.openalex_url, paper.openalex_url)],
    ["Paper URL", linkValue(paper.paper_url, paper.paper_url)],
    ["Task", humanize(paper.task)],
    ["Paper type", humanize(paper.entry_type)],
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
  const currentStatuses = new Set(["active", "needs_review"]);
  const currentMappings = mappings.filter((mapping) =>
    currentStatuses.has(text(mapping.mapping_status).trim().toLowerCase())
  );
  const historicalMappings = mappings.filter((mapping) =>
    !currentStatuses.has(text(mapping.mapping_status).trim().toLowerCase())
  );
  state.selectedMappings = mappings;
  const diagnostic = payload.mapping_diagnostic || {};
  elements["mapping-diagnostic"].hidden =
    diagnostic.status !== "missing_mapping";
  elements["mapping-diagnostic"].textContent = text(diagnostic.message);
  elements["mapping-paper-context"].textContent = [
    text(paper.title),
    paper.year || paper.publication_year,
    authorListText(paper.authors),
    paper.doi ? `DOI ${paper.doi}` : "",
    paper.openalex_url,
  ].filter(Boolean).join(" · ");

  const body = elements["mapping-table-body"];
  body.replaceChildren();
  currentMappings.forEach((mapping) => {
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
    row.append(actions);
    body.append(row);
  });

  const historicalBody = elements["historical-mapping-table-body"];
  historicalBody.replaceChildren();
  historicalMappings.forEach((mapping) => {
    const row = document.createElement("tr");
    row.className = "historical-mapping-row";
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
    [mapping.institution, mapping.institution_authors, evidence].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });

    const status = document.createElement("td");
    status.className = "historical-mapping-labels";
    const labels = ["Excluded"];
    if (/\bReplaced:/i.test(text(mapping.review_note))) labels.push("Replaced");
    labels.push("Retained for audit history");
    labels.forEach((label) => {
      const badge = document.createElement("span");
      badge.className = "historical-mapping-label";
      badge.textContent = label;
      status.append(badge);
    });
    row.append(status);

    [humanize(mapping.location_status), mapping.review_note].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = text(value) || "—";
      row.append(cell);
    });
    const availability = document.createElement("td");
    availability.className = "historical-mapping-availability";
    availability.textContent = "Audit record — not a current affiliation";
    row.append(availability);
    historicalBody.append(row);
  });

  elements["empty-mappings"].hidden = currentMappings.length !== 0;
  body.parentElement.hidden = currentMappings.length === 0;
  elements["historical-mappings"].hidden = historicalMappings.length === 0;
  elements["historical-mappings"].open = false;
  elements["historical-mapping-count"].textContent = `(${historicalMappings.length})`;
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
  elements["mapping-institution-id"].value = text(mapping.institution_id);
  renderMappingInstitutionOptions();
  elements["mapping-authors"].value = text(mapping.institution_authors);
  elements["mapping-raw-affiliation"].value = text(mapping.raw_affiliation);
  elements["mapping-evidence-source"].value = text(mapping.evidence_source);
  elements["mapping-evidence-url"].value = text(mapping.evidence_url);
  elements["mapping-affiliation-note"].value = text(mapping.affiliation_note);
  elements["mapping-status"].value =
    mapping.mapping_status === "needs_review" ? "needs_review" : "active";
  elements["mapping-review-note"].value =
    mode === "update" ? text(mapping.review_note) : "";
  elements["mapping-review-note"].required = mode === "replace";
  elements["mapping-review-note-label"].textContent = mode === "replace"
    ? "Review note (required for replacement)"
    : "Review note (optional)";
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

function canonicalInstitutionKey(value) {
  return text(value).normalize("NFKC").toLocaleLowerCase()
    .match(/[\p{L}\p{N}_]+/gu)?.join(" ") || "";
}

function mappingInstitutionMatches(value) {
  const key = canonicalInstitutionKey(value);
  return state.institutions.filter((row) => [
    row.canonical_name,
    ...(row.aliases || []),
  ].some((name) => canonicalInstitutionKey(name) === key));
}

function syncMappingInstitutionId() {
  const matches = mappingInstitutionMatches(elements["mapping-institution"].value);
  elements["mapping-institution-id"].value =
    matches.length === 1 ? text(matches[0].institution_id) : "";
}

function renderMappingInstitutionOptions() {
  const options = state.institutions
    .filter((row) => row.institution_status === "active")
    .map((row) => {
      const option = document.createElement("option");
      option.value = text(row.canonical_name);
      option.label = `${text(row.canonical_name)} (${text(row.institution_id)})`;
      return option;
    });
  elements["mapping-institution-options"].replaceChildren(...options);
}

function closeMappingDialog() {
  elements["mapping-dialog"].close();
}

function mappingDraft() {
  return {
    institution: elements["mapping-institution"].value.trim(),
    institution_id: elements["mapping-institution-id"].value,
    institution_authors: elements["mapping-authors"].value.trim(),
    raw_affiliation: elements["mapping-raw-affiliation"].value,
    evidence_source: elements["mapping-evidence-source"].value.trim(),
    evidence_url: elements["mapping-evidence-url"].value.trim(),
    affiliation_note: elements["mapping-affiliation-note"].value.trim(),
    provenance_source: "manually_confirmed",
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
    await Promise.all([
      loadSelectedMappings(),
      refreshInstitutions(),
      loadLocationReviews(),
    ]);
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
  elements["scope-paper-title"].textContent = [
    text(paper.title) || "Untitled paper",
    paper.openalex_url ? `OpenAlex ${paper.openalex_url}` : "",
    paper.doi ? `DOI ${paper.doi}` : "",
    text(paper.source_database) ? `Source ${text(paper.source_database)}` : "",
    text(paper.venue || paper.venue_name) ? `Venue ${text(paper.venue || paper.venue_name)}` : "",
  ].filter(Boolean).join(" · ");
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

function authorListText(value, separator = ", ") {
  let authors = value;
  if (typeof authors === "string" && /^[\[{]/.test(authors.trim())) {
    try {
      authors = JSON.parse(authors);
    } catch (_error) {
      authors = value;
    }
  }
  if (!Array.isArray(authors)) authors = authors == null || authors === "" ? [] : [authors];
  return authors.map((author) => {
    if (author && typeof author === "object") {
      return text(author.name || author.display_name || author.author).trim();
    }
    return text(author).trim();
  }).filter((name) => name && name.toLocaleLowerCase() !== "[object object]").join(separator);
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
