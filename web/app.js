"use strict";

const DATASET_CONFIG = {
  sample: {
    url: "data/sample_map_data.json",
    recordLabel: "fictional record",
    emptyMessage: "The fictional sample dataset contains no map records.",
  },
  openalex: {
    url: "data/openalex_candidate_map_data.json",
    recordLabel: "uncurated OpenAlex candidate",
    emptyMessage:
      "The OpenAlex candidate dataset contains no records with valid coordinates. Run the local export after adding reviewed coordinates to the processed affiliation data.",
  },
  preview: {
    url: "data/public_preview_map_data.json",
    recordLabel: "uncurated public preview record",
    emptyMessage: "The public preview dataset contains no eligible map records.",
  },
};

function resolveDatasetName(requestedName) {
  if (requestedName === "sample" || requestedName === "openalex") {
    return requestedName;
  }
  return "preview";
}

const requestedDataset = new URLSearchParams(window.location.search).get("dataset");
const shouldFallbackToSample = requestedDataset === null;
let datasetName = resolveDatasetName(requestedDataset);
let datasetConfig = DATASET_CONFIG[datasetName];
const WORLD_BOUNDS = L.latLngBounds(L.latLng(-60, -170), L.latLng(75, 170));
const TASK_COLORS = {
  detection: "#287d8e",
  source_attribution: "#b66a37",
  detection_and_source_attribution: "#76589b",
  uncertain: "#68747d",
};

const map = L.map("map", {
  minZoom: 2,
  maxBounds: WORLD_BOUNDS.pad(0.35),
  worldCopyJump: true,
}).fitBounds(WORLD_BOUNDS);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);
const keywordFilter = document.querySelector("#keyword-filter");
const taskFilter = document.querySelector("#task-filter");
const minYearFilter = document.querySelector("#min-year-filter");
const maxYearFilter = document.querySelector("#max-year-filter");
const resolutionFilter = document.querySelector("#resolution-filter");
const reviewFilter = document.querySelector("#review-filter");
const resetButton = document.querySelector("#reset-filters");
const mapStatus = document.querySelector("#map-status");
const recordCount = document.querySelector("#record-count");
const countryCount = document.querySelector("#country-count");
const institutionCount = document.querySelector("#institution-count");
const reviewCount = document.querySelector("#review-count");
const datasetRecordCount = document.querySelector("#dataset-record-count");
const datasetPaperCount = document.querySelector("#dataset-paper-count");
const datasetInstitutionCount = document.querySelector("#dataset-institution-count");
const datasetCountryCount = document.querySelector("#dataset-country-count");
const datasetDetectionCount = document.querySelector("#dataset-detection-count");
const datasetAttributionCount = document.querySelector("#dataset-attribution-count");
const datasetCombinedCount = document.querySelector("#dataset-combined-count");
const datasetPreprintCount = document.querySelector("#dataset-preprint-count");
const datasetPreprintStat = document.querySelector("#dataset-preprint-stat");
const datasetStatisticsNote = document.querySelector("#dataset-statistics-note");
const resultsCount = document.querySelector("#results-count");
const resultsList = document.querySelector("#results-list");
const resultsEmpty = document.querySelector("#results-empty");
const exportCsvButton = document.querySelector("#export-csv");
const prototypeNote = document.querySelector(".prototype-note");
const intro = document.querySelector(".intro");
const footer = document.querySelector("footer");

let records = [];
let currentFilteredRecords = [];

