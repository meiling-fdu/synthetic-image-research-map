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

  return { canonicalPaperLinkTarget, deduplicatePaperLinks };
}));
