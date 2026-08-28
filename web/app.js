"use strict";

function displayStartupFailure(error) {
  console.error("Public frontend initialization failed.", error);
  const status = document.querySelector("#map-status");
  if (status) {
    status.textContent = "Unable to load research map data.";
    status.classList.add("error");
  }
  const resultsStatus = document.querySelector("#results-count");
  if (resultsStatus) resultsStatus.textContent = "Data unavailable";
  const emptyState = document.querySelector("#results-empty");
  if (emptyState) {
    emptyState.textContent = "Unable to load research map data.";
    emptyState.hidden = false;
  }
  const results = document.querySelector("#results-list");
  if (results) results.hidden = true;
  document.querySelectorAll(".header-chart-content").forEach((container) => {
    container.innerHTML = '<p class="chart-empty">Unable to load data.</p>';
  });
}

window.addEventListener("error", (event) => {
  if (event.error) displayStartupFailure(event.error);
});
window.addEventListener("unhandledrejection", (event) => {
  displayStartupFailure(event.reason);
});

const DATASET_CONFIG = {
  openalex: {
    url: "data/openalex_candidate_map_data.json",
    recordLabel: "institution record",
    emptyMessage:
      "The local OpenAlex dataset contains no records with valid mapped locations.",
  },
  preview: {
    url: "data/public_preview_map_data.json",
    paperUrl: "data/public_preview_papers.json",
    recordLabel: "institution record",
    emptyMessage: "The public dataset contains no eligible map records.",
  },
};

function resolveDatasetName(requestedName) {
  return requestedName === "openalex" ? "openalex" : "preview";
}

const initialUrlSearchParams = new URLSearchParams(window.location.search);
const requestedDataset = initialUrlSearchParams.get("dataset");
const datasetName = resolveDatasetName(requestedDataset);
const datasetConfig = DATASET_CONFIG[datasetName];
const preservedDatasetParameter = ["preview", "openalex"].includes(requestedDataset)
  ? requestedDataset
  : "";
const URL_STATE_PARAMETER_ORDER = [
  "keyword", "task", "paper_type", "publication_type", "venue", "country",
  "institution_type", "version", "year_start", "year_end", "institution",
  "institution_label", "paper", "view", "sort",
];
const PAPER_ISSUE_URL = "https://github.com/meiling-fdu/synthetic-image-research-map/issues/new";
const TILE_BOUNDS = L.latLngBounds([[-85, -180], [85, 180]]);
const DISPLAY_BOUNDS = L.latLngBounds([[-50, -170], [72, 180]]);
const BASE_MIN_ZOOM = 1;
const WORLD_TILE_SIZE = 256;
const NO_WRAP_HORIZONTAL_BUFFER = 40;
const TASK_COLORS = {
  detection: "#287d8e",
  source_attribution: "#b66a37",
  detection_and_source_attribution: "#76589b",
  uncertain: "#68747d",
};
const PUBLIC_TASK_LABELS = {
  detection: "Detection",
  source_attribution: "Source Attribution",
  detection_and_source_attribution: "Detection + Source Attribution",
  uncertain: "Unknown",
};
const ENTRY_TYPE_LABELS = {
  method: "Method",
  dataset: "Dataset",
  benchmark: "Benchmark",
  survey: "Survey",
  analysis: "Analysis study",
};
const INSTITUTION_TYPE_ORDER = InstitutionTypeLabels.values;
const CHINA_REGION_BY_CODE = {
  HK: "Hong Kong",
  MO: "Macau",
  TW: "Taiwan",
};
const CHINA_REGION_CODE_BY_NAME = {
  "hong kong": "HK",
  "hong kong sar": "HK",
  "hong kong sar china": "HK",
  hk: "HK",
  macao: "MO",
  "macao sar": "MO",
  "macao sar china": "MO",
  macau: "MO",
  "macau sar": "MO",
  "macau sar china": "MO",
  mo: "MO",
  taiwan: "TW",
  "taiwan province of china": "TW",
  tw: "TW",
};
const COUNTRY_NAME_BY_CODE = {
  AE: "United Arab Emirates", AT: "Austria", AU: "Australia", BD: "Bangladesh",
  BE: "Belgium", BG: "Bulgaria", BR: "Brazil", CA: "Canada", CH: "Switzerland",
  CN: "China", CO: "Colombia", CZ: "Czechia", DE: "Germany", DK: "Denmark",
  DZ: "Algeria", EG: "Egypt", ES: "Spain", FI: "Finland", FR: "France",
  GB: "United Kingdom", GR: "Greece", HR: "Croatia", ID: "Indonesia",
  IE: "Ireland", IL: "Israel", IN: "India", IQ: "Iraq", IR: "Iran",
  IT: "Italy", JO: "Jordan", JP: "Japan", KR: "South Korea", LB: "Lebanon",
  ME: "Montenegro", MT: "Malta", MX: "Mexico", MY: "Malaysia",
  NL: "Netherlands", NO: "Norway", NP: "Nepal", NZ: "New Zealand",
  PK: "Pakistan", PL: "Poland", PT: "Portugal", RU: "Russia",
  SA: "Saudi Arabia", SE: "Sweden", SG: "Singapore", SI: "Slovenia",
  SK: "Slovakia", SY: "Syria", TH: "Thailand", TR: "Turkey",
  UA: "Ukraine", US: "United States", VN: "Vietnam", ZA: "South Africa",
};

function noWrapMinZoomForWidth(width) {
  return Math.max(
    BASE_MIN_ZOOM,
    Math.log2((Math.max(width, 1) + NO_WRAP_HORIZONTAL_BUFFER) / WORLD_TILE_SIZE),
  );
}

const mapElement = document.querySelector("#map");
const map = L.map(mapElement, {
  minZoom: noWrapMinZoomForWidth(mapElement.clientWidth),
  maxBounds: TILE_BOUNDS,
  maxBoundsViscosity: 1,
  attributionControl: false,
  zoomDelta: 0.25,
  zoomSnap: 0.25,
  wheelPxPerZoomLevel: 180,
}).fitBounds(DISPLAY_BOUNDS, { padding: [8, 8], animate: false });

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  noWrap: true,
  bounds: TILE_BOUNDS,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);
const hoverConnectionLayer = L.layerGroup().addTo(map);
const selectedConnectionLayer = L.layerGroup().addTo(map);
const institutionHoverTooltip = L.tooltip({
  className: "institution-marker-tooltip",
  direction: "top",
  interactive: false,
  offset: [0, -4],
  permanent: false,
  sticky: false,
});
const keywordFilter = document.querySelector("#keyword-filter");
const taskFilter = document.querySelector("#task-filter");
const entryTypeFilter = document.querySelector("#entry-type-filter");
const sortControl = document.querySelector("#sort-control");
const venueFilter = document.querySelector("#venue-filter");
const venueTypeFilter = document.querySelector("#venue-type-filter");
const countryFilter = document.querySelector("#country-filter");
const institutionTypeFilter = document.querySelector("#institution-type-filter");
const preprintFilter = document.querySelector("#preprint-filter");
const minYearFilter = document.querySelector("#min-year-filter");
const maxYearFilter = document.querySelector("#max-year-filter");
const yearRangeMinimum = document.querySelector("#year-range-min");
const yearRangeMaximum = document.querySelector("#year-range-max");
const yearRangeSlider = document.querySelector(".year-range-slider");
const resetButton = document.querySelector("#reset-filters");
const activeFilterBar = document.querySelector("#active-filter-bar");
const activeFilterChips = document.querySelector("#active-filter-chips");
const clearActiveFiltersButton = document.querySelector("#clear-active-filters");
const activeFilterStatus = document.querySelector("#active-filter-status");
const filtersPanel = document.querySelector("#filters-panel");
const filtersBackdrop = document.querySelector("#filters-backdrop");
const mobileFiltersTrigger = document.querySelector("#mobile-filters-trigger");
const mobileFiltersTriggerLabel = document.querySelector("#mobile-filters-trigger-label");
const closeFiltersButton = document.querySelector("#close-filters");
const doneFiltersButton = document.querySelector("#done-filters");
const filtersHeading = document.querySelector("#filters-heading");
const mobileFiltersMedia = window.matchMedia("(max-width: 820px)");
const mapStatus = document.querySelector("#map-status");
const datasetRecordCount = document.querySelector("#dataset-record-count");
const datasetPaperCount = document.querySelector("#dataset-paper-count");
const datasetInstitutionCount = document.querySelector("#dataset-institution-count");
const datasetCountryCount = document.querySelector("#dataset-country-count");
const datasetStatisticsNote = document.querySelector("#dataset-statistics-note");
const taskChartContent = document.querySelector("#task-chart-content");
const institutionChartContent = document.querySelector("#institution-chart-content");
const yearChartContent = document.querySelector("#year-chart-content");
const headerStatistics = document.querySelector(".header-statistics");
const resultsCount = document.querySelector("#results-count");
const resultsList = document.querySelector("#results-list");
const resultsLoading = document.querySelector("#results-loading");
const resultsEmpty = document.querySelector("#results-empty");
const resultsEmptyHeading = document.querySelector("#results-empty-heading");
const resultsEmptySummary = document.querySelector("#results-empty-summary");
const resultsEmptyFilterActions = document.querySelector("#results-empty-filter-actions");
const undoLastFilterButton = document.querySelector("#undo-last-filter");
const clearEmptyFiltersButton = document.querySelector("#clear-empty-filters");
const copyViewLinkButton = document.querySelector("#copy-view-link");
const copyViewLinkStatus = document.querySelector("#copy-view-link-status");
const exportCsvButton = document.querySelector("#export-csv");
const resultsViewButtons = document.querySelectorAll("[data-results-view]");
const paperDetails = document.querySelector("#paper-details");
const paperDetailsContent = document.querySelector("#paper-details-content");
const closePaperDetailsButton = document.querySelector("#close-paper-details");
const paperDetailsPinStatus = document.querySelector("#paper-details-pin-status");

let records = [];
let paperRecords = [];
let canonicalPaperRecordsByIdentity = new Map();
let mapRecordsByPaperIdentity = new Map();
let institutionAliases = [];
let institutionHierarchy = [];
let institutionSearchRelationships = [];
let canonicalInstitutionSearchIndex = {};
let institutionIdRedirects = {};
const normalizedRecordSearchTextById = new Map();
let cachedInstitutionFilterIndexes = null;
let currentFilteredRecords = [];
let currentFilteredPaperRecords = [];
let currentDisplayedResults = [];
let resultsView = "institutions";
let visibleMarkerEntries = [];
let visibleMarkerEntryByInstitutionKey = new Map();
let activeInstitutionFilter = null;
let displayedInstitutionFilter = null;
let yearRangeBounds = null;
let venueTypeOrder = ["conference", "journal", "preprint", "book"];
let filterDropdowns = [];
let filterDropdownBySelect = new Map();
let filtersDrawerOpen = false;
const resultsMasonryFrames = new Set();
let resultsRenderGeneration = 0;
let resultsObserver = null;
let resultsKeywordFrame = null;
let resultsResizeTimeout = null;
let resultsPipeline = null;
let keywordCompositionActive = false;
let filteringDataCacheGeneration = 0;
let searchTextPrewarmHandle = null;
let searchTextPrewarmGeneration = -1;
let activeFilterChipsSignature = "";
let lastKnownFilterState = null;
let lastFilterChange = null;
let urlStateReady = false;
let restoringUrlState = false;
let pendingUrlHistoryMode = "replace";
let lastCanonicalViewUrl = "";
let keywordHistoryStarted = false;
let yearHistoryStarted = false;
let copyLinkFeedbackTimer = null;
let copyPaperLinkFeedbackTimer = null;
let pendingResultReveal = null;
let requestedPaperIdentity = "";
let visiblePaperSelectionByIdentity = new Map();
const RESULTS_RESIZE_DEBOUNCE_MS = 100;
const RESULTS_INITIAL_VIEWPORTS = 2.25;
const RESULTS_OBSERVER_MARGIN = "125% 0px";
const interactionState = {
  hoveredMarkerId: null,
  selectedMarkerId: null,
  detailsSource: null,
  isPointerInsideDetails: false,
  hovered: null,
  selected: null,
};
let activeInstitutionTooltipMarker = null;

const supportsMarkerHover = window.matchMedia?.(
  "(hover: hover) and (pointer: fine)",
).matches ?? false;

const rootStyles = getComputedStyle(document.documentElement);
const MARKER_TASK_PALETTES = {
  detection: {
    fill: rootStyles.getPropertyValue("--map-detection-fill").trim() || "#5a9da6",
    stroke: rootStyles.getPropertyValue("--map-detection-stroke").trim() || "#376f78",
  },
  source_attribution: {
    fill: rootStyles.getPropertyValue("--map-attribution-fill").trim() || "#c58a55",
    stroke: rootStyles.getPropertyValue("--map-attribution-stroke").trim() || "#8b5a32",
  },
  detection_and_source_attribution: {
    fill: rootStyles.getPropertyValue("--map-mixed-fill").trim() || "#8b6fa8",
    stroke: rootStyles.getPropertyValue("--map-mixed-stroke").trim() || "#604877",
  },
  unknown: {
    fill: rootStyles.getPropertyValue("--map-unknown-fill").trim() || "#8a98a3",
    stroke: rootStyles.getPropertyValue("--map-unknown-stroke").trim() || "#5d6b75",
  },
};
const BASE_MARKER_STYLE = {
  radius: 8,
  weight: 1.5,
  fillOpacity: 0.5,
  opacity: 0.68,
};
const DIMMED_MARKER_STYLE = {
  radius: 7.5,
  weight: 1.1,
  fillOpacity: 0.24,
  opacity: 0.42,
};
const RELATED_MARKER_STYLE = {
  radius: 9.5,
  weight: 1.8,
  fillOpacity: 0.62,
  opacity: 0.82,
};
const CURRENT_MARKER_STYLE = {
  radius: 11.5,
  weight: 2.2,
  fillOpacity: 0.7,
  opacity: 0.9,
};
const CONNECTION_LINE_STYLE = {
  color: rootStyles.getPropertyValue("--map-connection-line").trim() || "#2f4554",
  weight: 2.4,
  opacity: 0.68,
  interactive: false,
  dashArray: "6 5",
  lineCap: "round",
  className: "paper-connection-line",
};
let mapResizeTimer = null;

function updateNoWrapMinZoom() {
  const minZoom = noWrapMinZoomForWidth(map.getSize().x);
  map.setMinZoom(minZoom);
  return minZoom;
}

function scheduleMapResize(fitWorld = false) {
  window.clearTimeout(mapResizeTimer);
  mapResizeTimer = window.setTimeout(() => {
    map.invalidateSize({ animate: false, pan: false });
    const minZoom = updateNoWrapMinZoom();
    if (fitWorld) {
      map.fitBounds(DISPLAY_BOUNDS, { padding: [8, 8], animate: false });
    }
    if (map.getZoom() < minZoom) {
      map.setZoom(minZoom, { animate: false });
    }
  }, 0);
}

const INSTITUTION_CSV_COLUMNS = [
  ["title", (record) => recordTitle(record)],
  ["authors", (record) => recordAuthors(record).join("; ")],
  ["institution_authors", (record) => recordInstitutionAuthors(record).join("; ")],
  ["publication_year", (record) => publicationYear(record) ?? ""],
  ["publication_type", (record) => record.publication_type || ""],
  ["venue_label", (record) => venueDisplayLabel(record)],
  ["venue_id", (record) => isBookRecord(record) ? "" : record.venue_id || ""],
  ["venue_name", (record) => getRecordVenue(record)],
  ["venue_acronym", (record) => isBookRecord(record) ? "" : record.venue_acronym || ""],
  ["venue_type", (record) => recordVenueType(record)],
  ["venue_track", (record) => canonicalVenueTrack(record)],
  ["paper_categories", (record) => getPaperCategories(record).join(";")],
  ["task", (record) => record.task || ""],
  ["institution_name", (record) => recordInstitution(record)],
  ["institution_id", (record) => String(record.institution_id || "")],
  ["institution_type", (record) => normalizeInstitutionType(record.institution_type)],
  ["country", (record) => record.country || ""],
  ["country_code", (record) => record.country_code || ""],
  ["region", (record) => record.region || ""],
  ["region_code", (record) => record.region_code || ""],
  ["raw_country", (record) => record.raw_country || ""],
  ["raw_country_code", (record) => record.raw_country_code || ""],
  ["doi", (record) => normalizedDoi(record.doi)],
  ["arxiv_id", (record) => recordArxivId(record)],
  ["arxiv_url", (record) => recordArxivUrl(record)],
  ["paper_url", (record) => recordPaperUrl(record)],
  ["openalex_url", (record) => record.openalex_url || ""],
];