const CSV_COLUMNS = [
  ["title", (record) => recordTitle(record)],
  ["authors", (record) => (
    Array.isArray(record.authors) ? record.authors.join("; ") : record.authors
  )],
  ["publication_year", (record) => publicationYear(record) ?? ""],
  ["venue_name", (record) => record.venue_name || record.venue || ""],
  ["task", (record) => record.task || ""],
  ["subtask", (record) => record.subtask || ""],
  ["institution_name", (record) => recordInstitution(record)],
  ["country", (record) => record.country || ""],
  ["country_code", (record) => record.country_code || ""],
  ["doi", (record) => normalizedDoi(record.doi)],
  ["arxiv_id", (record) => record.arxiv_id || ""],
  ["arxiv_url", (record) => record.arxiv_url || (
    record.arxiv_id ? `https://arxiv.org/abs/${record.arxiv_id}` : ""
  )],
  ["paper_url", (record) => (
    record.paper_url ||
    record.primary_url ||
    record.landing_page_url ||
    record.url ||
    record.openalex_url ||
    ""
  )],
  ["openalex_url", (record) => record.openalex_url || ""],
];

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = String(value);
  return element.innerHTML;
}

function formatTask(task) {
  const readableTask = String(task || "uncertain").replaceAll("_", " ");
  return readableTask.charAt(0).toUpperCase() + readableTask.slice(1);
}

function recordTitle(record) {
  return record.title ?? record.paper_title;
}

function normalizedIdentityValue(value) {
  return String(value || "").trim().toLowerCase().replace(/\/$/, "");
}

