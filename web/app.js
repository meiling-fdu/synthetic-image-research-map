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
    paperUrl: "data/public_preview_papers.json",
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
const ENTRY_TYPE_LABELS = {
  method: "Method",
  dataset: "Dataset",
  benchmark: "Benchmark",
  survey: "Survey",
  analysis: "Analysis study",
};
const INSTITUTION_TYPE_LABELS = {
  university: "University",
  research_unit: "Research unit",
  company: "Company",
  other: "Other",
};
const INSTITUTION_TYPE_ORDER = ["university", "research_unit", "company", "other"];
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
  SK: "Slovakia", SY: "Syria", TH: "Thailand", TR: "Türkiye",
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
const countryCombobox = document.querySelector("#country-combobox");
const countryComboboxButton = document.querySelector("#country-combobox-button");
const countryComboboxValue = document.querySelector("#country-combobox-value");
const countryComboboxPanel = document.querySelector("#country-combobox-panel");
const countryComboboxOptions = document.querySelector("#country-combobox-options");
const institutionTypeFilter = document.querySelector("#institution-type-filter");
const preprintFilter = document.querySelector("#preprint-filter");
const minYearFilter = document.querySelector("#min-year-filter");
const maxYearFilter = document.querySelector("#max-year-filter");
const yearRangeMinimum = document.querySelector("#year-range-min");
const yearRangeMaximum = document.querySelector("#year-range-max");
const yearRangeSlider = document.querySelector(".year-range-slider");
const resetButton = document.querySelector("#reset-filters");
const activeInstitutionFilterChip = document.querySelector("#active-institution-filter");
const mapStatus = document.querySelector("#map-status");
const datasetRecordCount = document.querySelector("#dataset-record-count");
const datasetPaperCount = document.querySelector("#dataset-paper-count");
const datasetInstitutionCount = document.querySelector("#dataset-institution-count");
const datasetCountryCount = document.querySelector("#dataset-country-count");
const datasetDetectionCount = document.querySelector("#dataset-detection-count");
const datasetAttributionCount = document.querySelector("#dataset-attribution-count");
const datasetCombinedCount = document.querySelector("#dataset-combined-count");
const datasetStatisticsNote = document.querySelector("#dataset-statistics-note");
const taskChartContent = document.querySelector("#task-chart-content");
const institutionChartContent = document.querySelector("#institution-chart-content");
const yearChartContent = document.querySelector("#year-chart-content");
const resultsCount = document.querySelector("#results-count");
const resultsList = document.querySelector("#results-list");
const resultsEmpty = document.querySelector("#results-empty");
const exportCsvButton = document.querySelector("#export-csv");
const resultsViewButtons = document.querySelectorAll("[data-results-view]");
const paperDetails = document.querySelector("#paper-details");
const paperDetailsContent = document.querySelector("#paper-details-content");
const closePaperDetailsButton = document.querySelector("#close-paper-details");
const paperDetailsPinStatus = document.querySelector("#paper-details-pin-status");
const datasetStatusNote = document.querySelector("#dataset-status-note");
const datasetNoticeCopy = document.querySelector("#dataset-notice-copy");

