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
const keywordFilter = document.querySelector("#keyword-filter");
const taskFilter = document.querySelector("#task-filter");
const entryTypeFilter = document.querySelector("#entry-type-filter");
const sortControl = document.querySelector("#sort-control");
const venueFilter = document.querySelector("#venue-filter");
const preprintFilter = document.querySelector("#preprint-filter");
const minYearFilter = document.querySelector("#min-year-filter");
const maxYearFilter = document.querySelector("#max-year-filter");
const resetButton = document.querySelector("#reset-filters");
const mapStatus = document.querySelector("#map-status");
const datasetRecordCount = document.querySelector("#dataset-record-count");
const datasetPaperCount = document.querySelector("#dataset-paper-count");
const datasetPaperWithoutLocationCount = document.querySelector("#dataset-paper-without-location-count");
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
const datasetStatusNote = document.querySelector("#dataset-status-note");
const datasetNoticeCopy = document.querySelector("#dataset-notice-copy");

let records = [];
let paperRecords = [];
let currentFilteredRecords = [];
let currentFilteredPaperRecords = [];
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
  ["institutions", (record) => (record.aggregated_institutions || []).join("; ")],
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
  const authors = Array.isArray(record.authors) ? record.authors : [record.authors];
  const names = authors
    .map((author) => String(
      author && typeof author === "object"
        ? author.name || author.author || ""
        : author || "",
    ).trim())
    .filter(Boolean);
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
    const raw = typeof rawAffiliation === "string"
      ? { name: rawAffiliation }
      : rawAffiliation || {};
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
        country: String(raw.country || "").trim(),
        region: String(raw.region || "").trim(),
        location: uniqueTextValues([
          raw.city,
          raw.region,
          raw.country,
        ]).join(", "),
        authors: [],
        authorKeys: new Set(),
        isCurrent: false,
      };
      affiliationsByIdentity.set(identity, affiliation);
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
    const name = String(raw.name || raw.author || rawAuthor || "").trim();
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

