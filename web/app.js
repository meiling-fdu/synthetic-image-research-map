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
const requestedDataset = new URLSearchParams(window.location.search).get("dataset");
const datasetName = ["openalex", "preview"].includes(requestedDataset)
  ? requestedDataset
  : "sample";
const datasetConfig = DATASET_CONFIG[datasetName];
const WORLD_BOUNDS = L.latLngBounds(L.latLng(-60, -170), L.latLng(75, 170));
const TASK_COLORS = {
  detection: "#287d8e",
  attribution: "#b66a37",
  both: "#76589b",
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
const taskFilter = document.querySelector("#task-filter");
const yearFilter = document.querySelector("#year-filter");
const resolutionFilter = document.querySelector("#resolution-filter");
const reviewFilter = document.querySelector("#review-filter");
const resetButton = document.querySelector("#reset-filters");
const mapStatus = document.querySelector("#map-status");
const recordCount = document.querySelector("#record-count");
const countryCount = document.querySelector("#country-count");
const institutionCount = document.querySelector("#institution-count");
const reviewCount = document.querySelector("#review-count");
const prototypeNote = document.querySelector(".prototype-note");
const intro = document.querySelector(".intro");
const footer = document.querySelector("footer");

let records = [];

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

function formatResolutionValue(value) {
  return formatTask(value || "unresolved");
}

function popupContent(record) {
  const authors = record.authors.map(escapeHtml).join(", ");
  const year = record.year ?? "Unknown";
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
      ${confidenceBadge}
      ${reviewBadge}
    </div>
    <h3 class="popup-title">${escapeHtml(recordTitle(record))}</h3>
    <dl class="popup-details">
      <dt>Year</dt><dd>${escapeHtml(year)}</dd>
      <dt>Task</dt><dd>${escapeHtml(formatTask(record.task))}</dd>
      <dt>Institution</dt><dd>${escapeHtml(record.institution)}</dd>
      <dt>Country</dt><dd>${escapeHtml(record.country)}</dd>
      <dt>Authors</dt><dd>${authors}</dd>
      ${methodRow}
      ${confidenceRow}
      ${reviewRow}
      ${resolutionNotesRow}
    </dl>
  `;
}

function updateSummary(visibleRecords) {
  recordCount.textContent = visibleRecords.length;
  countryCount.textContent = new Set(
    visibleRecords.map((record) => record.country).filter(Boolean),
  ).size;
  institutionCount.textContent = new Set(
    visibleRecords.map((record) => record.institution).filter(Boolean),
  ).size;
  reviewCount.textContent = visibleRecords.filter(
    (record) => reviewStatus(record) === true,
  ).length;
}

function renderRecords() {
  const selectedTask = taskFilter.value;
  const selectedYear = yearFilter.value;
  const selectedResolution = resolutionFilter.value;
  const selectedReview = reviewFilter.value;
  const visibleRecords = records.filter((record) => {
    const matchesTask = selectedTask === "all" || record.task === selectedTask;
    const matchesYear = selectedYear === "all" || String(record.year) === selectedYear;
    const matchesResolution =
      selectedResolution === "all" || resolutionConfidence(record) === selectedResolution;
    const status = reviewStatus(record);
    const matchesReview =
      selectedReview === "all" ||
      (selectedReview === "true" && status === true) ||
      (selectedReview === "false" && status === false);
    return matchesTask && matchesYear && matchesResolution && matchesReview;
  });

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
  const recordLabel = datasetConfig.recordLabel;
  mapStatus.textContent = visibleRecords.length
    ? `Showing ${visibleRecords.length} ${recordLabel}${visibleRecords.length === 1 ? "" : "s"}`
    : `No ${recordLabel}s match these filters`;
}

function populateYears() {
  const years = [...new Set(records.map((record) => record.year).filter(Number.isInteger))].sort(
    (a, b) => b - a,
  );
  years.forEach((year) => {
    const option = document.createElement("option");
    option.value = String(year);
    option.textContent = year;
    yearFilter.append(option);
  });
}

function enableControls() {
  taskFilter.disabled = false;
  yearFilter.disabled = false;
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
  markerLayer.clearLayers();
  updateSummary(records);
  mapStatus.textContent = message;
  mapStatus.classList.toggle("error", isError);
}

function updateDatasetLabels() {
  if (datasetName === "sample") {
    return;
  }
  if (datasetName === "preview") {
    prototypeNote.textContent = "Uncurated public preview";
    intro.textContent =
      "Explore a filtered public preview of automatically generated OpenAlex candidate metadata.";
    footer.textContent =
      "Uncurated public preview. These candidate records are not a manually curated bibliography.";
  } else {
    prototypeNote.textContent = "Uncurated OpenAlex candidates";
    intro.textContent =
      "Explore locally generated candidate records for synthetic image detection and attribution research.";
    footer.textContent =
      "Exploratory candidate view. Records are automatically extracted and require manual review.";
  }
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

async function loadData() {
  try {
    const response = await fetch(datasetConfig.url);
    if (!response.ok) {
      if (datasetName === "preview") {
        showDatasetMessage(
          "Preview dataset could not be loaded. Check that web/data/public_preview_map_data.json is published.",
          true,
        );
        return;
      }
      if (datasetName === "openalex") {
        showDatasetMessage(
          "OpenAlex candidate map data is not available. Generate it locally with scripts/export_candidate_map_data.py.",
          true,
        );
        return;
      }
      throw new Error(`Sample data request failed with status ${response.status}`);
    }

    const responseText = await response.text();
    if (!responseText.trim()) {
      showDatasetMessage(datasetConfig.emptyMessage, datasetName !== "sample");
      return;
    }

    const data = JSON.parse(responseText);
    const normalizedData = normalizeDatasetPayload(data);
    if (!normalizedData.records.every(validateRecord)) {
      throw new Error(`${datasetName} data does not match the expected format`);
    }
    if (normalizedData.records.length === 0) {
      showDatasetMessage(datasetConfig.emptyMessage);
      return;
    }

    records = normalizedData.records;
    displayMetadataWarning(normalizedData.metadata);
    populateYears();
    enableControls();
    renderRecords();
  } catch (error) {
    console.error(error);
    const messages = {
      openalex:
        "OpenAlex candidate map data could not be read. Regenerate the local export and try again.",
      preview:
        "Preview dataset could not be loaded. Regenerate the public preview export and try again.",
      sample: "Sample data could not be loaded. Preview the site through a local server.",
    };
    const message = messages[datasetName];
    showDatasetMessage(message, true);
  }
}

taskFilter.addEventListener("change", renderRecords);
yearFilter.addEventListener("change", renderRecords);
resolutionFilter.addEventListener("change", renderRecords);
reviewFilter.addEventListener("change", renderRecords);
resetButton.addEventListener("click", () => {
  taskFilter.value = "all";
  yearFilter.value = "all";
  resolutionFilter.value = "all";
  reviewFilter.value = "all";
  renderRecords();
});

updateDatasetLabels();
loadData();