let records = [];
let paperRecords = [];
let institutionAliases = [];
let institutionHierarchy = [];
let canonicalInstitutionSearchIndex = {};
let institutionIdRedirects = {};
let currentFilteredRecords = [];
let currentFilteredPaperRecords = [];
let currentDisplayedResults = [];
let resultsView = "institutions";
let visibleMarkerEntries = [];
let activeInstitutionFilter = null;
let displayedInstitutionFilter = null;
let yearRangeBounds = null;
let venueTypeOrder = ["conference", "journal", "preprint", "book"];
let countryComboboxOptionData = [];
let activeCountryOptionIndex = -1;
const interactionState = {
  hoveredMarkerId: null,
  pinnedMarkerId: null,
  detailsSource: null,
  isPointerInsideDetails: false,
  hovered: null,
  pinned: null,
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
  ["venue_label", (record) => venueDisplayLabel(record)],
  ["venue_id", (record) => record.venue_id || ""],
  ["venue_name", (record) => getRecordVenue(record)],
  ["venue_acronym", (record) => record.venue_acronym || ""],
  ["venue_type", (record) => recordVenueType(record)],
  ["venue_track", (record) => record.venue_track || "main"],
  ["entry_type", (record) => getEntryType(record)],
  ["task", (record) => record.task || ""],
  ["subtask", (record) => record.subtask || ""],
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
  ["venue_label", (record) => venueDisplayLabel(record)],
  ["venue_id", (record) => record.venue_id || ""],
  ["venue_name", (record) => getRecordVenue(record)],
  ["venue_acronym", (record) => record.venue_acronym || ""],
  ["venue_type", (record) => recordVenueType(record)],
  ["venue_track", (record) => record.venue_track || "main"],
  ["entry_type", (record) => getEntryType(record)],
  ["task", (record) => record.task || ""],
  ["subtask", (record) => record.subtask || ""],
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

function getEntryType(record) {
  const value = String(record.entry_type || "").trim().toLowerCase();
  if (Object.hasOwn(ENTRY_TYPE_LABELS, value)) {
    return value;
  }
  const legacyValue = String(record.material_type || "").trim().toLowerCase();
  return ["dataset", "benchmark", "survey"].includes(legacyValue)
    ? legacyValue
    : "method";
}

function getEntryTypeLabel(value) {
  return ENTRY_TYPE_LABELS[value] || ENTRY_TYPE_LABELS.method;
}

function recordTitle(record) {
  return record.title ?? record.paper_title;
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
        institution_type: record?.institution_type || "",
        country: record?.country || "",
        region: record?.region || "",
      };
  const currentIdentity = currentInstitution.name
    ? affiliationIdentity({
        institution: currentInstitution.name,
        institution_id: currentInstitution.institution_id,
        canonical_institution_name: currentInstitution.canonical_name,
      })
    : "";
  const affiliationsByIdentity = new Map();
  const sourceIndexIdentities = new Map();

  function addAffiliation(rawAffiliation, sourceRecord) {
    const rawValue = typeof rawAffiliation === "string"
      ? { name: rawAffiliation }
      : rawAffiliation || {};
    const raw = normalizeCountryRegionRecord(rawValue);
    const institution = String(
      raw.name
      || raw.canonical_name
      || raw.institution
      || raw.institution_name
      || "",
    ).trim();
    if (!institution) {
      return;
    }
    const identity = affiliationIdentity({
      institution,
      institution_id: raw.institution_id || raw.canonical_institution_id || "",
      canonical_institution_name: raw.canonical_name || "",
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
      addAffiliation(affiliation, sourceRecord);
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
    const explicitIndices = Array.isArray(raw.affiliation_indices)
      ? raw.affiliation_indices.map(Number).filter((index) => Number.isInteger(index) && index > 0)
      : [];
    const affiliationIndices = explicitIndices.length
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
      is_current_marker_author: isCurrentMarkerAuthor,
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

function renderPaperAuthors(record, currentAffiliationNumber = null) {
  const normalized = normalizePaperDetailsRecord(record);
  return PaperDetailsHelpers.renderPaperAuthors(
    normalized,
    escapeHtml,
    currentAffiliationNumber,
  );
}

function institutionFilterButtonHtml(affiliation) {
  const label = String(affiliation.institution || affiliation.name || "").trim();
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

function renderActiveInstitutionFilter() {
  activeInstitutionFilterChip.hidden = !displayedInstitutionFilter;
  activeInstitutionFilterChip.innerHTML = displayedInstitutionFilter
    ? `<span class="active-institution-label">Institution: ${escapeHtml(displayedInstitutionFilter.label)}</span><button type="button" data-clear-institution-filter aria-label="Clear institution filter for ${escapeHtml(displayedInstitutionFilter.label)}">×</button>`
    : "";
}

function applyInstitutionFilter(identity, label) {
  activeInstitutionFilter = { identity, label };
  renderRecords();
}

function clearInstitutionFilter() {
  if (!activeInstitutionFilter && displayedInstitutionFilter?.source === "keyword") {
    keywordFilter.value = "";
  }
  activeInstitutionFilter = null;
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
  return String(record.institution_name || record.institution || "").trim();
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
  const normalized = String(value || "")
    .normalize("NFKC")
    .trim()
    .toLocaleLowerCase()
    .replace(/[\s-]+/g, "_");
  const aliases = {
    university: "university",
    education: "university",
    educational: "university",
    research_unit: "research_unit",
    research: "research_unit",
    institute: "research_unit",
    laboratory: "research_unit",
    department: "research_unit",
    company: "company",
    corporate: "company",
    commercial: "company",
    unknown: "other",
  };
  const resolved = aliases[normalized] || normalized;
  return ["university", "research_unit", "company", "other"].includes(resolved)
    ? resolved
    : "other";
}

function institutionTypeLabel(value) {
  const normalized = normalizeInstitutionType(value);
  return INSTITUTION_TYPE_LABELS[normalized]
    || normalized.replaceAll("_", " ").replace(/^./, (character) => character.toUpperCase());
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

function venueFilterValue(record) {
  return String(record.venue_id || "").trim() || (getRecordVenue(record)
    ? getRecordVenue(record).toLocaleLowerCase()
    : "__unknown__");
}

function venueDisplayLabel(record) {
  const exported = String(record.venue_label || "").trim();
  if (exported) return exported;
  const name = getRecordVenue(record);
  if (!name) return "Unknown venue/source";
  const acronym = String(record.venue_acronym || "").trim();
  const track = String(record.venue_track || "main").trim();
  let label = name;
  if (acronym) label += ` (${acronym})`;
  if (track && track !== "main") label += ` · ${formatTask(track)}`;
  return label;
}

function recordVenueType(record) {
  return String(record.publication_type || record.venue_type || "").trim().toLocaleLowerCase();
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
    if (authoritative && identitiesByName.has(key)) identitiesByName.delete(key);
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
  const byName = new Map();
  const byId = new Map();
  Object.entries(canonicalIndex || {}).forEach(([id, entry]) => {
    const canonical = {
      id: String(id).trim(),
      name: String(entry?.canonical_name || "").trim(),
      type: String(entry?.institution_type || "").trim(),
    };
    if (!canonical.id || !canonical.name) return;
    byId.set(canonical.id, canonical);
    [canonical.name, ...(Array.isArray(entry?.names) ? entry.names : [])].forEach((name) => {
      byName.set(normalizedSearchText(name), canonical);
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
    if (!canonical.name) return;
    byName.set(normalizedSearchText(alias.alias_name), canonical);
    byName.set(normalizedSearchText(canonical.name), canonical);
    if (canonical.id) byId.set(canonical.id, canonical);
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
    const key = `${paperIdentity(record)}||${institutionIdentity(record)}`;
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
    if (!related.length) return;
    paper.map_record_count = related.length;
    paper.has_map_location = true;
    if (typeof orderedPaperLocationSummary === "function") {
      Object.assign(paper, orderedPaperLocationSummary(related));
    } else {
      paper.aggregated_institutions = [...new Set(related.map(recordInstitution))];
    }
  });
  return { mapRecords: canonicalMaps, paperRecords: publicPaperRecords };
}

function recordSearchText(record) {
  const authors = recordAuthors(record);
  return normalizedSearchText([
    recordTitle(record),
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
    record.venue_name,
    record.venue,
    record.venue_acronym,
    ...(record.venue_aliases || []),
    record.venue_type,
    record.venue_track,
    record.coverage_status,
    record.task,
    record.subtask,
    getEntryTypeLabel(getEntryType(record)),
  ].filter(Boolean).join(" "));
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

function recordMatchesInstitutionIdentities(record, identities, institutionRecord) {
  if (!identities?.size) return true;
  if (institutionRecord) return identities.has(institutionIdentity(record));
  const recordIdentities = recordInstitutionIdentities(record);
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
  const matchesKeyword = matchesInstitutionKeyword
    || searchTextMatchesTerms(recordSearchText(record), keywordTerms);
  const matchesTask = taskFilter.value === "all" || record.task === taskFilter.value;
  const matchesEntryType =
    entryTypeFilter.value === "all" || getEntryType(record) === entryTypeFilter.value;
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
    return (
      compareTextValues(firstMetadata.name, secondMetadata.name)
      || compareTextValues(firstMetadata.acronym, secondMetadata.acronym)
      || compareTextValues(firstMetadata.track, secondMetadata.track)
      || compareTextValues(first[0], second[0])
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

function nextCountryOptionIndex(visibleIndices, currentIndex, direction) {
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

function countryComboboxPlacement(
  triggerRect,
  panelHeight,
  viewportWidth,
  viewportHeight,
  padding = 8,
  gap = 4,
) {
  const width = Math.min(
    Math.max(triggerRect.width, 240),
    Math.max(0, viewportWidth - (padding * 2)),
  );
  const left = Math.min(
    Math.max(triggerRect.left, padding),
    Math.max(padding, viewportWidth - padding - width),
  );
  const availableBelow = viewportHeight - triggerRect.bottom - gap - padding;
  const availableAbove = triggerRect.top - gap - padding;
  const placement = availableBelow < panelHeight && availableAbove > availableBelow
    ? "up"
    : "down";
  const preferredTop = placement === "up"
    ? triggerRect.top - gap - panelHeight
    : triggerRect.bottom + gap;
  const top = Math.min(
    Math.max(preferredTop, padding),
    Math.max(padding, viewportHeight - padding - panelHeight),
  );
  return { left, top, width, placement };
}

function countryOptionElements() {
  return [...countryComboboxOptions.querySelectorAll("[role='option']")];
}

function setActiveCountryOption(index, scroll = false) {
  activeCountryOptionIndex = index;
  let activeElement = null;
  countryOptionElements().forEach((option) => {
    const isActive = Number(option.dataset.countryOptionIndex) === index;
    option.classList.toggle("is-active", isActive);
    if (isActive) activeElement = option;
  });
  const activeId = activeElement?.id || "";
  if (activeId) countryComboboxButton.setAttribute("aria-activedescendant", activeId);
  else countryComboboxButton.removeAttribute("aria-activedescendant");
  if (scroll && activeElement) {
    activeElement.scrollIntoView({ block: "nearest" });
  }
}

function visibleCountryOptionIndices() {
  return countryOptionElements()
    .filter((option) => !option.hidden)
    .map((option) => Number(option.dataset.countryOptionIndex));
}

function moveActiveCountryOption(direction) {
  setActiveCountryOption(
    nextCountryOptionIndex(
      visibleCountryOptionIndices(),
      activeCountryOptionIndex,
      direction,
    ),
    true,
  );
}

function syncCountryComboboxOptions() {
  countryComboboxOptionData = [...countryFilter.options].map((option, index) => ({
    value: option.value,
    label: option.textContent,
    index,
  }));
  countryComboboxOptions.replaceChildren(...countryComboboxOptionData.map((option) => {
    const element = document.createElement("li");
    element.id = `country-combobox-option-${option.index}`;
    element.className = "country-combobox-option";
    element.dataset.countryOptionIndex = String(option.index);
    element.dataset.countryValue = option.value;
    element.setAttribute("role", "option");
    element.setAttribute("aria-selected", String(option.value === countryFilter.value));
    element.textContent = option.label;
    return element;
  }));
  const selectedOption = countryComboboxOptionData.find(
    ({ value }) => value === countryFilter.value,
  ) || countryComboboxOptionData[0];
  countryComboboxValue.textContent = selectedOption?.label || "All";
  activeCountryOptionIndex = selectedOption?.index ?? -1;
  setActiveCountryOption(activeCountryOptionIndex);
}

function positionCountryComboboxPanel() {
  if (countryComboboxPanel.hidden) return;
  const triggerRect = countryComboboxButton.getBoundingClientRect();
  const panelHeight = Math.min(
    countryComboboxPanel.scrollHeight,
    420,
    window.innerHeight * 0.6,
  );
  const placement = countryComboboxPlacement(
    triggerRect,
    panelHeight,
    window.innerWidth,
    window.innerHeight,
  );
  countryComboboxPanel.style.left = `${placement.left}px`;
  countryComboboxPanel.style.top = `${placement.top}px`;
  countryComboboxPanel.style.width = `${placement.width}px`;
  countryComboboxPanel.dataset.placement = placement.placement;
}

function openCountryCombobox() {
  if (countryComboboxButton.disabled || !countryComboboxPanel.hidden) return;
  countryComboboxPanel.hidden = false;
  countryComboboxButton.setAttribute("aria-expanded", "true");
  positionCountryComboboxPanel();
  const selectedIndex = countryComboboxOptionData.findIndex(
    ({ value }) => value === countryFilter.value,
  );
  setActiveCountryOption(selectedIndex, true);
}

function closeCountryCombobox(returnFocus = false) {
  if (countryComboboxPanel.hidden) return;
  countryComboboxPanel.hidden = true;
  countryComboboxButton.setAttribute("aria-expanded", "false");
  countryComboboxButton.removeAttribute("aria-activedescendant");
  if (returnFocus) countryComboboxButton.focus();
}

function selectCountryComboboxValue(value) {
  if (!countryComboboxOptionData.some((option) => option.value === value)) return;
  countryFilter.value = value;
  closeCountryCombobox(true);
  countryFilter.dispatchEvent(new Event("change", { bubbles: true }));
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
  syncCountryComboboxOptions();

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

  const fallbackPapersByIdentity = new Map(
    aggregateRecords(filteredRecords).map((paper) => [identityForRecord(paper), paper]),
  );
  const filteredPapers = [...matchingPaperIdentities]
    .map((identity) => papersByIdentity.get(identity) || fallbackPapersByIdentity.get(identity))
    .filter(Boolean);

  return { filteredRecords, filteredPapers };
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
  const paperCoverageRecords = paperListRecordsForDisplay(datasetPaperRecords);
  datasetRecordCount.textContent = datasetRecords.length;
  datasetPaperCount.textContent = paperCoverageRecords.length;
  datasetInstitutionCount.textContent = normalizedSetSize(
    datasetRecords.map(institutionIdentity),
  );
  datasetCountryCount.textContent = normalizedSetSize(
    datasetRecords.map(recordCountry),
  );
  datasetDetectionCount.textContent = paperCoverageRecords.filter(
    (record) => record.task === "detection",
  ).length;
  datasetAttributionCount.textContent = paperCoverageRecords.filter(
    (record) => record.task === "source_attribution",
  ).length;
  datasetCombinedCount.textContent = paperCoverageRecords.filter(
    (record) => record.task === "detection_and_source_attribution",
  ).length;
}

function renderChartEmpty(container) {
  container.innerHTML = '<p class="chart-empty">No data</p>';
}

function renderTaskChart(paperCoverageRecords) {
  const tasks = [
    ["detection", "Detection"],
    ["source_attribution", "Source attribution"],
    ["detection_and_source_attribution", "Detection + attribution"],
  ].map(([task, label]) => ({
    task,
    label,
    color: TASK_COLORS[task],
    count: paperCoverageRecords.filter((record) => record.task === task).length,
  }));
  const total = tasks.reduce((sum, task) => sum + task.count, 0);
  if (!total) {
    renderChartEmpty(taskChartContent);
    return;
  }
  const segments = tasks
    .filter((task) => task.count)
    .map((task) => (
      `<span class="task-chart-segment" style="width:${(task.count / total) * 100}%;background:${task.color}" title="${escapeHtml(task.label)}: ${task.count}"></span>`
    ))
    .join("");
  const items = tasks
    .map((task) => (
      `<div class="task-chart-item"><i style="background:${task.color}"></i><span title="${escapeHtml(task.label)}">${escapeHtml(task.label)}</span><strong>${task.count}</strong></div>`
    ))
    .join("");
  taskChartContent.innerHTML = (
    `<div class="task-chart-bar" aria-label="${total} filtered papers">${segments}</div><div class="task-chart-list">${items}</div>`
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
  const topInstitutions = [...institutions.values()]
    .map((entry) => ({ name: entry.name, count: entry.papers.size }))
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
      `<div class="institution-chart-row" title="${escapeHtml(entry.name)}: ${entry.count} paper${entry.count === 1 ? "" : "s"}"><div class="institution-chart-label"><span class="institution-chart-fill" style="width:${(entry.count / maximum) * 100}%"></span><span class="institution-chart-name">${escapeHtml(entry.name)}</span></div><span class="institution-chart-count">${entry.count}</span></div>`
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
  yearChartContent.innerHTML = (
    `<div class="year-chart-bars">${years.map(([year, count]) => (
      `<div class="year-chart-item" title="${year}: ${count} paper${count === 1 ? "" : "s"}"><span class="year-chart-count">${count}</span><span class="year-chart-bar-slot"><span class="year-chart-bar" style="height:${(count / maximum) * 100}%"></span></span><span class="year-chart-label">${String(year).slice(-2)}</span></div>`
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
    ? `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`
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
  return PaperLinkHelpers.paperVersionLinks(record, safeArxivUrl)
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

function formatResolutionValue(value) {
  return formatTask(value || "unresolved");
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
      )
    : "Unknown";
  const institutionAuthors = recordInstitutionAuthors(record);
  const institutionAuthorsRow = !affiliations.length && institutionAuthors.length
    ? `<dt>Institution authors</dt><dd>${institutionAuthors.map(escapeHtml).join(", ")}</dd>`
    : "";
  const currentAffiliationNumber = currentAffiliation
    ? `<sup class="current-affiliation-number" aria-label="Affiliation ${currentAffiliation.number}">${currentAffiliation.number}</sup>`
    : "";
  const currentInstitutionButton = institutionFilterButtonHtml(currentAffiliation || {
    institution: recordInstitution(record),
    institutionId: record.institution_id || record.canonical_institution_id,
    canonicalName: record.canonical_institution_name,
    institutionType: normalizeInstitutionType(record.institution_type),
  });
  const year = record.publication_year ?? record.year ?? "Unknown";
  const venue = venueDisplayLabel(record) || "unknown";
  const publicationType = record.publication_type || "Unknown";
  const entryType = getEntryType(record);
  const entryTypeLabel = getEntryTypeLabel(entryType);
  const location = recordLocation(record) || "Unknown";
  const subtaskRow = record.subtask
    ? `<dt>Subtask</dt><dd>${escapeHtml(formatTask(record.subtask))}</dd>`
    : "";
  const detailLinks = paperExternalLinks(record);
  const linksBlock = detailLinks.length
    ? `<nav class="paper-details-links" aria-label="Paper links">${detailLinks.join("")}</nav>`
    : "";
  const versionBadge = isPreprintOnlyRecord(record)
    ? '<span class="popup-badge confidence-unresolved">Preprint-only</span>'
    : hasArxivVersion(record)
      ? '<span class="popup-badge confidence-unresolved">arXiv version</span>'
      : "";
  const hasResolution = hasResolutionMetadata(record);
  const confidence = resolutionConfidence(record);
  const needsReview = reviewStatus(record);
  const confidenceBadge = hasResolution
    ? `<span class="popup-badge confidence-${escapeHtml(confidence)}">${escapeHtml(formatResolutionValue(confidence))} confidence</span>`
    : "";
  const affiliationBadge = preliminaryAffiliationBadge(record);
  const methodRow = record.resolution_method
    ? `<dt>Resolution</dt><dd>${escapeHtml(formatResolutionValue(record.resolution_method))}</dd>`
    : "";
  const reviewRow = needsReview !== null
    ? `<dt>Needs review</dt><dd>${needsReview ? "Yes" : "No"}</dd>`
    : "";
  const resolutionNotesRow = record.resolution_notes
    ? `<dt>Resolution notes</dt><dd class="popup-resolution-notes">${escapeHtml(record.resolution_notes)}</dd>`
    : "";
  const abstract = String(record.abstract || "").trim();
  const abstractSource = String(record.abstract_source || "").trim();
  const abstractBlock = `
    <section class="paper-text-section paper-abstract-section">
      <h4>Abstract</h4>
      <p class="paper-abstract${abstract ? "" : " is-unavailable"}">${escapeHtml(abstract || "No abstract available.")}</p>
      ${abstract && abstractSource ? `<p class="paper-text-source">Source: ${escapeHtml(abstractSource)}</p>` : ""}
    </section>
  `;
  const affiliationsBlock = affiliations.length
    ? `<section class="paper-details-affiliation-section" aria-labelledby="paper-affiliations-heading"><h4 id="paper-affiliations-heading">Affiliations</h4><ol class="paper-details-affiliations">${affiliations.map((affiliation) => `<li${affiliation.isCurrent ? ' class="is-current is-hover-institution"' : ""}><div class="affiliation-heading"><span class="affiliation-institution">${institutionFilterButtonHtml(affiliation)}</span><span class="affiliation-type"> · ${escapeHtml(institutionTypeLabel(affiliation.institutionType))}</span>${affiliation.location ? `<span class="affiliation-location"> · ${escapeHtml(affiliation.location)}</span>` : ""}</div>${affiliation.authors.length ? `<div class="affiliation-authors">${affiliation.authors.map(escapeHtml).join("; ")}</div>` : ""}</li>`).join("")}</ol></section>`
    : "";

  return `
    <div class="popup-badges">
      <span class="popup-badge popup-task">${escapeHtml(formatTask(record.task))}</span>
      <span class="popup-badge entry-type-badge">${escapeHtml(entryTypeLabel)}</span>
      ${versionBadge}
      ${confidenceBadge}
      ${affiliationBadge}
    </div>
    <h3 class="popup-title">${escapeHtml(recordTitle(record))}</h3>
    <dl class="popup-details paper-details-summary">
      <dt>Authors</dt><dd>${authors}</dd>
      <dt class="current-institution-label">Current institution</dt><dd class="current-institution-value paper-current-institution${currentAffiliation ? " is-active is-hover-institution" : ""}">${currentAffiliationNumber}${currentInstitutionButton || "Unknown"}</dd>
      <dt>Year</dt><dd>${escapeHtml(year)}</dd>
      <dt>Venue</dt><dd>${venueDisplayHtml(record)}</dd>
    </dl>
    ${linksBlock}
    ${affiliationsBlock}
    ${abstractBlock}
    <details class="paper-details-more">
      <summary>More details</summary>
      <dl class="popup-details">
        <dt>Location</dt><dd>${escapeHtml(location)}</dd>
        <dt>Publication type</dt><dd>${escapeHtml(formatTask(publicationType))}</dd>
        ${institutionAuthorsRow}
        ${subtaskRow}
        ${methodRow}
        ${reviewRow}
        ${resolutionNotesRow}
      </dl>
    </details>
  `;
}

function resultContent(record, relatedEntries = [{ record }]) {
  const normalizedRecord = normalizePaperDetailsRecord(record, {
    relatedRecords: relatedEntries.map(({ record: relatedRecord }) => relatedRecord),
  });
  const title = recordTitle(record);
  const year = publicationYear(record) ?? "Unknown";
  const venue = venueDisplayLabel(record);
  const isPaperView = resultsView === "papers";
  const entryTypeLabel = getEntryTypeLabel(getEntryType(record));
  const affiliations = normalizedRecord.affiliations;
  const subtask = record.subtask
    ? `<span class="result-task result-subtask">${escapeHtml(formatTask(record.subtask))}</span>`
    : "";
  const venueRow = venue
    ? `<p class="result-venue">${venueDisplayHtml(record)}</p>`
    : "";

  const links = paperExternalLinks(record).join("");
  const linksRow = links ? `<div class="result-links">${links}</div>` : "";
  const authors = recordAuthors(normalizedRecord);
  const authorsHtml = authors.length
    ? renderPaperAuthors(normalizedRecord)
    : "Unknown";
  const authorsRow = `<p class="result-author-affiliations"><strong>Authors:</strong> ${authorsHtml}</p>`;
  const affiliationsHtml = compactAffiliationsHtml(affiliations);
  const affiliationsRow = affiliationsHtml
    ? `<p class="result-compact-affiliations"><strong>Affiliations:</strong> ${affiliationsHtml}</p>`
    : "";
  const affiliationBadge = preliminaryAffiliationBadge(record);
  const aggregatedCountryNames = record.aggregated_country_names || [];
  const aggregatedCountryCodes = record.aggregated_country_codes || [];
  const aggregatedRegions = record.aggregated_regions || [];
  const countriesRow = isPaperView
    ? `<p class="result-aggregate"><strong>Map coverage:</strong> ${escapeHtml(record.has_map_location ? `${record.map_record_count || 0} marker${record.map_record_count === 1 ? "" : "s"}` : "No map location yet")}</p><p class="result-aggregate"><strong>Countries:</strong> ${escapeHtml(aggregatedCountryNames.join(", ") || aggregatedCountryCodes.join(", ") || "Unknown")}</p>`
    : "";
  const regionsRow = isPaperView && aggregatedRegions.length
    ? `<p class="result-aggregate"><strong>Regions:</strong> ${escapeHtml(aggregatedRegions.join(", "))}</p>`
    : "";

  return `
    <article>
      <div class="result-title-row">
        <h3 class="result-title">${escapeHtml(title)}</h3>
        <span class="result-year">${escapeHtml(year)}</span>
      </div>
      ${venueRow}
      ${authorsRow}
      ${affiliationsRow}
      ${countriesRow}
      ${regionsRow}
      <div class="result-classification">
        <span class="result-task">${escapeHtml(formatTask(record.task))}</span>
        <span class="result-task entry-type-badge">${escapeHtml(entryTypeLabel)}</span>
        ${subtask}
        ${affiliationBadge}
      </div>
      ${linksRow}
    </article>
  `;
}

function renderResults(visibleRecords, visiblePaperRecords = []) {
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
  const count = displayedResults.length;
  resultsCount.textContent = resultsView === "papers"
    ? `Showing ${count} Unique Paper${count === 1 ? "" : "s"}`
    : `Showing ${count} Record${count === 1 ? "" : "s"}`;
  exportCsvButton.disabled = count === 0;
  resultsList.replaceChildren();
  resultsEmpty.hidden = count !== 0;
  resultsList.hidden = count === 0;

  if (!count) {
    return;
  }

  const fragment = document.createDocumentFragment();
  displayedResults.forEach((record) => {
    const item = document.createElement("li");
    item.className = "result-item";
    const relatedEntries = relatedEntriesByIdentity.get(paperIdentity(record)) || [];
    item.innerHTML = resultContent(record, relatedEntries);
    fragment.append(item);
  });
  resultsList.append(fragment);
}

function selectResultsView(view) {
  if (!["institutions", "papers"].includes(view)) {
    return;
  }
  resultsView = view;
  clearPaperInteraction();
  resultsViewButtons.forEach((button) => {
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.resultsView === resultsView),
    );
  });
  renderResults(currentFilteredRecords, currentFilteredPaperRecords);
}

function baseMapStatusText(visibleRecords) {
  const recordLabel = datasetName === "preview"
    ? "public preview record"
    : datasetConfig.recordLabel;
  const interactionHint = supportsMarkerHover
    ? " Hover over a marker to preview paper details; click to pin."
    : " Tap a marker to pin paper details.";
  return visibleRecords.length
    ? `Showing ${visibleRecords.length} ${recordLabel}${visibleRecords.length === 1 ? "" : "s"}.${interactionHint}`
    : "No Records Match the Current Filters.";
}

function resetPaperDetails() {
  paperDetails.classList.remove("has-content");
  paperDetailsContent.innerHTML =
    '<p class="paper-details-placeholder">Select or Hover Over a Marker to View Paper Details.</p>';
  closePaperDetailsButton.disabled = true;
  closePaperDetailsButton.textContent = "Close";
  closePaperDetailsButton.setAttribute("aria-label", "Close Paper Details");
  paperDetailsPinStatus.hidden = true;
  paperDetails.classList.remove("is-pinned");
}

function showPaperDetails(record, relatedEntries, source) {
  paperDetailsContent.innerHTML = paperDetailsHtml(record, relatedEntries);
  paperDetails.classList.add("has-content");
  closePaperDetailsButton.disabled = false;
  const isPinned = source === "pinned";
  paperDetails.classList.toggle("is-pinned", isPinned);
  paperDetailsPinStatus.hidden = !isPinned;
  closePaperDetailsButton.textContent = isPinned ? "Unpin" : "Close";
  closePaperDetailsButton.setAttribute(
    "aria-label",
    isPinned ? "Unpin paper details" : "Close paper details",
  );
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
  interactionState.pinned = null;
  interactionState.hoveredMarkerId = null;
  interactionState.pinnedMarkerId = null;
  interactionState.detailsSource = null;
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  restoreBaseMarkerStyles();
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
    const isCurrent = markerRecords.includes(selection.record);
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

function setMarkerPinnedState(markerId) {
  visibleMarkerEntries.forEach((entry) => {
    const isPinned = entry.institutionKey === markerId;
    const element = entry.marker.getElement?.();
    element?.classList.toggle("is-paper-pinned", isPinned);
    element?.setAttribute("aria-pressed", String(isPinned));
    element?.setAttribute(
      "aria-label",
      `${isPinned ? "Unpin" : "Pin"} paper details for ${recordInstitution(entry.record) || "institution"}`,
    );
  });
}

function renderPaperSelection(selection, source) {
  const relatedEntries = selection ? relatedMarkerEntries(selection) : [];
  if (!relatedEntries.length) {
    resetPaperDetails();
    return;
  }
  showPaperDetails(selection.record, relatedEntries, source);
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
  const connectionText = lineCount ? " · Connections shown." : ".";
  mapStatus.textContent =
    `Previewing ${visibleCount} visible institution record${visibleCount === 1 ? "" : "s"}${connectionText}`;
}

function renderActiveSelection() {
  const detailSelection = interactionState.pinned || interactionState.hovered;
  const connectionSelection = interactionState.hovered || interactionState.pinned;
  interactionState.detailsSource = interactionState.pinned
    ? "pinned"
    : interactionState.hovered ? "hover" : null;
  setMarkerPinnedState(interactionState.pinnedMarkerId);
  if (detailSelection) {
    showPaperInteraction(detailSelection, connectionSelection);
    return;
  }

  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  restoreBaseMarkerStyles();
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
  if (marker && interactionState.hovered?.marker !== marker) {
    return;
  }
  interactionState.hovered = null;
  interactionState.hoveredMarkerId = null;
  renderActiveSelection();
}

function setPinnedSelection(selection) {
  interactionState.hovered = null;
  interactionState.hoveredMarkerId = null;
  interactionState.pinned = selection;
  interactionState.pinnedMarkerId = selection?.markerId || null;
  renderActiveSelection();
  scheduleMapResize();
}

function clearPinnedSelection() {
  interactionState.pinned = null;
  interactionState.pinnedMarkerId = null;
  renderActiveSelection();
  scheduleMapResize();
}

function activateHoverPreview(record, identity, markerId, marker, paperCount, taskBreakdown) {
  openInstitutionTooltip(marker, record, paperCount, taskBreakdown);
  setHoveredSelection({ identity, record, markerId, marker });
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

function pinPaper(record, identity, institutionKey) {
  closeActiveInstitutionTooltip();
  if (interactionState.pinnedMarkerId === institutionKey &&
      interactionState.pinned?.identity === identity) {
    clearPinnedSelection();
    return;
  }
  setPinnedSelection({ identity, record, markerId: institutionKey, institutionKey });
}

function renderRecords() {
  const previousPin = interactionState.pinned;
  closeActiveInstitutionTooltip();
  interactionState.hovered = null;
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  const normalizedKeyword = normalizedSearchText(keywordFilter.value);
  const institutionSearchIndex = buildInstitutionSearchIndex(
    records,
    paperRecords,
    institutionAliases,
    institutionHierarchy,
    canonicalInstitutionSearchIndex,
  );
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
  const hierarchyIndex = buildInstitutionHierarchyIndex(institutionHierarchy);
  const selectedIdentity = activeInstitutionFilter?.identity || resolvedInstitutionIdentity;
  const resolvedInstitutionIdentities = institutionIdentitiesWithDescendants(
    directlyResolvedInstitutionIdentities,
    hierarchyIndex,
  );
  const activeInstitutionIdentities = institutionIdentityWithDescendants(
    activeInstitutionFilter?.identity || "",
    hierarchyIndex,
  );
  const institutionLabel = activeInstitutionFilter?.label
    || hierarchyInstitutionLabel(selectedIdentity, institutionHierarchy)
    || keywordFilter.value.trim();
  displayedInstitutionFilter = selectedIdentity ? {
    identity: selectedIdentity,
    label: institutionLabel,
    source: activeInstitutionFilter ? "chip" : "keyword",
  } : null;
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

  const institutionRepresentatives = new Map();
  records.forEach((record) => {
    const key = institutionIdentity(record);
    if (!institutionRepresentatives.has(key)) {
      institutionRepresentatives.set(key, record);
    }
  });
  const institutionGroups = MarkerSizeHelpers.groupInstitutionRecords(
    visibleRecords,
    institutionIdentity,
    paperIdentity,
  );

  institutionGroups.forEach((group) => {
    const record = group.record;
    const locationRecord = institutionRepresentatives.get(group.key) || record;
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
      click: () => pinPaper(record, identity, group.key),
      hover: () => activateHoverPreview(
        record,
        identity,
        group.key,
        marker,
        group.paperCount,
        taskBreakdown,
      ),
      leave: (event) => clearHoverPreview(marker, event),
    });
    visibleMarkerEntries.push({
      record,
      records: group.records,
      marker,
      identity,
      institutionKey: group.key,
      paperCount: group.paperCount,
      taskBreakdown,
      taskCounts,
      taskKey,
    });
  });

  const restoredPinEntry = previousPin
    ? visibleMarkerEntries.find(
      (entry) => entry.institutionKey === previousPin.institutionKey,
    )
    : null;
  const restoredPinRecord = restoredPinEntry?.records.find(
    (record) => paperIdentity(record) === previousPin?.identity,
  );
  if (restoredPinEntry && restoredPinRecord) {
    interactionState.pinned = {
      identity: previousPin.identity,
      record: restoredPinRecord,
      markerId: previousPin.institutionKey,
      institutionKey: previousPin.institutionKey,
    };
    interactionState.pinnedMarkerId = previousPin.institutionKey;
  } else {
    interactionState.pinned = null;
    interactionState.pinnedMarkerId = null;
  }

  updateDatasetStatistics(visibleRecords, visiblePaperRecords);
  renderActiveInstitutionFilter();
  renderHeaderStatistics(visibleRecords, visiblePaperRecords);
  renderResults(visibleRecords, visiblePaperRecords);
  mapStatus.classList.toggle("error", false);
  if (interactionState.pinned) {
    renderActiveSelection();
  } else {
    resetPaperDetails();
    mapStatus.classList.toggle("paper-highlight-active", false);
    mapStatus.textContent = baseMapStatusText(visibleRecords);
  }
  scheduleMapResize();
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
}

function updateVenueDimensionFilters(venuePapers, venueTypePapers) {
  const metadataByVenue = new Map();
  [...venuePapers, ...venueTypePapers].forEach((record) => {
    metadataByVenue.set(venueFilterValue(record), {
      label: venueDisplayLabel(record),
      name: getRecordVenue(record) || "Unknown venue/source",
      acronym: record.venue_acronym || "",
      track: record.venue_track || "main",
      type: recordVenueType(record) || "__unknown__",
    });
  });
  const venueCounts = dimensionPaperCounts(venuePapers, (record) => [venueFilterValue(record)]);
  const venueTypeCounts = dimensionPaperCounts(
    venueTypePapers,
    (record) => [recordVenueType(record) || "__unknown__"],
  );
  replaceCountedFilterOptions(
    venueFilter,
    "All",
    sortedVenueCounts(venueCounts, metadataByVenue),
    (value) => metadataByVenue.get(value)?.label
      || (value === "__unknown__" ? "Unknown venue/source" : value),
    false,
  );
  replaceCountedFilterOptions(
    venueTypeFilter,
    "All",
    sortedVenueTypeCounts(venueTypeCounts),
    (value) => value === "__unknown__" ? "Unknown" : formatTask(value),
  );
}

function enableControls() {
  keywordFilter.disabled = false;
  taskFilter.disabled = false;
  entryTypeFilter.disabled = false;
  sortControl.disabled = false;
  venueFilter.disabled = false;
  venueTypeFilter.disabled = false;
  countryFilter.disabled = false;
  countryComboboxButton.disabled = false;
  institutionTypeFilter.disabled = false;
  preprintFilter.disabled = false;
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

function showDatasetMessage(message, isError = false) {
  clearPaperInteraction(false);
  records = [];
  paperRecords = [];
  configureYearRange();
  currentFilteredRecords = [];
  currentFilteredPaperRecords = [];
  currentDisplayedResults = [];
  closeActiveInstitutionTooltip();
  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];
  interactionState.hovered = null;
  updateDatasetStatistics(records, paperRecords);
  renderHeaderStatistics(records, paperRecords);
  renderResults(records, paperRecords);
  mapStatus.textContent = message;
  mapStatus.classList.toggle("error", isError);
}

function updateDatasetLabels() {
  if (datasetName === "sample") {
    datasetStatusNote.textContent =
      "Fictional Sample";
    datasetNoticeCopy.textContent =
      "These fictional records are provided only for interface testing and are not literature data.";
    mapStatus.textContent = "Loading fictional sample data...";
    datasetStatisticsNote.textContent =
      "Institution-level records matching the current filters.";
  } else if (datasetName === "preview") {
    datasetStatusNote.textContent =
      "Uncurated Public Preview";
    datasetNoticeCopy.textContent =
      "This public preview is generated from OpenAlex candidate metadata and local manual review caches. It includes paper-level coverage even when institution/location data is incomplete; only papers with valid reviewed coordinates appear as map markers.";
    mapStatus.textContent = "Loading public preview data...";
    datasetStatisticsNote.textContent =
      "Institution-level records matching the current filters.";
  } else {
    datasetStatusNote.textContent =
      "Uncurated Candidate Data";
    datasetNoticeCopy.textContent =
      "This local view contains automatically extracted OpenAlex candidate metadata for exploratory review. Paper relevance, task labels, institution names, and coordinates may contain errors.";
    mapStatus.textContent = "Loading local OpenAlex candidate data...";
    datasetStatisticsNote.textContent =
      "Institution-level records matching the current filters.";
  }
  renderDatasetSwitcher();
}

function renderDatasetSwitcher() {
  let switcher = document.querySelector(".dataset-switcher");
  if (!switcher) {
    return;
  }

  const choices = [
    ["preview", "Public Preview"],
    ["sample", "Fictional Sample"],
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
    };
  }
  throw new Error(`${datasetName} data does not contain a records array`);
}

function displayMetadataWarning(metadata) {
  const warning =
    typeof metadata.warning === "string" ? metadata.warning.trim() : "";
  const repeatsDatasetNotice =
    /automatically generated candidate metadata/i.test(warning) ||
    /not a manually curated bibliography/i.test(warning);
  if (warning && !repeatsDatasetNotice) {
    datasetNoticeCopy.textContent = `${datasetNoticeCopy.textContent} ${warning}`;
  }
}

function formatPublicPreviewDate(value) {
  if (typeof value !== "string" || !value.trim()) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

function displayPublicPreviewDate(metadata) {
  const element = document.querySelector("#data-updated");
  if (!element) return;
  const formattedDate = formatPublicPreviewDate(metadata.public_preview_generated_at);
  element.hidden = !formattedDate;
  element.textContent = formattedDate ? `Data updated: ${formattedDate}` : "";
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
  institutionAliases = normalizedData.institutionAliases || [];
  institutionHierarchy = normalizedData.institutionHierarchy || [];
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
  displayMetadataWarning(normalizedData.metadata);
  displayPublicPreviewDate(normalizedData.metadata);
  if (normalizedData.paperMetadata) {
    displayMetadataWarning(normalizedData.paperMetadata);
  }
  configureYearRange();
  configureVenueFilter();
  enableControls();
  renderRecords();
  scheduleMapResize(true);
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
entryTypeFilter.addEventListener("change", renderRecords);
sortControl.addEventListener("change", renderRecords);
venueFilter.addEventListener("change", renderRecords);
venueTypeFilter.addEventListener("change", renderRecords);
countryFilter.addEventListener("change", renderRecords);
countryComboboxButton.addEventListener("click", () => {
  if (countryComboboxPanel.hidden) openCountryCombobox();
  else closeCountryCombobox(true);
});
countryComboboxButton.addEventListener("keydown", (event) => {
  if (["ArrowDown", "ArrowUp"].includes(event.key)) {
    event.preventDefault();
    if (countryComboboxPanel.hidden) openCountryCombobox();
    moveActiveCountryOption(event.key === "ArrowDown" ? 1 : -1);
  } else if (["Enter", " "].includes(event.key)) {
    event.preventDefault();
    if (countryComboboxPanel.hidden) {
      openCountryCombobox();
    } else {
      const option = countryComboboxOptionData[activeCountryOptionIndex];
      if (option && visibleCountryOptionIndices().includes(activeCountryOptionIndex)) {
        selectCountryComboboxValue(option.value);
      }
    }
  } else if (event.key === "Escape") {
    event.preventDefault();
    closeCountryCombobox(true);
  }
});
countryComboboxOptions.addEventListener("mousemove", (event) => {
  const option = event.target.closest("[data-country-option-index]");
  if (option && !option.hidden) {
    setActiveCountryOption(Number(option.dataset.countryOptionIndex));
  }
});
countryComboboxOptions.addEventListener("click", (event) => {
  const option = event.target.closest("[data-country-value]");
  if (option && !option.hidden) selectCountryComboboxValue(option.dataset.countryValue);
});
document.addEventListener("pointerdown", (event) => {
  if (!countryComboboxPanel.hidden && !countryCombobox.contains(event.target)) {
    closeCountryCombobox();
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !countryComboboxPanel.hidden) {
    event.preventDefault();
    closeCountryCombobox(true);
  }
});
window.addEventListener("resize", positionCountryComboboxPanel);
window.addEventListener("scroll", positionCountryComboboxPanel, true);
institutionTypeFilter.addEventListener("change", renderRecords);
preprintFilter.addEventListener("change", renderRecords);
minYearFilter.addEventListener("input", () => handleYearRangeInput("start"));
maxYearFilter.addEventListener("input", () => handleYearRangeInput("end"));
minYearFilter.addEventListener("keydown", (event) => {
  handleYearRangeKeydown(event, "start");
});
maxYearFilter.addEventListener("keydown", (event) => {
  handleYearRangeKeydown(event, "end");
});
[resultsList, paperDetails].forEach((container) => {
  container.addEventListener("click", (event) => {
    const button = event.target.closest("[data-institution-filter]");
    if (button) {
      applyInstitutionFilter(button.dataset.institutionFilter, button.dataset.institutionLabel);
    }
  });
});
activeInstitutionFilterChip.addEventListener("click", (event) => {
  if (event.target.closest("[data-clear-institution-filter]")) {
    clearInstitutionFilter();
  }
});
window.addEventListener("resize", () => scheduleMapResize());
exportCsvButton.addEventListener("click", downloadFilteredCsv);
closePaperDetailsButton.addEventListener("click", () => {
  if (interactionState.pinned) {
    clearPinnedSelection();
  } else {
    clearHoveredSelection();
  }
});
paperDetails.addEventListener("pointerenter", () => {
  interactionState.isPointerInsideDetails = true;
});
paperDetails.addEventListener("pointerleave", () => {
  interactionState.isPointerInsideDetails = false;
  if (!interactionState.pinned && !interactionState.hoveredMarkerId) {
    clearHoveredSelection();
  }
});
resultsViewButtons.forEach((button) => {
  button.addEventListener("click", () => selectResultsView(button.dataset.resultsView));
});
resetButton.addEventListener("click", () => {
  keywordFilter.value = "";
  taskFilter.value = "all";
  entryTypeFilter.value = "all";
  sortControl.value = "year-desc";
  venueFilter.value = "all";
  venueTypeFilter.value = "all";
  countryFilter.value = "all";
  institutionTypeFilter.value = "all";
  preprintFilter.value = "all";
  if (yearRangeBounds) {
    minYearFilter.value = String(yearRangeBounds.minimum);
    maxYearFilter.value = String(yearRangeBounds.maximum);
    syncYearRange();
  }
  activeInstitutionFilter = null;
  displayedInstitutionFilter = null;
  renderRecords();
  scheduleMapResize(true);
});

updateDatasetLabels();
loadData();
