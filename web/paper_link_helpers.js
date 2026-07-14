(function exposePaperLinkHelpers(root, factory) {
  const helpers = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  }
  root.PaperLinkHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers() {
  function normalizedPathname(url) {
    const pathname = url.pathname.replace(/\/+$/, "");
    return pathname || "/";
  }

  function canonicalPaperLinkTarget(value) {
    const text = String(value || "").trim();
    if (!text) {
      return "";
    }

    let url;
    try {
      url = new URL(text);
    } catch {
      return "";
    }
    if (!["http:", "https:"].includes(url.protocol) || !url.hostname) {
      return "";
    }

    const rawHostname = url.hostname.toLocaleLowerCase();
    const hostname = rawHostname.replace(/^www\./, "");
    const pathname = normalizedPathname(url);
    const arxivMatch = pathname.match(
      /^\/(?:abs|pdf)\/([a-z-]+(?:\.[a-z]{2})?\/\d{7}(?:v\d+)?|\d{4}\.\d{4,5}(?:v\d+)?)(?:\.pdf)?$/i,
    );
    if (["arxiv.org", "export.arxiv.org"].includes(hostname) && arxivMatch) {
      return `arxiv:${arxivMatch[1].toLocaleLowerCase()}`;
    }

    if (["doi.org", "dx.doi.org"].includes(hostname)) {
      let decodedPathname = pathname;
      try {
        decodedPathname = decodeURIComponent(pathname);
      } catch {
        // Keep malformed percent-encoding opaque instead of breaking rendering.
      }
      const doi = decodedPathname.replace(/^\/+/, "");
      if (/^10\.\d{4,9}\/\S+$/i.test(doi)) {
        return `doi:${doi.toLocaleLowerCase()}`;
      }
    }

    if (hostname === "openalex.org" && /^\/W\d+$/i.test(pathname)) {
      return `openalex:${pathname.slice(1).toLocaleLowerCase()}`;
    }

    const port = (
      (url.protocol === "http:" && url.port === "80")
      || (url.protocol === "https:" && url.port === "443")
    ) ? "" : url.port;
    return [
      url.protocol.toLocaleLowerCase(),
      rawHostname,
      port,
      pathname,
      url.search,
    ].join("|");
  }

  function deduplicatePaperLinks(candidates) {
    const links = candidates
      .map((candidate) => ({
        ...candidate,
        canonicalTarget: canonicalPaperLinkTarget(candidate.url),
      }))
      .filter((candidate) => candidate.canonicalTarget);
    const dedicatedTargets = new Set(
      links
        .filter((candidate) => candidate.label !== "Paper")
        .map((candidate) => candidate.canonicalTarget),
    );
    const seenTargets = new Set();

    return links.filter((candidate) => {
      if (
        candidate.label === "Paper"
        && dedicatedTargets.has(candidate.canonicalTarget)
      ) {
        return false;
      }
      if (seenTargets.has(candidate.canonicalTarget)) {
        return false;
      }
      seenTargets.add(candidate.canonicalTarget);
      return true;
    }).map(({ canonicalTarget, ...candidate }) => candidate);
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

  function normalizedDoi(value) {
    const doi = String(value || "")
      .trim()
      .replace(/^doi:\s*/i, "")
      .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")
      .trim();
    return /^10\.\d{4,9}\/\S+$/i.test(doi) ? doi : "";
  }

  function firstOfficialUrl(values) {
    for (const value of values) {
      const url = safeHttpUrl(value);
      const target = canonicalPaperLinkTarget(url);
      if (
        url
        && !target.startsWith("arxiv:")
        && !target.startsWith("doi:")
        && !target.startsWith("openalex:")
      ) {
        return url;
      }
    }
    return "";
  }

  function publishedVersionUrl(record) {
    const publisherUrl = firstOfficialUrl([
      record.publisher_url,
      record.published_url,
      record.official_publication_url,
      record.paper_url,
    ]);
    if (publisherUrl) {
      return publisherUrl;
    }

    for (const value of [record.doi, record.doi_url]) {
      const doi = normalizedDoi(value);
      if (doi && !doi.toLocaleLowerCase().startsWith("10.48550/arxiv.")) {
        return safeHttpUrl(`https://doi.org/${doi}`);
      }
    }

    return firstOfficialUrl([
      record.venue_url,
      record.proceedings_url,
      record.landing_page_url,
      record.primary_url,
      record.url,
    ]);
  }

  function paperVersionLinks(record, arxivUrl = "") {
    const preprintUrl = safeHttpUrl(
      arxivUrl || record.preprint_url || record.arxiv_url,
    );
    return deduplicatePaperLinks([
      { label: "Paper", url: publishedVersionUrl(record) },
      { label: "Preprint", url: preprintUrl },
    ]);
  }

  return {
    canonicalPaperLinkTarget,
    deduplicatePaperLinks,
    paperVersionLinks,
    publishedVersionUrl,
  };
}));
