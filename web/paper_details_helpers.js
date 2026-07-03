(function exposePaperDetailsHelpers(root, factory) {
  const helpers = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  }
  root.PaperDetailsHelpers = helpers;
}(typeof globalThis !== "undefined" ? globalThis : this, function buildHelpers() {
  function renderPaperAuthors(paper, escapeHtml, currentAffiliationNumber = null) {
    const authors = Array.isArray(paper?.authors) ? paper.authors : [];
    return authors.map((author) => {
      const numbers = Array.isArray(author.affiliation_indices)
        ? author.affiliation_indices
        : [];
      const superscript = numbers.length
        ? `<sup class="author-affiliation-numbers" aria-label="Affiliations ${numbers.join(", ")}">${numbers.join(",")}</sup>`
        : "";
      const isActive = author.is_current_marker_author === true || (
        currentAffiliationNumber !== null
        && numbers.includes(currentAffiliationNumber)
      );
      const authorHtml = `<span class="paper-author${isActive ? " is-active-institution-author is-hover-author" : ""}">${escapeHtml(author.name)}${superscript}</span>`;
      return isActive
        ? `<strong class="current-institution-author">${authorHtml}</strong>`
        : authorHtml;
    }).join(", ");
  }

  return { renderPaperAuthors };
}));