const PAPER_CSV_COLUMNS = [
  ["title", (record) => recordTitle(record)],
  ["authors", (record) => recordAuthors(record).join("; ")],
  ["publication_year", (record) => publicationYear(record) ?? ""],
  ["publication_type", (record) => record.publication_type || ""],
  ["venue_label", (record) => venueDisplayLabel(record)],
  ["venue_id", (record) => isBookRecord(record) ? "" : record.venue_id || ""],
  ["venue_name", (record) => getRecordVenue(record)],
  ["venue_acronym", (record) => isBookRecord(record) ? "" : record.venue_acronym || ""],
  ["venue_type", (record) => recordVenueType(record)],
  ["venue_track", (record) => canonicalVenueTrack(record)],
  ["paper_categories", (record) => getPaperCategories(record).join(";")],
  ["task", (record) => record.task || ""],
  ["institutions", (record) => (record.aggregated_institutions || []).join("; ")],
  ["institution_ids", (record) => canonicalInstitutionIds(record).join("; ")],
  ["institution_types", (record) => institutionTypesForRecord(record).join("; ")],
  ["locations", (record) => (record.aggregated_locations || [])
    .map((location) => location.location_display || "")
    .filter(Boolean).join("; ")],
  ["countries", (record) => (record.aggregated_country_names || []).join("; ")],
  ["country_codes", (record) => (record.aggregated_country_codes || []).join("; ")],
  ["regions", (record) => (record.aggregated_regions || []).join("; ")],
  ["region_codes", (record) => (record.aggregated_region_codes || []).join("; ")],
  ["has_map_location", (record) => String(Boolean(record.has_map_location))],
  ["map_record_count", (record) => record.map_record_count ?? ""],
  ["coverage_status", (record) => record.coverage_status || ""],
  ["doi", (record) => normalizedDoi(record.doi)],
  ["arxiv_id", (record) => recordArxivId(record)],
  ["arxiv_url", (record) => recordArxivUrl(record)],
  ["paper_url", (record) => recordPaperUrl(record)],
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

function formatPublicTask(task) {
  const normalized = MarkerSizeHelpers.normalizeTaskLabel(task);
  return PUBLIC_TASK_LABELS[normalized] || PUBLIC_TASK_LABELS.uncertain;
}

function canonicalPaperRecord(record) {
  return canonicalPaperRecordsByIdentity.get(paperIdentity(record)) || record;
}

function getPaperCategories(record) {
  if (isBookRecord(record)) return [];
  const raw = record.paper_categories ?? record.entry_type ?? record.material_type ?? "";
  const values = Array.isArray(raw) ? raw : String(raw).split(";");
  const selected = new Set(values.map((value) => String(value).trim().toLowerCase()).filter(Boolean));
  const unknown = [...selected].filter((value) => !Object.hasOwn(ENTRY_TYPE_LABELS, value));
  if (unknown.length) throw new Error(`Unknown paper categories: ${unknown.join(", ")}`);
  return Object.keys(ENTRY_TYPE_LABELS).filter((value) => selected.has(value));
}

function getEntryTypeLabel(value) {
  return ENTRY_TYPE_LABELS[value] || ENTRY_TYPE_LABELS.method;
}

function recordTitle(record) {
  return record.title ?? record.paper_title;
}

function paperTitleHtml(record) {
  return TitleMarkup.toHtml(recordTitle(record), escapeHtml);
}

function recordAuthors(record) {
  let authorValue = record.authors;
  if (typeof authorValue === "string" && /^[\[{]/.test(authorValue.trim())) {
    try {
      authorValue = JSON.parse(authorValue);
    } catch (_error) {
      authorValue = record.authors;
    }
  }
  const authors = Array.isArray(authorValue) ? authorValue : [authorValue];
  const names = authors
    .map((author) => String(
      author && typeof author === "object"
        ? author.name || author.display_name || author.author || ""
        : author || "",
    ).trim())
    .filter((name) => name && name.toLocaleLowerCase() !== "[object object]");
  if (names.length) {
    return names;
  }
  const legacyText = String(record.authors_text || "").trim();
  return legacyText ? [legacyText] : [];
}

function recordInstitutionAuthors(record) {
  const authors = Array.isArray(record.institution_authors)
    ? record.institution_authors
    : String(record.institution_authors || "").split(/[;,]/);
  return authors
    .map((author) => String(author || "").trim())
    .filter(Boolean);
}

function normalizedAuthorName(value) {
  const displayName = String(
    value && typeof value === "object"
      ? value.name || value.author || ""
      : value || "",
  ).trim();
  const commaParts = displayName.split(",");
  const orderedName = commaParts.length === 2
    ? `${commaParts[1].trim()} ${commaParts[0].trim()}`
    : displayName;
  return orderedName
    .normalize("NFKC")
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function matchingAuthorMapValue(authorName, valuesByAuthor) {
  const exact = valuesByAuthor.get(normalizedAuthorName(authorName));
  if (exact !== undefined) {
    return exact;
  }
  const matches = [...valuesByAuthor.entries()].filter(([candidate]) => (
    PaperDetailsHelpers.namesMatch(authorName, candidate)
  ));
  return matches.length === 1 ? matches[0][1] : undefined;
}

function institutionIdentity(record) {
  const stableId = String(
    record.institution_id || record.canonical_institution_id || "",
  ).trim();
  if (stableId) {
    return `id:${stableId.toLocaleLowerCase()}`;
  }
  return `name:${normalizedTitle(
    record.canonical_institution_name || recordInstitution(record),
  )}`;
}

function markerInstitutionIdentity(record) {
  const institution = institutionIdentity(record);
  const location = String(record?.location_id || "").trim();
  const coordinates = [
    record?.latitude ?? record?.lat ?? "",
    record?.longitude ?? record?.lon ?? "",
  ].map((value) => String(value).trim()).join(",");
  const site = location ? `location:${location}` : `coordinates:${coordinates}`;
  return coordinates === "," && !location ? institution : `${institution}||${site}`;
}

function recordInstitutionIdentities(record) {
  const identities = new Set();
  if (recordInstitution(record)) {
    identities.add(institutionIdentity(record));
  }
  const affiliations = [
    ...(Array.isArray(record.affiliations) ? record.affiliations : []),
    ...(Array.isArray(record.author_institution_affiliations)
      ? record.author_institution_affiliations
      : []),
  ];
  affiliations.forEach((rawAffiliation) => {
    const affiliation = typeof rawAffiliation === "string"
      ? { institution: rawAffiliation }
      : rawAffiliation || {};
    identities.add(institutionIdentity({
      institution: affiliation.name || affiliation.institution || affiliation.institution_name,
      institution_id: affiliation.institution_id || affiliation.canonical_institution_id,
      canonical_institution_name: affiliation.canonical_name,
      abbreviation: affiliation.abbreviation,
    }));
  });
  identities.delete("name:");
  return identities;
}

function canonicalInstitutionIds(record) {
  return [...recordInstitutionIdentities(record)]
    .filter((identity) => identity.startsWith("id:"))
    .map((identity) => identity.slice(3));
}

function affiliationIdentity(record) {
  const institution = institutionIdentity(record);
  return institution === "name:"
    ? `location:${normalizedTitle(recordLocation(record))}`
    : institution;
}

function normalizePaperDetailsRecord(record, context = {}) {
  const relatedRecords = (context.relatedRecords || []).filter(Boolean);
  const sourceRecords = [record, ...relatedRecords.filter((item) => item !== record)];
  const currentInstitutionValue = record?.current_institution;
  const currentInstitution = currentInstitutionValue
    && typeof currentInstitutionValue === "object"
    ? currentInstitutionValue
    : {
        name: typeof currentInstitutionValue === "string"
          ? currentInstitutionValue
          : recordInstitution(record || {}),
        institution_id: record?.institution_id || "",
        canonical_name: record?.canonical_institution_name || "",
        abbreviation: record?.abbreviation || "",
        institution_type: record?.institution_type || "",
        country: record?.country || "",
        region: record?.region || "",
      };
  const currentIdentity = currentInstitution.name
    ? affiliationIdentity({
        institution: currentInstitution.name,
        institution_id: currentInstitution.institution_id,
        canonical_institution_name: currentInstitution.canonical_name,
        abbreviation: currentInstitution.abbreviation,
      })
    : "";
  const affiliationsByIdentity = new Map();
  const sourceIndexIdentities = new Map();

  function addAffiliation(rawAffiliation, sourceRecord) {
    const rawValue = typeof rawAffiliation === "string"
      ? { name: rawAffiliation }
      : rawAffiliation || {};
    const raw = normalizeCountryRegionRecord(rawValue);
    const institution = InstitutionDisplay.formatRecord(raw);
    if (!institution) {
      return;
    }
    const identity = affiliationIdentity({
      institution,
      institution_id: raw.institution_id || raw.canonical_institution_id || "",
      canonical_institution_name: raw.canonical_name || "",
      abbreviation: raw.abbreviation || "",
      city: raw.city || "",
      region: raw.region || "",
      country: raw.country || "",
    });
    let affiliation = affiliationsByIdentity.get(identity);
    if (!affiliation) {
      affiliation = {
        number: Number(raw.index) || affiliationsByIdentity.size + 1,
        institution,
        institutionId: String(
          raw.institution_id || raw.canonical_institution_id || "",
        ).trim(),
        abbreviation: String(raw.abbreviation || "").trim(),
        institutionType: normalizeInstitutionType(raw.institution_type || raw.type),
        country: String(raw.country || "").trim(),
        region: String(raw.region || "").trim(),
        location: recordLocation(raw),
        authors: [],
        authorKeys: new Set(),
        isCurrent: false,
      };
      affiliationsByIdentity.set(identity, affiliation);
    } else if (
      affiliation.institutionType === "other"
      && normalizeInstitutionType(raw.institution_type || raw.type) !== "other"
    ) {
      affiliation.institutionType = normalizeInstitutionType(
        raw.institution_type || raw.type,
      );
    }
    const rawAuthors = Array.isArray(raw.authors) ? raw.authors : [];
    rawAuthors.forEach((author) => {
      const authorName = String(
        author && typeof author === "object"
          ? author.name || author.author || ""
          : author || "",
      ).trim();
      const authorKey = normalizedAuthorName(author);
      if (authorKey && !affiliation.authorKeys.has(authorKey)) {
        affiliation.authorKeys.add(authorKey);
        affiliation.authors.push(authorName);
      }
    });
    const rawIndex = Number(raw.index);
    if (sourceRecord && Number.isInteger(rawIndex) && rawIndex > 0) {
      if (!sourceIndexIdentities.has(sourceRecord)) {
        sourceIndexIdentities.set(sourceRecord, new Map());
      }
      sourceIndexIdentities.get(sourceRecord).set(rawIndex, identity);
    }
  }

  sourceRecords.forEach((sourceRecord) => {
    const exported = Array.isArray(sourceRecord?.affiliations)
      ? sourceRecord.affiliations
      : [];
    const legacy = Array.isArray(sourceRecord?.author_institution_affiliations)
      ? sourceRecord.author_institution_affiliations
      : [];
    const sourceAffiliations = exported.length ? exported : legacy;
    sourceAffiliations.forEach((affiliation) => {
      // The display schema carries location metadata; its matching legacy
      // row carries authors. Enrich existing IDs without unioning institutions.
      const authorRow = legacy.find((item) => affiliation?.institution_id
        && item?.institution_id === affiliation.institution_id);
      addAffiliation(authorRow
        ? { ...affiliation, authors: authorRow.authors || affiliation.authors || [] }
        : affiliation, sourceRecord);
    });
  });

  // Legacy records may only carry one institution per marker. Preserve that
  // paper-level information without manufacturing author mappings.
  if (!affiliationsByIdentity.size) {
    sourceRecords.forEach((sourceRecord) => {
      const institution = recordInstitution(sourceRecord || {});
      if (institution) {
        addAffiliation({
          name: institution,
          institution_id: sourceRecord.institution_id,
          institution_type: sourceRecord.institution_type,
          city: sourceRecord.city,
          region: sourceRecord.region,
          country: sourceRecord.country,
        }, sourceRecord);
      }
    });
  }

  const affiliations = [...affiliationsByIdentity.entries()]
    .sort(([, first], [, second]) => first.number - second.number)
    .map(([identity, affiliation], index) => ({
      ...affiliation,
      number: index + 1,
      isCurrent: Boolean(currentIdentity) && identity === currentIdentity,
    }));
  const affiliationNumberByIdentity = new Map(
    [...affiliationsByIdentity.keys()].map((identity, index) => [
      identity,
      index + 1,
    ]),
  );
  const affiliationNumbersByAuthor = new Map();
  affiliations.forEach((affiliation) => {
    affiliation.authors.forEach((author) => {
      const authorKey = normalizedAuthorName(author);
      const indices = affiliationNumbersByAuthor.get(authorKey) || [];
      if (authorKey && !indices.includes(affiliation.number)) {
        indices.push(affiliation.number);
        affiliationNumbersByAuthor.set(authorKey, indices);
      }
    });
  });

  sourceRecords.forEach((sourceRecord) => {
    const indexIdentities = sourceIndexIdentities.get(sourceRecord) || new Map();
    const mappings = [
      ...(Array.isArray(sourceRecord?.author_affiliation_indices)
        ? sourceRecord.author_affiliation_indices
        : []),
      ...(Array.isArray(sourceRecord?.author_institution_indices)
        ? sourceRecord.author_institution_indices
        : []),
    ];
    mappings.forEach((mapping) => {
      const authorKey = normalizedAuthorName(mapping.author || mapping.name);
      const mappedIndices = (
        mapping.indices
        ||
        mapping.institution_indices
        || mapping.affiliation_indices
        || []
      ).map((index) => affiliationNumberByIdentity.get(indexIdentities.get(Number(index))))
        .filter(Boolean);
      if (authorKey && mappedIndices.length) {
        affiliationNumbersByAuthor.set(
          authorKey,
          uniqueTextValues([
            ...(affiliationNumbersByAuthor.get(authorKey) || []),
            ...mappedIndices,
          ]).map(Number),
        );
      }
    });
  });

  const currentNumber = affiliations.find((affiliation) => affiliation.isCurrent)?.number;
  const institutionAuthorKeys = new Set(recordInstitutionAuthors(record || {}).map(
    normalizedAuthorName,
  ));
  const rawAuthors = Array.isArray(record?.authors) && record.authors.length
    ? record.authors
    : record?.authors_text
      ? [record.authors_text]
      : [record?.authors];
  const authors = rawAuthors.map((rawAuthor) => {
    const raw = rawAuthor && typeof rawAuthor === "object" ? rawAuthor : {};
    const name = String(raw.name || raw.display_name || raw.author || (typeof rawAuthor === "object" ? "" : rawAuthor) || "").trim();
    const authorKey = normalizedAuthorName(name);
    const explicitIndexSet = new Set(
      Array.isArray(raw.affiliation_indices)
        ? raw.affiliation_indices.map(Number).filter((index) => Number.isInteger(index) && index > 0)
        : [],
    );
    const explicitIndices = affiliations
      .map((affiliation) => affiliation.number)
      .filter((number) => explicitIndexSet.has(number));
    const nonInstitutional = raw.affiliation_status === "non_institutional"
      && raw.affiliation_review?.status === "non_institutional"
      && raw.affiliation_review?.review_id;
    const affiliationIndices = nonInstitutional ? [] : explicitIndices.length
      ? explicitIndices
      : matchingAuthorMapValue(name, affiliationNumbersByAuthor) || [];
    const isCurrentMarkerAuthor = typeof raw.is_current_marker_author === "boolean"
      ? raw.is_current_marker_author
      : Boolean(
          currentNumber
          && (
            affiliationIndices.includes(currentNumber)
            || institutionAuthorKeys.has(authorKey)
            || [...institutionAuthorKeys].some((candidate) => (
              PaperDetailsHelpers.namesMatch(name, candidate)
            ))
          )
        );
    return {
      name,
      affiliation_indices: affiliationIndices,
      is_current_marker_author: nonInstitutional ? false : isCurrentMarkerAuthor,
      affiliation_status: raw.affiliation_status,
      affiliation_review: raw.affiliation_review,
    };
  }).filter((author) => author.name);

  return {
    ...record,
    authors,
    affiliations,
    current_institution: currentNumber
      ? affiliations[currentNumber - 1]
      : currentInstitution.name
        ? currentInstitution
        : null,
  };
}

function visiblePaperAffiliations(currentRecord, relatedEntries) {
  const baseRecord = currentRecord || relatedEntries[0]?.record || {};
  return normalizePaperDetailsRecord(baseRecord, {
    relatedRecords: relatedEntries.map(({ record }) => record),
  }).affiliations;
}

function renderPaperAuthors(
  record,
  currentAffiliationNumber = null,
  visibleLimit = Infinity,
  regionId = "",
) {
  const normalized = normalizePaperDetailsRecord(record);
  return PaperDetailsHelpers.renderPaperAuthors(
    normalized,
    escapeHtml,
    currentAffiliationNumber,
    visibleLimit,
    regionId,
  );
}

function institutionFilterButtonHtml(affiliation) {
  const label = InstitutionDisplay.formatRecord({
    canonical_name: affiliation.canonicalName || affiliation.canonical_name,
    abbreviation: affiliation.abbreviation,
    institution: affiliation.institution || affiliation.name,
  });
  if (!label) {
    return "";
  }
  const identity = institutionIdentity({
    institution: label,
    institution_id: affiliation.institutionId || affiliation.institution_id,
    canonical_institution_name: affiliation.canonicalName || affiliation.canonical_name,
  });
  return `<button type="button" class="institution-filter-link" data-institution-filter="${escapeHtml(identity)}" data-institution-label="${escapeHtml(label)}" aria-label="Filter by institution ${escapeHtml(label)}">${escapeHtml(label)}</button>`;
}

function institutionFocusButtonHtml(affiliation, markerRecord = null) {
  const label = InstitutionDisplay.formatRecord({
    canonical_name: affiliation.canonicalName || affiliation.canonical_name,
    abbreviation: affiliation.abbreviation,
    institution: affiliation.institution || affiliation.name,
  });
  if (!label) return "";
  const institutionRecord = {
    institution: label,
    institution_id: affiliation.institutionId || affiliation.institution_id,
    canonical_institution_name: affiliation.canonicalName || affiliation.canonical_name,
  };
  const identity = markerRecord
    ? markerInstitutionIdentity({ ...institutionRecord, ...markerRecord })
    : institutionIdentity(institutionRecord);
  return `<button type="button" class="institution-filter-link institution-map-focus-link" data-focus-institution="${escapeHtml(identity)}" aria-label="Highlight ${escapeHtml(label)} on the map">${escapeHtml(label)}</button>`;
}

function compactAffiliationsHtml(affiliations, limit = 3) {
  const visibleAffiliations = affiliations.slice(0, limit);
  const items = visibleAffiliations.map((affiliation) => (
    `<span class="result-affiliation-item${affiliation.isCurrent ? " is-current" : ""}"><sup>${affiliation.number}</sup>${institutionFilterButtonHtml(affiliation)} <span class="affiliation-type">(${escapeHtml(institutionTypeLabel(affiliation.institutionType))})</span></span>`
  ));
  const remaining = affiliations.length - visibleAffiliations.length;
  if (remaining > 0) {
    items.push(`<span class="result-affiliation-more">+${remaining} more</span>`);
  }
  return items.join("; ");
}

function selectedFilterOptionLabel(control) {
  const label = control.selectedOptions?.[0]?.textContent || control.value;
  return String(label).replace(/\s+\([\d,]+\)$/, "").trim();
}

function activeFilterChipDescriptors() {
  const descriptors = [];
  const keyword = keywordFilter.value.trim();
  if (keyword) descriptors.push({ key: "keyword", category: "Keyword", value: keyword });
  if (taskFilter.value !== "all") {
    descriptors.push({ key: "task", category: "Task", value: formatPublicTask(taskFilter.value) });
  }
  if (entryTypeFilter.value !== "all") {
    descriptors.push({
      key: "entry-type", category: "Research Type", value: getEntryTypeLabel(entryTypeFilter.value),
    });
  }
  if (venueTypeFilter.value !== "all") {
    descriptors.push({
      key: "venue-type", category: "Publication Type",
      value: selectedFilterOptionLabel(venueTypeFilter),
    });
  }
  if (venueFilter.value !== "all") {
    descriptors.push({
      key: "venue", category: "Venue", value: selectedFilterOptionLabel(venueFilter),
    });
  }
  if (countryFilter.value !== "all") {
    descriptors.push({
      key: "country", category: "Country", value: selectedFilterOptionLabel(countryFilter),
    });
  }
  if (institutionTypeFilter.value !== "all") {
    descriptors.push({
      key: "institution-type", category: "Institution Type",
      value: institutionTypeLabel(institutionTypeFilter.value),
    });
  }
  if (preprintFilter.value !== "all") {
    descriptors.push({
      key: "version", category: "Version", value: selectedFilterOptionLabel(preprintFilter),
    });
  }
  const selection = currentYearSelection();
  if (yearRangeBounds && selection && (
    selection.start !== yearRangeBounds.minimum || selection.end !== yearRangeBounds.maximum
  )) {
    descriptors.push({
      key: "year", category: "Publication Year",
      value: selection.start === selection.end
        ? String(selection.start)
        : `${selection.start}\u2013${selection.end}`,
    });
  }
  if (activeInstitutionFilter) {
    descriptors.push({
      key: "institution", category: "Institution", value: activeInstitutionFilter.label,
    });
  }
  return descriptors;
}

function currentViewState() {
  const years = currentYearSelection();
  return {
    keyword: keywordFilter.value.trim(),
    task: taskFilter.value,
    paperType: entryTypeFilter.value,
    publicationType: venueTypeFilter.value,
    venue: venueFilter.value,
    country: countryFilter.value,
    institutionType: institutionTypeFilter.value,
    version: preprintFilter.value,
    yearStart: years?.start ?? null,
    yearEnd: years?.end ?? null,
    yearMinimum: yearRangeBounds?.minimum ?? null,
    yearMaximum: yearRangeBounds?.maximum ?? null,
    institution: activeInstitutionFilter?.identity || "",
    institutionLabel: activeInstitutionFilter?.label || "",
    paper: requestedPaperIdentity,
    view: resultsView,
    sort: sortControl.value,
  };
}

function currentFilterConstraintState() {
  const { view, sort, paper, ...filters } = currentViewState();
  return filters;
}

function filterConstraintSignature(state) {
  return JSON.stringify(state);
}

function rememberFilterChange(key, { coalesce = false } = {}) {
  const after = currentFilterConstraintState();
  const before = lastKnownFilterState || after;
  if (filterConstraintSignature(before) === filterConstraintSignature(after)) return;
  if (coalesce && lastFilterChange?.key === key) {
    lastFilterChange.after = after;
  } else {
    lastFilterChange = { key, before, after };
  }
  lastKnownFilterState = after;
}

function syncKnownFilterState() {
  const current = currentFilterConstraintState();
  if (lastKnownFilterState
    && filterConstraintSignature(lastKnownFilterState) !== filterConstraintSignature(current)
    && !restoringUrlState) {
    lastFilterChange = { key: "", before: lastKnownFilterState, after: current };
  }
  lastKnownFilterState = current;
}

function serializeViewState(state, datasetParameter = "") {
  const params = new URLSearchParams();
  if (["preview", "openalex"].includes(datasetParameter)) {
    params.set("dataset", datasetParameter);
  }
  const values = {
    keyword: state.keyword,
    task: state.task !== "all" ? state.task : "",
    paper_type: state.paperType !== "all" ? state.paperType : "",
    publication_type: state.publicationType !== "all" ? state.publicationType : "",
    venue: state.venue !== "all" ? state.venue : "",
    country: state.country !== "all" ? state.country : "",
    institution_type: state.institutionType !== "all" ? state.institutionType : "",
    version: state.version !== "all" ? state.version : "",
    year_start: Number.isInteger(state.yearStart)
      && state.yearStart !== state.yearMinimum ? String(state.yearStart) : "",
    year_end: Number.isInteger(state.yearEnd)
      && state.yearEnd !== state.yearMaximum ? String(state.yearEnd) : "",
    institution: state.institution,
    institution_label: state.institution ? state.institutionLabel : "",
    paper: state.paper,
    view: state.view !== "institutions" ? state.view : "",
    sort: state.sort !== "year-desc" ? state.sort : "",
  };
  URL_STATE_PARAMETER_ORDER.forEach((key) => {
    const value = String(values[key] ?? "").trim();
    if (value) params.set(key, value);
  });
  return params.toString();
}

function parseViewState(search) {
  const params = search instanceof URLSearchParams
    ? search
    : new URLSearchParams(String(search || "").replace(/^\?/, ""));
  const yearValue = (key) => {
    const raw = params.get(key);
    if (!/^\d{4}$/.test(raw || "")) return null;
    return Number(raw);
  };
  return {
    keyword: params.get("keyword") || "",
    task: params.get("task") || "all",
    paperType: params.get("paper_type") || "all",
    publicationType: params.get("publication_type") || "all",
    venue: params.get("venue") || "all",
    country: params.get("country") || "all",
    institutionType: params.get("institution_type") || "all",
    version: params.get("version") || "all",
    yearStart: yearValue("year_start"),
    yearEnd: yearValue("year_end"),
    institution: params.get("institution") || "",
    institutionLabel: params.get("institution_label") || "",
    paper: params.get("paper") || "",
    view: params.get("view") || "institutions",
    sort: params.get("sort") || "year-desc",
  };
}

function canonicalViewUrl(state = currentViewState(), href = window.location.href) {
  const url = new URL(href);
  url.search = serializeViewState(state, preservedDatasetParameter);
  url.hash = "";
  return url.href;
}

function selectContainsValue(select, value) {
  return [...select.options].some((option) => option.value === value);
}

function setRestoredSelectValue(select, value, { dynamic = false } = {}) {
  const normalized = String(value || "").trim();
  if (!normalized || normalized === "all") {
    select.value = "all";
    return;
  }
  if (!selectContainsValue(select, normalized)) {
    if (!dynamic) {
      select.value = "all";
      return;
    }
    const option = document.createElement("option");
    option.value = normalized;
    option.textContent = normalized;
    select.append(option);
  }
  select.value = normalized;
}

function setResultsViewState(view) {
  resultsView = ["institutions", "papers"].includes(view) ? view : "institutions";
  resultsViewButtons.forEach((button) => {
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.resultsView === resultsView),
    );
  });
}

function restoreViewState(state) {
  resetFilterValues({ resetSort: true });
  keywordFilter.value = state.keyword;
  setRestoredSelectValue(taskFilter, state.task);
  setRestoredSelectValue(entryTypeFilter, state.paperType);
  setRestoredSelectValue(venueTypeFilter, state.publicationType, { dynamic: true });
  setRestoredSelectValue(venueFilter, state.venue, { dynamic: true });
  setRestoredSelectValue(countryFilter, state.country, { dynamic: true });
  setRestoredSelectValue(institutionTypeFilter, state.institutionType, { dynamic: true });
  setRestoredSelectValue(preprintFilter, state.version);
  if (yearRangeBounds) {
    const selection = resolveYearSelection(yearRangeBounds, {
      start: state.yearStart ?? yearRangeBounds.minimum,
      end: state.yearEnd ?? yearRangeBounds.maximum,
    });
    minYearFilter.value = String(selection.start);
    maxYearFilter.value = String(selection.end);
    syncYearRange();
  }
  if (state.institution) {
    activeInstitutionFilter = {
      identity: state.institution,
      label: state.institutionLabel
        || hierarchyInstitutionLabel(state.institution, institutionHierarchy)
        || state.institution,
    };
  }
  requestedPaperIdentity = String(state.paper || "").trim();
  if (selectContainsValue(sortControl, state.sort)) sortControl.value = state.sort;
  setResultsViewState(state.view);
  filterDropdowns.forEach(syncFilterDropdown);
}

function requestUrlStateSync(mode = "push") {
  if (mode === "push" || pendingUrlHistoryMode !== "push") {
    pendingUrlHistoryMode = mode;
  }
}

function syncUrlFromState() {
  if (!urlStateReady || restoringUrlState) return;
  const nextUrl = canonicalViewUrl();
  if (nextUrl === window.location.href || nextUrl === lastCanonicalViewUrl) {
    lastCanonicalViewUrl = nextUrl;
    pendingUrlHistoryMode = "replace";
    return;
  }
  const method = pendingUrlHistoryMode === "push" ? "pushState" : "replaceState";
  window.history[method]({ researchMapView: true }, "", nextUrl);
  lastCanonicalViewUrl = nextUrl;
  pendingUrlHistoryMode = "replace";
}

function restoreViewStateFromLocation() {
  restoringUrlState = true;
  lastFilterChange = null;
  try {
    restoreViewState(parseViewState(window.location.search));
    renderRecords();
  } finally {
    restoringUrlState = false;
  }
  lastCanonicalViewUrl = "";
  pendingUrlHistoryMode = "replace";
  syncUrlFromState();
}

function renderActiveFilterChips() {
  const descriptors = activeFilterChipDescriptors();
  const signature = JSON.stringify(descriptors);
  if (signature === activeFilterChipsSignature) return;
  activeFilterChipsSignature = signature;
  const fragment = document.createDocumentFragment();
  descriptors.forEach(({ key, category, value }) => {
    const item = document.createElement("li");
    const label = document.createElement("span");
    const remove = document.createElement("button");
    item.className = "active-filter-chip";
    label.className = "active-filter-chip-label";
    label.textContent = `${category}: ${value}`;
    remove.type = "button";
    remove.dataset.removeFilter = key;
    remove.setAttribute("aria-label", `Remove ${category} filter: ${value}`);
    remove.textContent = "\u00d7";
    item.append(label, remove);
    fragment.append(item);
  });
  activeFilterChips.replaceChildren(fragment);
  activeFilterBar.hidden = descriptors.length === 0;
  clearActiveFiltersButton.hidden = descriptors.length < 2;
  activeFilterStatus.textContent = descriptors.length
    ? `${descriptors.length} active filter${descriptors.length === 1 ? "" : "s"}`
    : "No active filters";
}

function applyInstitutionFilter(identity, label) {
  activeInstitutionFilter = { identity, label };
  rememberFilterChange("institution");
  requestUrlStateSync("push");
  renderRecords();
}

function clearInstitutionFilter() {
  const clearedKeyword = !activeInstitutionFilter
    && displayedInstitutionFilter?.source === "keyword";
  if (!activeInstitutionFilter && displayedInstitutionFilter?.source === "keyword") {
    keywordFilter.value = "";
  }
  activeInstitutionFilter = null;
  rememberFilterChange(clearedKeyword ? "keyword" : "institution");
  requestUrlStateSync("push");
  renderRecords();
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
  const doi = normalizedDoi(record.doi).toLowerCase();
  if (doi) {
    return `doi:${doi}`;
  }

  const openalexUrl = normalizedIdentityValue(record.openalex_url);
  if (openalexUrl) {
    return `openalex:${openalexUrl}`;
  }

  const arxivId = normalizedIdentityValue(record.arxiv_id).replace(/^arxiv:/, "");
  if (arxivId) {
    return `arxiv:${arxivId}`;
  }

  const paperUrl = normalizedIdentityValue(recordPaperUrl(record));
  if (paperUrl) {
    return `url:${paperUrl}`;
  }

  const title = normalizedTitle(recordTitle(record));
  const year = record.publication_year ?? record.year ?? "";
  return `title-year:${title}:${year}`;
}

function recordInstitution(record) {
  return InstitutionDisplay.formatRecord(record);
}

function recordCountry(record) {
  return String(record.country_code || record.country || "").trim();
}

function recordLatLng(record) {
  return L.latLng(Number(record.latitude), Number(record.longitude));
}

function coordinateKey(latLng) {
  return `${latLng.lat.toFixed(6)},${latLng.lng.toFixed(6)}`;
}

function uniqueMarkerLocations(entries) {
  const seen = new Set();
  const locations = [];
  entries.forEach((entry) => {
    const latLng = recordLatLng(entry.record);
    if (!Number.isFinite(latLng.lat) || !Number.isFinite(latLng.lng)) {
      return;
    }
    const key = coordinateKey(latLng);
    if (seen.has(key)) {
      return;
    }
    seen.add(key);
    locations.push(latLng);
  });
  return locations;
}

function markerStyle(taskKey, state = "base", paperCount = 1) {
  const normalizedTask = taskKey === "mixed"
    ? "detection_and_source_attribution"
    : MarkerSizeHelpers.normalizeTaskLabel(taskKey);
  const palette = MARKER_TASK_PALETTES[normalizedTask] || MARKER_TASK_PALETTES.unknown;
  const colors = { color: palette.stroke, fillColor: palette.fill };
  const radius = MarkerSizeHelpers.getMarkerRadius(paperCount);
  if (state === "current") {
    return { ...CURRENT_MARKER_STYLE, ...colors, radius: Math.min(20, radius + 2) };
  }
  if (state === "related") {
    return { ...RELATED_MARKER_STYLE, ...colors, radius: Math.min(19, radius + 1) };
  }
  if (state === "dimmed") {
    return { ...DIMMED_MARKER_STYLE, ...colors, radius: Math.max(5.5, radius - 0.5) };
  }
  return { ...BASE_MARKER_STYLE, ...colors, radius };
}

function closeActiveInstitutionTooltip(marker = null) {
  if (marker && activeInstitutionTooltipMarker !== marker) {
    return;
  }
  institutionHoverTooltip.remove();
  activeInstitutionTooltipMarker = null;
}

function openInstitutionTooltip(marker, record, paperCount, taskBreakdown) {
  closeActiveInstitutionTooltip();
  const breakdownLine = taskBreakdown
    ? `<br>${escapeHtml(taskBreakdown)}`
    : "";
  institutionHoverTooltip
    .setLatLng(marker.getLatLng())
    .setContent(
      `<strong>${escapeHtml(recordInstitution(record) || "Unknown institution")}</strong><br>${escapeHtml(MarkerSizeHelpers.formatInstitutionPaperCount(paperCount))}${breakdownLine}`,
    )
    .openOn(map);
  activeInstitutionTooltipMarker = marker;
}

function clearActiveInstitutionHover() {
  const marker = activeInstitutionTooltipMarker;
  if (marker && interactionState.hovered?.marker === marker) {
    clearHoverPreview(marker);
    return;
  }
  closeActiveInstitutionTooltip();
}

map.on("movestart zoomstart", clearActiveInstitutionHover);
mapElement.addEventListener("mouseleave", (event) => {
  if (paperDetails.contains(event.relatedTarget)) {
    return;
  }
  clearActiveInstitutionHover();
});
function normalizedLocationName(value) {
  return String(value || "")
    .normalize("NFKC")
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function normalizeCountryRegionRecord(record) {
  const country = String(record.country || "").trim();
  const sourceCountryCode = String(record.country_code || "").trim();
  const countryCode = sourceCountryCode.toUpperCase();
  const region = String(record.region || "").trim();
  const regionCode = String(record.region_code || "").trim().toUpperCase();
  const rawCountry = Object.hasOwn(record, "raw_country")
    ? String(record.raw_country || "").trim()
    : country;
  const rawCountryCode = Object.hasOwn(record, "raw_country_code")
    ? String(record.raw_country_code || "").trim()
    : sourceCountryCode;

  let normalizedRegionCode = [regionCode, countryCode, rawCountryCode.toUpperCase()]
    .find((code) => Object.hasOwn(CHINA_REGION_BY_CODE, code)) || "";
  if (!normalizedRegionCode) {
    normalizedRegionCode = [region, country, rawCountry]
      .map(normalizedLocationName)
      .map((name) => CHINA_REGION_CODE_BY_NAME[name] || "")
      .find(Boolean) || "";
  }

  if (normalizedRegionCode) {
    return {
      ...record,
      country: "China",
      country_code: "CN",
      region: CHINA_REGION_BY_CODE[normalizedRegionCode],
      region_code: normalizedRegionCode,
      raw_country: rawCountry,
      raw_country_code: rawCountryCode,
    };
  }

  const countryAsCode = /^[A-Za-z]{2}$/.test(country) ? country.toUpperCase() : "";
  const normalizedCountryCode = countryCode || countryAsCode;

  return {
    ...record,
    country: COUNTRY_NAME_BY_CODE[countryAsCode] || country
      || COUNTRY_NAME_BY_CODE[normalizedCountryCode] || "",
    country_code: normalizedCountryCode,
    region,
    region_code: regionCode,
    raw_country: rawCountry,
    raw_country_code: rawCountryCode,
  };
}

function normalizeInstitutionType(value) {
  return InstitutionTypeLabels.normalize(value);
}

function institutionTypeLabel(value) {
  return InstitutionTypeLabels.label(value);
}

function canonicalCountryName(value, countryCode = "") {
  const candidate = String(value || "").trim();
  const code = String(countryCode || "").trim().toUpperCase();
  const candidateCode = /^[A-Za-z]{2}$/.test(candidate) ? candidate.toUpperCase() : "";
  return COUNTRY_NAME_BY_CODE[candidateCode] || COUNTRY_NAME_BY_CODE[code] || candidate;
}

function dimensionAffiliations(record) {
  const values = [
    ...(Array.isArray(record.affiliations) ? record.affiliations : []),
    ...(Array.isArray(record.author_institution_affiliations)
      ? record.author_institution_affiliations
      : []),
  ];
  const unique = new Map();
  values.forEach((rawValue) => {
    const value = typeof rawValue === "string" ? { institution: rawValue } : rawValue || {};
    const identity = institutionIdentity({
      institution: value.name || value.institution || value.institution_name,
      institution_id: value.institution_id || value.canonical_institution_id,
      canonical_institution_name: value.canonical_name,
      abbreviation: value.abbreviation,
    });
    if (identity !== "name:" && !unique.has(identity)) unique.set(identity, value);
  });
  return [...unique.values()];
}

function countriesForRecord(record, institutionRecord = false) {
  const values = [];
  const add = (country, code = "") => {
    const name = canonicalCountryName(country, code);
    if (name) values.push(name);
  };
  if (institutionRecord) {
    const normalized = normalizeCountryRegionRecord(record);
    add(normalized.country, normalized.country_code);
  } else {
    (record.aggregated_country_names || []).forEach((country) => add(country));
    (record.aggregated_country_codes || []).forEach((code) => add("", code));
    dimensionAffiliations(record).forEach((affiliation) => {
      const normalized = normalizeCountryRegionRecord(affiliation);
      add(normalized.country, normalized.country_code);
    });
    if (!values.length && recordInstitution(record)) {
      const normalized = normalizeCountryRegionRecord(record);
      add(normalized.country, normalized.country_code);
    }
  }
  return uniqueTextValues(values);
}

function institutionTypesForRecord(record, institutionRecord = false) {
  const values = [];
  const add = (value) => values.push(normalizeInstitutionType(value));
  if (institutionRecord) {
    add(record.institution_type || record.type);
  } else {
    (record.aggregated_institution_types || []).forEach(add);
    dimensionAffiliations(record).forEach((affiliation) => (
      add(affiliation.institution_type || affiliation.type)
    ));
    if (!values.length && recordInstitution(record)) {
      add(record.institution_type || record.type);
    }
  }
  return uniqueTextValues(values);
}

function recordMatchesInstitutionDimensions(
  record,
  selectedCountry,
  selectedInstitutionType,
  institutionRecord = false,
  requiredInstitutionIdentities = null,
) {
  if (institutionRecord) {
    const matchesIdentity = !requiredInstitutionIdentities?.size
      || requiredInstitutionIdentities.has(institutionIdentity(record));
    const matchesCountry = selectedCountry === "all"
      || countriesForRecord(record, true).includes(selectedCountry);
    const matchesInstitutionType = selectedInstitutionType === "all"
      || institutionTypesForRecord(record, true).includes(selectedInstitutionType);
    return matchesIdentity && matchesCountry && matchesInstitutionType;
  }

  const affiliations = dimensionAffiliations(record);
  if (affiliations.length) {
    return affiliations.some((affiliation) => {
      const matchesIdentity = !requiredInstitutionIdentities?.size
        || requiredInstitutionIdentities.has(institutionIdentity({
          institution: affiliation.name || affiliation.institution,
          institution_id: affiliation.institution_id
            || affiliation.canonical_institution_id,
          canonical_institution_name: affiliation.canonical_name,
          abbreviation: affiliation.abbreviation,
        }));
      const matchesCountry = selectedCountry === "all"
        || countriesForRecord(affiliation, true).includes(selectedCountry);
      const matchesInstitutionType = selectedInstitutionType === "all"
        || institutionTypesForRecord(affiliation, true).includes(
          selectedInstitutionType,
        );
      return matchesIdentity && matchesCountry && matchesInstitutionType;
    });
  }

  const matchesIdentity = !requiredInstitutionIdentities?.size
    || recordMatchesInstitutionIdentities(record, requiredInstitutionIdentities, false);
  const matchesCountry = selectedCountry === "all"
    || countriesForRecord(record).includes(selectedCountry);
  const matchesInstitutionType = selectedInstitutionType === "all"
    || institutionTypesForRecord(record).includes(selectedInstitutionType);
  return matchesIdentity && matchesCountry && matchesInstitutionType;
}

function recordLocation(record) {
  const exportedDisplay = String(record.location_display || "").trim();
  if (exportedDisplay) return exportedDisplay;
  const country = String(record.country || "").trim();
  const defensiveCountry = /^[A-Za-z]{2}$/.test(country) ? "" : country;
  return uniqueTextValues([record.region, defensiveCountry]).join(", ");
}

function recordPaperUrl(record) {
  return (
    record.paper_url ||
    record.primary_url ||
    record.landing_page_url ||
    record.url ||
    record.openalex_url ||
    ""
  );
}

function getRecordVenue(record) {
  if (isBookRecord(record)) return "";
  return String(
    record.venue_name ||
    record.venue ||
    record.source_name ||
    record.source ||
    record.host_venue ||
    record.host_venue_name ||
    record.primary_location?.source?.display_name ||
    "",
  ).trim();
}

function canonicalVenueTrack(record) {
  if (isBookRecord(record)) return "";
  if (String(record?.venue_type || "").trim().toLowerCase() !== "conference") return "";
  const track = String(record?.venue_track || "Main").trim();
  const key = track.toLowerCase().replace(/[_\s-]+/g, " ");
  return ({main:"Main", workshop:"Workshop", workshops:"Workshop", tutorial:"Tutorial", tutorials:"Tutorial",
    demo:"Demo", demos:"Demo", challenge:"Challenge", challenges:"Challenge", "short paper":"Short Paper",
    "short papers":"Short Paper", findings:"Findings", poster:"Poster", posters:"Poster", industry:"Industry",
    "doctoral consortium":"Doctoral Consortium", other:"Other", "main track":"Main", "workshop track":"Workshop",
    "industry track":"Industry", "demo track":"Demo", demonstration:"Demo", demonstrations:"Demo"})[key] || track;
}

function venueFilterValue(record) {
  if (isBookRecord(record)) return "__not_applicable__";
  return String(record.venue_id || "").trim() || (getRecordVenue(record)
    ? getRecordVenue(record).toLocaleLowerCase()
    : "__unknown__");
}

function venueBaseDisplayLabel(record) {
  const name = getRecordVenue(record);
  if (!name) return "Unknown publication venue";
  const acronym = String(record.venue_acronym || "").trim();
  return acronym ? `${name} (${acronym})` : name;
}

function venueDisplayLabel(record) {
  if (isBookRecord(record)) return "";
  const exported = String(record.venue_label || "").trim();
  if (exported) return exported;
  const name = getRecordVenue(record);
  if (!name) return "Unknown publication venue";
  const acronym = String(record.venue_acronym || "").trim();
  const track = canonicalVenueTrack(record);
  let label = name;
  if (acronym) label += ` (${acronym})`;
  const trackLabel = formatTask(track);
  const alreadyNamed = trackLabel && new RegExp(`\\b${trackLabel.replace(/s$/i, "")}s?\\b`, "i")
    .test(`${name} ${acronym}`);
  if (track && track !== "Main" && !alreadyNamed) label += ` · ${trackLabel}`;
  return label;
}

function recordVenueType(record) {
  return String(record.publication_type || record.venue_type || "").trim().toLocaleLowerCase();
}

function isBookRecord(record) {
  return String(record?.publication_type || "").trim().toLocaleLowerCase() === "book";
}

function venueDisplayHtml(record) {
  const label = venueDisplayLabel(record);
  const type = recordVenueType(record);
  if (!label || !type) return escapeHtml(label);
  return `<span class="venue-type-badge">${escapeHtml(formatTask(type))}</span><span class="venue-label-name"> · ${escapeHtml(label)}</span>`;
}

function getRecordYear(record) {
  const value = record.publication_year ?? record.year;
  const year = Number(value);
  return Number.isInteger(year) ? year : null;
}

function compareTextValues(first, second) {
  return String(first || "").localeCompare(String(second || ""), undefined, {
    sensitivity: "base",
    numeric: true,
  });
}

function compareRecordsForSort(first, second, sortMode) {
  const firstYear = getRecordYear(first);
  const secondYear = getRecordYear(second);
  if (sortMode === "year-asc" || sortMode === "year-desc") {
    const direction = sortMode === "year-asc" ? 1 : -1;
    if (firstYear !== null && secondYear !== null && firstYear !== secondYear) {
      return (firstYear - secondYear) * direction;
    }
    if (firstYear !== null && secondYear === null) {
      return -1;
    }
    if (firstYear === null && secondYear !== null) {
      return 1;
    }
    return compareTextValues(recordTitle(first), recordTitle(second));
  }

  if (sortMode === "venue-asc") {
    const firstVenue = getRecordVenue(first);
    const secondVenue = getRecordVenue(second);
    if (firstVenue && !secondVenue) {
      return -1;
    }
    if (!firstVenue && secondVenue) {
      return 1;
    }
    const venueOrder = compareTextValues(firstVenue, secondVenue);
    return venueOrder || compareTextValues(recordTitle(first), recordTitle(second));
  }

  const titleOrder = compareTextValues(recordTitle(first), recordTitle(second));
  return sortMode === "title-desc" ? -titleOrder : titleOrder;
}

function uniqueTextValues(values) {
  const seen = new Set();
  const unique = [];
  values.forEach((value) => {
    const text = String(value || "").trim();
    const key = text.toLocaleLowerCase();
    if (text && !seen.has(key)) {
      seen.add(key);
      unique.push(text);
    }
  });
  return unique;
}

function orderedPaperLocationSummary(institutionRecords) {
  const seenInstitutions = new Set();
  const locations = [];
  institutionRecords.forEach((sourceRecord) => {
    const identity = institutionIdentity(sourceRecord);
    if (seenInstitutions.has(identity)) return;
    seenInstitutions.add(identity);
    const record = normalizeCountryRegionRecord(sourceRecord);
    const locationDisplay = recordLocation(record);
    locations.push({
      institution_name: recordInstitution(record),
      institution_id: String(record.institution_id || "").trim(),
      institution_type: normalizeInstitutionType(record.institution_type || record.type),
      country: record.country,
      country_code: record.country_code,
      region: record.region,
      region_code: record.region_code,
      location_display: locationDisplay,
    });
  });
  const values = (field) => uniqueTextValues(locations.map((location) => location[field]));
  return {
    aggregated_locations: locations,
    aggregated_institutions: values("institution_name"),
    aggregated_institution_types: values("institution_type"),
    aggregated_countries: values("country_code"),
    aggregated_country_names: values("country"),
    aggregated_country_codes: values("country_code"),
    aggregated_regions: values("region"),
    aggregated_region_codes: values("region_code"),
  };
}

function aggregateUniquePapers(institutionRecords) {
  const papersByIdentity = new Map();
  institutionRecords.forEach((record) => {
    const identity = paperIdentity(record);
    let paper = papersByIdentity.get(identity);
    if (!paper) {
      paper = {
        ...record,
        // All institution records carry the same paper-level source order.
        // Keep the first list; institution aggregation must not alter it.
        authors: recordAuthors(record),
        aggregated_institutions: [],
        aggregated_institution_types: [],
        aggregated_locations: [],
        aggregated_countries: [],
        aggregated_country_names: [],
        aggregated_country_codes: [],
        aggregated_regions: [],
        aggregated_region_codes: [],
        _related_records: [],
      };
      papersByIdentity.set(identity, paper);
    }

    paper._related_records.push(record);
  });
  return [...papersByIdentity.values()].map((paper) => {
    Object.assign(paper, orderedPaperLocationSummary(paper._related_records));
    const normalized = normalizePaperDetailsRecord(
      {
        ...paper,
        authors: recordAuthors(paper),
        current_institution: null,
      },
      { relatedRecords: paper._related_records },
    );
    delete normalized._related_records;
    normalized.current_institution = null;
    normalized.authors = normalized.authors.map((author) => ({
      ...author,
      is_current_marker_author: false,
    }));
    return normalized;
  });
}

function paperListRecordsForDisplay(sourceRecords) {
  if (paperRecords.length || sourceRecords.length) {
    return sourceRecords.map((record) => ({
      aggregated_institutions: [],
      aggregated_institution_types: [],
      aggregated_country_names: [],
      aggregated_country_codes: [],
      aggregated_regions: [],
      aggregated_region_codes: [],
      map_record_count: 0,
      has_map_location: false,
      missing_affiliation: false,
      missing_coordinates: false,
      coverage_status: "paper_only_review",
      ...record,
    }));
  }
  return aggregateUniquePapers(currentFilteredRecords).map((record) => ({
    ...record,
    map_record_count: 1,
    has_map_location: true,
    coverage_status: "map_ready",
  }));
}

function publicationYear(record) {
  return getRecordYear(record);
}

function normalizedSearchText(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/\p{M}+/gu, "")
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function buildInstitutionSearchIndex(
  mapRecords,
  publicPaperRecords,
  aliases,
  hierarchy = [],
  canonicalIndex = {},
) {
  const identitiesByName = new Map();
  const add = (name, identity, authoritative = false) => {
    const key = normalizedSearchText(name);
    if (!key || !identity) return;
    if (!identitiesByName.has(key)) identitiesByName.set(key, new Set());
    identitiesByName.get(key).add(identity);
  };
  Object.entries(canonicalIndex || {}).forEach(([institutionId, entry]) => {
    const identity = institutionIdentity({ institution_id: institutionId });
    const names = Array.isArray(entry?.names) ? entry.names : [];
    [entry?.canonical_name, ...names].forEach((name) => add(name, identity, true));
  });
  aliases.forEach((alias) => {
    const identity = institutionIdentity({
      institution: alias.canonical_institution_name,
      canonical_institution_name: alias.canonical_institution_name,
      institution_id: alias.canonical_institution_id,
    });
    add(alias.alias_name, identity, true);
    add(alias.canonical_institution_name, identity, true);
  });
  const addRecord = (record) => {
    const identity = institutionIdentity(record);
    const canonicalName = record.canonical_institution_name || recordInstitution(record);
    if (!identitiesByName.has(normalizedSearchText(canonicalName))) {
      add(canonicalName, identity);
    }
    const affiliations = [
      ...(Array.isArray(record.affiliations) ? record.affiliations : []),
      ...(Array.isArray(record.author_institution_affiliations)
        ? record.author_institution_affiliations
        : []),
    ];
    affiliations.forEach((rawAffiliation) => {
      const affiliation = typeof rawAffiliation === "string"
        ? { institution: rawAffiliation }
        : rawAffiliation || {};
      const affiliationRecord = {
        institution: affiliation.name || affiliation.institution || affiliation.institution_name,
        canonical_institution_name: affiliation.canonical_name,
        abbreviation: affiliation.abbreviation,
        institution_id: affiliation.institution_id || affiliation.canonical_institution_id,
      };
      const name = affiliationRecord.canonical_institution_name
        || affiliationRecord.institution;
      if (!identitiesByName.has(normalizedSearchText(name))) {
        add(name, institutionIdentity(affiliationRecord));
      }
    });
  };
  [...mapRecords, ...publicPaperRecords].forEach(addRecord);
  hierarchy.forEach((relationship) => {
    add(
      relationship.parent_institution_name,
      institutionIdentity({ institution_id: relationship.parent_institution_id }),
    );
    add(
      relationship.child_institution_name,
      institutionIdentity({ institution_id: relationship.child_institution_id }),
    );
  });
  return identitiesByName;
}

function resolveInstitutionSearchIdentities(value, searchIndex) {
  const query = normalizedSearchText(value);
  if (!query) return new Set();
  const exact = searchIndex.get(query);
  if (exact?.size) return new Set(exact);
  const matches = new Set();
  searchIndex.forEach((identities, normalizedName) => {
    if (!normalizedName.includes(query)) return;
    identities.forEach((identity) => matches.add(identity));
  });
  return matches;
}

function resolveInstitutionSearch(value, searchIndex) {
  const matches = resolveInstitutionSearchIdentities(value, searchIndex);
  return matches?.size === 1 ? [...matches][0] : "";
}

function buildCanonicalInstitutionResolver(aliases, canonicalIndex = {}, idRedirects = {}) {
  const candidatesByName = new Map();
  const byId = new Map();
  const addName = (name, canonical) => {
    const key = normalizedSearchText(name);
    if (!key || !canonical?.id) return;
    if (!candidatesByName.has(key)) candidatesByName.set(key, new Map());
    candidatesByName.get(key).set(canonical.id, canonical);
  };
  Object.entries(canonicalIndex || {}).forEach(([id, entry]) => {
    const canonical = {
      id: String(id).trim(),
      name: String(entry?.canonical_name || "").trim(),
      type: String(entry?.institution_type || "").trim(),
    };
    if (!canonical.id || !canonical.name) return;
    byId.set(canonical.id, canonical);
    [canonical.name, ...(Array.isArray(entry?.names) ? entry.names : [])].forEach((name) => {
      addName(name, canonical);
    });
  });
  aliases.forEach((alias) => {
    const canonical = {
      name: String(alias.canonical_institution_name || "").trim(),
      id: String(alias.canonical_institution_id || "").trim(),
      type: String(
        canonicalIndex?.[alias.canonical_institution_id]?.institution_type || "",
      ).trim(),
    };
    if (!canonical.name || !canonical.id) return;
    addName(alias.alias_name, canonical);
    addName(canonical.name, canonical);
    if (canonical.id) byId.set(canonical.id, canonical);
  });
  const byName = new Map();
  candidatesByName.forEach((candidates, key) => {
    if (candidates.size === 1) byName.set(key, [...candidates.values()][0]);
  });
  byName.delete("");
  Object.entries(idRedirects || {}).forEach(([sourceId, targetId]) => {
    const canonical = byId.get(String(targetId).trim());
    if (canonical) byId.set(String(sourceId).trim(), canonical);
  });
  return { byName, byId };
}

function canonicalizeInstitutionObject(value, resolver) {
  if (!value || typeof value !== "object") return value;
  const nameField = Object.hasOwn(value, "name") ? "name" : "institution";
  const originalName = String(
    value[nameField]
      || value.institution_name
      || value.canonical_name
      || value.canonical_institution_name
      || "",
  ).trim();
  const originalId = String(
    value.institution_id || value.canonical_institution_id || "",
  ).trim();
  const sourceCanonical = resolver.byName.get(normalizedSearchText(value.source_institution));
  const idCanonical = resolver.byId.get(originalId);
  let canonical = idCanonical || resolver.byName.get(normalizedSearchText(originalName));
  if (!idCanonical && sourceCanonical && (!canonical || sourceCanonical.id !== canonical.id)) {
    canonical = sourceCanonical;
  }
  if (!canonical) return value;
  if (originalName && originalName !== canonical.name) {
    value.source_institution ||= originalName;
    value.source_institution_names = [...new Set([
      ...(Array.isArray(value.source_institution_names)
        ? value.source_institution_names
        : []),
      originalName,
    ])];
  }
  if (originalId && canonical.id && originalId !== canonical.id) {
    value.source_institution_id ||= originalId;
  }
  value[nameField] = canonical.name;
  if (Object.hasOwn(value, "institution_name")) value.institution_name = canonical.name;
  value.canonical_name = canonical.name;
  value.canonical_institution_name = canonical.name;
  if (canonical.id) value.institution_id = canonical.id;
  if (canonical.type) value.institution_type = canonical.type;
  return value;
}

function canonicalizePublicDataset(
  mapRecords, publicPaperRecords, aliases, canonicalIndex = {}, idRedirects = {},
) {
  const resolver = buildCanonicalInstitutionResolver(aliases, canonicalIndex, idRedirects);
  const mergeInstitutionEvidence = (target, source) => {
    [
      "authors", "source_institution_names", "raw_affiliation_evidence",
      "raw_affiliations", "provenance_sources", "review_states",
    ]
      .forEach((field) => {
        if (!Array.isArray(target[field]) && !Array.isArray(source[field])) return;
        target[field] = [...new Set([
          ...(Array.isArray(target[field]) ? target[field] : []),
          ...(Array.isArray(source[field]) ? source[field] : []),
        ])];
      });
    if (source.source_institution) {
      target.source_institution_names = [...new Set([
        ...(target.source_institution_names || []),
        source.source_institution,
      ])];
    }
    target.mapping_fallback = Boolean(target.mapping_fallback || source.mapping_fallback);
    target.preliminary = Boolean(target.preliminary || source.preliminary);
  };
  const deduplicateAffiliations = (record) => {
    const affiliations = Array.isArray(record.affiliations) ? record.affiliations : [];
    const oldToNew = new Map();
    const affiliationByIdentity = new Map();
    const deduplicated = [];
    affiliations.forEach((affiliation, offset) => {
      if (!affiliation || typeof affiliation !== "object") return;
      const oldIndex = Number(affiliation.index) || offset + 1;
      const identity = institutionIdentity({
        institution: affiliation.name || affiliation.institution,
        canonical_institution_name: affiliation.canonical_name,
        institution_id: affiliation.institution_id,
      });
      let existing = affiliationByIdentity.get(identity);
      if (!existing) {
        affiliation.index = deduplicated.length + 1;
        deduplicated.push(affiliation);
        affiliationByIdentity.set(identity, affiliation);
        existing = affiliation;
      } else {
        mergeInstitutionEvidence(existing, affiliation);
      }
      oldToNew.set(oldIndex, existing.index);
    });
    if (affiliations.length) record.affiliations = deduplicated;

    const remap = (values) => [...new Set((Array.isArray(values) ? values : [])
      .map(Number)
      .filter((index) => Number.isInteger(index) && index > 0)
      .map((index) => oldToNew.get(index) || index))].sort((first, second) => first - second);
    (Array.isArray(record.authors) ? record.authors : []).forEach((author) => {
      if (author && typeof author === "object") {
        author.affiliation_indices = remap(author.affiliation_indices);
      }
    });
    [
      ["author_affiliation_indices", "indices"],
      ["author_institution_indices", "institution_indices"],
    ].forEach(([field, indexField]) => {
      (Array.isArray(record[field]) ? record[field] : []).forEach((mapping) => {
        if (!mapping || typeof mapping !== "object") return;
        mapping[indexField] = remap(mapping[indexField]);
        mapping.institution_ids = mapping[indexField]
          .map((index) => record.affiliations?.[index - 1]?.institution_id)
          .filter(Boolean);
      });
    });

    if (Array.isArray(record.author_institution_affiliations)) {
      const byIdentity = new Map();
      record.author_institution_affiliations = record.author_institution_affiliations
        .filter((affiliation) => affiliation && typeof affiliation === "object")
        .reduce((result, affiliation) => {
          const identity = institutionIdentity(affiliation);
          const existing = byIdentity.get(identity);
          if (existing) {
            mergeInstitutionEvidence(existing, affiliation);
            return result;
          }
          const canonicalIndexForIdentity = deduplicated.findIndex((candidate) => (
            institutionIdentity(candidate) === identity
          ));
          affiliation.index = canonicalIndexForIdentity >= 0
            ? canonicalIndexForIdentity + 1
            : result.length + 1;
          byIdentity.set(identity, affiliation);
          result.push(affiliation);
          return result;
        }, []);
    }
    const currentIndex = Number(record.current_institution?.index);
    if (Number.isInteger(currentIndex) && oldToNew.has(currentIndex)) {
      record.current_institution.index = oldToNew.get(currentIndex);
    }
  };
  const canonicalizeRecord = (record) => {
    if (recordInstitution(record)) canonicalizeInstitutionObject(record, resolver);
    ["affiliations", "author_institution_affiliations"].forEach((field) => {
      if (Array.isArray(record[field])) {
        record[field].forEach((affiliation) => (
          canonicalizeInstitutionObject(affiliation, resolver)
        ));
      }
    });
    canonicalizeInstitutionObject(record.current_institution, resolver);
    deduplicateAffiliations(record);
    if (Array.isArray(record.aggregated_institutions)) {
      record.aggregated_institutions = [...new Set(
        record.aggregated_institutions.map((name) => (
          resolver.byName.get(normalizedSearchText(name))?.name || name
        )),
      )];
    }
    return record;
  };
  mapRecords.forEach(canonicalizeRecord);
  publicPaperRecords.forEach(canonicalizeRecord);

  const canonicalMapRecords = new Map();
  mapRecords.forEach((record) => {
    // A canonical institution can have multiple paper-specific campus markers.
    const site = record.location_id || [
      record.lat ?? record.latitude ?? "",
      record.lon ?? record.longitude ?? "",
    ].join(",");
    const key = `${paperIdentity(record)}||${institutionIdentity(record)}||${site}`;
    const existing = canonicalMapRecords.get(key);
    if (!existing) {
      canonicalMapRecords.set(key, record);
      return;
    }
    existing.institution_authors = [...new Set([
      ...recordInstitutionAuthors(existing),
      ...recordInstitutionAuthors(record),
    ])];
    existing.source_institution_names = [...new Set([
      ...(existing.source_institution_names || []),
      ...(record.source_institution_names || []),
      ...(record.source_institution ? [record.source_institution] : []),
    ])];
  });
  const canonicalMaps = [...canonicalMapRecords.values()];
  const mapsByPaper = new Map();
  canonicalMaps.forEach((record) => {
    const identity = paperIdentity(record);
    if (!mapsByPaper.has(identity)) mapsByPaper.set(identity, []);
    mapsByPaper.get(identity).push(record);
  });
  publicPaperRecords.forEach((paper) => {
    const related = mapsByPaper.get(paperIdentity(paper)) || [];
    if (["curated", "reviewed_empty"].includes(paper.affiliation_review_state)) {
      const byInstitution = new Map(related.map(record => [record.institution_id, record]));
      const summaryRecords = (paper.affiliations || []).map(affiliation => ({
        ...affiliation, ...byInstitution.get(affiliation.institution_id),
      }));
      Object.assign(paper, orderedPaperLocationSummary(summaryRecords));
      paper.map_record_count = related.length;
      paper.has_map_location = Boolean(related.length);
      return;
    }
    if (!related.length) return;
    paper.map_record_count = related.length;
    paper.has_map_location = true;
    if (typeof orderedPaperLocationSummary === "function") {
      Object.assign(paper, orderedPaperLocationSummary(related));
    } else {
      paper.aggregated_institutions = [...new Set(related.map(recordInstitution))];
    }
  });
  return {
    mapRecords: canonicalMaps,
    paperRecords: publicPaperRecords,
    mapRecordsByPaperIdentity: mapsByPaper,
  };
}

function recordSearchText(record) {
  const authors = recordAuthors(record);
  const venueTerms = isBookRecord(record) ? [] : [
    record.venue_name,
    record.venue,
    record.venue_acronym,
    ...(record.venue_aliases || []),
    record.venue_type,
    record.venue_track,
  ];
  return normalizedSearchText([
    TitleMarkup.searchText(recordTitle(record)),
    ...authors,
    publicationYear(record),
    record.country,
    record.country_code,
    record.region,
    record.region_code,
    ...(record.aggregated_country_names || []),
    ...(record.aggregated_country_codes || []),
    ...(record.aggregated_regions || []),
    ...(record.aggregated_region_codes || []),
    ...venueTerms,
    record.coverage_status,
    record.task,
    ...getPaperCategories(record).map(getEntryTypeLabel),
  ].filter(Boolean).join(" "));
}

function recordSearchCacheId(record) {
  const stableRecordId = String(record.id || record.record_id || "").trim();
  const paperId = stableRecordId || paperIdentity(record);
  const institutionId = recordInstitution(record) ? institutionIdentity(record) : "paper";
  return `${paperId}||${institutionId}`;
}

function cachedRecordSearchText(record) {
  const cacheId = recordSearchCacheId(record);
  if (!normalizedRecordSearchTextById.has(cacheId)) {
    normalizedRecordSearchTextById.set(cacheId, recordSearchText(record));
  }
  return normalizedRecordSearchTextById.get(cacheId);
}

function searchTextMatchesTerms(searchableText, keywordTerms) {
  return keywordTerms.every((term) => searchableText.includes(term));
}

function buildInstitutionHierarchyIndex(relationships) {
  const childrenByParent = new Map();
  relationships.forEach((relationship) => {
    if (relationship.review_status !== "confirmed") return;
    const parent = institutionIdentity({
      institution_id: relationship.parent_institution_id,
    });
    const child = institutionIdentity({
      institution_id: relationship.child_institution_id,
    });
    if (!parent || !child || parent === child) return;
    if (!childrenByParent.has(parent)) childrenByParent.set(parent, new Set());
    childrenByParent.get(parent).add(child);
  });
  return childrenByParent;
}

function buildInstitutionSearchRelationshipIndex(relationships) {
  const relatedByRoot = new Map();
  relationships.forEach((relationship) => {
    if (relationship.review_status !== "confirmed"
        || relationship.relationship_type !== "search_family") return;
    const root = institutionIdentity({
      institution_id: relationship.root_institution_id,
    });
    const related = institutionIdentity({
      institution_id: relationship.related_institution_id,
    });
    if (!root || !related || root === related) return;
    if (!relatedByRoot.has(root)) relatedByRoot.set(root, new Set());
    relatedByRoot.get(root).add(related);
  });
  return relatedByRoot;
}

function invalidateFilteringDataCaches() {
  filteringDataCacheGeneration += 1;
  normalizedRecordSearchTextById.clear();
  cachedInstitutionFilterIndexes = null;
  if (searchTextPrewarmHandle) {
    if (searchTextPrewarmHandle.idle && typeof cancelIdleCallback === "function") {
      cancelIdleCallback(searchTextPrewarmHandle.id);
    } else {
      clearTimeout(searchTextPrewarmHandle.id);
    }
  }
  searchTextPrewarmHandle = null;
  searchTextPrewarmGeneration = -1;
}

function requestSearchTextPrewarmIdle(callback) {
  if (typeof requestIdleCallback === "function") {
    return {
      id: requestIdleCallback(callback, { timeout: 1000 }),
      idle: true,
    };
  }
  return {
    id: setTimeout(() => {
      const started = performance.now();
      callback({
        didTimeout: false,
        timeRemaining: () => Math.max(0, 6 - (performance.now() - started)),
      });
    }, 0),
    idle: false,
  };
}

function scheduleSearchTextCachePrewarm() {
  const dataGeneration = filteringDataCacheGeneration;
  if (searchTextPrewarmGeneration === dataGeneration) return;
  searchTextPrewarmGeneration = dataGeneration;
  const sourceRecords = [...records, ...paperRecords];
  let nextIndex = 0;
  const warmNextChunk = (deadline) => {
    searchTextPrewarmHandle = null;
    if (dataGeneration !== filteringDataCacheGeneration) return;
    let processed = 0;
    while (nextIndex < sourceRecords.length
        && dataGeneration === filteringDataCacheGeneration
        && (deadline.timeRemaining() > 1 || (deadline.didTimeout && processed < 25))
        && processed < 100) {
      cachedRecordSearchText(sourceRecords[nextIndex]);
      nextIndex += 1;
      processed += 1;
    }
    if (nextIndex < sourceRecords.length
        && dataGeneration === filteringDataCacheGeneration) {
      searchTextPrewarmHandle = requestSearchTextPrewarmIdle(warmNextChunk);
    }
  };
  searchTextPrewarmHandle = requestSearchTextPrewarmIdle(warmNextChunk);
}

function institutionFilterIndexes() {
  if (!cachedInstitutionFilterIndexes) {
    cachedInstitutionFilterIndexes = {
      search: buildInstitutionSearchIndex(
        records,
        paperRecords,
        institutionAliases,
        institutionHierarchy,
        canonicalInstitutionSearchIndex,
      ),
      hierarchy: buildInstitutionHierarchyIndex(institutionHierarchy),
      searchRelationships: buildInstitutionSearchRelationshipIndex(
        institutionSearchRelationships,
      ),
    };
  }
  return cachedInstitutionFilterIndexes;
}

function institutionIdentityWithDescendants(identity, hierarchyIndex) {
  const identities = new Set(identity ? [identity] : []);
  if (!identity) return identities;
  const isSpecificChild = [...hierarchyIndex.values()].some((children) => (
    children.has(identity)
  ));
  if (isSpecificChild) return identities;
  const pending = [...(hierarchyIndex.get(identity) || [])];
  while (pending.length) {
    const child = pending.pop();
    if (identities.has(child)) continue;
    identities.add(child);
    pending.push(...(hierarchyIndex.get(child) || []));
  }
  return identities;
}

function institutionIdentitiesWithDescendants(identities, hierarchyIndex) {
  const expanded = new Set();
  (identities || []).forEach((identity) => {
    institutionIdentityWithDescendants(identity, hierarchyIndex).forEach(
      (candidate) => expanded.add(candidate),
    );
  });
  return expanded;
}

function institutionIdentitiesWithSearchExpansion(
  identities,
  hierarchyIndex,
  searchRelationshipIndex,
) {
  const expanded = institutionIdentitiesWithDescendants(
    identities,
    hierarchyIndex,
  );
  const pending = [...expanded];
  while (pending.length) {
    const root = pending.pop();
    (searchRelationshipIndex.get(root) || []).forEach((related) => {
      institutionIdentityWithDescendants(related, hierarchyIndex).forEach(
        (candidate) => {
          if (expanded.has(candidate)) return;
          expanded.add(candidate);
          pending.push(candidate);
        },
      );
    });
  }
  return expanded;
}

function recordMatchesInstitutionIdentities(record, identities, institutionRecord) {
  if (!identities?.size) return true;
  if (institutionRecord) return identities.has(institutionIdentity(record));
  const recordIdentities = recordInstitutionIdentities(record);
  (Array.isArray(record.search_institution_ids)
    ? record.search_institution_ids : []).forEach((institutionId) => {
    recordIdentities.add(institutionIdentity({ institution_id: institutionId }));
  });
  return [...identities].some((identity) => recordIdentities.has(identity));
}

function hierarchyInstitutionLabel(identity, relationships) {
  for (const relationship of relationships) {
    if (institutionIdentity({ institution_id: relationship.parent_institution_id }) === identity) {
      return relationship.parent_institution_name || "";
    }
    if (institutionIdentity({ institution_id: relationship.child_institution_id }) === identity) {
      return relationship.child_institution_name || "";
    }
  }
  return "";
}

function yearFilterValue(input) {
  if (!input.value.trim()) {
    return null;
  }
  const value = Number(input.value);
  return Number.isInteger(value) ? value : null;
}

function recordMatchesActiveFilters(record, keywordTerms, options = {}) {
  const institutionRecord = options.institutionRecord === true;
  const resolvedInstitutionIdentities = options.resolvedInstitutionIdentities;
  const activeInstitutionIdentities = options.activeInstitutionIdentities;
  const matchesInstitutionKeyword = resolvedInstitutionIdentities?.size
    && recordMatchesInstitutionIdentities(
      record, resolvedInstitutionIdentities, institutionRecord,
    );
  const matchesKeyword = keywordTerms.length === 0
    || matchesInstitutionKeyword
    || searchTextMatchesTerms(cachedRecordSearchText(record), keywordTerms);
  const matchesTask = taskFilter.value === "all" || record.task === taskFilter.value;
  const selectedEntryTypes = [...entryTypeFilter.selectedOptions]
    .map((option) => option.value).filter((value) => value !== "all");
  const matchesEntryType = selectedEntryTypes.length === 0
    || selectedEntryTypes.some((value) => getPaperCategories(record).includes(value));
  const matchesVenue =
    options.ignoreVenue === true || venueFilter.value === "all"
    || venueFilterValue(record) === venueFilter.value;
  const matchesVenueType = options.ignoreVenueType === true || venueTypeFilter.value === "all"
    || recordVenueType(record) === venueTypeFilter.value;
  const selectedVersion = preprintFilter.value;
  const matchesVersion =
    selectedVersion === "all" ||
    (selectedVersion === "has-arxiv" && hasArxivVersion(record)) ||
    (selectedVersion === "no-arxiv" && !hasArxivVersion(record));
  const year = publicationYear(record);
  const minimumYear = yearFilterValue(minYearFilter);
  const maximumYear = yearFilterValue(maxYearFilter);
  const isFullYearRange = yearRangeBounds
    && minimumYear === yearRangeBounds.minimum
    && maximumYear === yearRangeBounds.maximum;
  const matchesMinimumYear = isFullYearRange
    || minimumYear === null || (year !== null && year >= minimumYear);
  const matchesMaximumYear = isFullYearRange
    || maximumYear === null || (year !== null && year <= maximumYear);
  const matchesInstitution = !activeInstitutionFilter
    || recordMatchesInstitutionIdentities(
      record, activeInstitutionIdentities, institutionRecord,
    );
  const matchesInstitutionDimensions = recordMatchesInstitutionDimensions(
    record,
    options.ignoreCountry === true ? "all" : countryFilter.value,
    options.ignoreInstitutionType === true ? "all" : institutionTypeFilter.value,
    institutionRecord,
    activeInstitutionFilter
      ? activeInstitutionIdentities
      : resolvedInstitutionIdentities?.size
        ? resolvedInstitutionIdentities
        : null,
  );
  return (
    matchesKeyword &&
    matchesTask &&
    matchesEntryType &&
    matchesVenue &&
    matchesVenueType &&
    matchesVersion &&
    matchesMinimumYear &&
    matchesMaximumYear &&
    matchesInstitution &&
    matchesInstitutionDimensions
  );
}

function dimensionPaperCounts(papers, valuesForRecord) {
  const counts = new Map();
  papers.forEach((paper) => {
    new Set(valuesForRecord(paper)).forEach((value) => {
      if (value) counts.set(value, (counts.get(value) || 0) + 1);
    });
  });
  return counts;
}

function sortedDimensionCounts(counts, labelForValue = (value) => value) {
  return [...counts.entries()].sort((first, second) => (
    second[1] - first[1]
    || compareTextValues(labelForValue(first[0]), labelForValue(second[0]))
  ));
}

function sortedInstitutionTypeCounts(counts) {
  return INSTITUTION_TYPE_ORDER
    .filter((value) => (counts.get(value) || 0) > 0)
    .map((value) => [value, counts.get(value)]);
}

function venueTypeRank(value) {
  const index = venueTypeOrder.indexOf(String(value || "").toLocaleLowerCase());
  return index >= 0 ? index : venueTypeOrder.length;
}

function sortedVenueTypeCounts(counts) {
  return [...counts.entries()].sort((first, second) => (
    venueTypeRank(first[0]) - venueTypeRank(second[0])
    || compareTextValues(formatTask(first[0]), formatTask(second[0]))
  ));
}

function compareStableVenueText(first, second) {
  const normalizedFirst = String(first || "").normalize("NFKC");
  const normalizedSecond = String(second || "").normalize("NFKC");
  const foldedFirst = normalizedFirst.toLowerCase();
  const foldedSecond = normalizedSecond.toLowerCase();
  if (foldedFirst < foldedSecond) return -1;
  if (foldedFirst > foldedSecond) return 1;
  if (normalizedFirst < normalizedSecond) return -1;
  if (normalizedFirst > normalizedSecond) return 1;
  return 0;
}

function sortedVenueCounts(counts, metadataByVenue) {
  return [...counts.entries()].sort((first, second) => {
    const firstMetadata = metadataByVenue.get(first[0]) || {
      name: first[0], type: "__unknown__",
    };
    const secondMetadata = metadataByVenue.get(second[0]) || {
      name: second[0], type: "__unknown__",
    };
    const firstUnknown = first[0] === "__unknown__";
    const secondUnknown = second[0] === "__unknown__";
    if (firstUnknown !== secondUnknown) return firstUnknown ? 1 : -1;
    // Dynamic relevance first; canonical display metadata provides a stable,
    // locale-independent tie-break. Unknown remains the final fallback option.
    return (
      second[1] - first[1]
      || compareStableVenueText(firstMetadata.name, secondMetadata.name)
      || compareStableVenueText(firstMetadata.acronym, secondMetadata.acronym)
      || compareStableVenueText(firstMetadata.track, secondMetadata.track)
      || compareStableVenueText(first[0], second[0])
    );
  });
}

function replaceCountedFilterOptions(
  select, defaultLabel, entries, labelForValue, preserveMissingSelection = true,
) {
  const selectedValue = select.value || "all";
  const options = [["all", defaultLabel], ...entries.map(([value, count]) => (
    [value, `${labelForValue(value)} (${count})`]
  ))];
  const selectedStillAvailable = entries.some(([value]) => value === selectedValue);
  if (preserveMissingSelection && selectedValue !== "all" && !selectedStillAvailable) {
    options.push([selectedValue, `${labelForValue(selectedValue)} (0)`]);
  }
  select.replaceChildren(...options.map(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    return option;
  }));
  select.value = selectedValue === "all" || selectedStillAvailable
    ? selectedValue
    : "all";
}

function nextFilterOptionIndex(visibleIndices, currentIndex, direction) {
  if (!visibleIndices.length) return -1;
  const currentPosition = visibleIndices.indexOf(currentIndex);
  if (currentPosition === -1) {
    return direction < 0
      ? visibleIndices[visibleIndices.length - 1]
      : visibleIndices[0];
  }
  const nextPosition = (
    currentPosition + direction + visibleIndices.length
  ) % visibleIndices.length;
  return visibleIndices[nextPosition];
}

function filterDropdownPlacement(
  triggerRect,
  panelHeight,
  viewportHeight,
  padding = 8,
) {
  const availableBelow = viewportHeight - triggerRect.bottom - padding;
  const availableAbove = triggerRect.top - padding;
  const placement = availableBelow < panelHeight && availableAbove > availableBelow
    ? "up"
    : "down";
  return { placement };
}

function filterDropdownOptionElements(dropdown) {
  return [...dropdown.options.querySelectorAll("[role='option']")];
}

function setActiveFilterDropdownOption(dropdown, index, scroll = false) {
  dropdown.activeIndex = index;
  let activeElement = null;
  filterDropdownOptionElements(dropdown).forEach((option) => {
    const isActive = Number(option.dataset.filterOptionIndex) === index;
    option.classList.toggle("is-active", isActive);
    if (isActive) activeElement = option;
  });
  const activeId = activeElement?.id || "";
  if (activeId) dropdown.button.setAttribute("aria-activedescendant", activeId);
  else dropdown.button.removeAttribute("aria-activedescendant");
  if (scroll && activeElement) {
    activeElement.scrollIntoView({ block: "nearest" });
  }
}

function visibleFilterDropdownOptionIndices(dropdown) {
  return filterDropdownOptionElements(dropdown)
    .filter((option) => !option.hidden)
    .map((option) => Number(option.dataset.filterOptionIndex));
}

function moveActiveFilterDropdownOption(dropdown, direction) {
  setActiveFilterDropdownOption(
    dropdown,
    nextFilterOptionIndex(
      visibleFilterDropdownOptionIndices(dropdown),
      dropdown.activeIndex,
      direction,
    ),
    true,
  );
}

function syncFilterDropdown(dropdown) {
  dropdown.optionData = [...dropdown.select.options].map((option, index) => ({
    value: option.value,
    label: option.textContent,
    index,
  }));
  dropdown.options.replaceChildren(...dropdown.optionData.map((option) => {
    const element = document.createElement("li");
    element.id = `${dropdown.select.id}-dropdown-option-${option.index}`;
    element.className = "filter-dropdown-option";
    element.dataset.filterOptionIndex = String(option.index);
    element.dataset.filterValue = option.value;
    element.setAttribute("role", "option");
    element.setAttribute("aria-selected", String(option.value === dropdown.select.value));
    element.textContent = option.label;
    return element;
  }));
  const selectedOption = dropdown.optionData.find(
    ({ value }) => value === dropdown.select.value,
  ) || dropdown.optionData[0];
  dropdown.value.textContent = selectedOption?.label || "All";
  dropdown.activeIndex = selectedOption?.index ?? -1;
  dropdown.panel.classList.toggle("is-long", dropdown.optionData.length > 8);
  setActiveFilterDropdownOption(dropdown, dropdown.activeIndex);
}

function positionFilterDropdownPanel(dropdown) {
  if (dropdown.panel.hidden) return;
  const triggerRect = dropdown.button.getBoundingClientRect();
  const panelHeight = Math.min(
    dropdown.panel.scrollHeight, 320, window.innerHeight * 0.4,
  );
  const placement = filterDropdownPlacement(
    triggerRect, panelHeight, window.innerHeight,
  );
  dropdown.panel.dataset.placement = placement.placement;
}

function closeFilterDropdown(dropdown, returnFocus = false) {
  if (dropdown.panel.hidden) return;
  dropdown.panel.hidden = true;
  dropdown.button.setAttribute("aria-expanded", "false");
  dropdown.button.removeAttribute("aria-activedescendant");
  if (returnFocus) dropdown.button.focus();
}

function closeAllFilterDropdowns(except = null) {
  filterDropdowns.forEach((dropdown) => {
    if (dropdown !== except) closeFilterDropdown(dropdown);
  });
}

function openFilterDropdown(dropdown) {
  if (dropdown.button.disabled || !dropdown.panel.hidden) return;
  closeAllFilterDropdowns(dropdown);
  dropdown.panel.hidden = false;
  dropdown.button.setAttribute("aria-expanded", "true");
  positionFilterDropdownPanel(dropdown);
  const selectedIndex = dropdown.optionData.findIndex(
    ({ value }) => value === dropdown.select.value,
  );
  setActiveFilterDropdownOption(dropdown, selectedIndex, true);
}

function selectFilterDropdownValue(dropdown, value) {
  if (!dropdown.optionData.some((option) => option.value === value)) return;
  dropdown.select.value = value;
  closeFilterDropdown(dropdown, true);
  dropdown.select.dispatchEvent(new Event("change", { bubbles: true }));
}

function createFilterDropdown(select) {
  const field = select.closest("[data-filter-dropdown]");
  const label = field.querySelector(".filter-label");
  const dropdownElement = document.createElement("div");
  const button = document.createElement("button");
  const value = document.createElement("span");
  const chevron = document.createElement("span");
  const panel = document.createElement("div");
  const options = document.createElement("ul");
  const buttonId = `${select.id}-dropdown-button`;
  const valueId = `${select.id}-dropdown-value`;
  const optionsId = `${select.id}-dropdown-options`;

  field.classList.add("is-enhanced");
  select.tabIndex = -1;
  select.setAttribute("aria-hidden", "true");
  dropdownElement.className = "filter-dropdown";
  button.id = buttonId;
  button.className = "filter-dropdown-button";
  button.type = "button";
  button.setAttribute("role", "combobox");
  button.setAttribute("aria-labelledby", `${label.id} ${valueId}`);
  const descriptionIds = select.getAttribute("aria-describedby");
  if (descriptionIds) button.setAttribute("aria-describedby", descriptionIds);
  button.setAttribute("aria-controls", optionsId);
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-haspopup", "listbox");
  button.disabled = select.disabled;
  value.id = valueId;
  chevron.className = "filter-dropdown-chevron";
  chevron.setAttribute("aria-hidden", "true");
  panel.className = "filter-dropdown-panel";
  panel.hidden = true;
  options.id = optionsId;
  options.className = "filter-dropdown-options";
  options.setAttribute("role", "listbox");
  options.setAttribute("aria-labelledby", label.id);
  button.append(value, chevron);
  panel.append(options);
  dropdownElement.append(button, panel);
  field.append(dropdownElement);

  const dropdown = {
    select, field, root: dropdownElement, button, value, panel, options,
    optionData: [], activeIndex: -1,
  };
  button.addEventListener("click", () => {
    if (panel.hidden) openFilterDropdown(dropdown);
    else closeFilterDropdown(dropdown, true);
  });
  button.addEventListener("keydown", (event) => {
    if (["ArrowDown", "ArrowUp"].includes(event.key)) {
      event.preventDefault();
      if (panel.hidden) openFilterDropdown(dropdown);
      moveActiveFilterDropdownOption(dropdown, event.key === "ArrowDown" ? 1 : -1);
    } else if (["Enter", " "].includes(event.key)) {
      event.preventDefault();
      if (panel.hidden) {
        openFilterDropdown(dropdown);
      } else {
        const option = dropdown.optionData[dropdown.activeIndex];
        if (option && visibleFilterDropdownOptionIndices(dropdown).includes(
          dropdown.activeIndex,
        )) {
          selectFilterDropdownValue(dropdown, option.value);
        }
      }
    } else if (event.key === "Escape") {
      event.preventDefault();
      closeFilterDropdown(dropdown, true);
    }
  });
  options.addEventListener("mousemove", (event) => {
    const option = event.target.closest("[data-filter-option-index]");
    if (option && !option.hidden) {
      setActiveFilterDropdownOption(
        dropdown, Number(option.dataset.filterOptionIndex),
      );
    }
  });
  options.addEventListener("click", (event) => {
    const option = event.target.closest("[data-filter-value]");
    if (option && !option.hidden) {
      selectFilterDropdownValue(dropdown, option.dataset.filterValue);
    }
  });
  select.addEventListener("change", () => syncFilterDropdown(dropdown));
  syncFilterDropdown(dropdown);
  return dropdown;
}

function syncFilterDropdownForSelect(select) {
  const dropdown = filterDropdownBySelect.get(select);
  if (dropdown) syncFilterDropdown(dropdown);
}

function updateInstitutionDimensionFilters(countryPapers, institutionTypePapers) {
  const countryCounts = dimensionPaperCounts(
    countryPapers,
    (paper) => countriesForRecord(paper),
  );
  replaceCountedFilterOptions(
    countryFilter,
    "All",
    sortedDimensionCounts(countryCounts),
    (value) => value,
    false,
  );
  syncFilterDropdownForSelect(countryFilter);

  const typeCounts = dimensionPaperCounts(
    institutionTypePapers,
    (paper) => institutionTypesForRecord(paper),
  );
  replaceCountedFilterOptions(
    institutionTypeFilter,
    "All",
    sortedInstitutionTypeCounts(typeCounts),
    institutionTypeLabel,
    false,
  );
  syncFilterDropdownForSelect(institutionTypeFilter);
}

function deriveFilteredRecordSets(
  mapRecords,
  publicPaperRecords,
  matchesInstitutionRecord,
  matchesPublicPaper = matchesInstitutionRecord,
  identityForRecord = paperIdentity,
  aggregateRecords = aggregateUniquePapers,
) {
  const filteredRecords = mapRecords.filter(matchesInstitutionRecord);
  const papersByIdentity = new Map();

  // Paper-level records preserve the public preview's standalone-paper coverage and
  // are the preferred display record when a matching map record references them.
  publicPaperRecords.forEach((paper) => {
    const identity = identityForRecord(paper);
    if (!papersByIdentity.has(identity)) {
      papersByIdentity.set(identity, paper);
    }
  });

  const matchingPaperIdentities = new Set(
    filteredRecords.map(identityForRecord),
  );
  publicPaperRecords.forEach((paper) => {
    if (matchesPublicPaper(paper)) {
      matchingPaperIdentities.add(identityForRecord(paper));
    }
  });

  const missingPaperIdentities = new Set(
    [...matchingPaperIdentities].filter((identity) => !papersByIdentity.has(identity)),
  );
  const fallbackPapersByIdentity = missingPaperIdentities.size
    ? new Map(
      aggregateRecords(
        filteredRecords.filter((record) => missingPaperIdentities.has(identityForRecord(record))),
      ).map((paper) => [identityForRecord(paper), paper]),
    )
    : new Map();
  const filteredPapers = [...matchingPaperIdentities]
    .map((identity) => papersByIdentity.get(identity) || fallbackPapersByIdentity.get(identity))
    .filter(Boolean);

  return { filteredRecords, filteredPapers, matchingPaperIdentities };
}

function normalizedSetSize(values) {
  return new Set(
    values
      .map((value) => String(value || "").trim().toLowerCase())
      .filter(Boolean),
  ).size;
}

function hasPreprintMetadata(record) {
  return hasArxivVersion(record) || hasPreprintSignal(record) || [
    "publication_type",
    "source_type",
    "venue_type",
  ].some((field) => Object.hasOwn(record, field));
}

function extractArxivId(value) {
  let text = String(value || "").trim();
  if (!text) {
    return "";
  }
  try {
    text = decodeURIComponent(text);
  } catch {
    // Keep the original text when it is not valid percent-encoding.
  }

  const arxivDoi = text.match(
    /(?:https?:\/\/(?:dx\.)?doi\.org\/)?10\.48550\/arxiv\.([a-z-]+(?:\.[a-z]{2})?\/\d{7}(?:v\d+)?|\d{4}\.\d{4,5}(?:v\d+)?)/i,
  );
  if (arxivDoi) {
    return arxivDoi[1];
  }

  const arxivUrl = text.match(
    /arxiv\.org\/(?:abs|pdf)\/([a-z-]+(?:\.[a-z]{2})?\/\d{7}(?:v\d+)?|\d{4}\.\d{4,5}(?:v\d+)?)(?:\.pdf)?(?:[?#]|$)/i,
  );
  if (arxivUrl) {
    return arxivUrl[1];
  }

  const directId = text
    .replace(/^arxiv:\s*/i, "")
    .replace(/\.pdf$/i, "")
    .trim();
  return (
    /^(?:[a-z-]+(?:\.[a-z]{2})?\/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?$/i.test(directId)
      ? directId
      : ""
  );
}

function recordArxivId(record) {
  const candidates = [
    record.arxiv_id,
    record.arxiv_url,
  ];
  for (const candidate of candidates) {
    const arxivId = extractArxivId(candidate);
    if (arxivId) {
      return arxivId;
    }
  }
  return "";
}

function recordArxivUrl(record) {
  const arxivId = recordArxivId(record);
  return arxivId ? `https://arxiv.org/abs/${arxivId}` : "";
}

function hasArxivVersion(record) {
  return Boolean(recordArxivId(record));
}

function hasPreprintSignal(record) {
  const text = [
    record.publication_type,
    record.source_type,
    record.venue_type,
    getRecordVenue(record),
  ].join(" ").toLocaleLowerCase();
  return (
    booleanValue(record.has_arxiv_version) ||
    booleanValue(record.is_arxiv_preprint) ||
    /\b(?:arxiv|preprint|pre-print)\b/.test(text)
  );
}

function hasPublishedVenue(record) {
  const venue = getRecordVenue(record);
  const normalizedVenue = venue
    .normalize("NFKC")
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
  if (!normalizedVenue) {
    return false;
  }
  const missingVenueValues = new Set([
    "unknown",
    "unknown venue",
    "unknown source",
    "unknown venue source",
    "arxiv",
    "preprint",
    "pre print",
    "openalex",
    "none",
    "null",
    "nan",
    "n a",
    "na",
  ]);
  return (
    !missingVenueValues.has(normalizedVenue) &&
    !/\b(?:arxiv|preprint|pre print)\b/.test(normalizedVenue)
  );
}

function isPreprintOnlyRecord(record) {
  return (
    (hasArxivVersion(record) || hasPreprintSignal(record)) &&
    !hasPublishedVenue(record)
  );
}

function updateDatasetStatistics(datasetRecords, datasetPaperRecords = []) {
  datasetRecordCount.textContent = datasetRecords.length;
  // The filtered-paper pipeline is already keyed by paper identity; use its
  // length directly rather than cloning or scanning it again for this metric.
  datasetPaperCount.textContent = datasetPaperRecords.length;
  datasetInstitutionCount.textContent = normalizedSetSize(
    datasetRecords.map(institutionIdentity),
  );
  datasetCountryCount.textContent = normalizedSetSize(
    datasetRecords.map(recordCountry),
  );
}

function renderChartEmpty(container) {
  container.innerHTML = '<p class="chart-empty">No data</p>';
}

function activateChartFilter(filter, value, label = "") {
  if (filter === "task") {
    if (!selectContainsValue(taskFilter, value)) return;
    taskFilter.value = taskFilter.value === value ? "all" : value;
    syncFilterDropdownForSelect(taskFilter);
  } else if (filter === "institution") {
    if (!value) return;
    if (activeInstitutionFilter?.identity === value) {
      activeInstitutionFilter = null;
      displayedInstitutionFilter = null;
    } else {
      activeInstitutionFilter = { identity: value, label: label || value };
    }
  } else if (filter === "year") {
    const year = Number(value);
    if (!yearRangeBounds || !Number.isInteger(year)
      || year < yearRangeBounds.minimum || year > yearRangeBounds.maximum) return;
    const selection = currentYearSelection();
    const isActive = selection?.start === year && selection?.end === year;
    minYearFilter.value = String(isActive ? yearRangeBounds.minimum : year);
    maxYearFilter.value = String(isActive ? yearRangeBounds.maximum : year);
    yearHistoryStarted = false;
    syncYearRange();
  } else {
    return;
  }
  rememberFilterChange(filter === "task" ? "task" : filter);
  hideChartTooltip();
  requestUrlStateSync("push");
  renderRecords();
  const refreshedControl = [...headerStatistics.querySelectorAll("button[data-chart-filter]")]
    .find((control) => (
      control.dataset.chartFilter === filter && control.dataset.chartValue === value
    ));
  refreshedControl?.focus({ preventScroll: true });
}

function renderTaskChart(paperCoverageRecords) {
  const tasks = [
    ["detection", "Detection"],
    ["source_attribution", "Source Attribution"],
    ["detection_and_source_attribution", "Detection + Source Attribution"],
  ].map(([task, label]) => ({
    task,
    label,
    color: TASK_COLORS[task],
    count: paperCoverageRecords.filter((record) => record.task === task).length,
  }));
  // The chart receives a list deduplicated by paper identity, so Total cannot
  // double-count a paper even if category behavior changes in the future.
  const total = paperCoverageRecords.length;
  const segments = tasks
    .filter((task) => task.count)
    .map((task) => (
      `<span class="task-chart-segment" style="width:${(task.count / total) * 100}%;background:${task.color}" title="${escapeHtml(task.label)}: ${task.count} unique paper${task.count === 1 ? "" : "s"}"></span>`
    ))
    .join("");
  const items = tasks
    .map((task) => (
      `<button type="button" class="task-chart-item" data-chart-filter="task" data-chart-value="${task.task}" data-chart-tooltip="${escapeHtml(task.label)} — ${task.count} unique paper${task.count === 1 ? "" : "s"}" aria-pressed="${taskFilter.value === task.task}" aria-label="${taskFilter.value === task.task ? "Clear" : "Filter by"} task ${escapeHtml(task.label)}; ${task.count} unique paper${task.count === 1 ? "" : "s"}"><i style="background:${task.color}"></i><span title="${escapeHtml(task.label)}">${escapeHtml(task.label)}</span><strong>${task.count}</strong></button>`
    ))
    .join("");
  taskChartContent.innerHTML = (
    `<div class="task-chart-bar" aria-label="${total} filtered unique paper${total === 1 ? "" : "s"}">${segments}</div><div class="task-chart-list" aria-label="Unique paper counts by task">${items}</div><div class="task-chart-total" aria-label="Total filtered unique papers"><span>Total Unique Papers</span><strong>${total}</strong></div>`
  );
}

function renderInstitutionChart(datasetRecords) {
  const institutions = new Map();
  datasetRecords.forEach((record) => {
    const institution = String(recordInstitution(record) || "").trim();
    if (!institution) {
      return;
    }
    const key = institutionIdentity(record);
    const entry = institutions.get(key) || { name: institution, papers: new Set() };
    entry.papers.add(paperIdentity(record));
    institutions.set(key, entry);
  });
  const topInstitutions = [...institutions.entries()]
    .map(([key, entry]) => ({ key, name: entry.name, count: entry.papers.size }))
    .sort((first, second) => (
      second.count - first.count || compareTextValues(first.name, second.name)
    ))
    .slice(0, 10);
  if (!topInstitutions.length) {
    renderChartEmpty(institutionChartContent);
    return;
  }
  const maximum = topInstitutions[0].count;
  institutionChartContent.innerHTML = (
    `<div class="institution-chart-list">${topInstitutions.map((entry) => (
      `<button type="button" class="institution-chart-row" data-chart-filter="institution" data-chart-value="${escapeHtml(entry.key)}" data-chart-label="${escapeHtml(entry.name)}" data-chart-tooltip="${escapeHtml(entry.name)} — ${entry.count} unique paper${entry.count === 1 ? "" : "s"}" aria-pressed="${activeInstitutionFilter?.identity === entry.key}" aria-label="${activeInstitutionFilter?.identity === entry.key ? "Clear" : "Filter by"} institution ${escapeHtml(entry.name)}; ${entry.count} unique paper${entry.count === 1 ? "" : "s"}"><span class="institution-chart-label"><span class="institution-chart-fill" style="width:${(entry.count / maximum) * 100}%"></span><span class="institution-chart-name">${escapeHtml(entry.name)}</span></span><span class="institution-chart-count">${entry.count}</span></button>`
    )).join("")}</div>`
  );
}

function renderYearChart(paperCoverageRecords) {
  const countsByYear = new Map();
  paperCoverageRecords.forEach((record) => {
    const year = publicationYear(record);
    if (year === null) {
      return;
    }
    countsByYear.set(year, (countsByYear.get(year) || 0) + 1);
  });
  const years = [...countsByYear.entries()].sort((first, second) => first[0] - second[0]);
  if (!years.length) {
    renderChartEmpty(yearChartContent);
    return;
  }
  const maximum = Math.max(...years.map(([, count]) => count));
  const yearSelection = currentYearSelection();
  yearChartContent.innerHTML = (
    `<div class="year-chart-bars">${years.map(([year, count]) => (
      `<button type="button" class="year-chart-item" data-chart-filter="year" data-chart-value="${year}" data-chart-tooltip="${year} — ${count} unique paper${count === 1 ? "" : "s"}" aria-pressed="${yearSelection?.start === year && yearSelection?.end === year}" aria-label="${yearSelection?.start === year && yearSelection?.end === year ? "Clear" : "Filter by"} publication year ${year}; ${count} unique paper${count === 1 ? "" : "s"}"><span class="year-chart-count">${count}</span><span class="year-chart-bar-slot"><span class="year-chart-bar" style="height:${(count / maximum) * 100}%"></span></span><span class="year-chart-label">${String(year).slice(-2)}</span></button>`
    )).join("")}</div>`
  );
}

function renderHeaderStatistics(datasetRecords, datasetPaperRecords = []) {
  const paperCoverageRecords = paperListRecordsForDisplay(datasetPaperRecords);
  renderTaskChart(paperCoverageRecords);
  renderInstitutionChart(datasetRecords);
  renderYearChart(paperCoverageRecords);
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
  return "unresolved";
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

function preliminaryAffiliationBadge(record) {
  return record?.affiliation_review_state === "unreviewed"
    ? '<span class="popup-badge confidence-unresolved">Preliminary affiliations</span>'
    : "";
}

function booleanValue(value) {
  if (typeof value === "boolean") {
    return value;
  }
  return ["1", "true", "yes", "y"].includes(String(value || "").toLowerCase());
}

function safeHttpUrl(value) {
  const text = String(value || "").trim();
  if (!text) {
    return "";
  }
  try {
    const url = new URL(text);
    return ["http:", "https:"].includes(url.protocol) && url.hostname
      ? url.href
      : "";
  } catch {
    return "";
  }
}

function externalLink(url, label) {
  const safeUrl = safeHttpUrl(url);
  return safeUrl
    ? `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer" aria-label="${escapeHtml(label)} (opens in a new tab)">${escapeHtml(label)}</a>`
    : "";
}

function normalizedDoi(value) {
  const doi = String(value || "")
    .trim()
    .replace(/^doi:\s*/i, "")
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")
    .trim();
  return /^10\.\d{4,9}\/\S+$/i.test(doi) ? doi : "";
}

function paperExternalLinks(record) {
  const arxivId = recordArxivId(record);
  const safeArxivUrl = arxivId
    ? safeHttpUrl(`https://arxiv.org/abs/${arxivId}`)
    : "";
  const versionLinks = PaperLinkHelpers.paperVersionLinks(record, safeArxivUrl)
    .map((link) => ({
      ...link,
      label: link.label === "Preprint" && safeArxivUrl ? "arXiv" : link.label,
    }));
  const resourceLinks = [
    { label: "Project", url: record.project_url || record.project_page_url },
    { label: "Code", url: record.code_url || record.repository_url },
    { label: "Dataset", url: record.dataset_url },
  ];
  return PaperLinkHelpers.deduplicatePaperLinks([...versionLinks, ...resourceLinks])
    .map((link) => externalLink(link.url, link.label))
    .filter(Boolean);
}

function escapeCsvValue(value) {
  const text = String(value ?? "");
  return /[",\r\n]/.test(text)
    ? `"${text.replaceAll('"', '""')}"`
    : text;
}

function buildCsv(exportRecords, columns) {
  const header = columns.map(([name]) => escapeCsvValue(name)).join(",");
  const rows = exportRecords.map((record) => columns
    .map(([, valueForRecord]) => escapeCsvValue(valueForRecord(record)))
    .join(","));
  return [header, ...rows].join("\r\n");
}

function exportFilename() {
  const date = new Date().toISOString().slice(0, 10);
  const viewLabel = resultsView === "papers" ? "unique-papers" : "institution-records";
  return `synthetic-image-research-map-${datasetName}-${viewLabel}-${date}.csv`;
}

function downloadFilteredCsv() {
  if (!currentDisplayedResults.length) {
    return;
  }

  const columns = resultsView === "papers"
    ? PAPER_CSV_COLUMNS
    : INSTITUTION_CSV_COLUMNS;
  const csv = buildCsv(currentDisplayedResults, columns);
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

async function writeViewUrlToClipboard(url, writeText = null) {
  const clipboardWriter = writeText || navigator.clipboard?.writeText?.bind(navigator.clipboard);
  if (clipboardWriter) {
    await clipboardWriter(url);
    return;
  }
  const fallback = document.createElement("textarea");
  fallback.value = url;
  fallback.setAttribute("readonly", "");
  fallback.className = "visually-hidden";
  document.body.append(fallback);
  fallback.select();
  const copied = document.execCommand?.("copy");
  fallback.remove();
  if (!copied) throw new Error("Clipboard access is unavailable.");
}

function showCopyLinkFeedback(message, copied = false) {
  copyViewLinkStatus.textContent = message;
  copyViewLinkButton.classList.toggle("is-copied", copied);
  copyViewLinkButton.textContent = copied ? "Copied" : "Copy link";
  window.clearTimeout(copyLinkFeedbackTimer);
  copyLinkFeedbackTimer = window.setTimeout(() => {
    copyViewLinkButton.classList.remove("is-copied");
    copyViewLinkButton.textContent = "Copy link";
  }, 1800);
}

async function copyCanonicalViewUrl() {
  const url = canonicalViewUrl();
  try {
    await writeViewUrlToClipboard(url);
    showCopyLinkFeedback("View link copied to clipboard.", true);
  } catch (_error) {
    showCopyLinkFeedback("Unable to copy the view link.");
  }
  return url;
}

function publicIssueText(value, fallback = "Not available") {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text ? text.replaceAll("`", "'") : fallback;
}

function publicIssueList(values, limit = 8) {
  const unique = [...new Set((values || [])
    .map((value) => publicIssueText(value, ""))
    .filter(Boolean))];
  if (!unique.length) return "Not available";
  const visible = unique.slice(0, limit);
  return `${visible.join("; ")}${unique.length > limit ? `; +${unique.length - limit} more` : ""}`;
}

function paperIssueReportUrl(context = {}) {
  const title = publicIssueText(context.title, "Unknown title");
  const params = new URLSearchParams({
    title: `Paper metadata issue: ${title}`.slice(0, 180),
    body: [
      "### Problem type",
      "- [ ] Incorrect affiliation",
      "- [ ] Incorrect location",
      "- [ ] Incorrect publication metadata",
      "- [ ] Duplicate record",
      "- [ ] Missing information",
      "- [ ] Other",
      "",
      "### Paper",
      `- Stable ID: \`${publicIssueText(context.paperId)}\``,
      `- Title: ${title}`,
      `- Paper deep link: ${publicIssueText(context.deepLink)}`,
      "",
      "### Current public metadata",
      `- Publication type: ${publicIssueText(context.publicationType)}`,
      `- Publication venue: ${publicIssueText(context.venue)}`,
      `- Publication year: ${publicIssueText(context.year)}`,
      `- Research type: ${publicIssueList(context.researchTypes)}`,
      `- Task: ${publicIssueText(context.task)}`,
      `- Institutions: ${publicIssueList(context.institutions)}`,
      `- Locations: ${publicIssueList(context.locations)}`,
      "",
      "### What should be corrected?",
      "Please describe the expected metadata and, if possible, provide a source.",
    ].join("\n"),
  });
  return `${PAPER_ISSUE_URL}?${params.toString()}`;
}

function paperIssueContext(record, relatedEntries, paperId, deepLink) {
  const sourceRecord = record || {};
  const publication = paperDetailsPublication(sourceRecord);
  const affiliations = [
    ...(Array.isArray(sourceRecord.affiliations) ? sourceRecord.affiliations : []),
    ...(Array.isArray(sourceRecord.author_institution_affiliations)
      ? sourceRecord.author_institution_affiliations : []),
  ];
  const relatedRecords = (relatedEntries || [])
    .map(({ record: relatedRecord }) => relatedRecord)
    .filter(Boolean);
  const institutions = [
    ...(sourceRecord.aggregated_institutions || []),
    ...affiliations.map((affiliation) => (
      typeof affiliation === "string" ? affiliation
        : affiliation?.name || affiliation?.institution || affiliation?.institution_name
    )),
    ...relatedRecords.map(recordInstitution),
  ];
  const locations = [
    ...(sourceRecord.aggregated_locations || []).map((location) => (
      typeof location === "string" ? location : location?.location_display
    )),
    ...affiliations.map((affiliation) => {
      if (!affiliation || typeof affiliation === "string") return "";
      return affiliation.location_display
        || [affiliation.region, affiliation.country].filter(Boolean).join(", ");
    }),
    ...relatedRecords.map(recordLocation),
  ];
  return {
    paperId,
    title: recordTitle(sourceRecord),
    deepLink,
    publicationType: publication.typeLabel,
    venue: publication.venue,
    year: publicationYear(sourceRecord),
    researchTypes: record
      ? getPaperCategories(sourceRecord).map(getEntryTypeLabel) : [],
    task: record ? formatPublicTask(sourceRecord.task) : "",
    institutions,
    locations,
  };
}

function appendCopyPaperLinkAction(record = null, relatedEntries = []) {
  const reportPaperIdentity = requestedPaperIdentity
    || (record ? paperIdentity(record) : "");
  if (!reportPaperIdentity) return;
  const container = document.createElement("div");
  const button = document.createElement("button");
  const reportLink = document.createElement("a");
  const status = document.createElement("span");
  const deepLink = canonicalViewUrl({
    ...currentViewState(),
    paper: reportPaperIdentity,
  });
  container.className = "paper-details-share-actions";
  button.type = "button";
  button.className = "copy-paper-link-button";
  button.dataset.copyPaperLink = "";
  button.textContent = "Copy paper link";
  reportLink.className = "report-paper-issue-link";
  reportLink.href = paperIssueReportUrl(paperIssueContext(
    record, relatedEntries, reportPaperIdentity, deepLink,
  ));
  reportLink.target = "_blank";
  reportLink.rel = "noopener noreferrer";
  reportLink.textContent = "Report issue";
  reportLink.setAttribute(
    "aria-label", "Report a metadata issue for this paper (opens in a new tab)",
  );
  status.className = "visually-hidden";
  status.dataset.copyPaperLinkStatus = "";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  if (requestedPaperIdentity) container.append(button, reportLink, status);
  else container.append(reportLink);
  paperDetailsContent.append(container);
}

function showCopyPaperLinkFeedback(message, copied = false) {
  const button = paperDetailsContent.querySelector("[data-copy-paper-link]");
  const status = paperDetailsContent.querySelector("[data-copy-paper-link-status]");
  if (!button || !status) return;
  status.textContent = message;
  button.classList.toggle("is-copied", copied);
  button.textContent = copied ? "Copied" : "Copy paper link";
  window.clearTimeout(copyPaperLinkFeedbackTimer);
  copyPaperLinkFeedbackTimer = window.setTimeout(() => {
    const currentButton = paperDetailsContent.querySelector("[data-copy-paper-link]");
    currentButton?.classList.remove("is-copied");
    if (currentButton) currentButton.textContent = "Copy paper link";
  }, 1800);
}

async function copySelectedPaperUrl() {
  if (!requestedPaperIdentity) return "";
  const url = canonicalViewUrl({
    ...currentViewState(),
    paper: requestedPaperIdentity,
  });
  try {
    await writeViewUrlToClipboard(url);
    showCopyPaperLinkFeedback("Paper link copied to clipboard.", true);
  } catch (_error) {
    showCopyPaperLinkFeedback("Unable to copy the paper link.");
  }
  return url;
}

function formatResolutionValue(value) {
  return formatTask(value || "unresolved");
}

function paperDetailsPublication(record) {
  return PaperDetailsHelpers.publicationMetadata(
    record,
    venueDisplayLabel(record),
    null,
  );
}

function paperDetailsPublicationHtml(record) {
  const metadata = PaperDetailsHelpers.publicationMetadata(
    record,
    venueDisplayLabel(record),
    record.publication_year ?? record.year,
  );
  const publication = [
    metadata.typeLabel
      ? `<span class="paper-details-publication-type"><span class="visually-hidden">Publication type: </span>${escapeHtml(metadata.typeLabel)}</span>`
      : "",
    metadata.typeLabel && metadata.venue
      ? '<span class="paper-details-metadata-separator paper-details-type-venue-separator" aria-hidden="true">|</span>'
      : "",
    metadata.venue
      ? `<span class="paper-details-publication-venue"><span class="visually-hidden">Publication venue: </span>${escapeHtml(metadata.venue)}</span>`
      : "",
    metadata.year && (metadata.typeLabel || metadata.venue)
      ? '<span class="paper-details-metadata-separator" aria-hidden="true">·</span>'
      : "",
    metadata.year
      ? `<span class="paper-details-publication-year"><span class="visually-hidden">Year: </span>${escapeHtml(metadata.year)}</span>`
      : "",
  ].filter(Boolean).join(" ");
  return publication
    ? `<p class="paper-details-venue-row">${publication}</p>`
    : "";
}

function paperDetailsHtml(record, relatedEntries) {
  const normalizedRecord = normalizePaperDetailsRecord(record, {
    relatedRecords: relatedEntries.map(({ record: relatedRecord }) => relatedRecord),
  });
  const orderedAuthors = recordAuthors(normalizedRecord);
  const affiliations = normalizedRecord.affiliations;
  const currentAffiliation = affiliations.find((affiliation) => affiliation.isCurrent);
  const authors = orderedAuthors.length
    ? renderPaperAuthors(
        normalizedRecord,
        currentAffiliation?.number ?? null,
        8,
        "paper-details-authors-overflow",
      )
    : "Unknown";
  const publicationMetadataBlock = paperDetailsPublicationHtml(record);
  const entryTypeBadge = getPaperCategories(record)
    .map((category) => `<span class="popup-badge entry-type-badge">${escapeHtml(getEntryTypeLabel(category))}</span>`)
    .join("");
  const detailLinks = paperExternalLinks(record);
  const linksBlock = detailLinks.length
    ? `<nav class="paper-details-links" aria-label="Paper links">${detailLinks.join("")}</nav>`
    : "";
  const abstract = String(record.abstract || "").trim();
  const abstractSource = String(record.abstract_source || "").trim();
  const abstractBlock = `
    <section class="paper-text-section paper-abstract-section">
      <h4 class="paper-details-section-heading">Abstract</h4>
      <p class="paper-abstract${abstract ? "" : " is-unavailable"}">${escapeHtml(abstract || "No abstract available.")}</p>
      ${abstract && abstractSource ? `<p class="paper-text-source">Source: ${escapeHtml(abstractSource)}</p>` : ""}
    </section>
  `;
  const affiliationsBlock = affiliations.length
    ? `<section class="paper-details-affiliation-section" aria-labelledby="paper-affiliations-heading"><h4 id="paper-affiliations-heading" class="paper-details-section-heading">Affiliations</h4><ol class="paper-details-affiliations">${affiliations.map((affiliation) => `<li${affiliation.isCurrent ? ' class="is-current is-hover-institution"' : ""}><div class="affiliation-heading"><span class="affiliation-institution">${institutionFilterButtonHtml(affiliation)}</span><span class="affiliation-type"> · ${escapeHtml(institutionTypeLabel(affiliation.institutionType))}</span>${affiliation.location ? `<span class="affiliation-location"> · ${escapeHtml(affiliation.location)}</span>` : ""}</div>${affiliation.authors.length ? `<div class="affiliation-authors">${affiliation.authors.map(escapeHtml).join("; ")}</div>` : ""}</li>`).join("")}</ol></section>`
    : "";

  return `
    <h3 class="popup-title paper-details-title">${paperTitleHtml(record)}</h3>
    <div class="popup-badges">
      <span class="popup-badge popup-task task-${escapeHtml(MarkerSizeHelpers.normalizeTaskLabel(record.task))}">${escapeHtml(formatPublicTask(record.task))}</span>
      ${entryTypeBadge}
    </div>
    ${publicationMetadataBlock}
    <section class="paper-details-group paper-details-authors" aria-labelledby="paper-authors-heading">
      <h4 id="paper-authors-heading" class="paper-details-section-heading">Authors</h4>
      <p>${authors}</p>
    </section>
    ${affiliationsBlock}
    ${linksBlock}
    ${abstractBlock}
  `;
}

function resultBadges(record) {
  const canonicalRecord = canonicalPaperRecord(record);
  const taskClass = MarkerSizeHelpers.normalizeTaskLabel(canonicalRecord.task);
  const entryTypes = getPaperCategories(canonicalRecord);
  return `
    <div class="popup-badges result-badges" aria-label="Paper categories">
      <span class="popup-badge popup-task task-${escapeHtml(taskClass)}">${escapeHtml(formatPublicTask(canonicalRecord.task))}</span>
      ${entryTypes.map((category) => `<span class="popup-badge entry-type-badge">${escapeHtml(getEntryTypeLabel(category))}</span>`).join("")}
    </div>
  `;
}

function resultVenueYear(record) {
  const { typeLabel, venue: rawVenue } = paperDetailsPublication(record);
  const venue = /^unknown publication venue$/i.test(rawVenue) ? "" : rawVenue;
  const year = publicationYear(record);
  const publication = [typeLabel, venue].filter(Boolean).join(" ");
  if (!publication && year === null) return "";
  return `
    <p class="result-venue-year">
      ${publication ? `<span><span class="visually-hidden">Publication: </span><span class="result-publication-type">${escapeHtml(typeLabel)}</span>${venue ? ` ${escapeHtml(venue)}` : ""}</span>` : ""}
      ${year !== null ? `<span><span class="visually-hidden">Year: </span>${escapeHtml(year)}</span>` : ""}
    </p>
  `;
}

function resultLinks(record) {
  const links = paperExternalLinks(record).join("");
  return links
    ? `<nav class="paper-details-links result-links" aria-label="Paper links">${links}</nav>`
    : "";
}

function resultAuthors(authors, label, regionId, visibleLimit = 6) {
  const authorsHtml = PaperDetailsHelpers.renderPaperAuthors(
    { authors },
    escapeHtml,
    null,
    visibleLimit,
    `${regionId}-overflow`,
  ) || "Unknown";
  return `
    <section class="result-entity-section result-authors">
      <h4>${escapeHtml(label)}</h4>
      <div class="result-authors-content" id="${regionId}" aria-label="${escapeHtml(label)}">
        <p>${authorsHtml}</p>
      </div>
    </section>
  `;
}

function institutionResultContent(record, relatedEntries = [{ record }], cardId = "institution-result") {
  const normalizedRecord = normalizePaperDetailsRecord(record, {
    relatedRecords: relatedEntries.map(({ record: relatedRecord }) => relatedRecord),
  });
  const institution = normalizedRecord.affiliations.find(
    (affiliation) => affiliation.isCurrent,
  ) || normalizedRecord.affiliations.find(
    (affiliation) => institutionIdentity({
      institution: affiliation.institution,
      institution_id: affiliation.institutionId,
    }) === institutionIdentity(record),
  );
  const institutionName = institution?.institution || recordInstitution(record);
  const location = institution?.location || recordLocation(record);
  const institutionType = institution?.institutionType
    || normalizeInstitutionType(record.institution_type);
  const scopedAuthors = institution?.authors?.length
    ? institution.authors
    : recordInstitutionAuthors(record);
  const authors = scopedAuthors.length ? scopedAuthors : recordAuthors(normalizedRecord);
  const authorLabel = scopedAuthors.length
    ? "Authors at this institution"
    : "Paper authors";

  return `
    <article class="result-card result-card-institution" aria-labelledby="${cardId}">
      <p class="result-entity-kicker">Institution record</p>
      <h3 class="result-title" id="${cardId}">${paperTitleHtml(record)}</h3>
      <div class="result-card-adaptive">
        <section class="result-institution-primary" aria-label="Institution represented by this record">
          <h4 title="${escapeHtml(institutionName || "Unknown institution")}">${institutionFocusButtonHtml(institution || {
            institution: institutionName,
            institutionId: record.institution_id,
            canonicalName: record.canonical_institution_name,
          }, record) || escapeHtml(institutionName || "Unknown institution")}</h4>
          ${location ? `<p title="${escapeHtml(location)}">${escapeHtml(location)}</p>` : ""}
          ${institutionType !== "other" ? `<p>${escapeHtml(institutionTypeLabel(institutionType))}</p>` : ""}
        </section>
        ${resultAuthors(authors, authorLabel, `${cardId}-authors`, 4)}
      </div>
      <div class="result-secondary">
        ${resultVenueYear(record)}
        ${resultBadges(record)}
        ${resultLinks(record)}
      </div>
    </article>
  `;
}

function uniquePaperInstitutions(affiliations) {
  const seen = new Set();
  return affiliations.filter((affiliation) => {
    const identity = institutionIdentity({
      institution: affiliation.institution,
      institution_id: affiliation.institutionId,
    });
    if (seen.has(identity)) return false;
    seen.add(identity);
    return true;
  });
}

function resultInstitutions(affiliations, regionId, visibleLimit = 4) {
  const uniqueAffiliations = uniquePaperInstitutions(affiliations);
  if (!uniqueAffiliations.length) return "";
  const affiliationHtml = (affiliation) => `
    <li>
      <sup class="result-institution-number" aria-label="Institution ${escapeHtml(affiliation.number)}">${escapeHtml(affiliation.number)}</sup>
      ${institutionFocusButtonHtml(affiliation)}
      ${affiliation.location ? `<span class="result-institution-location">${escapeHtml(affiliation.location)}</span>` : ""}
    </li>
  `;
  const visible = uniqueAffiliations.slice(0, visibleLimit).map(affiliationHtml).join("");
  const overflow = uniqueAffiliations.slice(visibleLimit).map(affiliationHtml).join("");
  return `
    <section class="result-entity-section result-paper-institutions">
      <h4>Institutions <span class="result-section-count">(${uniqueAffiliations.length})</span></h4>
      <div class="result-institutions-content" id="${regionId}" aria-label="Paper institutions">
        <ul>${visible}</ul>
        ${overflow ? `<ul class="result-institutions-overflow" hidden>${overflow}</ul>` : ""}
      </div>
      ${overflow ? `<button type="button" class="result-institutions-toggle" aria-expanded="false" aria-controls="${regionId}">Show all institutions</button>` : ""}
    </section>
  `;
}

function paperResultContent(record, relatedEntries = [], cardId = "paper-result") {
  const normalizedRecord = normalizePaperDetailsRecord(record, {
    relatedRecords: relatedEntries.map(({ record: relatedRecord }) => relatedRecord),
  });
  return `
    <article class="result-card result-card-paper" aria-labelledby="${cardId}">
      <p class="result-entity-kicker">Unique paper</p>
      <h3 class="result-title" id="${cardId}">${paperTitleHtml(record)}</h3>
      <div class="result-card-adaptive">
        ${resultAuthors(normalizedRecord.authors, "Authors", `${cardId}-authors`, 4)}
        ${resultInstitutions(normalizedRecord.affiliations, `${cardId}-institutions`, 3)}
      </div>
      <div class="result-secondary">
        ${resultVenueYear(record)}
        ${resultBadges(record)}
        ${resultLinks(record)}
      </div>
    </article>
  `;
}

function setResultsLayoutPending(isPending, showSkeleton = false) {
  resultsList.setAttribute("aria-busy", String(isPending));
  resultsList.classList.toggle("is-updating", isPending && !showSkeleton);
  resultsLoading.hidden = !(isPending && showSkeleton);
}

function invalidateResultsRenderPipeline() {
  resultsRenderGeneration += 1;
  resultsMasonryFrames.forEach((frame) => cancelAnimationFrame(frame));
  resultsMasonryFrames.clear();
  if (resultsObserver) resultsObserver.disconnect();
  resultsObserver = null;
  document.querySelector(".results-list-staging")?.remove();
  resultsPipeline = null;
  pendingResultReveal = null;
  resultsKeywordFrame = null;
  return resultsRenderGeneration;
}

function requestResultsAnimationFrame(callback) {
  const frame = requestAnimationFrame(() => {
    resultsMasonryFrames.delete(frame);
    callback();
  });
  resultsMasonryFrames.add(frame);
  return frame;
}

function resultsColumnCount(list = resultsList) {
  if (mobileFiltersMedia.matches) return 1;
  const columns = getComputedStyle(list).gridTemplateColumns
    .split(" ")
    .filter(Boolean).length;
  return Math.max(columns, 1);
}

function resultsLayoutSignature(list = resultsList) {
  return `${Math.round(list.getBoundingClientRect().width)}:${resultsColumnCount(list)}`;
}

function measureMasonryItems(list, cards, generation) {
  if (generation !== resultsRenderGeneration) return false;
  if (mobileFiltersMedia.matches) {
    cards.forEach((card) => card.style.removeProperty("grid-row-end"));
    list.classList.remove("is-masonry-ready");
    return true;
  }

  const listStyles = getComputedStyle(list);
  const documentStyles = getComputedStyle(document.documentElement);
  const rowHeight = Number.parseFloat(
    documentStyles.getPropertyValue("--masonry-row"),
  );
  const tokenGap = Number.parseFloat(
    documentStyles.getPropertyValue("--masonry-gap"),
  );
  const computedGap = Number.parseFloat(listStyles.rowGap);
  const rowGap = Number.isFinite(computedGap) ? computedGap : tokenGap;
  if (!Number.isFinite(rowHeight) || !Number.isFinite(rowGap)) {
    return false;
  }

  cards.forEach((card) => {
    if (generation !== resultsRenderGeneration) return;
    const cardStyles = getComputedStyle(card);
    const borderHeight = Number.parseFloat(cardStyles.borderTopWidth)
      + Number.parseFloat(cardStyles.borderBottomWidth);
    const renderedCard = card.querySelector(".result-card");
    const renderedRect = renderedCard?.getBoundingClientRect();
    const renderedHeight = renderedRect?.height || 0;
    const contentHeight = renderedCard?.scrollHeight || 0;
    const finalChild = renderedCard?.lastElementChild;
    const finalChildBottom = finalChild?.getBoundingClientRect().bottom || 0;
    const cardPaddingBottom = Number.parseFloat(
      renderedCard ? getComputedStyle(renderedCard).paddingBottom : "0",
    );
    const descendantHeight = renderedRect
      ? finalChildBottom - renderedRect.top + cardPaddingBottom
      : 0;
    const cardHeight = Math.ceil(
      Math.max(
        card.scrollHeight,
        renderedHeight,
        contentHeight,
        descendantHeight,
      ) + borderHeight,
    );
    const span = Math.ceil((cardHeight + rowGap) / (rowHeight + rowGap));
    card.style.gridRowEnd = `span ${span}`;
  });
  if (generation !== resultsRenderGeneration) return false;
  list.classList.add("is-masonry-ready");
  return true;
}

function scheduleMasonryMeasurement(list, cards, generation, onComplete) {
  if (generation !== resultsRenderGeneration) return;
  requestResultsAnimationFrame(() => {
    if (generation !== resultsRenderGeneration) return;
    requestResultsAnimationFrame(() => {
      if (generation !== resultsRenderGeneration) return;
      if (!measureMasonryItems(list, cards, generation)) return;
      if (generation !== resultsRenderGeneration) return;
      cards.forEach((card) => card.classList.remove("is-masonry-pending"));
      onComplete?.();
    });
  });
}

function resultSentinelNeedsMoreCards() {
  const sentinel = document.querySelector("#results-sentinel");
  if (!sentinel) return false;
  return sentinel.getBoundingClientRect().top <= window.innerHeight * RESULTS_INITIAL_VIEWPORTS;
}

function addResultIndex(indexes, key, index) {
  if (!key) return;
  const values = indexes.get(key) || new Set();
  values.add(index);
  indexes.set(key, values);
}

function interactionResultIndexes(selection, pipeline = resultsPipeline) {
  const indexes = new Set();
  if (!selection || !pipeline) return indexes;
  const paperIdentities = selection.resultPaperIdentities?.length
    ? selection.resultPaperIdentities
    : [selection.identity];
  paperIdentities.forEach((identity) => {
    pipeline.resultIndexesByPaperIdentity.get(identity)?.forEach((index) => indexes.add(index));
  });
  if (selection.resultScope === "institution" && selection.institutionKey) {
    pipeline.resultIndexesByInstitutionKey.get(selection.institutionKey)
      ?.forEach((index) => indexes.add(index));
  }
  return indexes;
}

function renderedResultItem(index, generation = resultsRenderGeneration) {
  return resultsList.querySelector(
    `.result-item[data-result-generation="${generation}"][data-result-index="${index}"]`,
  );
}

function syncResultHighlights() {
  const selectedIndexes = interactionResultIndexes(interactionState.selected);
  const hoveredIndexes = interactionResultIndexes(interactionState.hovered);
  resultsList.querySelectorAll(
    `.result-item[data-result-generation="${resultsRenderGeneration}"]`,
  ).forEach((item) => {
    const index = Number(item.dataset.resultIndex);
    const isSelected = selectedIndexes.has(index);
    const isHovered = hoveredIndexes.has(index);
    item.classList.toggle("is-interaction-selected", isSelected);
    item.classList.toggle("is-interaction-hovered", isHovered);
    if (isSelected) item.setAttribute("aria-current", "true");
    else item.removeAttribute("aria-current");
  });
}

function selectionNeedsResultsReveal(selection = interactionState.selected) {
  const indexes = interactionResultIndexes(selection);
  return indexes.size > 0 && ![...indexes].some((index) => renderedResultItem(index));
}

function updateShowInResultsAction() {
  paperDetailsContent.querySelector("[data-show-selection-in-results]")?.remove();
  if (!interactionState.selected || !selectionNeedsResultsReveal()) return;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "show-in-results-button";
  button.dataset.showSelectionInResults = "";
  button.textContent = "Show in results";
  button.setAttribute("aria-label", "Show the selected paper or institution in results");
  paperDetailsContent.append(button);
}

function revealPendingResult() {
  if (!pendingResultReveal || pendingResultReveal.generation !== resultsRenderGeneration) {
    pendingResultReveal = null;
    return;
  }
  const item = renderedResultItem(pendingResultReveal.index);
  if (!item) return;
  pendingResultReveal = null;
  syncResultHighlights();
  updateShowInResultsAction();
  item.focus({ preventScroll: true });
  item.scrollIntoView({ block: "nearest", behavior: "auto" });
}

function continuePendingResultReveal() {
  if (!pendingResultReveal || !resultsPipeline || resultsPipeline.isPreparing) return;
  const { generation, index } = pendingResultReveal;
  if (generation !== resultsRenderGeneration || resultsPipeline.generation !== generation) {
    pendingResultReveal = null;
    return;
  }
  if (index < resultsPipeline.renderedCount) {
    revealPendingResult();
    return;
  }
  appendResultChunk(generation, index - resultsPipeline.renderedCount + 1);
}

function showSelectionInResults() {
  const indexes = [...interactionResultIndexes(interactionState.selected)].sort((a, b) => a - b);
  if (!indexes.length || !resultsPipeline) return;
  pendingResultReveal = { generation: resultsRenderGeneration, index: indexes[0] };
  continuePendingResultReveal();
}

function createResultItem(record, index, pipeline) {
  const item = document.createElement("li");
  item.className = `result-item result-item-${pipeline.view === "papers" ? "paper" : "institution"} is-masonry-pending`;
  item.dataset.resultIndex = String(index);
  item.dataset.resultGeneration = String(pipeline.generation);
  item.tabIndex = -1;
  const relatedEntries = pipeline.relatedEntriesByIdentity.get(paperIdentity(record)) || [];
  const cardId = `result-card-title-${pipeline.view}-${index}`;
  item.innerHTML = pipeline.view === "papers"
    ? paperResultContent(record, relatedEntries, cardId)
    : institutionResultContent(record, relatedEntries, cardId);
  const identity = paperIdentity(record);
  item.querySelectorAll("[data-focus-institution]").forEach((button) => {
    let markerEntry = visibleMarkerEntryByInstitutionKey.get(button.dataset.focusInstitution);
    if (!markerEntry?.records.some((candidate) => paperIdentity(candidate) === identity)) {
      // Paper cards name an institution, not a campus. Choose one of this
      // paper's visible sites instead of a different paper's default campus.
      markerEntry = visibleMarkerEntries.find((entry) => (
        institutionIdentity(entry.record) === button.dataset.focusInstitution
        && entry.records.some((candidate) => paperIdentity(candidate) === identity)
      ));
    }
    const hasVisiblePaperMarker = markerEntry?.records.some(
      (markerRecord) => paperIdentity(markerRecord) === identity,
    );
    if (hasVisiblePaperMarker) {
      button.dataset.focusInstitution = markerEntry.institutionKey;
    } else {
      button.disabled = true;
      button.setAttribute("aria-label", `${button.textContent} has no visible map marker`);
    }
  });
  return item;
}

function initialResultChunkSize(pipeline) {
  const columns = resultsColumnCount(resultsList);
  return Math.min(
    pipeline.displayedResults.length,
    Math.max(columns * 4, Math.ceil(
      (window.innerHeight * RESULTS_INITIAL_VIEWPORTS / pipeline.estimatedCardHeight) * columns,
    )),
  );
}

function nextResultChunkSize(pipeline) {
  const columns = resultsColumnCount(resultsList);
  return Math.max(
    columns * 2,
    Math.ceil((window.innerHeight / pipeline.estimatedCardHeight) * columns),
  );
}

function updateEstimatedCardHeight(pipeline, cards, generation) {
  if (generation !== resultsRenderGeneration || !cards.length) return;
  const total = cards.reduce((sum, card) => (
    sum + Math.max(card.getBoundingClientRect().height, card.scrollHeight)
  ), 0);
  const measuredAverage = total / cards.length;
  if (Number.isFinite(measuredAverage) && measuredAverage > 0) {
    pipeline.estimatedCardHeight = measuredAverage;
  }
}

function appendResultChunk(generation, requestedCount = null) {
  const pipeline = resultsPipeline;
  if (!pipeline || generation !== resultsRenderGeneration || pipeline.isAppending) return;
  if (pipeline.renderedCount >= pipeline.displayedResults.length) {
    resultsObserver?.disconnect();
    return;
  }
  pipeline.isAppending = true;
  const start = pipeline.renderedCount;
  const end = Math.min(
    pipeline.displayedResults.length,
    start + (requestedCount || nextResultChunkSize(pipeline)),
  );
  const fragment = document.createDocumentFragment();
  const newCards = pipeline.displayedResults
    .slice(start, end)
    .map((record, offset) => createResultItem(record, start + offset, pipeline));
  newCards.forEach((card) => fragment.append(card));
  if (generation !== resultsRenderGeneration) return;
  resultsList.append(fragment);
  syncResultHighlights();
  scheduleMasonryMeasurement(resultsList, newCards, generation, () => {
    if (generation !== resultsRenderGeneration || resultsPipeline !== pipeline) return;
    updateEstimatedCardHeight(pipeline, newCards, generation);
    pipeline.renderedCount = end;
    pipeline.isAppending = false;
    pipeline.layoutSignature = resultsLayoutSignature();
    updateShowInResultsAction();
    continuePendingResultReveal();
    if (end >= pipeline.displayedResults.length) {
      resultsObserver?.disconnect();
    } else if (resultSentinelNeedsMoreCards()) {
      appendResultChunk(generation);
    }
  });
}

function observeResultSentinel(generation) {
  if (generation !== resultsRenderGeneration || !resultsPipeline) return;
  if (resultsObserver) resultsObserver.disconnect();
  const sentinel = document.querySelector("#results-sentinel");
  if (!sentinel || typeof IntersectionObserver === "undefined") {
    appendResultChunk(generation);
    return;
  }
  resultsObserver = new IntersectionObserver((entries) => {
    if (generation !== resultsRenderGeneration || resultsPipeline?.generation !== generation) return;
    if (entries.some((entry) => entry.isIntersecting)) appendResultChunk(generation);
  }, { rootMargin: RESULTS_OBSERVER_MARGIN });
  if (generation !== resultsRenderGeneration) return;
  resultsObserver.observe(sentinel);
  if (resultSentinelNeedsMoreCards()) appendResultChunk(generation);
}

function prepareFirstResultViewport(generation) {
  const pipeline = resultsPipeline;
  if (!pipeline || generation !== resultsRenderGeneration) return;
  const stagingList = document.createElement("ol");
  stagingList.className = "results-list results-list-staging";
  stagingList.setAttribute("aria-hidden", "true");
  const firstEnd = initialResultChunkSize(pipeline);
  const firstCards = pipeline.displayedResults
    .slice(0, firstEnd)
    .map((record, index) => createResultItem(record, index, pipeline));
  firstCards.forEach((card) => stagingList.append(card));
  resultsList.after(stagingList);
  scheduleMasonryMeasurement(stagingList, firstCards, generation, () => {
    if (generation !== resultsRenderGeneration || resultsPipeline !== pipeline) return;
    updateEstimatedCardHeight(pipeline, firstCards, generation);
    const masonryReady = stagingList.classList.contains("is-masonry-ready");
    const preparedCards = [...stagingList.children];
    stagingList.remove();
    if (generation !== resultsRenderGeneration) return;
    resultsList.replaceChildren(...preparedCards);
    resultsList.classList.toggle("is-masonry-ready", masonryReady);
    resultsList.hidden = false;
    pipeline.renderedCount = firstEnd;
    pipeline.isPreparing = false;
    pipeline.layoutSignature = resultsLayoutSignature();
    syncResultHighlights();
    updateShowInResultsAction();
    continuePendingResultReveal();
    setResultsLayoutPending(false);
    observeResultSentinel(generation);
    requestResultsAnimationFrame(() => {
      if (generation !== resultsRenderGeneration || resultsPipeline !== pipeline) return;
      scheduleSearchTextCachePrewarm();
    });
  });
}

function scheduleResultsMasonryLayout(cards = null) {
  const pipeline = resultsPipeline;
  const generation = resultsRenderGeneration;
  if (!pipeline || pipeline.generation !== generation) return;
  const items = cards ? [...cards] : [...resultsList.querySelectorAll(".result-item")];
  if (!items.length) return;
  scheduleMasonryMeasurement(resultsList, items, generation, () => {
    if (generation !== resultsRenderGeneration || resultsPipeline !== pipeline) return;
    pipeline.layoutSignature = resultsLayoutSignature();
  });
}

function renderNoResultsState(resultNoun) {
  const descriptors = activeFilterChipDescriptors();
  const constraintCount = descriptors.length;
  resultsEmptyHeading.textContent = `No matching ${resultNoun}s`;
  resultsEmptySummary.textContent = constraintCount
    ? `${constraintCount} active filter/search constraint${constraintCount === 1 ? "" : "s"} ${constraintCount === 1 ? "is" : "are"} currently excluding all ${resultNoun}s.`
    : `No ${resultNoun}s are available in the current dataset view.`;
  const fragment = document.createDocumentFragment();
  descriptors.forEach(({ key, category, value }) => {
    const item = document.createElement("li");
    const remove = document.createElement("button");
    remove.type = "button";
    remove.dataset.emptyRemoveFilter = key;
    remove.textContent = `Remove ${category}: ${value}`;
    remove.setAttribute("aria-label", `Remove ${category} filter: ${value}`);
    item.append(remove);
    fragment.append(item);
  });
  resultsEmptyFilterActions.replaceChildren(fragment);
  undoLastFilterButton.hidden = !lastFilterChange;
  clearEmptyFiltersButton.hidden = constraintCount === 0;
}

function renderResults(visibleRecords, visiblePaperRecords = [], generation = null) {
  const activeGeneration = generation ?? invalidateResultsRenderPipeline();
  if (activeGeneration !== resultsRenderGeneration) return;
  const relatedEntriesByIdentity = new Map();
  visibleRecords.forEach((record) => {
    const identity = paperIdentity(record);
    const relatedEntries = relatedEntriesByIdentity.get(identity) || [];
    relatedEntries.push({ record });
    relatedEntriesByIdentity.set(identity, relatedEntries);
  });
  const displayedResults = resultsView === "papers"
    ? paperListRecordsForDisplay(visiblePaperRecords)
    : visibleRecords;
  currentDisplayedResults = displayedResults;
  pendingResultReveal = null;
  const resultIndexesByPaperIdentity = new Map();
  const resultIndexesByInstitutionKey = new Map();
  for (const [index, record] of displayedResults.entries()) {
    const identity = paperIdentity(record);
    addResultIndex(resultIndexesByPaperIdentity, identity, index);
    const institutionKeys = resultsView === "papers"
      ? new Set([
          ...recordInstitutionIdentities(record),
          ...(relatedEntriesByIdentity.get(identity) || [])
            .map(({ record: relatedRecord }) => markerInstitutionIdentity(relatedRecord)),
        ])
      : new Set([institutionIdentity(record), markerInstitutionIdentity(record)]);
    institutionKeys.forEach((key) => {
      addResultIndex(resultIndexesByInstitutionKey, key, index);
    });
  }
  const count = displayedResults.length;
  const resultNoun = resultsView === "papers" ? "unique paper" : "institution record";
  resultsCount.textContent = count
    ? `${count.toLocaleString("en-US")} ${resultNoun}${count === 1 ? "" : "s"}`
    : `No matching ${resultNoun}s`;
  exportCsvButton.disabled = count === 0;
  resultsEmpty.hidden = count !== 0;

  if (!count) {
    renderNoResultsState(resultNoun);
    resultsPipeline = null;
    resultsList.replaceChildren();
    resultsList.hidden = true;
    resultsList.classList.remove("is-masonry-ready");
    setResultsLayoutPending(false);
    return;
  }
  const hasCurrentCards = resultsList.querySelector(".result-item") !== null;
  resultsPipeline = {
    generation: activeGeneration,
    displayedResults,
    relatedEntriesByIdentity,
    resultIndexesByPaperIdentity,
    resultIndexesByInstitutionKey,
    view: resultsView,
    renderedCount: 0,
    estimatedCardHeight: 260,
    isAppending: false,
    isPreparing: true,
    layoutSignature: "",
  };
  setResultsLayoutPending(true, !hasCurrentCards);
  prepareFirstResultViewport(activeGeneration);
}

function selectResultsView(view) {
  if (!["institutions", "papers"].includes(view)) {
    return;
  }
  const generation = invalidateResultsRenderPipeline();
  requestUrlStateSync("push");
  setResultsViewState(view);
  closeActiveInstitutionTooltip();
  interactionState.hovered = null;
  interactionState.hoveredMarkerId = null;
  pendingResultReveal = null;
  renderRecordsForGeneration({ generation });
}

function baseMapStatusText(visibleRecords) {
  const recordLabel = datasetConfig.recordLabel;
  const interactionHint = supportsMarkerHover
    ? " Hover over a marker to view paper details; click to pin."
    : " Tap a marker to pin paper details.";
  return visibleRecords.length
    ? `Showing ${visibleRecords.length} ${recordLabel}${visibleRecords.length === 1 ? "" : "s"}.${interactionHint}`
    : "No records match the current filters.";
}

function resetPaperDetails() {
  window.clearTimeout(copyPaperLinkFeedbackTimer);
  paperDetails.classList.remove("has-content");
  paperDetailsContent.innerHTML =
    '<p class="paper-details-placeholder">Select or hover over a marker to view paper details.</p>';
  closePaperDetailsButton.disabled = true;
  closePaperDetailsButton.textContent = "×";
  closePaperDetailsButton.setAttribute("aria-label", "Close paper details");
  paperDetailsPinStatus.hidden = true;
  paperDetails.classList.remove("is-pinned");
}

function showPaperDetails(record, relatedEntries, source, { filteredOut = false } = {}) {
  paperDetailsContent.innerHTML = paperDetailsHtml(record, relatedEntries);
  paperDetails.classList.add("has-content");
  closePaperDetailsButton.disabled = false;
  const isPinned = source === "selected";
  paperDetails.classList.toggle("is-pinned", isPinned);
  paperDetailsPinStatus.hidden = !isPinned;
  closePaperDetailsButton.textContent = "×";
  closePaperDetailsButton.setAttribute(
    "aria-label",
    "Close paper details",
  );
  if (filteredOut) {
    const notice = document.createElement("p");
    notice.className = "paper-details-filter-notice";
    notice.setAttribute("role", "status");
    notice.textContent = "This linked paper does not match the current filters. Your filters were not changed.";
    paperDetailsContent.prepend(notice);
  }
  appendCopyPaperLinkAction(record, relatedEntries);
  paperDetails.scrollTop = 0;
  updateShowInResultsAction();
}

function showLinkedPaperUnavailable() {
  paperDetailsContent.innerHTML = `
    <section class="paper-details-link-unavailable" role="status">
      <h3>Linked paper unavailable</h3>
      <p>The paper identifier in this link was not found in the current dataset. Your filters were not changed.</p>
    </section>
  `;
  paperDetails.classList.add("has-content", "is-pinned");
  closePaperDetailsButton.disabled = false;
  closePaperDetailsButton.setAttribute("aria-label", "Close linked paper details");
  paperDetailsPinStatus.hidden = false;
  appendCopyPaperLinkAction();
  paperDetails.scrollTop = 0;
}

function restoreBaseMarkerStyles() {
  visibleMarkerEntries.forEach(({ marker, taskKey, paperCount }) => {
    marker.setStyle(markerStyle(taskKey, "base", paperCount));
  });
}

function clearPaperInteraction(updateStatus = true) {
  closeActiveInstitutionTooltip();
  interactionState.hovered = null;
  interactionState.selected = null;
  interactionState.hoveredMarkerId = null;
  interactionState.selectedMarkerId = null;
  interactionState.detailsSource = null;
  pendingResultReveal = null;
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  restoreBaseMarkerStyles();
  syncResultHighlights();
  resetPaperDetails();
  scheduleMapResize();
  if (updateStatus) {
    mapStatus.classList.toggle("paper-highlight-active", false);
    mapStatus.textContent = baseMapStatusText(currentFilteredRecords);
  }
}

function drawConnectionLines(relatedEntries, currentRecord, targetLayer) {
  targetLayer.clearLayers();
  const locations = uniqueMarkerLocations(relatedEntries);
  if (locations.length < 2) {
    return 0;
  }

  const hub = recordLatLng(currentRecord);
  const hubKey = coordinateKey(hub);
  const connectedLocations = locations.filter(
    (location) => coordinateKey(location) !== hubKey,
  );
  connectedLocations.forEach((location) => {
    L.polyline([hub, location], CONNECTION_LINE_STYLE).addTo(targetLayer);
  });
  return connectedLocations.length;
}

function relatedMarkerEntries(selection) {
  return visibleMarkerEntries
    .map((entry) => {
      const matchingRecord = entry.records.find(
        (candidate) => paperIdentity(candidate) === selection.identity,
      );
      return matchingRecord ? { ...entry, record: matchingRecord } : null;
    })
    .filter(Boolean);
}

function renderConnectionSelection(selection, mode) {
  const relatedEntries = selection ? relatedMarkerEntries(selection) : [];
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  if (!relatedEntries.length) {
    restoreBaseMarkerStyles();
    return { lineCount: 0, visibleCount: 0 };
  }

  let currentMarker = null;
  visibleMarkerEntries.forEach((entry) => {
    const {
      marker,
      record: markerRecord,
      records: markerRecords,
      taskKey,
      paperCount,
    } = entry;
    const isCurrent = entry.institutionKey === selection.institutionKey;
    const isRelated = markerRecords.some(
      (candidate) => paperIdentity(candidate) === selection.identity,
    );
    if (isCurrent) {
      currentMarker = marker;
    }
    marker.setStyle(markerStyle(
      taskKey,
      isCurrent ? "current" : isRelated ? "related" : "dimmed",
      paperCount,
    ));
  });

  const isHover = mode === "hover";
  const targetLayer = isHover ? hoverConnectionLayer : selectedConnectionLayer;
  const lineCount = drawConnectionLines(
    relatedEntries,
    selection.record,
    targetLayer,
  );
  relatedEntries.forEach(({ marker }) => marker.bringToFront());
  currentMarker?.bringToFront();
  return { lineCount, visibleCount: relatedEntries.length };
}

function setMarkerSelectionState(selection) {
  visibleMarkerEntries.forEach((entry) => {
    const isSelectedPaper = Boolean(selection && entry.records.some(
      (record) => paperIdentity(record) === selection.identity,
    ));
    const isOrigin = isSelectedPaper && entry.institutionKey === selection.institutionKey;
    const element = entry.marker.getElement?.();
    element?.classList.toggle("is-paper-pinned", isSelectedPaper);
    element?.classList.toggle("is-paper-selection-origin", isOrigin);
    element?.setAttribute("aria-pressed", String(isOrigin));
    element?.setAttribute(
      "aria-label",
      `${isOrigin ? "Clear" : "Select"} paper details for ${recordInstitution(entry.record) || "institution"}`,
    );
  });
}

function renderPaperSelection(selection, source) {
  if (!selection) {
    resetPaperDetails();
    return;
  }
  const visibleRelatedEntries = relatedMarkerEntries(selection);
  const detailEntries = visibleRelatedEntries.length
    ? visibleRelatedEntries
    : (mapRecordsByPaperIdentity.get(selection.identity) || [])
      .map((record) => ({ record }));
  showPaperDetails(selection.record, detailEntries, source, {
    filteredOut: selection.filteredOut === true,
  });
}

function showPaperInteraction(detailSelection, connectionSelection) {
  const isHoverConnection = connectionSelection === interactionState.hovered;
  const { lineCount, visibleCount } = renderConnectionSelection(
    connectionSelection,
    isHoverConnection ? "hover" : "pinned",
  );
  renderPaperSelection(detailSelection, interactionState.detailsSource);
  mapStatus.classList.toggle("error", false);
  mapStatus.classList.toggle("paper-highlight-active", true);
  if (detailSelection?.filteredOut) {
    mapStatus.textContent = "The linked paper does not match the current filters. Filters were not changed.";
    return;
  }
  const connectionText = lineCount ? " · Connections shown." : ".";
  mapStatus.textContent =
    `Showing ${visibleCount} visible institution record${visibleCount === 1 ? "" : "s"}${connectionText}`;
}

function renderActiveSelection() {
  const detailSelection = interactionState.selected || interactionState.hovered;
  const connectionSelection = interactionState.hovered || interactionState.selected;
  interactionState.detailsSource = interactionState.selected
    ? "selected"
    : interactionState.hovered ? "hover" : null;
  setMarkerSelectionState(interactionState.selected);
  syncResultHighlights();
  if (detailSelection) {
    showPaperInteraction(detailSelection, connectionSelection);
    return;
  }

  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  restoreBaseMarkerStyles();
  if (requestedPaperIdentity
      && !canonicalPaperRecordsByIdentity.has(requestedPaperIdentity)) {
    showLinkedPaperUnavailable();
    mapStatus.classList.toggle("paper-highlight-active", true);
    mapStatus.textContent = "The linked paper was not found. Filters were not changed.";
    return;
  }
  resetPaperDetails();
  mapStatus.classList.toggle("paper-highlight-active", false);
  mapStatus.textContent = baseMapStatusText(currentFilteredRecords);
}

function setHoveredSelection(selection) {
  interactionState.hovered = selection;
  interactionState.hoveredMarkerId = selection?.markerId || null;
  renderActiveSelection();
}

function clearHoveredSelection(marker) {
  // Pinning already clears hover. A later result-button blur must not rebuild
  // the pinned pane while its next control is receiving focus/click.
  if (!interactionState.hovered) return;
  if (marker && interactionState.hovered?.marker !== marker) {
    return;
  }
  interactionState.hovered = null;
  interactionState.hoveredMarkerId = null;
  renderActiveSelection();
}

function setPersistentSelection(selection, { syncUrl = true } = {}) {
  interactionState.hovered = null;
  interactionState.hoveredMarkerId = null;
  interactionState.selected = selection;
  interactionState.selectedMarkerId = selection?.markerId || null;
  requestedPaperIdentity = selection?.identity || "";
  renderActiveSelection();
  if (syncUrl) {
    requestUrlStateSync("push");
    syncUrlFromState();
  }
  scheduleMapResize();
}

function clearPersistentSelection({ syncUrl = true } = {}) {
  interactionState.selected = null;
  interactionState.selectedMarkerId = null;
  requestedPaperIdentity = "";
  pendingResultReveal = null;
  renderActiveSelection();
  if (syncUrl) {
    requestUrlStateSync("push");
    syncUrlFromState();
  }
  scheduleMapResize();
}

function restoreLinkedPaperSelection(matchingPaperIdentities) {
  if (!requestedPaperIdentity) {
    interactionState.selected = null;
    interactionState.selectedMarkerId = null;
    return "closed";
  }
  const paper = canonicalPaperRecordsByIdentity.get(requestedPaperIdentity);
  if (!paper) {
    interactionState.selected = null;
    interactionState.selectedMarkerId = null;
    return "unavailable";
  }
  const visibleOrigin = visiblePaperSelectionByIdentity.get(requestedPaperIdentity);
  interactionState.selected = {
    identity: requestedPaperIdentity,
    record: visibleOrigin?.record || paper,
    markerId: visibleOrigin?.institutionKey || null,
    marker: visibleOrigin?.marker || null,
    institutionKey: visibleOrigin?.institutionKey || null,
    resultPaperIdentities: [requestedPaperIdentity],
    resultScope: "paper",
    source: "deep-link",
    filteredOut: !matchingPaperIdentities.has(requestedPaperIdentity),
  };
  interactionState.selectedMarkerId = visibleOrigin?.institutionKey || null;
  return interactionState.selected.filteredOut ? "filtered-out" : "open";
}

function activateHoverPreview(
  record, identity, markerId, marker, paperCount, taskBreakdown, resultPaperIdentities,
) {
  openInstitutionTooltip(marker, record, paperCount, taskBreakdown);
  setHoveredSelection({
    identity,
    record,
    markerId,
    marker,
    institutionKey: markerId,
    resultPaperIdentities,
    resultScope: "institution",
    source: "marker-hover",
  });
}

function clearHoverPreview(marker, event = null) {
  closeActiveInstitutionTooltip(marker);
  const relatedTarget = event?.originalEvent?.relatedTarget || event?.relatedTarget;
  if (relatedTarget && paperDetails.contains(relatedTarget)) {
    interactionState.isPointerInsideDetails = true;
    return;
  }
  if (interactionState.isPointerInsideDetails) {
    return;
  }
  clearHoveredSelection(marker);
}

function pinPaper(record, identity, institutionKey, resultPaperIdentities = [identity]) {
  closeActiveInstitutionTooltip();
  if (interactionState.selectedMarkerId === institutionKey &&
      interactionState.selected?.identity === identity) {
    clearPersistentSelection();
    return;
  }
  setPersistentSelection({
    identity,
    record,
    markerId: institutionKey,
    institutionKey,
    resultPaperIdentities,
    resultScope: "institution",
    source: "marker",
  });
}

function resultInstitutionSelection(button) {
  const item = button.closest(".result-item");
  const index = Number(item?.dataset.resultIndex);
  if (!resultsPipeline || item?.dataset.resultGeneration !== String(resultsRenderGeneration)
      || !Number.isInteger(index)) return null;
  const displayedRecord = resultsPipeline.displayedResults[index];
  const institutionKey = button.dataset.focusInstitution;
  const markerEntry = visibleMarkerEntryByInstitutionKey.get(institutionKey);
  if (!displayedRecord || !markerEntry) return null;
  const identity = paperIdentity(displayedRecord);
  const markerRecord = markerEntry.records.find(
    (record) => paperIdentity(record) === identity,
  );
  if (!markerRecord) return null;
  return {
    identity: paperIdentity(markerRecord),
    record: markerRecord,
    markerId: institutionKey,
    marker: markerEntry.marker,
    institutionKey,
    resultPaperIdentities: [identity],
    resultScope: "paper",
    source: "result",
  };
}

function previewInstitutionFromResult(button) {
  const selection = resultInstitutionSelection(button);
  if (selection) setHoveredSelection(selection);
}

function selectInstitutionFromResult(button) {
  const selection = resultInstitutionSelection(button);
  if (!selection) {
    mapStatus.textContent = "No visible map marker matches this institution.";
    return;
  }
  setPersistentSelection(selection);
  selection.marker.bringToFront();
}

function renderRecords() {
  return renderRecordsForGeneration();
}

function renderRecordsForGeneration({ generation = null } = {}) {
  const activeGeneration = generation ?? invalidateResultsRenderPipeline();
  if (activeGeneration !== resultsRenderGeneration) return;
  syncKnownFilterState();
  closeActiveInstitutionTooltip();
  interactionState.hovered = null;
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  const normalizedKeyword = normalizedSearchText(keywordFilter.value);
  const filterIndexes = institutionFilterIndexes();
  const institutionSearchIndex = filterIndexes.search;
  const directlyResolvedInstitutionIdentities = resolveInstitutionSearchIdentities(
    normalizedKeyword,
    institutionSearchIndex,
  );
  const resolvedInstitutionIdentity = directlyResolvedInstitutionIdentities.size === 1
    ? [...directlyResolvedInstitutionIdentities][0]
    : "";
  const keywordTerms = normalizedKeyword
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  const hierarchyIndex = filterIndexes.hierarchy;
  const searchRelationshipIndex = filterIndexes.searchRelationships;
  const selectedIdentity = activeInstitutionFilter?.identity || resolvedInstitutionIdentity;
  const resolvedInstitutionIdentities = institutionIdentitiesWithSearchExpansion(
    directlyResolvedInstitutionIdentities,
    hierarchyIndex,
    searchRelationshipIndex,
  );
  const activeInstitutionIdentities = institutionIdentitiesWithSearchExpansion(
    activeInstitutionFilter?.identity
      ? new Set([activeInstitutionFilter.identity])
      : new Set(),
    hierarchyIndex,
    searchRelationshipIndex,
  );
  const institutionLabel = activeInstitutionFilter?.label
    || hierarchyInstitutionLabel(selectedIdentity, institutionHierarchy)
    || keywordFilter.value.trim();
  displayedInstitutionFilter = selectedIdentity ? {
    identity: selectedIdentity,
    label: institutionLabel,
    source: activeInstitutionFilter ? "chip" : "keyword",
  } : null;
  updateMobileFiltersTrigger();
  const matchesInstitutionRecord = (record) => recordMatchesActiveFilters(
    record,
    keywordTerms,
    { institutionRecord: true, resolvedInstitutionIdentities, activeInstitutionIdentities },
  );
  const matchesPublicPaper = (record) => recordMatchesActiveFilters(
    record,
    keywordTerms,
    { resolvedInstitutionIdentities, activeInstitutionIdentities },
  );
  const dimensionSets = (ignoredDimension) => deriveFilteredRecordSets(
    records,
    paperRecords,
    (record) => recordMatchesActiveFilters(record, keywordTerms, {
      institutionRecord: true,
      resolvedInstitutionIdentities,
      activeInstitutionIdentities,
      [ignoredDimension]: true,
    }),
    (record) => recordMatchesActiveFilters(record, keywordTerms, {
      resolvedInstitutionIdentities,
      activeInstitutionIdentities,
      [ignoredDimension]: true,
    }),
  );
  const countryDimensionSets = dimensionSets("ignoreCountry");
  const institutionTypeDimensionSets = dimensionSets("ignoreInstitutionType");
  const venueDimensionSets = dimensionSets("ignoreVenue");
  const venueTypeDimensionSets = dimensionSets("ignoreVenueType");
  updateInstitutionDimensionFilters(
    countryDimensionSets.filteredPapers,
    institutionTypeDimensionSets.filteredPapers,
  );
  updateVenueDimensionFilters(
    venueDimensionSets.filteredPapers,
    venueTypeDimensionSets.filteredPapers,
  );
  renderActiveFilterChips();
  syncUrlFromState();
  const filteredSets = deriveFilteredRecordSets(
    records,
    paperRecords,
    matchesInstitutionRecord,
    matchesPublicPaper,
  );
  const visibleRecords = filteredSets.filteredRecords
    .sort((first, second) => compareRecordsForSort(first, second, sortControl.value));
  const visiblePaperRecords = filteredSets.filteredPapers
    .sort((first, second) => compareRecordsForSort(first, second, sortControl.value));

  currentFilteredRecords = visibleRecords;
  currentFilteredPaperRecords = visiblePaperRecords;

  closeActiveInstitutionTooltip();
  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];
  visibleMarkerEntryByInstitutionKey = new Map();
  visiblePaperSelectionByIdentity = new Map();

  const institutionGroups = MarkerSizeHelpers.groupInstitutionRecords(
    visibleRecords,
    markerInstitutionIdentity,
    paperIdentity,
  );

  institutionGroups.forEach((group) => {
    const record = group.record;
    const locationRecord = record;
    const identity = paperIdentity(record);
    const taskCounts = MarkerSizeHelpers.getInstitutionTaskCounts(
      group.records,
      paperIdentity,
    );
    const taskKey = MarkerSizeHelpers.getDominantInstitutionTask(taskCounts);
    const taskBreakdown = MarkerSizeHelpers.formatTaskBreakdown(taskCounts);
    const marker = L.circleMarker(
      [locationRecord.latitude, locationRecord.longitude],
      markerStyle(taskKey, "base", group.paperCount),
    )
      .on("remove", () => closeActiveInstitutionTooltip(marker))
      .addTo(markerLayer);
    MarkerInteractionHelpers.bindMarkerHandlers(marker, {
      supportsHover: supportsMarkerHover,
      accessibleLabel: `${recordInstitution(locationRecord) || "Unknown institution"}; ${MarkerSizeHelpers.formatInstitutionPaperCount(group.paperCount)}. Show paper details.`,
      click: () => pinPaper(
        record,
        identity,
        group.key,
        [...new Set(group.records.map(paperIdentity))],
      ),
      hover: () => activateHoverPreview(
        record,
        identity,
        group.key,
        marker,
        group.paperCount,
        taskBreakdown,
        [...new Set(group.records.map(paperIdentity))],
      ),
      leave: (event) => clearHoverPreview(marker, event),
    });
    const markerEntry = {
      record,
      records: group.records,
      marker,
      identity,
      institutionKey: group.key,
      paperCount: group.paperCount,
      taskBreakdown,
      taskCounts,
      taskKey,
    };
    visibleMarkerEntries.push(markerEntry);
    visibleMarkerEntryByInstitutionKey.set(group.key, markerEntry);
    const canonicalInstitutionKey = institutionIdentity(record);
    if (!visibleMarkerEntryByInstitutionKey.has(canonicalInstitutionKey)) {
      visibleMarkerEntryByInstitutionKey.set(canonicalInstitutionKey, markerEntry);
    }
    group.records.forEach((groupRecord) => {
      const groupPaperIdentity = paperIdentity(groupRecord);
      if (!visiblePaperSelectionByIdentity.has(groupPaperIdentity)) {
        visiblePaperSelectionByIdentity.set(groupPaperIdentity, {
          record: groupRecord,
          marker,
          institutionKey: group.key,
        });
      }
    });
  });

  const linkedPaperState = restoreLinkedPaperSelection(
    filteredSets.matchingPaperIdentities,
  );

  updateDatasetStatistics(visibleRecords, visiblePaperRecords);
  renderHeaderStatistics(visibleRecords, visiblePaperRecords);
  renderResults(visibleRecords, visiblePaperRecords, activeGeneration);
  mapStatus.classList.toggle("error", false);
  if (interactionState.selected) {
    renderActiveSelection();
  } else if (linkedPaperState === "unavailable") {
    setMarkerSelectionState(null);
    syncResultHighlights();
    showLinkedPaperUnavailable();
    mapStatus.classList.toggle("paper-highlight-active", true);
    mapStatus.textContent = "The linked paper was not found. Filters were not changed.";
  } else {
    resetPaperDetails();
    mapStatus.classList.toggle("paper-highlight-active", false);
    mapStatus.textContent = baseMapStatusText(visibleRecords);
  }
  scheduleMapResize();
}

// A category is active when its authoritative value differs from its neutral default.
// The two year handles form one category, as does an institution selected from a record.
function activeFilterCategoryCount() {
  return activeFilterChipDescriptors().length;
}

function updateMobileFiltersTrigger() {
  const count = activeFilterCategoryCount();
  const label = count ? `Filters (${count})` : "Filters";
  mobileFiltersTriggerLabel.textContent = label;
  mobileFiltersTrigger.setAttribute("aria-label", label);
}

function drawerFocusableElements() {
  return [...filtersPanel.querySelectorAll(
    'button:not([disabled]), input:not([disabled]), select:not([disabled]), a[href], [tabindex]',
  )].filter((element) => (
    element.tabIndex >= 0
    && !element.hidden
    && !element.closest("[inert]")
    && element.getClientRects().length
    && getComputedStyle(element).visibility !== "hidden"
  ));
}

function syncFiltersPanelAccessibility() {
  const isOpenMobileDialog = mobileFiltersMedia.matches && filtersDrawerOpen;
  filtersPanel.setAttribute("role", isOpenMobileDialog ? "dialog" : "region");
  if (isOpenMobileDialog) filtersPanel.setAttribute("aria-modal", "true");
  else filtersPanel.removeAttribute("aria-modal");
  filtersPanel.toggleAttribute("inert", mobileFiltersMedia.matches && !filtersDrawerOpen);
}

function openFiltersDrawer() {
  if (!mobileFiltersMedia.matches || filtersDrawerOpen) return;
  filtersDrawerOpen = true;
  filtersPanel.classList.add("is-open");
  filtersBackdrop.hidden = false;
  document.body.classList.add("filters-drawer-open");
  mobileFiltersTrigger.setAttribute("aria-expanded", "true");
  syncFiltersPanelAccessibility();
  filtersHeading.focus();
}

function closeFiltersDrawer({ restoreFocus = true } = {}) {
  if (!filtersDrawerOpen) return;
  filtersDrawerOpen = false;
  closeAllFilterDropdowns();
  filtersPanel.classList.remove("is-open");
  filtersBackdrop.hidden = true;
  document.body.classList.remove("filters-drawer-open");
  mobileFiltersTrigger.setAttribute("aria-expanded", "false");
  if (restoreFocus && mobileFiltersMedia.matches) mobileFiltersTrigger.focus();
  syncFiltersPanelAccessibility();
}

function handleFiltersDrawerKeydown(event) {
  if (!mobileFiltersMedia.matches || !filtersDrawerOpen) return;
  if (event.key === "Escape") {
    event.preventDefault();
    closeFiltersDrawer();
    return;
  }
  if (event.key !== "Tab") return;
  const focusable = drawerFocusableElements();
  if (!focusable.length) {
    event.preventDefault();
    filtersHeading.focus();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (!filtersPanel.contains(document.activeElement)) {
    event.preventDefault();
    (event.shiftKey ? last : first).focus();
  } else if (event.shiftKey && (
    document.activeElement === first || document.activeElement === filtersHeading
  )) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function handleMobileFiltersMediaChange(event) {
  if (!event.matches) closeFiltersDrawer({ restoreFocus: false });
  syncFiltersPanelAccessibility();
}

function deriveYearBounds(datasetRecords) {
  const years = datasetRecords
    .map(publicationYear)
    .filter((year) => Number.isInteger(year));
  return years.length
    ? { minimum: Math.min(...years), maximum: Math.max(...years) }
    : null;
}

function clampYear(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function resolveYearSelection(bounds, selection = null) {
  if (!bounds) return null;
  if (!selection || !Number.isInteger(selection.start) || !Number.isInteger(selection.end)) {
    return { start: bounds.minimum, end: bounds.maximum };
  }
  const start = clampYear(selection.start, bounds.minimum, bounds.maximum);
  const end = clampYear(selection.end, bounds.minimum, bounds.maximum);
  return start <= end ? { start, end } : { start: end, end };
}

function keyboardYearValue(key, currentValue, minimum, maximum, pageStep) {
  const changes = {
    ArrowLeft: -1,
    ArrowDown: -1,
    ArrowRight: 1,
    ArrowUp: 1,
    PageDown: -pageStep,
    PageUp: pageStep,
  };
  if (key === "Home") return minimum;
  if (key === "End") return maximum;
  if (!Object.hasOwn(changes, key)) return null;
  return clampYear(currentValue + changes[key], minimum, maximum);
}

function currentYearSelection() {
  const start = yearFilterValue(minYearFilter);
  const end = yearFilterValue(maxYearFilter);
  return Number.isInteger(start) && Number.isInteger(end) ? { start, end } : null;
}

function syncYearRange(changedHandle = null) {
  if (!yearRangeBounds) return;
  let start = clampYear(
    Number(minYearFilter.value), yearRangeBounds.minimum, yearRangeBounds.maximum,
  );
  let end = clampYear(
    Number(maxYearFilter.value), yearRangeBounds.minimum, yearRangeBounds.maximum,
  );
  if (start > end) {
    if (changedHandle === "end") start = end;
    else end = start;
  }
  minYearFilter.value = String(start);
  maxYearFilter.value = String(end);
  minYearFilter.setAttribute("aria-valuemax", String(end));
  maxYearFilter.setAttribute("aria-valuemin", String(start));
  minYearFilter.setAttribute("aria-valuetext", `Start Publication Year ${start}`);
  maxYearFilter.setAttribute("aria-valuetext", `End Publication Year ${end}`);

  const span = yearRangeBounds.maximum - yearRangeBounds.minimum;
  const startPercent = span ? ((start - yearRangeBounds.minimum) / span) * 100 : 0;
  const endPercent = span ? ((end - yearRangeBounds.minimum) / span) * 100 : 100;
  yearRangeSlider.style.setProperty("--range-start", `${startPercent}%`);
  yearRangeSlider.style.setProperty("--range-end", `${endPercent}%`);
}

function configureYearRange() {
  const previousSelection = yearRangeBounds ? currentYearSelection() : null;
  const filterSourceRecords = paperRecords.length ? paperRecords : records;
  yearRangeBounds = deriveYearBounds(filterSourceRecords);
  if (!yearRangeBounds) {
    minYearFilter.value = "";
    maxYearFilter.value = "";
    minYearFilter.disabled = true;
    maxYearFilter.disabled = true;
    yearRangeMinimum.textContent = "\u2014";
    yearRangeMaximum.textContent = "\u2014";
    return;
  }
  const selection = resolveYearSelection(yearRangeBounds, previousSelection);
  [minYearFilter, maxYearFilter].forEach((input) => {
    input.min = String(yearRangeBounds.minimum);
    input.max = String(yearRangeBounds.maximum);
  });
  minYearFilter.value = String(selection.start);
  maxYearFilter.value = String(selection.end);
  yearRangeMinimum.textContent = String(yearRangeBounds.minimum);
  yearRangeMaximum.textContent = String(yearRangeBounds.maximum);
  syncYearRange();
}

function handleYearRangeInput(handle) {
  syncYearRange(handle);
  rememberFilterChange("year", { coalesce: yearHistoryStarted });
  requestUrlStateSync(yearHistoryStarted ? "replace" : "push");
  yearHistoryStarted = true;
  renderRecords();
}

function handleYearRangeKeydown(event, handle) {
  if (!yearRangeBounds) return;
  const selection = currentYearSelection();
  if (!selection) return;
  const isStart = handle === "start";
  const minimum = isStart ? yearRangeBounds.minimum : selection.start;
  const maximum = isStart ? selection.end : yearRangeBounds.maximum;
  const currentValue = isStart ? selection.start : selection.end;
  const pageStep = Math.max(1, Math.round(
    (yearRangeBounds.maximum - yearRangeBounds.minimum) / 10,
  ));
  const nextValue = keyboardYearValue(
    event.key, currentValue, minimum, maximum, pageStep,
  );
  if (nextValue === null) return;
  event.preventDefault();
  (isStart ? minYearFilter : maxYearFilter).value = String(nextValue);
  handleYearRangeInput(handle);
}

function configureVenueFilter() {
  venueFilter.replaceChildren(new Option("All", "all"));
  venueTypeFilter.replaceChildren(new Option("All", "all"));
  venueFilter.value = "all";
  venueTypeFilter.value = "all";
  syncFilterDropdownForSelect(venueFilter);
  syncFilterDropdownForSelect(venueTypeFilter);
}

function updateVenueDimensionFilters(venuePapers, venueTypePapers) {
  const metadataByVenue = new Map();
  [...venuePapers, ...venueTypePapers].filter((record) => !isBookRecord(record)).forEach((record) => {
    const value = venueFilterValue(record);
    const existing = metadataByVenue.get(value);
    const track = canonicalVenueTrack(record);
    if (existing) {
      if (track) existing.tracks.add(track);
      return;
    }
    metadataByVenue.set(value, {
      label: venueDisplayLabel(record),
      baseLabel: venueBaseDisplayLabel(record),
      name: getRecordVenue(record) || "Unknown publication venue",
      acronym: record.venue_acronym || "",
      track,
      tracks: new Set(track ? [track] : []),
      type: recordVenueType(record) || "__unknown__",
    });
  });
  metadataByVenue.forEach((metadata) => {
    if (metadata.tracks.size > 1) {
      metadata.label = `${metadata.baseLabel} — All Tracks`;
      metadata.track = "";
    }
  });
  const venueCounts = dimensionPaperCounts(venuePapers,
    (record) => isBookRecord(record) ? [] : [venueFilterValue(record)],
  );
  const venueTypeCounts = dimensionPaperCounts(
    venueTypePapers,
    (record) => [recordVenueType(record) || "__unknown__"],
  );
  replaceCountedFilterOptions(
    venueFilter,
    "All",
    sortedVenueCounts(venueCounts, metadataByVenue),
    (value) => metadataByVenue.get(value)?.label
      || (value === "__unknown__" ? "Unknown publication venue" : value),
    false,
  );
  replaceCountedFilterOptions(
    venueTypeFilter,
    "All",
    sortedVenueTypeCounts(venueTypeCounts),
    (value) => value === "__unknown__" ? "Unknown" : formatTask(value),
  );
  syncFilterDropdownForSelect(venueFilter);
  syncFilterDropdownForSelect(venueTypeFilter);
}

function enableControls() {
  keywordFilter.disabled = false;
  taskFilter.disabled = false;
  entryTypeFilter.disabled = false;
  sortControl.disabled = false;
  venueFilter.disabled = false;
  venueTypeFilter.disabled = false;
  countryFilter.disabled = false;
  institutionTypeFilter.disabled = false;
  preprintFilter.disabled = false;
  filterDropdowns.forEach((dropdown) => {
    dropdown.button.disabled = dropdown.select.disabled;
  });
  minYearFilter.disabled = !yearRangeBounds;
  maxYearFilter.disabled = !yearRangeBounds;
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

function validatePaperRecord(record) {
  const validTasks = Object.keys(TASK_COLORS);
  const mapRecordCount = Number(record.map_record_count);
  return (
    typeof recordTitle(record) === "string" &&
    (record.year === null || Number.isInteger(record.year)) &&
    validTasks.includes(record.task) &&
    Array.isArray(record.authors) &&
    typeof record.coverage_status === "string" &&
    typeof record.has_map_location === "boolean" &&
    typeof record.missing_affiliation === "boolean" &&
    typeof record.missing_coordinates === "boolean" &&
    Number.isInteger(mapRecordCount) &&
    mapRecordCount >= 0
  );
}

function showDatasetMessage(message, isError = false, isLoadFailure = false) {
  clearPaperInteraction(false);
  records = [];
  paperRecords = [];
  canonicalPaperRecordsByIdentity = new Map();
  mapRecordsByPaperIdentity = new Map();
  invalidateFilteringDataCaches();
  configureYearRange();
  currentFilteredRecords = [];
  currentFilteredPaperRecords = [];
  currentDisplayedResults = [];
  closeActiveInstitutionTooltip();
  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];
  visibleMarkerEntryByInstitutionKey = new Map();
  interactionState.hovered = null;
  updateDatasetStatistics(records, paperRecords);
  renderHeaderStatistics(records, paperRecords);
  renderResults(records, paperRecords);
  if (isLoadFailure) {
    resultsCount.textContent = "Data unavailable";
    resultsEmpty.textContent = message;
    document.querySelectorAll(".header-chart-content").forEach((container) => {
      container.innerHTML = '<p class="chart-empty">Unable to load data.</p>';
    });
  }
  mapStatus.textContent = message;
  mapStatus.classList.toggle("error", isError);
}

function updateDatasetLabels() {
  mapStatus.textContent = datasetName === "preview"
    ? "Loading research map data..."
    : "Loading local OpenAlex data...";
  datasetStatisticsNote.textContent =
    "Filtered institution records represent paper–institution links; unique papers include papers without mapped institutions.";
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
    return {
      metadata,
      records: payload.records,
      institutionAliases: Array.isArray(payload.institution_aliases)
        ? payload.institution_aliases
        : [],
      canonicalInstitutionSearchIndex:
        payload.canonical_institution_search_index
        && typeof payload.canonical_institution_search_index === "object"
        && !Array.isArray(payload.canonical_institution_search_index)
          ? payload.canonical_institution_search_index
          : {},
      institutionIdRedirects:
        payload.institution_id_redirects
        && typeof payload.institution_id_redirects === "object"
        && !Array.isArray(payload.institution_id_redirects)
          ? payload.institution_id_redirects
          : {},
      institutionHierarchy: Array.isArray(payload.institution_hierarchy)
        ? payload.institution_hierarchy.filter((relationship) => (
          relationship.review_status === "confirmed"
        ))
        : [],
      institutionSearchRelationships: Array.isArray(
        payload.institution_search_relationships
      )
        ? payload.institution_search_relationships.filter((relationship) => (
          relationship.review_status === "confirmed"
          && relationship.relationship_type === "search_family"
        ))
        : [],
    };
  }
  throw new Error(`${datasetName} data does not contain a records array`);
}

function displayPublicPreviewDate(metadata) {
  const element = document.querySelector("#data-updated");
  const timeElement = document.querySelector("#data-updated-time");
  if (!element || !timeElement) return;
  const timestamp = metadata.public_preview_generated_at;
  const formattedDate = PublicExportMetadata.formatPublicPreviewDate(
    timestamp,
  );
  element.hidden = !formattedDate;
  timeElement.dateTime = formattedDate ? timestamp.slice(0, 10) : "";
  timeElement.textContent = formattedDate;
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
  normalizedData.records = normalizedData.records.map(normalizeCountryRegionRecord);
  if (!normalizedData.records.every(validateRecord)) {
    throw new Error(`${name} data does not match the expected format`);
  }
  if (config.paperUrl) {
    const paperResponse = await fetch(config.paperUrl, { cache: "no-cache" });
    if (!paperResponse.ok) {
      throw new Error(`${name} paper data request failed with status ${paperResponse.status}`);
    }
    const paperText = await paperResponse.text();
    const normalizedPaperData = paperText.trim()
      ? normalizeDatasetPayload(JSON.parse(paperText))
      : { metadata: {}, records: [] };
    normalizedPaperData.records = normalizedPaperData.records.map((record) => ({
      aggregated_institutions: [],
      aggregated_institution_types: [],
      aggregated_country_names: [],
      aggregated_country_codes: [],
      aggregated_regions: [],
      aggregated_region_codes: [],
      ...record,
    }));
    if (!normalizedPaperData.records.every(validatePaperRecord)) {
      throw new Error(`${name} paper data does not match the expected format`);
    }
    normalizedData.paperMetadata = normalizedPaperData.metadata;
    normalizedData.paperRecords = normalizedPaperData.records;
  }
  return normalizedData;
}

function displayDataset(normalizedData) {
  lastKnownFilterState = null;
  lastFilterChange = null;
  clearPaperInteraction(false);
  visibleMarkerEntryByInstitutionKey = new Map();
  institutionAliases = normalizedData.institutionAliases || [];
  institutionHierarchy = normalizedData.institutionHierarchy || [];
  institutionSearchRelationships = normalizedData.institutionSearchRelationships || [];
  canonicalInstitutionSearchIndex = normalizedData.canonicalInstitutionSearchIndex || {};
  institutionIdRedirects = normalizedData.institutionIdRedirects || {};
  if (Array.isArray(normalizedData.metadata?.venue_type_order)) {
    const exportedOrder = normalizedData.metadata.venue_type_order
      .map((value) => String(value || "").trim().toLocaleLowerCase())
      .filter(Boolean);
    if (exportedOrder.length) venueTypeOrder = exportedOrder;
  }
  const canonicalized = canonicalizePublicDataset(
    normalizedData.records,
    normalizedData.paperRecords || [],
    institutionAliases,
    canonicalInstitutionSearchIndex,
    institutionIdRedirects,
  );
  records = canonicalized.mapRecords;
  paperRecords = canonicalized.paperRecords;
  mapRecordsByPaperIdentity = canonicalized.mapRecordsByPaperIdentity;
  invalidateFilteringDataCaches();
  canonicalPaperRecordsByIdentity = new Map(
    [
      ...records.map((record) => [paperIdentity(record), record]),
      ...paperRecords.map((record) => [paperIdentity(record), record]),
    ],
  );
  displayPublicPreviewDate(normalizedData.metadata);
  configureYearRange();
  configureVenueFilter();
  enableControls();
  restoreViewState(parseViewState(window.location.search));
  urlStateReady = true;
  pendingUrlHistoryMode = "replace";
  renderRecords();
  scheduleMapResize(true);
}

async function loadData() {
  try {
    const normalizedData = await readDataset(datasetName);
    if (normalizedData.records.length === 0) {
      showDatasetMessage(datasetConfig.emptyMessage, true);
      return;
    }
    displayDataset(normalizedData);
  } catch (error) {
    console.error("Dataset initialization failed.", error);
    const messages = {
      openalex:
        "Local OpenAlex data could not be loaded.",
      preview:
        "Unable to load public data.",
    };
    showDatasetMessage(messages[datasetName], true, true);
  }
}

filterDropdowns = [
  sortControl,
  taskFilter,
  entryTypeFilter,
  venueTypeFilter,
  venueFilter,
  countryFilter,
  institutionTypeFilter,
  preprintFilter,
].map(createFilterDropdown);
filterDropdownBySelect = new Map(
  filterDropdowns.map((dropdown) => [dropdown.select, dropdown]),
);

const chartTooltip = document.createElement("div");
chartTooltip.className = "chart-tooltip";
chartTooltip.setAttribute("role", "tooltip");
chartTooltip.hidden = true;
document.body.append(chartTooltip);

function positionChartTooltip(target) {
  const targetBounds = target.getBoundingClientRect();
  const tooltipBounds = chartTooltip.getBoundingClientRect();
  const viewportPadding = 10;
  const preferredLeft = targetBounds.left + (targetBounds.width - tooltipBounds.width) / 2;
  const left = Math.min(
    window.innerWidth - tooltipBounds.width - viewportPadding,
    Math.max(viewportPadding, preferredLeft),
  );
  const below = targetBounds.bottom + 7;
  const top = below + tooltipBounds.height <= window.innerHeight - viewportPadding
    ? below
    : Math.max(viewportPadding, targetBounds.top - tooltipBounds.height - 7);
  chartTooltip.style.left = `${left}px`;
  chartTooltip.style.top = `${top}px`;
}

function showChartTooltip(target) {
  const text = target.dataset.chartTooltip;
  if (!text) return;
  chartTooltip.textContent = text;
  chartTooltip.hidden = false;
  positionChartTooltip(target);
}

function hideChartTooltip() {
  chartTooltip.hidden = true;
}

headerStatistics.addEventListener("click", (event) => {
  const control = event.target.closest("button[data-chart-filter]");
  if (!control || !headerStatistics.contains(control)) return;
  activateChartFilter(
    control.dataset.chartFilter,
    control.dataset.chartValue,
    control.dataset.chartLabel,
  );
});

document.addEventListener("pointerover", (event) => {
  const target = event.target.closest("[data-chart-tooltip]");
  if (target) showChartTooltip(target);
});
document.addEventListener("pointerout", (event) => {
  const target = event.target.closest("[data-chart-tooltip]");
  if (target && !target.contains(event.relatedTarget)) hideChartTooltip();
});
document.addEventListener("focusin", (event) => {
  const target = event.target.closest("[data-chart-tooltip]");
  if (target) showChartTooltip(target);
});
document.addEventListener("focusout", (event) => {
  if (event.target.closest("[data-chart-tooltip]")) hideChartTooltip();
});
window.addEventListener("resize", hideChartTooltip);
window.addEventListener("scroll", hideChartTooltip, true);

function requestKeywordUrlSync() {
  requestUrlStateSync(keywordHistoryStarted ? "replace" : "push");
  keywordHistoryStarted = true;
}

function scheduleKeywordRender() {
  const generation = invalidateResultsRenderPipeline();
  setResultsLayoutPending(true, resultsList.querySelector(".result-item") === null);
  resultsKeywordFrame = requestResultsAnimationFrame(() => {
    resultsKeywordFrame = null;
    if (generation !== resultsRenderGeneration) return;
    renderRecordsForGeneration({ generation });
  });
}

function resetFilterValues({ resetSort = false } = {}) {
  keywordFilter.value = "";
  taskFilter.value = "all";
  entryTypeFilter.value = "all";
  if (resetSort) sortControl.value = "year-desc";
  venueFilter.value = "all";
  venueTypeFilter.value = "all";
  countryFilter.value = "all";
  institutionTypeFilter.value = "all";
  preprintFilter.value = "all";
  filterDropdowns.forEach(syncFilterDropdown);
  if (yearRangeBounds) {
    minYearFilter.value = String(yearRangeBounds.minimum);
    maxYearFilter.value = String(yearRangeBounds.maximum);
    syncYearRange();
  }
  activeInstitutionFilter = null;
  displayedInstitutionFilter = null;
}

function clearActiveFilter(key) {
  const controls = {
    keyword: keywordFilter,
    task: taskFilter,
    "entry-type": entryTypeFilter,
    "venue-type": venueTypeFilter,
    venue: venueFilter,
    country: countryFilter,
    "institution-type": institutionTypeFilter,
    version: preprintFilter,
  };
  if (key === "keyword") keywordFilter.value = "";
  else if (key === "year" && yearRangeBounds) {
    minYearFilter.value = String(yearRangeBounds.minimum);
    maxYearFilter.value = String(yearRangeBounds.maximum);
    syncYearRange();
  } else if (key === "institution") {
    activeInstitutionFilter = null;
    displayedInstitutionFilter = null;
  } else if (controls[key]) {
    controls[key].value = "all";
    syncFilterDropdownForSelect(controls[key]);
  } else return;
  rememberFilterChange(key);
  requestUrlStateSync("push");
  renderRecords();
}

function clearAllActiveFilters() {
  resetFilterValues();
  rememberFilterChange("all");
  requestUrlStateSync("push");
  renderRecords();
}

function focusResultsRecoveryDestination() {
  const nextAction = resultsEmpty.hidden
    ? null
    : resultsEmpty.querySelector("button:not([hidden])");
  (nextAction || resultsCount).focus({ preventScroll: true });
}

function undoLastFilterChange() {
  if (!lastFilterChange) return;
  const previousFilters = lastFilterChange.before;
  const { view, sort, paper } = currentViewState();
  lastFilterChange = null;
  restoreViewState({ ...previousFilters, view, sort, paper });
  lastKnownFilterState = currentFilterConstraintState();
  requestUrlStateSync("push");
  renderRecords();
  focusResultsRecoveryDestination();
}

function focusFilterControl(key) {
  const controls = {
    keyword: keywordFilter,
    task: taskFilter,
    "entry-type": entryTypeFilter,
    "venue-type": venueTypeFilter,
    venue: venueFilter,
    country: countryFilter,
    "institution-type": institutionTypeFilter,
    version: preprintFilter,
    year: minYearFilter,
  };
  const control = controls[key];
  (filterDropdownBySelect.get(control)?.button || control || filtersHeading).focus();
}

keywordFilter.addEventListener("compositionstart", () => {
  keywordCompositionActive = true;
});
keywordFilter.addEventListener("compositionend", () => {
  keywordCompositionActive = false;
  rememberFilterChange("keyword", { coalesce: keywordHistoryStarted });
  requestKeywordUrlSync();
  scheduleKeywordRender();
});
keywordFilter.addEventListener("input", (event) => {
  if (keywordCompositionActive || event.isComposing) return;
  rememberFilterChange("keyword", { coalesce: keywordHistoryStarted });
  requestKeywordUrlSync();
  scheduleKeywordRender();
});
keywordFilter.addEventListener("focus", () => { keywordHistoryStarted = false; });
keywordFilter.addEventListener("blur", () => { keywordHistoryStarted = false; });
function handleFilterControlChange(event) {
  const filterKeys = new Map([
    [taskFilter, "task"],
    [entryTypeFilter, "entry-type"],
    [venueTypeFilter, "venue-type"],
    [venueFilter, "venue"],
    [countryFilter, "country"],
    [institutionTypeFilter, "institution-type"],
    [preprintFilter, "version"],
  ]);
  const key = filterKeys.get(event.currentTarget);
  if (key) rememberFilterChange(key);
  requestUrlStateSync("push");
  renderRecords();
}
taskFilter.addEventListener("change", handleFilterControlChange);
entryTypeFilter.addEventListener("change", handleFilterControlChange);
sortControl.addEventListener("change", handleFilterControlChange);
venueFilter.addEventListener("change", handleFilterControlChange);
venueTypeFilter.addEventListener("change", handleFilterControlChange);
countryFilter.addEventListener("change", handleFilterControlChange);
document.addEventListener("pointerdown", (event) => {
  filterDropdowns.forEach((dropdown) => {
    if (!dropdown.panel.hidden && !dropdown.root.contains(event.target)) {
      closeFilterDropdown(dropdown);
    }
  });
});
document.addEventListener("keydown", (event) => {
  const openDropdown = filterDropdowns.find((dropdown) => !dropdown.panel.hidden);
  if (event.key === "Escape" && openDropdown) {
    event.preventDefault();
    closeFilterDropdown(openDropdown, true);
  }
});
window.addEventListener("resize", () => {
  filterDropdowns.forEach(positionFilterDropdownPanel);
});
mobileFiltersTrigger.addEventListener("click", openFiltersDrawer);
closeFiltersButton.addEventListener("click", () => closeFiltersDrawer());
doneFiltersButton.addEventListener("click", () => closeFiltersDrawer());
filtersBackdrop.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  closeFiltersDrawer();
});
document.addEventListener("keydown", handleFiltersDrawerKeydown);
mobileFiltersMedia.addEventListener("change", handleMobileFiltersMediaChange);
syncFiltersPanelAccessibility();
institutionTypeFilter.addEventListener("change", handleFilterControlChange);
preprintFilter.addEventListener("change", handleFilterControlChange);
minYearFilter.addEventListener("input", () => handleYearRangeInput("start"));
maxYearFilter.addEventListener("input", () => handleYearRangeInput("end"));
[minYearFilter, maxYearFilter].forEach((input) => {
  input.addEventListener("change", () => { yearHistoryStarted = false; });
  input.addEventListener("blur", () => { yearHistoryStarted = false; });
});
minYearFilter.addEventListener("keydown", (event) => {
  handleYearRangeKeydown(event, "start");
});
maxYearFilter.addEventListener("keydown", (event) => {
  handleYearRangeKeydown(event, "end");
});
[resultsList, paperDetails].forEach((container) => {
  container.addEventListener("click", (event) => {
    const copyPaperLink = event.target.closest("[data-copy-paper-link]");
    if (copyPaperLink) {
      copySelectedPaperUrl();
      return;
    }
    const authorToggle = event.target.closest(".paper-authors-toggle");
    if (authorToggle) {
      event.preventDefault();
      event.stopPropagation();
      PaperDetailsHelpers.togglePaperAuthors(authorToggle);
      scheduleResultsMasonryLayout([authorToggle.closest(".result-item")].filter(Boolean));
      return;
    }
    const institutionToggle = event.target.closest(".result-institutions-toggle");
    if (institutionToggle) {
      const section = institutionToggle.closest(".result-paper-institutions");
      const overflow = section?.querySelector(".result-institutions-overflow");
      const isExpanded = institutionToggle.getAttribute("aria-expanded") === "true";
      institutionToggle.setAttribute("aria-expanded", String(!isExpanded));
      institutionToggle.textContent = isExpanded
        ? "Show all institutions"
        : "Show fewer institutions";
      if (overflow) overflow.hidden = isExpanded;
      scheduleResultsMasonryLayout([institutionToggle.closest(".result-item")].filter(Boolean));
      return;
    }
    const showInResults = event.target.closest("[data-show-selection-in-results]");
    if (showInResults) {
      showSelectionInResults();
      return;
    }
    const focusInstitution = event.target.closest("[data-focus-institution]");
    if (focusInstitution) {
      selectInstitutionFromResult(focusInstitution);
      return;
    }
    const button = event.target.closest("[data-institution-filter]");
    if (button) {
      applyInstitutionFilter(button.dataset.institutionFilter, button.dataset.institutionLabel);
    }
  });
});
resultsList.addEventListener("pointerover", (event) => {
  const button = event.target.closest("[data-focus-institution]");
  if (button && !button.contains(event.relatedTarget)) previewInstitutionFromResult(button);
});
resultsList.addEventListener("pointerout", (event) => {
  const button = event.target.closest("[data-focus-institution]");
  if (button && !button.contains(event.relatedTarget)) clearHoveredSelection();
});
resultsList.addEventListener("focusin", (event) => {
  const button = event.target.closest("[data-focus-institution]");
  if (button) previewInstitutionFromResult(button);
});
resultsList.addEventListener("focusout", (event) => {
  const button = event.target.closest("[data-focus-institution]");
  if (button && !button.contains(event.relatedTarget)) clearHoveredSelection();
});
activeFilterChips.addEventListener("click", (event) => {
  const remove = event.target.closest("[data-remove-filter]");
  if (!remove) return;
  const key = remove.dataset.removeFilter;
  clearActiveFilter(key);
  focusFilterControl(key);
});
clearActiveFiltersButton.addEventListener("click", () => {
  clearAllActiveFilters();
  filtersHeading.focus();
});
resultsEmpty.addEventListener("click", (event) => {
  const remove = event.target.closest("[data-empty-remove-filter]");
  if (remove) {
    clearActiveFilter(remove.dataset.emptyRemoveFilter);
    focusResultsRecoveryDestination();
    return;
  }
  if (event.target === undoLastFilterButton) {
    undoLastFilterChange();
    return;
  }
  if (event.target === clearEmptyFiltersButton) {
    clearAllActiveFilters();
    focusResultsRecoveryDestination();
  }
});
copyViewLinkButton.addEventListener("click", copyCanonicalViewUrl);
window.addEventListener("popstate", () => {
  if (!urlStateReady) return;
  restoreViewStateFromLocation();
});
window.addEventListener("resize", () => scheduleMapResize());
window.addEventListener("resize", () => {
  if (resultsResizeTimeout !== null) clearTimeout(resultsResizeTimeout);
  const generation = resultsRenderGeneration;
  resultsResizeTimeout = setTimeout(() => {
    if (generation !== resultsRenderGeneration || !resultsPipeline?.renderedCount) return;
    resultsResizeTimeout = null;
    if (resultsLayoutSignature() !== resultsPipeline.layoutSignature) {
      scheduleResultsMasonryLayout();
    }
  }, RESULTS_RESIZE_DEBOUNCE_MS);
});
const fontLayoutGeneration = resultsRenderGeneration;
document.fonts?.ready.then(() => {
  const generation = fontLayoutGeneration;
  if (generation !== resultsRenderGeneration || !resultsPipeline?.renderedCount) return;
  if (resultsLayoutSignature() !== resultsPipeline.layoutSignature) {
    scheduleResultsMasonryLayout();
  }
});
exportCsvButton.addEventListener("click", downloadFilteredCsv);
closePaperDetailsButton.addEventListener("click", () => {
  const selectionOrigin = interactionState.selected?.marker?.getElement?.()
    || visibleMarkerEntryByInstitutionKey
      .get(interactionState.selectedMarkerId)?.marker?.getElement?.();
  if (interactionState.selected || requestedPaperIdentity) {
    clearPersistentSelection();
  } else {
    clearHoveredSelection();
  }
  (selectionOrigin || mapElement).focus({ preventScroll: true });
});
paperDetails.addEventListener("pointerenter", () => {
  interactionState.isPointerInsideDetails = true;
});
paperDetails.addEventListener("pointerleave", () => {
  interactionState.isPointerInsideDetails = false;
  if (!interactionState.selected && !interactionState.hoveredMarkerId) {
    clearHoveredSelection();
  }
});
resultsViewButtons.forEach((button) => {
  button.addEventListener("click", () => selectResultsView(button.dataset.resultsView));
});
resetButton.addEventListener("click", () => {
  resetFilterValues({ resetSort: true });
  rememberFilterChange("all");
  requestUrlStateSync("push");
  renderRecords();
  scheduleMapResize(true);
});

updateDatasetLabels();
loadData();