function compactAffiliationsHtml(affiliations, limit = 3) {
  const visibleAffiliations = affiliations.slice(0, limit);
  const items = visibleAffiliations.map((affiliation) => (
    `<span class="result-affiliation-item${affiliation.isCurrent ? " is-current" : ""}"><sup>${affiliation.number}</sup>${escapeHtml(affiliation.institution)}</span>`
  ));
  const remaining = affiliations.length - visibleAffiliations.length;
  if (remaining > 0) {
    items.push(`<span class="result-affiliation-more">+${remaining} more</span>`);
  }
  return items.join("; ");
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
        _related_records: [],
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
    paper._related_records.push(record);
  });
  return [...papersByIdentity.values()].map((paper) => {
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
    record.coverage_status,
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

function recordMatchesActiveFilters(record, keywordTerms) {
  const searchableText = recordSearchText(record);
  const matchesKeyword = keywordTerms.every((term) => searchableText.includes(term));
  const matchesTask = taskFilter.value === "all" || record.task === taskFilter.value;
  const matchesEntryType =
    entryTypeFilter.value === "all" || getEntryType(record) === entryTypeFilter.value;
  const matchesVenue =
    venueFilter.value === "all" || venueFilterValue(record) === venueFilter.value;
  const selectedVersion = preprintFilter.value;
  const matchesVersion =
    selectedVersion === "all" ||
    (selectedVersion === "preprint-only" && isPreprintOnlyRecord(record)) ||
    (selectedVersion === "published" && hasPublishedVenue(record)) ||
    (selectedVersion === "has-arxiv" && hasArxivVersion(record)) ||
    (selectedVersion === "no-arxiv" && !hasArxivVersion(record));
  const year = publicationYear(record);
  const minimumYear = yearFilterValue(minYearFilter);
  const maximumYear = yearFilterValue(maxYearFilter);
  const matchesMinimumYear = minimumYear === null || (year !== null && year >= minimumYear);
  const matchesMaximumYear = maximumYear === null || (year !== null && year <= maximumYear);
  return (
    matchesKeyword &&
    matchesTask &&
    matchesEntryType &&
    matchesVenue &&
    matchesVersion &&
    matchesMinimumYear &&
    matchesMaximumYear
  );
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
  if (datasetPaperWithoutLocationCount) {
    datasetPaperWithoutLocationCount.textContent = paperCoverageRecords.filter(
      (record) => !record.has_map_location,
    ).length;
  }
  datasetInstitutionCount.textContent = normalizedSetSize(
    datasetRecords.map(recordInstitution),
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
    const key = normalizedSearchText(institution);
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

function recordDoi(record) {
  for (const candidate of [record.doi, record.doi_url]) {
    const doi = normalizedDoi(candidate);
    if (doi) {
      return doi;
    }
  }
  return "";
}

function recordLandingPageUrl(record) {
  for (const candidate of [
    record.paper_url,
    record.primary_url,
    record.landing_page_url,
    record.url,
  ]) {
    const url = safeHttpUrl(candidate);
    if (url) {
      return url;
    }
  }
  return "";
}

function paperExternalLinks(record, includeArxivId = false) {
  const doi = recordDoi(record);
  const doiUrl = doi ? safeHttpUrl(`https://doi.org/${doi}`) : "";
  const arxivId = recordArxivId(record);
  const arxivUrl = recordArxivUrl(record);
  const safeArxivUrl = safeHttpUrl(arxivUrl);
  const openalexUrl = safeHttpUrl(record.openalex_url);
  const paperUrl = recordLandingPageUrl(record);
  const paperLinkIsDistinct = paperUrl
    && ![doiUrl, safeArxivUrl, openalexUrl].includes(paperUrl);

  return [
    paperLinkIsDistinct ? externalLink(paperUrl, "Paper") : "",
    doiUrl ? externalLink(doiUrl, "DOI") : "",
    safeArxivUrl
      ? externalLink(
          safeArxivUrl,
          includeArxivId && arxivId ? `arXiv ${arxivId}` : "arXiv",
        )
      : "",
    openalexUrl ? externalLink(openalexUrl, "OpenAlex") : "",
  ].filter(Boolean);
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
  const year = record.publication_year ?? record.year ?? "Unknown";
  const venue = getRecordVenue(record) || "unknown";
  const publicationType = record.publication_type || "Unknown";
  const entryType = getEntryType(record);
  const entryTypeLabel = getEntryTypeLabel(entryType);
  const location = recordLocation(record) || "Unknown";
  const subtaskRow = record.subtask
    ? `<dt>Subtask</dt><dd>${escapeHtml(formatTask(record.subtask))}</dd>`
    : "";
  const detailLinks = paperExternalLinks(record, true);
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
  const aiSummary = String(record.ai_summary || "").trim();
  const aiSummaryBlock = `
    <section class="paper-text-section paper-ai-summary-section">
      <h4>AI-generated summary</h4>
      <p class="paper-ai-summary${aiSummary ? "" : " is-unavailable"}">${escapeHtml(aiSummary || "AI summary is not generated yet.")}</p>
    </section>
  `;
  const affiliationsBlock = affiliations.length
    ? `<section class="paper-details-affiliation-section" aria-labelledby="paper-affiliations-heading"><h4 id="paper-affiliations-heading">Affiliations</h4><ol class="paper-details-affiliations">${affiliations.map((affiliation) => `<li${affiliation.isCurrent ? ' class="is-current is-hover-institution"' : ""}><div class="affiliation-heading"><span class="affiliation-institution">${escapeHtml(affiliation.institution)}</span>${affiliation.location ? `<span class="affiliation-location"> · ${escapeHtml(affiliation.location)}</span>` : ""}</div>${affiliation.authors.length ? `<div class="affiliation-authors">${affiliation.authors.map(escapeHtml).join("; ")}</div>` : ""}</li>`).join("")}</ol></section>`
    : "";

  return `
    <div class="popup-badges">
      <span class="popup-badge popup-task">${escapeHtml(formatTask(record.task))}</span>
      <span class="popup-badge entry-type-badge">${escapeHtml(entryTypeLabel)}</span>
      ${versionBadge}
      ${confidenceBadge}
    </div>
    <h3 class="popup-title">${escapeHtml(recordTitle(record))}</h3>
    <dl class="popup-details paper-details-summary">
      <dt>Authors</dt><dd>${authors}</dd>
      <dt class="current-institution-label">Current institution</dt><dd class="current-institution-value paper-current-institution${currentAffiliation ? " is-active is-hover-institution" : ""}">${currentAffiliationNumber}${escapeHtml(recordInstitution(record) || "Unknown")}</dd>
      <dt>Year</dt><dd>${escapeHtml(year)}</dd>
      <dt>Venue</dt><dd>${escapeHtml(venue)}</dd>
    </dl>
    ${linksBlock}
    ${affiliationsBlock}
    ${abstractBlock}
    ${aiSummaryBlock}
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
  const venue = getRecordVenue(record);
  const isPaperView = resultsView === "papers";
  const entryTypeLabel = getEntryTypeLabel(getEntryType(record));
  const affiliations = normalizedRecord.affiliations;
  const subtask = record.subtask
    ? `<span class="result-task result-subtask">${escapeHtml(formatTask(record.subtask))}</span>`
    : "";
  const venueRow = venue
    ? `<p class="result-venue">${escapeHtml(venue)}</p>`
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
  const visibleRecords = records
    .filter((record) => recordMatchesActiveFilters(record, keywordTerms))
    .sort((first, second) => compareRecordsForSort(first, second, sortControl.value));
  const visiblePaperRecords = paperRecords
    .filter((record) => recordMatchesActiveFilters(record, keywordTerms))
    .sort((first, second) => compareRecordsForSort(first, second, sortControl.value));

  currentFilteredRecords = visibleRecords;
  currentFilteredPaperRecords = visiblePaperRecords;

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

  updateDatasetStatistics(visibleRecords, visiblePaperRecords);
  renderHeaderStatistics(visibleRecords, visiblePaperRecords);
  renderResults(visibleRecords, visiblePaperRecords);
  mapStatus.classList.toggle("error", false);
  mapStatus.classList.toggle("paper-highlight-active", false);
  mapStatus.textContent = baseMapStatusText(visibleRecords);
  scheduleMapResize();
}

function configureYearRange() {
  const filterSourceRecords = paperRecords.length ? paperRecords : records;
  const years = filterSourceRecords.map(publicationYear).filter((year) => year !== null);
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
  const filterSourceRecords = paperRecords.length ? paperRecords : records;
  filterSourceRecords.forEach((record) => {
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
  currentFilteredRecords = [];
  currentFilteredPaperRecords = [];
  currentDisplayedResults = [];
  markerLayer.clearLayers();
  hoverConnectionLayer.clearLayers();
  selectedConnectionLayer.clearLayers();
  visibleMarkerEntries = [];
  hoveredPaperIdentity = "";
  updateDatasetStatistics(records, paperRecords);
  renderHeaderStatistics(records, paperRecords);
  renderResults(records, paperRecords);
  mapStatus.textContent = message;
  mapStatus.classList.toggle("error", isError);
}

function updateDatasetLabels() {
  if (datasetName === "sample") {
    datasetStatusNote.textContent =
      "Fictional sample";
    datasetNoticeCopy.textContent =
      "These fictional records are provided only for interface testing and are not literature data.";
    mapStatus.textContent = "Loading fictional sample data...";
    datasetStatisticsNote.textContent =
      "Institution-level records matching the current filters.";
  } else if (datasetName === "preview") {
    datasetStatusNote.textContent =
      "Uncurated public preview";
    datasetNoticeCopy.textContent =
      "This public preview is generated from OpenAlex candidate metadata and local manual review caches. It includes paper-level coverage even when institution/location data is incomplete; only papers with valid reviewed coordinates appear as map markers.";
    mapStatus.textContent = "Loading public preview data...";
    datasetStatisticsNote.textContent =
      "Paper coverage includes records without map markers; map records require institution coordinates.";
  } else {
    datasetStatusNote.textContent =
      "Uncurated candidate data";
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
  const repeatsDatasetNotice =
    /automatically generated candidate metadata/i.test(warning) ||
    /not a manually curated bibliography/i.test(warning);
  if (warning && !repeatsDatasetNotice) {
    datasetNoticeCopy.textContent = `${datasetNoticeCopy.textContent} ${warning}`;
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
  records = normalizedData.records;
  paperRecords = normalizedData.paperRecords || [];
  displayMetadataWarning(normalizedData.metadata);
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
preprintFilter.addEventListener("change", renderRecords);
minYearFilter.addEventListener("input", renderRecords);
maxYearFilter.addEventListener("input", renderRecords);
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
  renderRecords();
  scheduleMapResize(true);
});

updateDatasetLabels();
loadData();
