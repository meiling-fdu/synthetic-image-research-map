"use strict";

const SAMPLE_DATA_URL = "data/sample_map_data.json";
const WORLD_BOUNDS = L.latLngBounds(L.latLng(-60, -170), L.latLng(75, 170));
const TASK_COLORS = {
  detection: "#287d8e",
  attribution: "#b66a37",
  both: "#76589b",
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
const resetButton = document.querySelector("#reset-filters");
const mapStatus = document.querySelector("#map-status");
const recordCount = document.querySelector("#record-count");
const countryCount = document.querySelector("#country-count");
const institutionCount = document.querySelector("#institution-count");

let records = [];

function escapeHtml(value) {
  const element = document.createElement("span");
  element.textContent = String(value);
  return element.innerHTML;
}

function formatTask(task) {
  return task.charAt(0).toUpperCase() + task.slice(1);
}

function popupContent(record) {
  const authors = record.authors.map(escapeHtml).join(", ");

  return `
    <span class="popup-task">${escapeHtml(formatTask(record.task))}</span>
    <h3 class="popup-title">${escapeHtml(record.paper_title)}</h3>
    <dl class="popup-details">
      <dt>Year</dt><dd>${escapeHtml(record.year)}</dd>
      <dt>Task</dt><dd>${escapeHtml(formatTask(record.task))}</dd>
      <dt>Institution</dt><dd>${escapeHtml(record.institution)}</dd>
      <dt>Country</dt><dd>${escapeHtml(record.country)}</dd>
      <dt>Authors</dt><dd>${authors}</dd>
    </dl>
  `;
}

function updateSummary(visibleRecords) {
  recordCount.textContent = visibleRecords.length;
  countryCount.textContent = new Set(visibleRecords.map((record) => record.country)).size;
  institutionCount.textContent = new Set(
    visibleRecords.map((record) => record.institution),
  ).size;
}

function renderRecords() {
  const selectedTask = taskFilter.value;
  const selectedYear = yearFilter.value;
  const visibleRecords = records.filter((record) => {
    const matchesTask = selectedTask === "all" || record.task === selectedTask;
    const matchesYear = selectedYear === "all" || String(record.year) === selectedYear;
    return matchesTask && matchesYear;
  });

  markerLayer.clearLayers();

  visibleRecords.forEach((record) => {
    L.circleMarker([record.latitude, record.longitude], {
      radius: 8,
      color: "#ffffff",
      weight: 2,
      fillColor: TASK_COLORS[record.task],
      fillOpacity: 0.94,
    })
      .bindPopup(popupContent(record), { maxWidth: 320 })
      .bindTooltip(record.institution, { direction: "top", offset: [0, -7] })
      .addTo(markerLayer);
  });

  updateSummary(visibleRecords);
  mapStatus.textContent = visibleRecords.length
    ? `Showing ${visibleRecords.length} fictional record${visibleRecords.length === 1 ? "" : "s"}`
    : "No fictional records match these filters";
}

function populateYears() {
  const years = [...new Set(records.map((record) => record.year))].sort((a, b) => b - a);
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
  resetButton.disabled = false;
}

function validateRecord(record) {
  const validTasks = Object.keys(TASK_COLORS);
  return (
    typeof record.paper_title === "string" &&
    Number.isInteger(record.year) &&
    validTasks.includes(record.task) &&
    typeof record.institution === "string" &&
    typeof record.country === "string" &&
    Array.isArray(record.authors) &&
    Number.isFinite(record.latitude) &&
    Number.isFinite(record.longitude)
  );
}

async function loadData() {
  try {
    const response = await fetch(SAMPLE_DATA_URL);
    if (!response.ok) {
      throw new Error(`Sample data request failed with status ${response.status}`);
    }

    const data = await response.json();
    if (!Array.isArray(data.records) || !data.records.every(validateRecord)) {
      throw new Error("Sample data does not match the expected format");
    }

    records = data.records;
    populateYears();
    enableControls();
    renderRecords();
  } catch (error) {
    console.error(error);
    mapStatus.textContent = "Sample data could not be loaded. Preview the site through a local server.";
    mapStatus.classList.add("error");
  }
}

taskFilter.addEventListener("change", renderRecords);
yearFilter.addEventListener("change", renderRecords);
resetButton.addEventListener("click", () => {
  taskFilter.value = "all";
  yearFilter.value = "all";
  renderRecords();
});

loadData();
