(function exposePaperDetailsHelpers(root, factory) {
  const helpers = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  }
  root.PaperDetailsHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers() {
  function canonicalNameTokens(value) {
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
      .normalize("NFKD")
      .replace(/\p{M}/gu, "")
      .toLocaleLowerCase()
      .match(/[\p{L}\p{N}]+/gu) || [];
  }

  function namesMatch(left, right) {
    const leftTokens = canonicalNameTokens(left);
    const rightTokens = canonicalNameTokens(right);
    if (!leftTokens.length || leftTokens.length !== rightTokens.length) {
      return false;
    }
    if (leftTokens.every((token, index) => token === rightTokens[index])) {
      return true;
    }
    const sortedLeft = [...leftTokens].sort();
    const sortedRight = [...rightTokens].sort();
    if (sortedLeft.every((token, index) => token === sortedRight[index])) {
      return true;
    }
    if (leftTokens.length < 3) {
      return false;
    }
    const tokenMatches = (leftToken, rightToken) => (
      leftToken === rightToken
      || (
        Math.min(leftToken.length, rightToken.length) === 1
        && leftToken[0] === rightToken[0]
      )
    );
    return leftTokens.every((token, index) => tokenMatches(token, rightTokens[index]))
      || leftTokens.every((token, index) => (
        tokenMatches(token, rightTokens[rightTokens.length - index - 1])
      ));
  }

  const PUBLICATION_TYPE_LABELS = {
    journal: "Journal",
    journal_article: "Journal",
    conference: "Conference",
    conference_paper: "Conference",
    workshop: "Workshop",
    workshop_paper: "Workshop",
    preprint: "Preprint",
    book: "Book",
    book_chapter: "Book Chapter",
    chapter: "Book Chapter",
    thesis: "Thesis",
    report: "Report",
    position_paper: "Position Paper",
    dataset_paper: "Dataset Paper",
  };

  function publicationTypeLabel(value) {
    const rawValue = String(value || "").trim();
    if (!rawValue) return "";
    const normalized = rawValue.toLocaleLowerCase().replace(/[\s-]+/g, "_");
    return PUBLICATION_TYPE_LABELS[normalized] || normalized
      .split("_")
      .filter(Boolean)
      .map((part) => part[0].toLocaleUpperCase() + part.slice(1))
      .join(" ");
  }

  function publicationMetadata(record, venueValue, yearValue) {
    const typeLabel = publicationTypeLabel(record?.publication_type);
    const rawVenue = String(venueValue || "").trim();
    // Only strip an explicitly delimited duplicate label. A venue beginning
    // with "Journal" or "Conference" may legitimately contain that word.
    const escapedType = typeLabel.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const duplicatePrefix = typeLabel
      ? new RegExp(`^${escapedType}\\s*(?:[:|–—-])\\s*`, "i")
      : null;
    const venue = duplicatePrefix ? rawVenue.replace(duplicatePrefix, "").trim() : rawVenue;
    const year = yearValue === null || yearValue === undefined
      ? ""
      : String(yearValue).trim();
    return { typeLabel, venue, year };
  }

  function renderPaperAuthorItems(
    paper,
    escapeHtml,
    currentAffiliationNumber = null,
  ) {
    const authors = Array.isArray(paper?.authors) ? paper.authors : [];
    return authors.map((author) => {
      const authorName = String(
        author && typeof author === "object"
          ? author.name || author.display_name || author.author || ""
          : author || "",
      ).trim();
      if (!authorName) {
        return "";
      }
      const numbers = Array.isArray(author.affiliation_indices)
        ? [...new Set(author.affiliation_indices)]
        : [];
      const superscript = numbers.length
        ? `<sup class="author-affiliation-numbers" aria-label="Affiliations ${numbers.join(", ")}">${numbers.join(",")}</sup>`
        : "";
      const isActive = author.is_current_marker_author === true || (
        currentAffiliationNumber !== null
        && numbers.includes(currentAffiliationNumber)
      );
      const nonInstitutional = author.affiliation_status === "non_institutional"
        && author.affiliation_review?.status === "non_institutional";
      const roleText = author.affiliation_review?.reason_kind === "contact_only"
        ? "No institution listed (contact only)"
        : author.affiliation_review?.source_text;
      const role = nonInstitutional
        ? `<span class="author-role" title="Reviewed: no institutional affiliation in the publication"> (${escapeHtml(roleText)})</span>`
        : "";
      const authorHtml = `<span class="paper-author${isActive ? " is-active-institution-author is-hover-author" : ""}">${escapeHtml(authorName)}${superscript}${role}</span>`;
      return isActive
        ? `<strong class="current-institution-author">${authorHtml}</strong>`
        : authorHtml;
    }).filter(Boolean);
  }

  function renderPaperAuthors(
    paper,
    escapeHtml,
    currentAffiliationNumber = null,
    visibleLimit = Infinity,
    regionId = "",
  ) {
    const authorItems = renderPaperAuthorItems(
      paper,
      escapeHtml,
      currentAffiliationNumber,
    );
    if (authorItems.length <= visibleLimit) {
      return authorItems.join(", ");
    }
    return [
      '<span data-paper-authors>',
      authorItems.slice(0, visibleLimit).join(", "),
      `<span class="paper-authors-overflow" hidden${regionId ? ` id="${escapeHtml(regionId)}"` : ""}>, ${authorItems.slice(visibleLimit).join(", ")}</span>`,
      `<button type="button" class="paper-authors-toggle" aria-expanded="false"${regionId ? ` aria-controls="${escapeHtml(regionId)}"` : ""}>Show all authors</button>`,
      '</span>',
    ].join("");
  }

  function togglePaperAuthors(button) {
    const group = button.closest("[data-paper-authors]");
    const overflow = group?.querySelector(".paper-authors-overflow");
    if (!overflow) return false;
    // State belongs to this rendered disclosure, not a paper/title cache.
    // Update in place to retain focus; a new render starts collapsed.
    const isExpanded = button.getAttribute("aria-expanded") === "true";
    overflow.hidden = isExpanded;
    button.setAttribute("aria-expanded", String(!isExpanded));
    button.textContent = isExpanded ? "Show all authors" : "Show fewer authors";
    return true;
  }

  return {
    namesMatch,
    publicationMetadata,
    publicationTypeLabel,
    renderPaperAuthorItems,
    renderPaperAuthors,
    togglePaperAuthors,
  };
}));
