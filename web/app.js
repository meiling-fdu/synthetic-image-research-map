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
const WORLD_BOUNDS = L.latLngBounds(L.latLng(-60, -180), L.latLng(85, 180));
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

const map = L.map("map", {
  minZoom: 1,
  maxBounds: WORLD_BOUNDS.pad(0.35),
  worldCopyJump: true,
}).fitBounds(WORLD_BOUNDS, { padding: [12, 12], animate: false });

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);
const hoverConnectionLayer = L.layerGroup().addTo(map);
const selectedConnectionLayer = L.layerGroup().addTo(map);
const keywordFilter = document.querySelector("#keyword-filter");
const taskFilter = document.querySelector("#task-filter");
const entryTypeFilter = document.querySelector("#entry-type-filter");
const sortControl = document.querySelector("#sort-control");
const venueFilter = document.querySelector("#venue-filter");
const preprintFilter = document.querySelector("#preprint-filter");
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
const resultsViewButtons = document.querySelectorAll("[data-results-view]");
const paperDetails = document.querySelector("#paper-details");
const paperDetailsContent = document.querySelector("#paper-details-content");
const closePaperDetailsButton = document.querySelector("#close-paper-details");
const prototypeNote = document.querySelector(".prototype-note");
const intro = document.querySelector(".intro");
const footer = document.querySelector("footer");

let records = [];
let currentFilteredRecords = [];
let currentDisplayedResults = [];
let resultsView = "institutions";
let visibleMarkerEntries = [];
let hoveredPaperIdentity = "";
let hoveredPaperRecord = null;
let hoveredMarker = null;
let pinnedPaperIdentity = "";
let pinnedPaperRecord = null;

const supportsMarkerHover = window.matchMedia?.(
  "(hover: hover) and (pointer: fine)",
).matches ?? false;

const BASE_MARKER_STYLE = {
  radius: 8,
  color: "#ffffff",
  weight: 2,
  fillOpacity: 0.94,
  opacity: 1,
};
const DIMMED_MARKER_STYLE = {
  radius: 7.5,
  color: "#d7e0e4",
  weight: 1.25,
  fillOpacity: 0.55,
  opacity: 0.68,
};
const RELATED_MARKER_STYLE = {
  radius: 9.5,
  color: "#263744",
  weight: 2.5,
  fillOpacity: 1,
  opacity: 1,
};
const CURRENT_MARKER_STYLE = {
  radius: 11.5,
  color: "#c83f35",
  weight: 3.5,
  fillOpacity: 1,
  opacity: 1,
};
const CONNECTION_LINE_STYLE = {
  color: "#455d6c",
  weight: 2,
  opacity: 0.5,
  interactive: false,
  dashArray: "6 5",
  lineCap: "round",
  className: "paper-connection-line",
};
let mapResizeTimer = null;

function scheduleMapResize(fitWorld = false) {
  window.clearTimeout(mapResizeTimer);
  mapResizeTimer = window.setTimeout(() => {
    map.invalidateSize({ animate: false, pan: false });
    if (fitWorld) {
      map.fitBounds(WORLD_BOUNDS, { padding: [12, 12], animate: false });
    }
  }, 0);
}

