(function exposePaperSearchHelpers(root, factory) {
  const helpers = factory(typeof module === "object" && module.exports
    ? require("./paper_link_helpers.js") : root.PaperLinkHelpers);
  if (typeof module === "object" && module.exports) module.exports = helpers;
  root.PaperSearchHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers(links) {
  function normalizedIdentifier(value) {
    let text = String(value || "").trim();
    const target = links.canonicalPaperLinkTarget(text);
    if (/^(doi|arxiv):/.test(target)) text = target;
    const doi = links.normalizedDoi(text);
    if (doi) return `doi:${doi.toLowerCase()}`;
    const arxiv = text.replace(/^arxiv:\s*/i, "");
    if (/^(?:[a-z-]+(?:\.[a-z]{2})?\/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?$/i.test(arxiv)) {
      return `arxiv:${arxiv.replace(/v\d+$/i, "").toLowerCase()}`;
    }
    return "";
  }

  function identifiers(record) {
    return [...new Set([
      record.doi, record.doi_url, record.arxiv_id, record.arxiv_url,
      record.preprint_url, record.paper_url, record.primary_url, record.url,
    ].map(normalizedIdentifier).filter(Boolean))];
  }

  // Recognized identifiers stay whole, including punctuation. Delimiters prevent
  // one complete DOI/arXiv ID from matching a different ID with the same prefix.
  function identifierSearchText(record) {
    return identifiers(record).map((id) => `[${id}]`).join(" ");
  }

  function queryTerms(value, normalize) {
    const identifier = normalizedIdentifier(value);
    return identifier ? [`[${identifier}]`] : normalize(value).split(/\s+/).filter(Boolean);
  }

  function relevanceScore(fields, query, normalize) {
    const text = normalize(query);
    if (!text) return 0;
    if (fields.title === text) return 10000;
    const identifier = normalizedIdentifier(query);
    if (identifier && fields.identifiers.includes(identifier)) return 9000;
    if (fields.title.startsWith(text)) return 8000;
    const terms = [...new Set(text.split(/\s+/))];
    const weights = { title: 4000, authors: 1000, institutions: 500, venue: 250,
      taxonomy: 125, abstract: 16, year: 8 };
    // Each distinct term contributes its strongest field match. Averaging keeps
    // every partial match below an exact title/identifier or title prefix.
    return terms.reduce((total, term) => total + Math.max(0,
      ...Object.entries(weights).map(([field, weight]) => (
        fields[field]?.includes(term) ? weight : 0
      ))), 0) / terms.length;
  }

  return { normalizedIdentifier, identifiers, identifierSearchText, queryTerms, relevanceScore };
}));