function normalizedTitle(value) {
  return String(value || "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function paperIdentity(record) {
  const openalexUrl = normalizedIdentityValue(record.openalex_url);
  if (openalexUrl) {
    return `openalex:${openalexUrl}`;
  }

  const doi = normalizedDoi(record.doi).toLowerCase();
  if (doi) {
    return `doi:${doi}`;
  }

  const arxivId = normalizedIdentityValue(record.arxiv_id).replace(/^arxiv:/, "");
  if (arxivId) {
    return `arxiv:${arxivId}`;
  }

  const paperUrl = normalizedIdentityValue(
    record.paper_url || record.primary_url || record.landing_page_url || record.url,
  );
  if (paperUrl) {
    return `url:${paperUrl}`;
  }

  const title = normalizedTitle(recordTitle(record));
  const year = record.publication_year ?? record.year ?? "";
  return `title-year:${title}:${year}`;
}

function recordInstitution(record) {
  return String(record.institution_name || record.institution || "").trim();
}

function recordCountry(record) {
  return String(record.country_code || record.country || "").trim();
}

function publicationYear(record) {
  const value = record.publication_year ?? record.year;
  const year = Number(value);
  return Number.isInteger(year) ? year : null;
}

function normalizedSearchText(value) {
  return String(value || "").normalize("NFKC").toLocaleLowerCase();
}

function recordSearchText(record) {
  const authors = Array.isArray(record.authors)
    ? record.authors
    : [record.authors];
  return normalizedSearchText([
    recordTitle(record),
    ...authors,
    record.institution_name,
    record.institution,
    record.country,
    record.country_code,
    record.venue_name,
    record.venue,
    record.task,
    record.subtask,
  ].filter(Boolean).join(" "));
}

function yearFilterValue(input) {
  if (!input.value.trim()) {
    return null;
  }
  const value = Number(input.value);
  return Number.isInteger(value) ? value : null;
}

function normalizedSetSize(values) {
  return new Set(
    values
      .map((value) => String(value || "").trim().toLowerCase())
      .filter(Boolean),
  ).size;
}

function hasPreprintMetadata(record) {
  return ["is_arxiv_preprint", "arxiv_id", "arxiv_url"].some((field) =>
    Object.hasOwn(record, field),
  );
}

function isArxivPreprint(record) {
  return (
    booleanValue(record.is_arxiv_preprint) ||
    Boolean(String(record.arxiv_id || "").trim()) ||
    Boolean(String(record.arxiv_url || "").trim())
  );
}

function updateDatasetStatistics(datasetRecords) {
  datasetRecordCount.textContent = datasetRecords.length;
  datasetPaperCount.textContent = new Set(datasetRecords.map(paperIdentity)).size;
  datasetInstitutionCount.textContent = normalizedSetSize(
    datasetRecords.map(recordInstitution),
  );
  datasetCountryCount.textContent = normalizedSetSize(
    datasetRecords.map(recordCountry),
  );
  datasetDetectionCount.textContent = datasetRecords.filter(
    (record) => record.task === "detection",
  ).length;
  datasetAttributionCount.textContent = datasetRecords.filter(
    (record) => record.task === "source_attribution",
  ).length;
  datasetCombinedCount.textContent = datasetRecords.filter(
    (record) => record.task === "detection_and_source_attribution",
  ).length;

  const supportsPreprintMetadata = records.some(hasPreprintMetadata);
  datasetPreprintStat.hidden = !supportsPreprintMetadata;
  datasetPreprintCount.textContent = supportsPreprintMetadata
    ? datasetRecords.filter(isArxivPreprint).length
    : 0;
}

function hasResolutionMetadata(record) {
  return [
    "resolution_method",
    "resolution_confidence",
    "needs_review",
    "resolution_notes",
  ].some((field) => Object.hasOwn(record, field));
}

function resolutionConfidence(record) {
  const confidence = String(record.resolution_confidence || "").toLowerCase();
  if (["high", "medium", "low", "unresolved"].includes(confidence)) {
    return confidence;
  }
  if (hasResolutionMetadata(record)) {
    return "unresolved";
  }
  return datasetName === "sample" ? "" : "unresolved";
}

function reviewStatus(record) {
  if (!Object.hasOwn(record, "needs_review")) {
    return null;
  }
  if (typeof record.needs_review === "boolean") {
    return record.needs_review;
  }
  return ["1", "true", "yes", "y"].includes(
    String(record.needs_review).toLowerCase(),
  );
}

function booleanValue(value) {
  if (typeof value === "boolean") {
    return value;
  }
  return ["1", "true", "yes", "y"].includes(String(value || "").toLowerCase());
}

function safeHttpUrl(value) {
  try {
    const url = new URL(String(value || ""), window.location.href);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

function externalLink(url, label) {
  const safeUrl = safeHttpUrl(url);
  return safeUrl
    ? `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`
    : "";
}

function normalizedDoi(value) {
  return String(value || "")
    .trim()
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "");
}

function escapeCsvValue(value) {
  const text = String(value ?? "");
  return /[",\r\n]/.test(text)
    ? `"${text.replaceAll('"', '""')}"`
    : text;
}

function buildCsv(exportRecords) {
  const header = CSV_COLUMNS.map(([name]) => escapeCsvValue(name)).join(",");
  const rows = exportRecords.map((record) => CSV_COLUMNS
    .map(([, valueForRecord]) => escapeCsvValue(valueForRecord(record)))
    .join(","));
  return [header, ...rows].join("\r\n");
}

function exportFilename() {
  const date = new Date().toISOString().slice(0, 10);
  return `synthetic-image-research-map-${datasetName}-${date}.csv`;
}

function downloadFilteredCsv() {
  if (!currentFilteredRecords.length) {
    return;
  }

  const csv = buildCsv(currentFilteredRecords);
  const blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = exportFilename();
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
}

function formatResolutionValue(value) {
  return formatTask(value || "unresolved");
}

function popupContent(record) {
  const authors = record.authors.length
    ? record.authors.map(escapeHtml).join(", ")
    : "Unknown";
  const year = record.publication_year ?? record.year ?? "Unknown";
  const venue = record.venue_name || record.venue || "unknown";
  const publicationType = record.publication_type || "Unknown";
  const location = [record.city, record.country].filter(Boolean).join(", ") || "Unknown";
  const subtaskRow = record.subtask
    ? `<dt>Subtask</dt><dd>${escapeHtml(formatTask(record.subtask))}</dd>`
    : "";
  const doi = normalizedDoi(record.doi);
  const doiRow = doi
    ? `<dt>DOI</dt><dd>${externalLink(`https://doi.org/${doi}`, doi)}</dd>`
    : "";
  const arxivUrl = record.arxiv_url || (
    record.arxiv_id ? `https://arxiv.org/abs/${record.arxiv_id}` : ""
  );
  const arxivRow = arxivUrl
    ? `<dt>arXiv</dt><dd>${externalLink(arxivUrl, record.arxiv_id || "View preprint")}</dd>`
    : "";
  const paperUrl =
    record.primary_url ||
    record.landing_page_url ||
    record.url ||
    record.openalex_url ||
    "";
  const paperUrlRow = paperUrl
    ? `<dt>Paper</dt><dd>${externalLink(paperUrl, "Open record")}</dd>`
    : "";
  const isArxivPreprint =
    booleanValue(record.is_arxiv_preprint) || Boolean(record.arxiv_id || arxivUrl);
  const preprintBadge = isArxivPreprint
    ? '<span class="popup-badge confidence-unresolved">arXiv / preprint</span>'
    : "";
  const hasResolution = hasResolutionMetadata(record);
  const confidence = resolutionConfidence(record);
  const needsReview = reviewStatus(record);
  const confidenceBadge = hasResolution
    ? `<span class="popup-badge confidence-${escapeHtml(confidence)}">${escapeHtml(formatResolutionValue(confidence))} confidence</span>`
    : "";
  const reviewBadge = needsReview === true
    ? '<span class="popup-badge needs-review-badge">Needs review</span>'
    : "";
  const methodRow = record.resolution_method
    ? `<dt>Resolution</dt><dd>${escapeHtml(formatResolutionValue(record.resolution_method))}</dd>`
    : "";
  const confidenceRow = hasResolution
    ? `<dt>Confidence</dt><dd>${escapeHtml(formatResolutionValue(confidence))}</dd>`
    : "";
  const reviewRow = needsReview !== null
    ? `<dt>Needs review</dt><dd>${needsReview ? "Yes" : "No"}</dd>`
    : "";
  const resolutionNotesRow = record.resolution_notes
    ? `<dt>Resolution notes</dt><dd class="popup-resolution-notes">${escapeHtml(record.resolution_notes)}</dd>`
    : "";

  return `
    <div class="popup-badges">
      <span class="popup-badge popup-task">${escapeHtml(formatTask(record.task))}</span>
      ${preprintBadge}
      ${confidenceBadge}
      ${reviewBadge}
    </div>
    <h3 class="popup-title">${escapeHtml(recordTitle(record))}</h3>
    <dl class="popup-details">
      <dt>Authors</dt><dd>${authors}</dd>
      <dt>Institution</dt><dd>${escapeHtml(record.institution)}</dd>
      <dt>Location</dt><dd>${escapeHtml(location)}</dd>
      <dt>Year</dt><dd>${escapeHtml(year)}</dd>
      <dt>Venue</dt><dd>${escapeHtml(venue)}</dd>
      <dt>Publication type</dt><dd>${escapeHtml(formatTask(publicationType))}</dd>
      ${doiRow}
      ${arxivRow}
      ${paperUrlRow}
      <dt>Task</dt><dd>${escapeHtml(formatTask(record.task))}</dd>
      ${subtaskRow}
      ${methodRow}
      ${confidenceRow}
      ${reviewRow}
      ${resolutionNotesRow}
    </dl>
  `;
}

function resultContent(record) {
  const title = recordTitle(record);
  const year = publicationYear(record) ?? "Unknown";
  const venue = record.venue_name || record.venue || "";
  const institution = recordInstitution(record) || "Unknown institution";
  const country = recordCountry(record);
  const affiliation = [institution, country].filter(Boolean).join(" · ");
  const subtask = record.subtask
    ? `<span class="result-task result-subtask">${escapeHtml(formatTask(record.subtask))}</span>`
    : "";
  const venueRow = venue
    ? `<p class="result-venue">${escapeHtml(venue)}</p>`
    : "";

  const doi = normalizedDoi(record.doi);
  const doiLink = doi
    ? externalLink(`https://doi.org/${doi}`, "DOI")
    : "";
  const arxivUrl = record.arxiv_url || (
    record.arxiv_id ? `https://arxiv.org/abs/${record.arxiv_id}` : ""
  );
  const arxivLink = arxivUrl ? externalLink(arxivUrl, "arXiv") : "";
  const paperUrl =
    record.paper_url ||
    record.primary_url ||
    record.landing_page_url ||
    record.url ||
    record.openalex_url ||
    "";
  const paperLabel = paperUrl && paperUrl === record.openalex_url
    ? "OpenAlex"
    : "Paper";
  const paperLink = paperUrl ? externalLink(paperUrl, paperLabel) : "";
  const links = [doiLink, arxivLink, paperLink].filter(Boolean).join("");
  const linksRow = links ? `<div class="result-links">${links}</div>` : "";

  return `
    <article>
      <div class="result-title-row">
        <h3 class="result-title">${escapeHtml(title)}</h3>
        <span class="result-year">${escapeHtml(year)}</span>
      </div>
      ${venueRow}
      <p class="result-affiliation">${escapeHtml(affiliation)}</p>
      <div class="result-classification">
        <span class="result-task">${escapeHtml(formatTask(record.task))}</span>
        ${subtask}
      </div>
      ${linksRow}
    </article>
  `;
}

function renderResults(visibleRecords) {
  const count = visibleRecords.length;
  resultsCount.textContent = `Showing ${count} record${count === 1 ? "" : "s"}`;
  exportCsvButton.disabled = count === 0;
  resultsList.replaceChildren();
  resultsEmpty.hidden = count !== 0;
  resultsList.hidden = count === 0;

  if (!count) {
    return;
  }

  const fragment = document.createDocumentFragment();
  visibleRecords.forEach((record) => {
    const item = document.createElement("li");
    item.className = "result-item";
    item.innerHTML = resultContent(record);
    fragment.append(item);
  });
  resultsList.append(fragment);
}

function updateSummary(visibleRecords) {
  recordCount.textContent = visibleRecords.length;
  countryCount.textContent = normalizedSetSize(visibleRecords.map(recordCountry));
  institutionCount.textContent = normalizedSetSize(
    visibleRecords.map(recordInstitution),
  );
  reviewCount.textContent = visibleRecords.filter(
    (record) => reviewStatus(record) === true,
  ).length;
}

function renderRecords() {
  const keywordTerms = normalizedSearchText(keywordFilter.value)
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  const selectedTask = taskFilter.value;
  const minimumYear = yearFilterValue(minYearFilter);
  const maximumYear = yearFilterValue(maxYearFilter);
  const selectedResolution = resolutionFilter.value;
  const selectedReview = reviewFilter.value;
  const visibleRecords = records.filter((record) => {
    const searchableText = recordSearchText(record);
    const matchesKeyword = keywordTerms.every((term) => searchableText.includes(term));
    const matchesTask = selectedTask === "all" || record.task === selectedTask;
    const year = publicationYear(record);
    const matchesMinimumYear = minimumYear === null || (year !== null && year >= minimumYear);
    const matchesMaximumYear = maximumYear === null || (year !== null && year <= maximumYear);
    const matchesResolution =
      selectedResolution === "all" || resolutionConfidence(record) === selectedResolution;
    const status = reviewStatus(record);
    const matchesReview =
      selectedReview === "all" ||
      (selectedReview === "true" && status === true) ||
      (selectedReview === "false" && status === false);
    return (
      matchesKeyword &&
      matchesTask &&
      matchesMinimumYear &&
      matchesMaximumYear &&
      matchesResolution &&
      matchesReview
    );
  });

  currentFilteredRecords = visibleRecords;

  markerLayer.clearLayers();

  visibleRecords.forEach((record) => {
    L.circleMarker([record.latitude, record.longitude], {
      radius: 8,
      color: "#ffffff",
      weight: 2,
      fillColor: TASK_COLORS[record.task] ?? TASK_COLORS.uncertain,
      fillOpacity: 0.94,
    })
      .bindPopup(popupContent(record), { maxWidth: 320 })
      .bindTooltip(record.institution, { direction: "top", offset: [0, -7] })
      .addTo(markerLayer);
  });

  updateSummary(visibleRecords);
  updateDatasetStatistics(visibleRecords);
  renderResults(visibleRecords);
  mapStatus.classList.toggle("error", false);
  const recordLabel = datasetConfig.recordLabel;
  mapStatus.textContent = visibleRecords.length
    ? `Showing ${visibleRecords.length} ${recordLabel}${visibleRecords.length === 1 ? "" : "s"}`
    : "No records match the current filters.";
}

function configureYearRange() {
  const years = records.map(publicationYear).filter((year) => year !== null);
  if (!years.length) {
    return;
  }
  const earliestYear = Math.min(...years);
  const latestYear = Math.max(...years);
  [minYearFilter, maxYearFilter].forEach((input) => {
    input.min = String(earliestYear);
    input.max = String(latestYear);
  });
  minYearFilter.placeholder = String(earliestYear);
  maxYearFilter.placeholder = String(latestYear);
}

function enableControls() {
  keywordFilter.disabled = false;
  taskFilter.disabled = false;
  minYearFilter.disabled = false;
  maxYearFilter.disabled = false;
  const supportsResolution = records.some(hasResolutionMetadata);
  resolutionFilter.disabled = !supportsResolution;
  reviewFilter.disabled = !supportsResolution;
  resetButton.disabled = false;
}

function validateRecord(record) {
  const validTasks = Object.keys(TASK_COLORS);
  return (
    typeof recordTitle(record) === "string" &&
    (record.year === null || Number.isInteger(record.year)) &&
    validTasks.includes(record.task) &&
    typeof record.institution === "string" &&
    typeof record.country === "string" &&
    Array.isArray(record.authors) &&
    Number.isFinite(record.latitude) &&
    Number.isFinite(record.longitude)
  );
}

function showDatasetMessage(message, isError = false) {
  records = [];
  currentFilteredRecords = [];
  markerLayer.clearLayers();
  updateSummary(records);
  updateDatasetStatistics(records);
  renderResults(records);
  mapStatus.textContent = message;
  mapStatus.classList.toggle("error", isError);
}

function updateDatasetLabels() {
  if (datasetName === "sample") {
    prototypeNote.textContent = "Fictional sample data only";
    intro.textContent =
      "Explore toy records representing research in synthetic image detection and source attribution.";
    footer.textContent =
      "Prototype interface. Records shown here are fictional and are not literature data.";
    mapStatus.textContent = "Loading fictional sample data...";
    datasetStatisticsNote.textContent =
      "Fictional sample records for interface testing; not literature data.";
  } else if (datasetName === "preview") {
    prototypeNote.textContent = "Uncurated public preview";
    intro.textContent =
      "Explore a filtered public preview of automatically generated OpenAlex candidate metadata.";
    footer.textContent =
      "Uncurated public preview. These candidate records are not a manually curated bibliography.";
    mapStatus.textContent = "Loading public preview data...";
    datasetStatisticsNote.textContent =
      "Automatically generated OpenAlex candidate metadata; not manually curated.";
  } else {
    prototypeNote.textContent = "Uncurated OpenAlex candidates";
    intro.textContent =
      "Explore locally generated candidate records for synthetic image detection and source attribution research.";
    footer.textContent =
      "Exploratory candidate view. Records are automatically extracted and require manual review.";
    mapStatus.textContent = "Loading local OpenAlex candidate data...";
    datasetStatisticsNote.textContent =
      "Locally generated OpenAlex candidate metadata; not manually curated.";
  }
  renderDatasetSwitcher();
}

function renderDatasetSwitcher() {
  let switcher = document.querySelector(".dataset-switcher");
  if (!switcher) {
    switcher = document.createElement("nav");
    switcher.className = "dataset-switcher";
    switcher.setAttribute("aria-label", "Dataset selection");
    intro.insertAdjacentElement("afterend", switcher);
  }

  const choices = [
    ["preview", "Public preview"],
    ["sample", "Fictional sample"],
  ];
  const content = document.createElement("small");
  content.append("Dataset: ");
  choices.forEach(([name, label], index) => {
    if (index > 0) {
      content.append(" · ");
    }
    const link = document.createElement("a");
    link.href = `?dataset=${name}`;
    link.textContent = label;
    if (datasetName === name) {
      link.setAttribute("aria-current", "page");
    }
    content.append(link);
  });
  switcher.replaceChildren(content);
}

function normalizeDatasetPayload(payload) {
  if (Array.isArray(payload)) {
    return { metadata: {}, records: payload };
  }
  if (payload && typeof payload === "object" && Array.isArray(payload.records)) {
    const metadata =
      payload.metadata &&
      typeof payload.metadata === "object" &&
      !Array.isArray(payload.metadata)
        ? payload.metadata
        : {};
    return { metadata, records: payload.records };
  }
  throw new Error(`${datasetName} data does not contain a records array`);
}

function displayMetadataWarning(metadata) {
  const warning =
    typeof metadata.warning === "string" ? metadata.warning.trim() : "";
  if (warning) {
    intro.textContent = `${intro.textContent} ${warning}`;
  }
}

async function readDataset(name) {
  const config = DATASET_CONFIG[name];
  const response = await fetch(config.url, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`${name} data request failed with status ${response.status}`);
  }

  const responseText = await response.text();
  if (!responseText.trim()) {
    return { metadata: {}, records: [] };
  }

  const normalizedData = normalizeDatasetPayload(JSON.parse(responseText));
  if (!normalizedData.records.every(validateRecord)) {
    throw new Error(`${name} data does not match the expected format`);
  }
  return normalizedData;
}

function displayDataset(normalizedData) {
  records = normalizedData.records;
  displayMetadataWarning(normalizedData.metadata);
  configureYearRange();
  enableControls();
  renderRecords();
}

function selectDataset(name) {
  datasetName = name;
  datasetConfig = DATASET_CONFIG[name];
  updateDatasetLabels();
}

async function loadSampleFallback() {
  selectDataset("sample");
  try {
    const sampleData = await readDataset("sample");
    if (sampleData.records.length === 0) {
      throw new Error("sample data contains no records");
    }
    displayDataset(sampleData);
    mapStatus.textContent =
      "Public preview dataset could not be loaded. Showing the fictional sample dataset instead.";
  } catch (error) {
    console.error(error);
    showDatasetMessage(
      "Neither the public preview nor the fictional sample dataset could be loaded.",
      true,
    );
  }
}

async function loadData() {
  try {
    const normalizedData = await readDataset(datasetName);
    if (normalizedData.records.length === 0) {
      if (datasetName === "preview" && shouldFallbackToSample) {
        await loadSampleFallback();
        return;
      }
      showDatasetMessage(datasetConfig.emptyMessage, datasetName !== "sample");
      return;
    }
    displayDataset(normalizedData);
  } catch (error) {
    console.error(error);
    if (datasetName === "preview" && shouldFallbackToSample) {
      await loadSampleFallback();
      return;
    }
    const messages = {
      openalex:
        "OpenAlex candidate map data could not be loaded. Generate it locally with scripts/export_candidate_map_data.py.",
      preview:
        "Preview dataset could not be loaded. Check that web/data/public_preview_map_data.json is published.",
      sample: "Fictional sample data could not be loaded. Preview the site through a local server.",
    };
    showDatasetMessage(messages[datasetName], true);
  }
}

keywordFilter.addEventListener("input", renderRecords);
taskFilter.addEventListener("change", renderRecords);
minYearFilter.addEventListener("input", renderRecords);
maxYearFilter.addEventListener("input", renderRecords);
resolutionFilter.addEventListener("change", renderRecords);
reviewFilter.addEventListener("change", renderRecords);
exportCsvButton.addEventListener("click", downloadFilteredCsv);
resetButton.addEventListener("click", () => {
  keywordFilter.value = "";
  taskFilter.value = "all";
  minYearFilter.value = "";
  maxYearFilter.value = "";
  resolutionFilter.value = "all";
  reviewFilter.value = "all";
  renderRecords();
});

updateDatasetLabels();
loadData();