const INSTITUTION_CSV_COLUMNS = [
  ["title", (record) => recordTitle(record)],
  ["authors", (record) => recordAuthors(record).join("; ")],
  ["institution_authors", (record) => recordInstitutionAuthors(record).join("; ")],
  ["publication_year", (record) => publicationYear(record) ?? ""],
  ["venue_name", (record) => getRecordVenue(record)],
  ["entry_type", (record) => getEntryType(record)],
  ["task", (record) => record.task || ""],
  ["subtask", (record) => record.subtask || ""],
  ["institution_name", (record) => recordInstitution(record)],
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
  ["venue_name", (record) => getRecordVenue(record)],
  ["entry_type", (record) => getEntryType(record)],
  ["task", (record) => record.task || ""],
  ["subtask", (record) => record.subtask || ""],
  ["institutions", (record) => record.aggregated_institutions.join("; ")],
  ["countries", (record) => record.aggregated_country_names.join("; ")],
  ["country_codes", (record) => record.aggregated_country_codes.join("; ")],
  ["regions", (record) => record.aggregated_regions.join("; ")],
  ["region_codes", (record) => record.aggregated_region_codes.join("; ")],
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
  const authors = Array.isArray(record.authors) ? record.authors : [record.authors];
  return authors
    .map((author) => String(author || "").trim())
    .filter(Boolean);
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
  return String(value || "")
    .normalize("NFKC")
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function highlightedPaperAuthors(record) {
  const institutionAuthorCounts = new Map();
  recordInstitutionAuthors(record).forEach((author) => {
    const key = normalizedAuthorName(author);
    institutionAuthorCounts.set(key, (institutionAuthorCounts.get(key) || 0) + 1);
  });

  return recordAuthors(record).map((author) => {
    const key = normalizedAuthorName(author);
    const remaining = institutionAuthorCounts.get(key) || 0;
    if (remaining > 0) {
      institutionAuthorCounts.set(key, remaining - 1);
      return `<strong class="institution-author-highlight">${escapeHtml(author)}</strong>`;
    }
    return escapeHtml(author);
  }).join(", ");
}

function affiliationIdentity(record) {
  return [recordInstitution(record), recordLocation(record)]
    .map((value) => String(value || "").normalize("NFKC").toLocaleLowerCase().trim())
    .join("|");
}

function visiblePaperAffiliations(currentRecord, relatedEntries) {
  const currentIdentity = affiliationIdentity(currentRecord);
  const affiliationsByIdentity = new Map();
  relatedEntries.forEach(({ record }) => {
    const identity = affiliationIdentity(record);
    let affiliation = affiliationsByIdentity.get(identity);
    if (!affiliation) {
      affiliation = {
        institution: recordInstitution(record) || "Unknown institution",
        location: recordLocation(record),
        authors: [],
        authorKeys: new Set(),
        isCurrent: identity === currentIdentity,
      };
      affiliationsByIdentity.set(identity, affiliation);
    } else if (identity === currentIdentity) {
      affiliation.isCurrent = true;
    }
    recordInstitutionAuthors(record).forEach((author) => {
      const authorKey = normalizedAuthorName(author);
      if (authorKey && !affiliation.authorKeys.has(authorKey)) {
        affiliation.authorKeys.add(authorKey);
        affiliation.authors.push(author);
      }
    });
  });
  return [...affiliationsByIdentity.values()].map((affiliation, index) => ({
    ...affiliation,
    number: index + 1,
  }));
}

function paperAuthorsWithAffiliations(record, affiliations) {
  const affiliationNumbersByAuthor = new Map();
  affiliations.forEach((affiliation) => {
    affiliation.authors.forEach((author) => {
      const authorKey = normalizedAuthorName(author);
      if (!authorKey) {
        return;
      }
      const numbers = affiliationNumbersByAuthor.get(authorKey) || [];
      if (!numbers.includes(affiliation.number)) {
        numbers.push(affiliation.number);
      }
      affiliationNumbersByAuthor.set(authorKey, numbers);
    });
  });

  return recordAuthors(record).map((author) => {
    const numbers = affiliationNumbersByAuthor.get(normalizedAuthorName(author)) || [];
    const superscript = numbers.length
      ? `<sup class="author-affiliation-numbers" aria-label="Affiliations ${numbers.join(", ")}">${numbers.join(",")}</sup>`
      : "";
    return `${escapeHtml(author)}${superscript}`;
  }).join(", ");
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

function markerStyle(record, state = "base") {
  const fillColor = TASK_COLORS[record.task] ?? TASK_COLORS.uncertain;
  if (state === "current") {
    return { ...CURRENT_MARKER_STYLE, fillColor };
  }
  if (state === "related") {
    return { ...RELATED_MARKER_STYLE, fillColor };
  }
  if (state === "dimmed") {
    return { ...DIMMED_MARKER_STYLE, fillColor };
  }
  return { ...BASE_MARKER_STYLE, fillColor };
}

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

  return {
    ...record,
    country: country || countryCode,
    country_code: countryCode,
    region,
    region_code: regionCode,
    raw_country: rawCountry,
    raw_country_code: rawCountryCode,
  };
}

function recordLocation(record) {
  return uniqueTextValues([record.city, record.region, record.country]).join(", ");
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
  const venue = getRecordVenue(record);
  return venue ? venue.toLocaleLowerCase() : "__unknown__";
}

function venueDisplayLabel(record) {
  return getRecordVenue(record) || "Unknown venue/source";
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

  return compareTextValues(recordTitle(first), recordTitle(second));
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
        aggregated_countries: [],
        aggregated_country_names: [],
        aggregated_country_codes: [],
        aggregated_regions: [],
        aggregated_region_codes: [],
      };
      papersByIdentity.set(identity, paper);
    }

    paper.aggregated_institutions = uniqueTextValues([
      ...paper.aggregated_institutions,
      recordInstitution(record),
    ]);
    paper.aggregated_countries = uniqueTextValues([
      ...paper.aggregated_countries,
      recordCountry(record),
    ]);
    paper.aggregated_country_names = uniqueTextValues([
      ...paper.aggregated_country_names,
      record.country,
    ]);
    paper.aggregated_country_codes = uniqueTextValues([
      ...paper.aggregated_country_codes,
      record.country_code,
    ]);
    paper.aggregated_regions = uniqueTextValues([
      ...paper.aggregated_regions,
      record.region,
    ]);
    paper.aggregated_region_codes = uniqueTextValues([
      ...paper.aggregated_region_codes,
      record.region_code,
    ]);
  });
  return [...papersByIdentity.values()];
}

