"use strict";

const state = {
  token: "",
  papers: [],
  filtered: [],
  selectedId: "",
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  [
    "connection-status",
    "token-panel",
    "token-form",
    "token-input",
    "summary-grid",
    "workspace",
    "search-input",
    "filter-year",
    "filter-task",
    "filter-subtask",
    "filter-coverage",
    "filter-map",
    "filter-source",
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
    "marker-count",
    "marker-table-body",
    "empty-markers",
    "count-total",
    "count-mapped",
    "count-affiliation",
    "count-coordinates",
    "count-curated",
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
  ].forEach((id) => elements[id].addEventListener("change", applyFilters));

  if (state.token) {
    loadApplication();
  } else {
    requestToken();
  }
});

async function apiFetch(path) {
  const response = await fetch(path, {
    headers: { "X-Admin-Token": state.token },
    cache: "no-store",
  });
  const payload = await response.json().catch(() => ({ error: "Invalid server response" }));
  if (!response.ok) {
    const error = new Error(payload.error || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function loadApplication() {
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
    setConnection("ok", "Read-only · connected");
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

function renderSummary(counts) {
  elements["count-total"].textContent = formatNumber(counts.total_papers);
  elements["count-mapped"].textContent = formatNumber(counts.papers_with_map_locations);
  elements["count-affiliation"].textContent = formatNumber(counts.papers_missing_affiliations);
  elements["count-coordinates"].textContent = formatNumber(counts.papers_missing_coordinates);
  elements["count-curated"].textContent = formatNumber(counts.curated_papers);
}

function populateFilters() {
  setOptions("filter-year", uniqueValues("year", true));
  setOptions("filter-task", uniqueValues("task"));
  setOptions("filter-subtask", uniqueValues("subtask"));
  setOptions("filter-coverage", uniqueValues("coverage_status"));
  setOptions("filter-source", uniqueValues("source_database"));
}

function uniqueValues(field, numericDescending = false) {
  const values = new Set(
    state.papers.map((paper) => text(paper[field])).filter(Boolean)
  );
  return [...values].sort((left, right) =>
    numericDescending
      ? Number(right) - Number(left)
      : left.localeCompare(right, undefined, { sensitivity: "base" })
  );
}

function setOptions(id, values) {
  const select = elements[id];
  while (select.options.length > 1) {
    select.remove(1);
  }
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = humanize(value);
    select.append(option);
  });
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

  state.filtered = state.papers.filter((paper) => {
    const searchable = normalize([
      paper.title,
      ...(Array.isArray(paper.authors) ? paper.authors : [paper.authors]),
      ...(paper.institutions || []),
      paper.doi,
      paper.openalex_url,
    ].filter(Boolean).join(" "));
    if (query && !searchable.includes(query)) return false;
    if (Object.entries(filters).some(([field, expected]) =>
      expected && text(paper[field]) !== expected
    )) return false;
    if (mapFilter && String(Boolean(paper.has_map_location)) !== mapFilter) return false;
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
    const button = document.createElement("button");
    button.type = "button";
    button.className = "paper-card";
    button.dataset.paperId = paper.display_id;
    if (paper.display_id === state.selectedId) button.setAttribute("aria-current", "true");

    const title = document.createElement("strong");
    title.textContent = text(paper.title) || "Untitled paper";
    const byline = document.createElement("span");
    const authors = Array.isArray(paper.authors) ? paper.authors.join(", ") : text(paper.authors);
    byline.textContent = authors || "Authors unavailable";
    const meta = document.createElement("span");
    meta.className = "paper-meta";
    meta.textContent = [paper.year || paper.publication_year, humanize(paper.task)]
      .filter(Boolean).join(" · ");
    const badges = document.createElement("span");
    badges.className = "card-badges";
    if (paper.has_map_location) badges.append(makeBadge("Mapped", "map"));
    if (paper.is_in_curated_papers) badges.append(makeBadge("Curated", "curated"));
    if (paper.is_in_curated_exclusions) badges.append(makeBadge("Excluded", "excluded"));

    button.append(title, byline, meta, badges);
    button.addEventListener("click", () => selectPaper(paper.display_id));
    item.append(button);
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
  try {
    const payload = await apiFetch(`/api/paper?id=${encodeURIComponent(id)}`);
    renderPaperDetail(payload.paper);
  } catch (error) {
    elements["detail-title"].textContent = "Could not load paper";
    elements["detail-notes"].textContent = error.message;
  }
}

function renderPaperDetail(paper) {
  elements["detail-source"].textContent =
    paper.record_source === "curated_only" ? "Curated-only record" : "Public preview record";
  elements["detail-title"].textContent = text(paper.title) || "Untitled paper";
  elements["detail-badges"].replaceChildren();
  if (paper.has_map_location) elements["detail-badges"].append(makeBadge("Mapped", "map"));
  if (paper.is_in_curated_papers) elements["detail-badges"].append(makeBadge("Curated", "curated"));
  if (paper.is_in_curated_exclusions) elements["detail-badges"].append(makeBadge("Exclusion record", "excluded"));

  const venue = paper.venue || paper.venue_name;
  const metadata = [
    ["Display ID", paper.display_id],
    ["Year", paper.year || paper.publication_year],
    ["Authors", listText(paper.authors)],
    ["Venue", venue],
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
  renderMarkers(paper.marker_records || []);
}

function renderMarkers(markers) {
  elements["marker-count"].textContent = `${formatNumber(markers.length)} record${markers.length === 1 ? "" : "s"}`;
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