function publicationYear(record) {
  return getRecordYear(record);
}

function normalizedSearchText(value) {
  return String(value || "").normalize("NFKC").toLocaleLowerCase();
}

function recordSearchText(record) {
  const authors = recordAuthors(record);
  return normalizedSearchText([
    recordTitle(record),
    ...authors,
    record.institution_name,
    record.institution,
    record.country,
    record.country_code,
    record.region,
    record.region_code,
    record.venue_name,
    record.venue,
    record.task,
    record.subtask,
    getEntryTypeLabel(getEntryType(record)),
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
    record.doi,
    record.doi_url,
    record.paper_url,
    record.primary_url,
    record.landing_page_url,
    record.url,
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
    ? datasetRecords.filter(isPreprintOnlyRecord).length
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
  const orderedAuthors = recordAuthors(record);
  const affiliations = visiblePaperAffiliations(record, relatedEntries);
  const authors = orderedAuthors.length
    ? affiliations.length
      ? paperAuthorsWithAffiliations(record, affiliations)
      : highlightedPaperAuthors(record)
    : "Unknown";
  const institutionAuthors = recordInstitutionAuthors(record);
  const institutionAuthorsRow = !affiliations.length && institutionAuthors.length
    ? `<dt>Institution authors</dt><dd>${institutionAuthors.map(escapeHtml).join(", ")}</dd>`
    : "";
  const currentAffiliation = affiliations.find((affiliation) => affiliation.isCurrent);
  const currentAffiliationNumber = currentAffiliation
    ? `<sup class="current-affiliation-number" aria-label="Affiliation ${currentAffiliation.number}">${currentAffiliation.number}</sup>`
    : "";
  const year = record.publication_year ?? record.year ?? "Unknown";
  const venue = getRecordVenue(record) || "unknown";
  const publicationType = record.publication_type || "Unknown";
  const entryType = getEntryType(record);
  const entryTypeLabel = getEntryTypeLabel(entryType);
  const location = recordLocation(record) || "Unknown";
  const subtaskRow = record.subtask
    ? `<dt>Subtask</dt><dd>${escapeHtml(formatTask(record.subtask))}</dd>`
    : "";
  const doi = normalizedDoi(record.doi);
  const doiRow = doi
    ? `<dt>DOI</dt><dd>${externalLink(`https://doi.org/${doi}`, doi)}</dd>`
    : "";
  const arxivId = recordArxivId(record);
  const arxivUrl = recordArxivUrl(record);
  const arxivRow = arxivUrl
    ? `<dt>arXiv</dt><dd>${externalLink(arxivUrl, arxivId || "View arXiv version")}</dd>`
    : "";
  const paperUrl = recordPaperUrl(record);
  const safePaperUrl = safeHttpUrl(paperUrl);
  const openalexUrl = safeHttpUrl(record.openalex_url);
  const paperUrlRow = safePaperUrl && safePaperUrl !== openalexUrl
    ? `<dt>Paper</dt><dd>${externalLink(paperUrl, "Open paper")}</dd>`
    : "";
  const openalexRow = openalexUrl
    ? `<dt>OpenAlex</dt><dd>${externalLink(openalexUrl, "Open record")}</dd>`
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
  const affiliationsRow = affiliations.length
    ? `<dt>Affiliations</dt><dd><ol class="paper-details-affiliations">${affiliations.map((affiliation) => `<li${affiliation.isCurrent ? ' class="is-current"' : ""}><div class="affiliation-heading"><span class="affiliation-institution">${escapeHtml(affiliation.institution)}</span>${affiliation.location ? `<span class="affiliation-location"> · ${escapeHtml(affiliation.location)}</span>` : ""}</div>${affiliation.authors.length ? `<div class="affiliation-authors">${affiliation.authors.map(escapeHtml).join("; ")}</div>` : ""}</li>`).join("")}</ol></dd>`
    : "";

  return `
    <div class="popup-badges">
      <span class="popup-badge popup-task">${escapeHtml(formatTask(record.task))}</span>
      <span class="popup-badge entry-type-badge">${escapeHtml(entryTypeLabel)}</span>
      ${versionBadge}
      ${confidenceBadge}
      ${reviewBadge}
    </div>
    <h3 class="popup-title">${escapeHtml(recordTitle(record))}</h3>
    <dl class="popup-details">
      <dt>Authors</dt><dd>${authors}</dd>
      ${institutionAuthorsRow}
      <dt class="current-institution-label">Current institution</dt><dd class="current-institution-value">${currentAffiliationNumber}${escapeHtml(recordInstitution(record) || "Unknown")}</dd>
      <dt>Location</dt><dd>${escapeHtml(location)}</dd>
      ${affiliationsRow}
      <dt>Year</dt><dd>${escapeHtml(year)}</dd>
      <dt>Venue</dt><dd>${escapeHtml(venue)}</dd>
      <dt>Publication type</dt><dd>${escapeHtml(formatTask(publicationType))}</dd>
      <dt>Entry type</dt><dd>${escapeHtml(entryTypeLabel)}</dd>
      ${doiRow}
      ${arxivRow}
      ${paperUrlRow}
      ${openalexRow}
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
  const venue = getRecordVenue(record);
  const isPaperView = resultsView === "papers";
  const entryTypeLabel = getEntryTypeLabel(getEntryType(record));
  const institution = recordInstitution(record) || "Unknown institution";
  const location = recordLocation(record);
  const affiliation = [institution, location].filter(Boolean).join(" · ");
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
  const arxivUrl = recordArxivUrl(record);
  const arxivLink = arxivUrl ? externalLink(arxivUrl, "arXiv") : "";
  const paperUrl = recordPaperUrl(record);
  const paperLabel = paperUrl && paperUrl === record.openalex_url
    ? "OpenAlex"
    : "Paper";
  const paperLink = paperUrl ? externalLink(paperUrl, paperLabel) : "";
  const links = [doiLink, arxivLink, paperLink].filter(Boolean).join("");
  const linksRow = links ? `<div class="result-links">${links}</div>` : "";
  const authorsRow = isPaperView
    ? `<p class="result-aggregate"><strong>Authors:</strong> ${escapeHtml(recordAuthors(record).join("; ") || "Unknown")}</p>`
    : "";
  const institutionAuthors = recordInstitutionAuthors(record);
  const institutionAuthorsRow = !isPaperView && institutionAuthors.length
    ? `<p class="result-aggregate"><strong>Institution authors:</strong> ${escapeHtml(institutionAuthors.join("; "))}</p>`
    : "";
  const institutionsRow = isPaperView
    ? `<p class="result-aggregate"><strong>Institutions:</strong> ${escapeHtml(record.aggregated_institutions.join("; ") || "Unknown")}</p>`
    : `<p class="result-affiliation">${escapeHtml(affiliation)}</p>`;
  const countriesRow = isPaperView
    ? `<p class="result-aggregate"><strong>Countries:</strong> ${escapeHtml(record.aggregated_country_names.join(", ") || record.aggregated_country_codes.join(", ") || "Unknown")}</p>`
    : "";
  const regionsRow = isPaperView && record.aggregated_regions.length
    ? `<p class="result-aggregate"><strong>Regions:</strong> ${escapeHtml(record.aggregated_regions.join(", "))}</p>`
    : "";

  return `
    <article>
      <div class="result-title-row">
        <h3 class="result-title">${escapeHtml(title)}</h3>
        <span class="result-year">${escapeHtml(year)}</span>
      </div>
      ${venueRow}
      ${authorsRow}
      ${institutionAuthorsRow}
      ${institutionsRow}
      ${countriesRow}
      ${regionsRow}
      <div class="result-classification">
        <span class="result-task">${escapeHtml(formatTask(record.task))}</span>
        <span class="result-task entry-type-badge">${escapeHtml(entryTypeLabel)}</span>
        ${subtask}
      </div>
      ${linksRow}
    </article>
  `;
}

function renderResults(visibleRecords) {
  const displayedResults = resultsView === "papers"
    ? aggregateUniquePapers(visibleRecords)
    : visibleRecords;
  currentDisplayedResults = displayedResults;
  const count = displayedResults.length;
  resultsCount.textContent = resultsView === "papers"
    ? `Showing ${count} unique paper${count === 1 ? "" : "s"}`
    : `Showing ${count} record${count === 1 ? "" : "s"}`;
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
    item.innerHTML = resultContent(record);
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
  renderResults(currentFilteredRecords);
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

function baseMapStatusText(visibleRecords) {
  const recordLabel = datasetConfig.recordLabel;
  const interactionHint = supportsMarkerHover
    ? " Hover over a marker to preview paper details; click to pin them."
    : " Tap a marker to pin paper details.";
  return visibleRecords.length
    ? `Showing ${visibleRecords.length} ${recordLabel}${visibleRecords.length === 1 ? "" : "s"}.${interactionHint}`
    : "No records match the current filters.";
}

function resetPaperDetails() {
  paperDetails.classList.remove("has-content");
  paperDetailsContent.innerHTML =
    '<p class="paper-details-placeholder">Select or hover over a marker to view paper details.</p>';
  closePaperDetailsButton.disabled = true;
}

function showPaperDetails(record, relatedEntries) {
  paperDetailsContent.innerHTML = paperDetailsHtml(record, relatedEntries);
  paperDetails.classList.add("has-content");
  closePaperDetailsButton.disabled = false;
  paperDetails.scrollTop = 0;
}

function restoreBaseMarkerStyles() {
  visibleMarkerEntries.forEach(({ marker, record }) => {
    marker.setStyle(markerStyle(record));
  });
}

function clearPaperInteraction(updateStatus = true) {
  hoveredPaperIdentity = "";
  hoveredPaperRecord = null;
  hoveredMarker = null;
  pinnedPaperIdentity = "";
  pinnedPaperRecord = null;
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

function showPaperInteraction(record, identity, mode) {
  const relatedEntries = visibleMarkerEntries.filter(
    (entry) => entry.identity === identity,
  );
  if (!relatedEntries.length) {
    return;
  }

  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  let currentMarker = null;
  visibleMarkerEntries.forEach(({ marker, record: markerRecord, identity: markerIdentity }) => {
    const isCurrent = markerRecord === record;
    if (isCurrent) {
      currentMarker = marker;
    }
    marker.setStyle(markerStyle(
      markerRecord,
      isCurrent ? "current" : markerIdentity === identity ? "related" : "dimmed",
    ));
  });

  const isHover = mode === "hover";
  const targetLayer = isHover ? hoverConnectionLayer : selectedConnectionLayer;
  const lineCount = drawConnectionLines(relatedEntries, record, targetLayer);
  relatedEntries.forEach(({ marker }) => marker.bringToFront());
  currentMarker?.bringToFront();
  showPaperDetails(record, relatedEntries);
  const paperTitle = recordTitle(record) || "Selected paper";
  mapStatus.classList.toggle("error", false);
  mapStatus.classList.toggle("paper-highlight-active", true);
  const action = mode === "pinned" ? "Pinned" : "Previewing";
  const visibleCount = relatedEntries.length;
  const connectionText = lineCount ? " Connections shown." : "";
  mapStatus.textContent =
    `${action} ${visibleCount} visible institution record${visibleCount === 1 ? "" : "s"} for “${paperTitle}”.${connectionText}`;
}

function restorePaperInteraction() {
  if (hoveredPaperIdentity && hoveredPaperRecord) {
    showPaperInteraction(hoveredPaperRecord, hoveredPaperIdentity, "hover");
    return;
  }
  if (pinnedPaperIdentity && pinnedPaperRecord) {
    showPaperInteraction(pinnedPaperRecord, pinnedPaperIdentity, "pinned");
    return;
  }

  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  restoreBaseMarkerStyles();
  resetPaperDetails();
  mapStatus.classList.toggle("paper-highlight-active", false);
  mapStatus.textContent = baseMapStatusText(currentFilteredRecords);
}

function activateHoverPreview(record, identity, marker) {
  hoveredPaperIdentity = identity;
  hoveredPaperRecord = record;
  hoveredMarker = marker;
  restorePaperInteraction();
}

function clearHoverPreview(marker) {
  if (hoveredMarker !== marker) {
    return;
  }
  hoveredPaperIdentity = "";
  hoveredPaperRecord = null;
  hoveredMarker = null;
  restorePaperInteraction();
}

function pinPaper(record, identity) {
  hoveredPaperIdentity = "";
  hoveredPaperRecord = null;
  hoveredMarker = null;
  pinnedPaperIdentity = identity;
  pinnedPaperRecord = record;
  restorePaperInteraction();
  scheduleMapResize();
}

function renderRecords() {
  clearPaperInteraction(false);
  const keywordTerms = normalizedSearchText(keywordFilter.value)
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  const selectedTask = taskFilter.value;
  const selectedEntryType = entryTypeFilter.value;
  const selectedVenue = venueFilter.value;
  const selectedVersion = preprintFilter.value;
  const minimumYear = yearFilterValue(minYearFilter);
  const maximumYear = yearFilterValue(maxYearFilter);
  const selectedResolution = resolutionFilter.value;
  const selectedReview = reviewFilter.value;
  const visibleRecords = records.filter((record) => {
    const searchableText = recordSearchText(record);
    const matchesKeyword = keywordTerms.every((term) => searchableText.includes(term));
    const matchesTask = selectedTask === "all" || record.task === selectedTask;
    const matchesEntryType =
      selectedEntryType === "all" || getEntryType(record) === selectedEntryType;
    const matchesVenue =
      selectedVenue === "all" || venueFilterValue(record) === selectedVenue;
    const matchesVersion =
      selectedVersion === "all" ||
      (selectedVersion === "preprint-only" && isPreprintOnlyRecord(record)) ||
      (selectedVersion === "published" && hasPublishedVenue(record)) ||
      (selectedVersion === "has-arxiv" && hasArxivVersion(record)) ||
      (selectedVersion === "no-arxiv" && !hasArxivVersion(record));
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
      matchesEntryType &&
      matchesVenue &&
      matchesVersion &&
      matchesMinimumYear &&
      matchesMaximumYear &&
      matchesResolution &&
      matchesReview
    );
  }).sort((first, second) => compareRecordsForSort(first, second, sortControl.value));

  currentFilteredRecords = visibleRecords;

  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];

  visibleRecords.forEach((record) => {
    const identity = paperIdentity(record);
    const marker = L.circleMarker(
      [record.latitude, record.longitude],
      markerStyle(record),
    )
      .on("click", () => pinPaper(record, identity))
      .addTo(markerLayer);
    if (supportsMarkerHover) {
      marker
        .on("mouseover", () => activateHoverPreview(record, identity, marker))
        .on("mouseout", () => clearHoverPreview(marker));
    }
    visibleMarkerEntries.push({ record, marker, identity });
  });

  updateSummary(visibleRecords);
  updateDatasetStatistics(visibleRecords);
  renderResults(visibleRecords);
  mapStatus.classList.toggle("error", false);
  mapStatus.classList.toggle("paper-highlight-active", false);
  mapStatus.textContent = baseMapStatusText(visibleRecords);
  scheduleMapResize();
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

function configureVenueFilter() {
  const venuesByValue = new Map();
  let hasUnknownVenue = false;
  records.forEach((record) => {
    const value = venueFilterValue(record);
    if (value === "__unknown__") {
      hasUnknownVenue = true;
      return;
    }
    if (!venuesByValue.has(value)) {
      venuesByValue.set(value, venueDisplayLabel(record));
    }
  });

  const options = [["all", "All venues/sources"]];
  [...venuesByValue.entries()]
    .sort((first, second) => compareTextValues(first[1], second[1]))
    .forEach(([value, label]) => options.push([value, label]));
  if (hasUnknownVenue) {
    options.push(["__unknown__", "Unknown venue/source"]);
  }

  venueFilter.replaceChildren();
  options.forEach(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    venueFilter.append(option);
  });
  venueFilter.value = "all";
}

function enableControls() {
  keywordFilter.disabled = false;
  taskFilter.disabled = false;
  entryTypeFilter.disabled = false;
  sortControl.disabled = false;
  venueFilter.disabled = false;
  preprintFilter.disabled = false;
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
  clearPaperInteraction(false);
  records = [];
  currentFilteredRecords = [];
  currentDisplayedResults = [];
  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];
  hoveredPaperIdentity = "";
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
  normalizedData.records = normalizedData.records.map(normalizeCountryRegionRecord);
  if (!normalizedData.records.every(validateRecord)) {
    throw new Error(`${name} data does not match the expected format`);
  }
  return normalizedData;
}

function displayDataset(normalizedData) {
  records = normalizedData.records;
  displayMetadataWarning(normalizedData.metadata);
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
preprintFilter.addEventListener("change", renderRecords);
minYearFilter.addEventListener("input", renderRecords);
maxYearFilter.addEventListener("input", renderRecords);
resolutionFilter.addEventListener("change", renderRecords);
reviewFilter.addEventListener("change", renderRecords);
window.addEventListener("resize", () => scheduleMapResize());
exportCsvButton.addEventListener("click", downloadFilteredCsv);
closePaperDetailsButton.addEventListener("click", () => clearPaperInteraction());
resultsViewButtons.forEach((button) => {
  button.addEventListener("click", () => selectResultsView(button.dataset.resultsView));
});
resetButton.addEventListener("click", () => {
  keywordFilter.value = "";
  taskFilter.value = "all";
  entryTypeFilter.value = "all";
  sortControl.value = "year-desc";
  venueFilter.value = "all";
  preprintFilter.value = "all";
  minYearFilter.value = "";
  maxYearFilter.value = "";
  resolutionFilter.value = "all";
  reviewFilter.value = "all";
  renderRecords();
  scheduleMapResize(true);
});

updateDatasetLabels();
loadData();
